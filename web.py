import requests
from bs4 import BeautifulSoup

import os
import json
import firebase_admin
from firebase_admin import credentials, firestore

# 判斷是在 Vercel 還是本地
if os.path.exists('serviceAccountKey.json'):
    # 本地環境：讀取檔案
    cred = credentials.Certificate('serviceAccountKey.json')
else:
   
    firebase_config = os.environ.get('FIREBASE_CONFIG')
    cred_dict = json.loads(firebase_config)
    cred = credentials.Certificate(cred_dict)

# 初始化 Firebase (加入防重複啟動機制)
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

db = firestore.client()


from flask import Flask, render_template, request
from datetime import datetime

app = Flask(__name__)

@app.route("/")
def index():
    link = "<h1>歡迎進入許允蓁的首頁</h1>"
    link += "<a href=/mis>課程</a><br>"
    link += "<a href=/today>今天日期</a><br>"
    link += "<a href=/about>關於允蓁</a><br>"
    link += "<a href=/welcome?u=允蓁&dep=靜宜企管>GET傳值</a><br>"
    link += "<a href=/account>POST傳值(帳號密碼)</a><br>"
    link += "<a href=/math>數學運算</a><br>"
    link += "<a href=/cup>擲茭</a><br>"
    link += "<br><a href=/read>讀取Firestore資料(根據lab遞減排序,取前4)</a><br>"
    # === 新增這行：點擊後會前往 /search_page 頁面 ===
    link += "<a href=/search_page>查詢老師與研究室</a><br>"
    return link

# === 這是點擊連結後，進入的「輸入關鍵字」頁面 ===
@app.route('/search_page')
def search_page():
    page = "<h2>查詢老師與研究室</h2>"
    page += "<form action='/search' method='GET'>"
    page += "請輸入老師名字關鍵字：<input type='text' name='keyword' required> "
    page += "<button type='submit'>開始查詢</button>"
    page += "</form>"
    page += "<br><br><a href='/'>返回首頁</a>"
    return page

# === 這是按下查詢後，顯示「結果」的頁面 ===
@app.route('/search')
def search_teacher():
    keyword = request.args.get('keyword', '')
    result_page = f"<h2>「{keyword}」的查詢結果：</h2>"
    
    if keyword:
        teachers_ref = db.collection('靜宜資管2026a')
        docs = teachers_ref.stream()

        found = False 
        
        for doc in docs:
            teacher_data = doc.to_dict()
            teacher_name = teacher_data.get('name', '')
            
            if keyword in teacher_name:
                room = teacher_data.get('lab', '未提供研究室')
                result_page += f"<p><strong>{teacher_name}</strong> 老師 - 研究室：{room}</p>"
                found = True
        
        if not found:
            result_page += "<p>找不到符合條件的老師！</p>"

    result_page += "<br><br><a href='/search_page'>繼續查詢</a> | <a href='/'>返回首頁</a>"
    return result_page
    
@app.route("/read")
def read():
    db = firestore.client()

    Temp = ""
    collection_ref = db.collection("靜宜資管2026a")
    docs = collection_ref.order_by("lab",direction=firestore.Query.DESCENDING).limit(4).get()
    for doc in docs:
        Temp += str(doc.to_dict()) + "<br>"

    return Temp

@app.route("/sp1")
def sp1():
    R = ""
    url = "https://hsuyc2026-a-po1l.vercel.app/about"
    Data = requests.get(url)
    Data.encoding = "utf-8"
    #print(Data.text)
    sp = BeautifulSoup(Data.text, "html.parser")
    result=sp.select("td a")
    print(result)

    for item in result:
        R += item.text + "<br>" + item.get("href") + "<br><br>"
    return R

@app.route("/mis")
def course():
    return "<h1>資訊管理導論</h1><a href=/>回到網站首頁</a>"

@app.route("/today")
def today():
    now   = datetime.now()
    year  = str(now.year)  #取得年份
    month = str(now.month) #取得月份
    day   = str(now.day)   #取得日期
    now = year + "年" + month + "月" + day + "日"
    return render_template("today.html", datetime = now)

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/welcome", methods=["GET"])
def welcome():
    x = request.values.get("u")
    y = request.values.get("dep")
    return render_template("welcome.html", name = x, dep = y)

@app.route("/account", methods=["GET", "POST"])
def account():
    if request.method == "POST":
        user = request.form["user"]
        pwd = request.form["pwd"]
        result = "您輸入的帳號是：" + user + "; 密碼為：" + pwd 
        return result
    else:
        return render_template("account.html")

@app.route("/math", methods=["GET", "POST"])
def math():
    result = ""  # 預設結果

    if request.method == "POST":
        try:
            x = int(request.form["x"])
            opt = request.form["opt"]
            y = int(request.form["y"])

            if opt == "/" and y == 0:
                result = "除數不能為0"
            else:
                if opt == "+":
                    result_value = x + y
                elif opt == "-":
                    result_value = x - y
                elif opt == "*":
                    result_value = x * y
                elif opt == "/":
                    result_value = x / y
                else:
                    result = "運算符錯誤"
                    return render_template("math.html", result=result)

                result = f"{x} {opt} {y} 的結果是 {result_value}"

        except:
            result = "請輸入正確的數字"

    return render_template("math.html", result=result)

@app.route('/cup', methods=["GET"])
def cup():
    # 檢查網址是否有 ?action=toss
    #action = request.args.get('action')
    action = request.values.get("action")
    result = None
    
    if action == 'toss':
        # 0 代表陽面，1 代表陰面
        x1 = random.randint(0, 1)
        x2 = random.randint(0, 1)
        
        # 判斷結果文字
        if x1 != x2:
            msg = "聖筊：表示神明允許、同意，或行事會順利。"
        elif x1 == 0:
            msg = "笑筊：表示神明一笑、不解，或者考慮中，行事狀況不明。"
        else:
            msg = "陰筊：表示神明否定、憤怒，或者不宜行事。"
            
        result = {
            "cup1": "/static/" + str(x1) + ".jpg",
            "cup2": "/static/" + str(x2) + ".jpg",
            "message": msg
        }
                
    return render_template('cup.html', result=result)

if __name__ == "__main__":
	app.run(debug=True)



