from flask import Flask, jsonify
import mysql.connector
import json

app = Flask(__name__)
with open("data/taipei-attractions.json", encoding="utf-8") as json_file:
    data = json.load(json_file)

# 將取得的資料存入串列
spotsInfo = data["result"]["results"]

taipeiPool = mysql.connector.pooling.MySQLConnectionPool(
    pool_name="connectionPool",
    pool_size=1,
    pool_reset_session=True,
    host='localhost',
    database='taipeitrip',
    user='root',
    password='1qaz@WSX')

mydb = taipeiPool.get_connection()
cur = mydb.cursor()
# 將所有景點的資訊(除了圖片)存到資料庫
for i in spotsInfo:
    cur.execute("INSERT IGNORE INTO spot_info(_id, CAT, MEMO_TIME, MRT, POI, REF_WP, RowNumber, SERIAL_NO, address, avBegin, avEnd, date, description, direction, idpt, langinfo, latitude, longitude, name, rate) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                (i["_id"], i["CAT"], i["MEMO_TIME"], i["MRT"], i["POI"], i["REF_WP"], i["RowNumber"], i["SERIAL_NO"], i["address"], (i["avBegin"]).replace('/', '-'), (i["avEnd"]).replace('/', '-'), (i["date"]).replace('/', '-'), i["description"], i["direction"], i["idpt"], i["langinfo"], i["latitude"], i["longitude"], i["name"], i["rate"]))
mydb.commit()
cur.close()
mydb.close()


spotIdAndImage = {}
# 儲存一個所有照片檔案的字典
for i in spotsInfo:
    spotImageAddress = []
    spotImageAddressWithJpgPng = []
    _id = i["_id"]
    spotImageAddress = i["file"].split('https://')
    # pop為根據索引刪除元素
    spotImageAddress.pop(0)
    spotImageAddressWithJpgPng = spotImageAddress
    for address in spotImageAddress[:]:
        # 過濾不是jpg或是png的檔案
        if (address[-3:]).upper() == "PNG" or (address[-3:]).upper() == "JPG":
            pass
        else:
            # remove為根據值刪除元素
            spotImageAddressWithJpgPng.remove(address)
    # 將id和該景點的圖片位置存到字典
    spotIdAndImage[_id] = spotImageAddressWithJpgPng


# 將所有圖片資訊存到資料庫
for i in spotsInfo:
    for image in spotIdAndImage[i["_id"]]:
        cur.execute("INSERT INTO image(name, _id, file) VALUES(%s,%s,%s)",
                    (i["name"], i["_id"], image))
mydb.commit()
cur.close()
mydb.close()


app.run(port=5000)
