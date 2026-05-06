import requests, json, time
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "application/json"
}

url = "https://datacenter.taichung.gov.tw/swagger/OpenData/a1b899c0-511f-4e3d-b22b-814982a97e41"

Data = None

for i in range(5):
    try:
        Data = requests.get(url, headers=headers, verify=False, timeout=10)
        
        if Data.status_code == 200:
            break
            
    except Exception as e:
        print(f"伺服器忙碌中，等待 2 秒後進行第 {i+2} 次重試...")
        time.sleep(2)

if Data and Data.status_code == 200:
    JsonData = json.loads(Data.text)
    Result = ""
    Road = input("請輸入欲查詢的路名:")

    for item in JsonData:
        if Road in item.get("路口名稱", ""):
            Result += item.get("路口名稱", "") + "：發生" + str(item.get("總件數", "")) + "件，主因是" + item.get("主要肇因", "") + "\n\n"

    if Result == "":
        Result = "抱歉，查無相關資料！"

    print(Result.strip())
else:
    print("嘗試了 5 次還是失敗，政府的伺服器現在可能在維護中。")