from flask import *
from flask import request
import decimal
from decimal import Decimal
import mysql.connector
from mysql.connector import pooling

app = Flask(
    __name__,
    static_folder="public",
    static_url_path="/"
)
app.config["JSON_AS_ASCII"] = False
app.config["TEMPLATES_AUTO_RELOAD"] = True
# Json檔案不要按照字母順序
app.config['JSON_SORT_KEYS'] = False

taipeiPool = mysql.connector.pooling.MySQLConnectionPool(
    pool_name="connectionPool",
    pool_size=15,
    pool_reset_session=True,
    host='localhost',
    database='taipeitrip',
    user='user',
    password='1qaz@WSX')

# Pages


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/attraction/<id>")
def attractionnn(id):
    # 如果從後端做
    # src = "http://127.0.0.1:3000/api/attraction/"+id
    # with urllib.request.urlopen(src) as response:
    #     data = json.load(response)
    # print(data)
    # # 取得照片的串列
    # photo = data['data']["image"]
    # return render_template("attraction.html", information=data, photo=photo)
    return render_template("attraction.html")


# @app.route("/booking")
# def booking():
#     return render_template("booking.html")


# @app.route("/thankyou")
# def thankyou():
#     return render_template("thankyou.html")


# api
# 取得景點分類名稱列表
@app.route("/api/categories")
def cat():
    categories = []
    try:
        mydb = taipeiPool.get_connection()
        cur = mydb.cursor()
        cur.execute("SELECT CAT FROM spot_info GROUP BY CAT")
        info = cur.fetchall()
        for category in info:
            # 從tuple轉為string
            string = ''.join(category)
            string.replace('\u3000', ' ')
            categories.append(string)
        return jsonify({'data': categories})
    except Exception as e:
        return {'error': True, "message": str(e)}
    finally:
        cur.close()
        mydb.close()


# 取得景點資料列表
@app.route("/api/attractions")
def attraction():
    # 景點資訊是一個串列格式，裡面放字典檔
    spotInfo = []
    spot = {}
    spotInfoWithKey = []
    imgList = []
    # 顯示每頁幾筆，然後用slice的方式抓出來
    page = request.args.get("page", 0)
    attractionPerPage = 12
    keyword = request.args.get("keyword")

    mydb = taipeiPool.get_connection()
    cur = mydb.cursor()

    if keyword is not None:
        cur.execute(
            "SELECT _id, CAT, MEMO_TIME, MRT, address, description, direction, latitude, longitude, name FROM spot_info WHERE CAT=%s;", [keyword])
        info = cur.fetchall()
        if (int(page)+1) * attractionPerPage < len(info):
            nextpage = int(page)+1
        else:
            nextpage = None
        cur.execute(
            "SELECT _id, CAT, MEMO_TIME, MRT, address, description, direction, latitude, longitude, name FROM spot_info WHERE CAT=%s LIMIT %s, %s;", (keyword, (int(page)*12), 12))
    else:
        # 取得總筆數
        cur.execute(
            "SELECT _id, CAT, MEMO_TIME, MRT, address, description, direction, latitude, longitude, name FROM spot_info")
        info = cur.fetchall()
        if (int(page)+1) * attractionPerPage < len(info):
            nextpage = int(page)+1
        else:
            nextpage = None
        cur.execute(
            "SELECT _id, CAT, MEMO_TIME, MRT, address, description, direction, latitude, longitude, name FROM spot_info LIMIT %s, %s;", ((int(page)*12), 12))
    spotInfo = cur.fetchall()
    # 新增字典最後再append到串列裡
    for i in spotInfo:
        # 新增一個圖片的串列
        imgCursor = mydb.cursor()
        imgCursor.execute("SELECT file FROM image WHERE _id=%s", [i[0]])
        imgAddress = imgCursor.fetchall()
        for img in imgAddress:
            string = ''.join(img)
            imgList.append("https://" + string)
        spot["id"] = i[0]
        spot["name"] = i[9]
        spot["category"] = i[1]
        spot["description"] = i[5]
        spot["address"] = i[4]
        spot["trasnport"] = i[6]
        spot["mrt"] = i[3]
        spot["lat"] = float(str(i[7]))
        spot["lng"] = float(str(i[8]))
        spot["image"] = imgList
        dictCopy = spot.copy()
        spot = {}
        imgList = []

        spotInfoWithKey.append(dictCopy)

    mydb.close()
    cur.close()
    try:
        return jsonify({'nextpage': nextpage, "data": spotInfoWithKey})
    except Exception as e:
        return {'error': True, "message": str(e)}


# 根據景點編號取得景點資料
@app.route("/api/attraction/<id>")
def specificAttraction(id):
    spot = {}
    imgList = []
    mydb = taipeiPool.get_connection()
    cur = mydb.cursor()
    cur.execute(
        "SELECT _id, CAT, MEMO_TIME, MRT, address, description, direction, latitude, longitude, name FROM spot_info WHERE _id=%s;", [id])
    spotInfo = cur.fetchall()
    try:
        # return {'error': True, "message": str(e)}
        if spotInfo:
            cur.close()
            imgCursor = mydb.cursor()
            imgCursor.execute("SELECT file FROM image WHERE _id=%s", [id])
            imgAddress = imgCursor.fetchall()
            for img in imgAddress:
                string = ''.join(img)
                imgList.append("https://" + string)
            spot["id"] = spotInfo[0][0]
            spot["category"] = spotInfo[0][1]
            spot["description"] = spotInfo[0][5]
            spot["address"] = spotInfo[0][4]
            spot["transport"] = spotInfo[0][6]
            spot["mrt"] = spotInfo[0][3]
            spot["lat"] = float(str(spotInfo[0][7]))
            spot["lng"] = float(str(spotInfo[0][8]))
            spot["image"] = imgList
            spot["name"] = spotInfo[0][9]
            return jsonify({"data": spot})
        else:
            return jsonify({"error": True, "message": "請輸入正確景點編號"})

    except Exception as e:
        return {'error': True, "message": str(e)}
    finally:
        imgCursor.close()
        mydb.close()


app.run(host='0.0.0.0', port=3000)
# app.run(port=3000)
