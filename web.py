from flask import Flask, render_template, request,make_response, jsonify
import requests
import json
import urllib3
import time

import random
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
    if firebase_config is not None:
        cred_dict = json.loads(firebase_config)
        cred = credentials.Certificate(cred_dict)
    else:
        print("錯誤：找不到 serviceAccountKey.json 也找不到環境變數 FIREBASE_CONFIG")
        cred = credentials.Certificate('serviceAccountKey.json')

if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

db = firestore.client()


from flask import Flask, render_template, request
from datetime import datetime

app = Flask(__name__)
@app.route("/")
def index():
    return render_template("index.html")
    link = "<h1>歡迎進入許允蓁的首頁</h1>"
    link += "<a href='https://bot.dialogflow.com/你的專屬ID' target='_blank'><b>[聊天機器人] Web Demo 測試連結</b></a><br><br>"
    
    link += "<a href=/mis>課程</a><br>"
    link += "<a href=/today>今天日期</a><br>"
    link += "<a href=/about>關於允蓁</a><br>"
    link += "<a href=/welcome?u=允蓁&dep=靜宜企管>GET傳值</a><br>"
    link += "<a href=/account>POST傳值(帳號密碼)</a><br>"
    link += "<a href=/math>數學運算</a><br>"
    link += "<a href=/cup>擲茭</a><br>"
    link += "<br><a href=/read>讀取Firestore資料(根據lab遞減排序,取前4)</a><br>"
    link += "<a href=/search_page>查詢老師與研究室</a><br>"
    link += "<br><a href=/movies>查詢即將上映電影</a><br>"
    link += "<br><a href=/movie2>讀取開眼電影即將上映影片，寫入Firestore</a><br>"
    link += "<a href='/movie3'>查詢即將上映電影資訊 (關鍵字查詢)</a><br>"
    link += "<a href='/traffic'>台中市十大肇事路口查詢</a><br>"
    link += "<a href='/weather'>查詢縣市天氣</a><br>"
    link += "<a href='/rate'>本週新片進DB</a><br>"

    link += '<script src="https://www.gstatic.com/dialogflow-console/fast/messenger/bootstrap.js?v=1"></script>'
    link += '<df-messenger intent="WELCOME" chat-title="許允蓁(行銷四B)的聊天機器人" agent-id="74b4f6e1-e760-47d2-a4b4-149b3dbddcfa" language-code="zh-tw"></df-messenger>'

    return link

@app.route("/webhook4", methods=["POST"])
def webhook4():
    req = request.get_json(force=True)
    action = req.get("queryResult", {}).get("action")
    info = "我不確定你想執行的動作是什麼呢。"

    if action == "rateChoice":
        rate = req.get("queryResult", {}).get("parameters", {}).get("rate", "")
        
        if rate == "普級":
            rate = "普遍級"

        db = firestore.client()
        movies_ref = db.collection("本週新片含分級") 
        query = movies_ref.where("rate", "==", rate).stream()
        
        movie_list = []
        for doc in query:
            movie_list.append(doc.to_dict().get("title", ""))
        
        if movie_list:
            movies_str = "、\n".join(movie_list)
            info = f"我是許允蓁設計的電影聊天機器人，為您查詢到分級為【{rate}】的電影有：\n\n{movies_str}"
        else:
            info = f"我是許允蓁設計的電影聊天機器人，目前資料庫中沒有【{rate}】的電影喔！"
            
    elif action == "MovieDetail":
        question = req.get("queryResult", {}).get("parameters", {}).get("filmq", "")
        keyword = req.get("queryResult", {}).get("parameters", {}).get("any", "")
        info = "我是許允蓁開發的電影聊天機器人，您要查詢電影的" + question + "，關鍵字是：" + keyword + "\n\n"

        if question == "片名":
            db = firestore.client()
            collection_ref = db.collection("本週新片含分級") 
            docs = collection_ref.get()
            found = False
            
            for doc in docs:
                movie_data = doc.to_dict()
                if keyword in movie_data.get("title", ""):
                    found = True 
                    info += "片名：" + movie_data.get("title", "") + "\n"
                    info += "海報：" + movie_data.get("picture", "") + "\n"
                    info += "影片介紹：" + movie_data.get("hyperlink", "") + "\n"
                    info += "片長：" + str(movie_data.get("showLength", "")) + " 分鐘\n"
                    info += "分級：" + movie_data.get("rate", "") + "\n" 
                    info += "上映日期：" + movie_data.get("showDate", "") + "\n\n"
                    
            if not found:
                info += "很抱歉，目前無符合這個關鍵字的相關電影喔"

    return make_response(jsonify({"fulfillmentText": info}))

@app.route("/webhook2", methods=["POST"])
def webhook2():
    req = request.get_json(force=True)
    action = req.get("queryResult", {}).get("action")
    
    if action == "rateChoice":
        rate = req["queryResult"]["parameters"].get("rate")
        
        movies_ref = db.collection("本週新片含分級")
        query = movies_ref.where("rate", "==", rate).stream()
        
        movie_list = []
        for doc in query:
            movie_list.append(doc.to_dict().get("title", "未知片名"))
        
        if movie_list:
            movies_str = "、\n".join(movie_list)
            info = f"我是許允蓁設計的電影聊天機器人,您選擇的電影分級是：{rate}，相關電影：\n\n{movies_str}"
        else:
            info = f"我是許允蓁設計的電影聊天機器人,本週目前沒有 {rate} 的新電影喔！"
            
    else:
        info = "我不確定你想執行的動作是什麼呢。"

    return make_response(jsonify({"fulfillmentText": info}))

@app.route("/webhook", methods=["POST"])
def webhook():
    # build a request object
    req = request.get_json(force=True)
    # fetch queryResult from json
    action =  req["queryResult"]["action"]
    #msg =  req.get["queryResult"].get["queryText"]
    #info = "我是許允蓁設計的電影聊天機器人, 動作：" + action + " 查詢內容：" + msg
    if (action == "rateChoice"):
        rate =  req["queryResult"]["parameters"]["rate"]
        info = "我是許允蓁設計的電影聊天機器人,您選擇的電影分級是：" + rate + "，相關電影：\n"
    return make_response(jsonify({"fulfillmentText": info}))

@app.route("/rate")
def rate():
    #本週新片
    url = "https://www.atmovies.com.tw/movie/new/"
    Data = requests.get(url)
    Data.encoding = "utf-8"
    sp = BeautifulSoup(Data.text, "html.parser")
    lastUpdate = sp.find(class_="smaller09").text[5:]
    print(lastUpdate)
    print()

    result=sp.select(".filmList")

    for x in result:
        title = x.find("a").text
        introduce = x.find("p").text

        movie_id = x.find("a").get("href").replace("/", "").replace("movie", "")
        hyperlink = "http://www.atmovies.com.tw/movie/" + movie_id
        picture = "https://www.atmovies.com.tw/photo101/" + movie_id + "/pm_" + movie_id + ".jpg"

        r = x.find(class_="runtime").find("img")
        rate = ""
        if r != None:
            rr = r.get("src").replace("/images/cer_", "").replace(".gif", "")
            if rr == "G":
                rate = "普遍級"
            elif rr == "P":
                rate = "保護級"
            elif rr == "F2":
                rate = "輔12級"
            elif rr == "F5":
                rate = "輔15級"
            else:
                rate = "限制級"

        t = x.find(class_="runtime").text

        t1 = t.find("片長")
        t2 = t.find("分")
        showLength = t[t1+3:t2]

        t1 = t.find("上映日期")
        t2 = t.find("上映廳數")
        showDate = t[t1+5:t2-8]

        doc = {
            "title": title,
            "introduce": introduce,
            "picture": picture,
            "hyperlink": hyperlink,
            "showDate": showDate,
            "showLength": int(showLength),
            "rate": rate,
            "lastUpdate": lastUpdate
        }

        db = firestore.client()
        doc_ref = db.collection("本週新片含分級").document(movie_id)
        doc_ref.set(doc)
    return "本週新片已爬蟲及存檔完畢，網站最近更新日期為：" + lastUpdate

@app.route('/weather', methods=['GET', 'POST'])
def weather_query():
    weather_info = None
    search_city = ""
    error_msg = ""

    if request.method == 'POST':
        search_city = request.form.get('city_name')
        
        if search_city:
            search_city = search_city.replace("台", "臺")
            
            try:
                with open('py/weather.json', 'r', encoding='utf-8') as file:
                    json_data = json.load(file)
                
                locations = json_data["records"]["location"]
                for loc in locations:
                    if loc["locationName"] == search_city:
                        weather_info = {
                            "city": loc["locationName"],
                            "status": loc["weatherElement"][0]["time"][0]["parameter"]["parameterName"],
                            "rain": loc["weatherElement"][1]["time"][0]["parameter"]["parameterName"]
                        }
                        break
                
                if not weather_info:
                    error_msg = f"找不到「{search_city}」的天氣資料，請確認輸入是否正確。"
                        
            except FileNotFoundError:
                error_msg = "系統錯誤：找不到 weather.json 檔案，請確認檔案位置！"
            except Exception as e:
                error_msg = f"發生錯誤：{e}"

    return render_template('weather.html', info=weather_info, search_city=search_city, error_msg=error_msg)

@app.route('/traffic', methods=['GET', 'POST'])
def traffic_query():
    results = []
    search_road = ""
    error_msg = ""

    if request.method == 'POST':
        search_road = request.form.get('road_name')
        
        if search_road:
            try:
                with open('py/data.json', 'r', encoding='utf-8') as file:
                    data_list = json.load(file) 
                    
                for item in data_list:
                    if search_road in item.get("路口名稱", ""):
                        results.append(item)
                        
            except FileNotFoundError:
                error_msg = "系統錯誤：找不到 py/data.json 檔案！"
            except Exception as e:
                error_msg = f"發生錯誤：{e}"

    return render_template('traffic.html', results=results, search_road=search_road, error_msg=error_msg)

@app.route("/movie2")
def movie2():
    url = "http://www.atmovies.com.tw/movie/next/"
    Data = requests.get(url)
    Data.encoding = "utf-8"
    sp = BeautifulSoup(Data.text, "html.parser")
    result = sp.select(".filmListAllX li")
    lastUpdate = sp.find("div", class_="smaller09").text[5:]

    db = firestore.client()
    batch = db.batch()

    for item in result:
        picture = item.find("img").get("src").replace(" ", "")
        title = item.find("div", class_="filmtitle").text
        
        a_tag = item.find("div", class_="filmtitle").find("a")
        movie_id = a_tag.get("href").replace("/", "").replace("movie", "")
        hyperlink = "http://www.atmovies.com.tw" + a_tag.get("href")
        
        runtime_div = item.find("div", class_="runtime")
        if runtime_div:
            show = runtime_div.text.replace("上映日期：", "").replace("片長：", "").replace("分", "")
            showDate = show[0:10] if len(show) >= 10 else "未知"
            showLength = show[13:] if len(show) > 13 else "未知"
        else:
            showDate = "未知"
            showLength = "未知"

        doc = {
            "title": title,
            "picture": picture,
            "hyperlink": hyperlink,
            "showDate": showDate,
            "showLength": showLength,
            "lastUpdate": lastUpdate
        }

        doc_ref = db.collection("電影2A").document(movie_id)
        batch.set(doc_ref, doc)  

    batch.commit()
    
    return "近期上映電影已爬蟲及存檔完畢，網站最近更新日期為：" + lastUpdate

@app.route("/movie3")
def movie3():
    keyword = request.args.get("keyword", "")
    movies_list = []
    
    if keyword:
        db = firestore.client()
        docs = db.collection("電影2A").stream()
        
        for doc in docs:
            movie_data = doc.to_dict()
            # 判斷輸入的關鍵字是否包含在電影標題中
            if keyword in movie_data.get("title", ""):
                movies_list.append(movie_data)
                
    return render_template("movie3.html", movies=movies_list, keyword=keyword)

@app.route('/search_page')
def search_page():
    page = "<h2>查詢老師與研究室</h2>"
    page += "<form action='/search' method='GET'>"
    page += "請輸入老師名字關鍵字：<input type='text' name='keyword' required> "
    page += "<button type='submit'>開始查詢</button>"
    page += "</form>"
    page += "<br><br><a href='/'>返回首頁</a>"
    return page

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

@app.route("/movies")
def upcoming_movies():
    try:
        url = "http://www.atmovies.com.tw/movie/next/"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        
        response = requests.get(url, headers=headers)
        response.encoding = "utf-8" 
        
        soup = BeautifulSoup(response.text, "html.parser")
    
        all_links = soup.find_all("a")
        
        result_html = "<h2>即將上映電影</h2>"
        result_html += "<ul style='line-height: 1.8; font-size: 18px;'>"
        
        added_urls = set()
        count = 0
        
        for item in all_links:
            title = item.text.strip()
            href = item.get("href", "")
            
            if title and href.startswith("/movie/f"):
                full_link = f"http://www.atmovies.com.tw{href}"
                
                if full_link not in added_urls:
                    result_html += f"<li><a href='{full_link}' target='_blank'>{title}</a></li>"
                    added_urls.add(full_link)
                    count += 1
                    
        result_html += "</ul>"
        
        if count == 0:
            result_html += "<p style='color:red;'>有成功連線，但沒有抓出任何電影，可能是網站大改版了！</p>"
            
        result_html += "<br><a href='/'>返回首頁</a>"
        
        return result_html
        
    except Exception as e:
        return f"<h2>爬蟲發生錯誤！</h2><p>錯誤訊息：{e}</p><br><a href='/'>返回首頁</a>"

if __name__ == "__main__":
	app.run(debug=True)



