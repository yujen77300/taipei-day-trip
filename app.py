from flask import *
from flask import request
import requests

import decimal
from decimal import Decimal
import mysql.connector
from mysql.connector import pooling
import jwt
from datetime import datetime, timedelta
from functools import wraps
import re
import json


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
    pool_size=32,
    pool_reset_session=True,
    host='localhost',
    database='taipeitrip',
    user='root',
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


@app.route("/booking")
def booking():
    return render_template("booking.html")


@app.route("/thankyou")
def thankyou():
    return render_template("thankyou.html")


@app.route("/member")
def member():
    return render_template("member.html")

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

# 註冊一個新的會員


@app.route("/api/user", methods=["POST"])
def signup():
    mydb = taipeiPool.get_connection()
    cur = mydb.cursor()
    inputName = request.get_json()["name"]
    inputEmail = request.get_json()["email"]
    inputPassword = request.get_json()["password"]
    cur.execute(
        "SELECT member_id,name,email,password FROM member WHERE email=%s", [inputEmail])
    memberInfo = cur.fetchone()
    try:
        if memberInfo is not None:
            return jsonify({"error": True, "message": "註冊失敗，此信箱已被使用"}), 400
        else:
            cur.execute("INSERT INTO member(name,email,password) VALUES(%s,%s,%s)",
                        (inputName, inputEmail, inputPassword))
            mydb.commit()
            return jsonify({'ok': True})
    except Exception as e:
        return {'error': True, "message": str(e)}
    finally:
        cur.close()
        mydb.close()

# 取得當前登入的會員資訊


@app.route("/api/user/auth")
def member_info():
    # 取得目前在瀏覽器的token
    token = request.cookies.get('token')
    try:
        data = jwt.decode(token, "dylanwehelp", algorithms="HS256")
        return jsonify({'data': data}), 200
    except Exception as e:
        return {'error': True, "message": str(e)}


# 登入會員


@app.route("/api/user/auth", methods=["PUT"])
def login():
    mydb = taipeiPool.get_connection()
    cur = mydb.cursor()
    inputEmail = request.get_json()["email"]
    inputPassword = request.get_json()["password"]
    cur.execute(
        "SELECT member_id,name,email,password FROM member WHERE email=%s and password=%s;", (inputEmail, inputPassword))
    memberInfo = cur.fetchone()

    try:
        # if帳號密碼正確
        if memberInfo is not None:
            exptime = datetime.now() + timedelta(days=7)
            exp_epoc_time = exptime.timestamp()
            payload_data = {}
            payload_data["id"] = memberInfo[0]
            payload_data["name"] = memberInfo[1]
            payload_data["email"] = memberInfo[2]
            # payload_data["exp"] = int(exp_epoc_time)
            encoded_jwt = jwt.encode(
                payload=payload_data, key="dylanwehelp", algorithm="HS256")
            # 登入成功，使用 JWT 加密資訊並存放到 Cookie 中，保存七天
            response = make_response(jsonify({"ok": True}), 200)
            response.set_cookie(key='token', value=encoded_jwt,
                                expires=exp_epoc_time, httponly=True)
            return response

        else:
            return jsonify({"error": True, "message": "帳號或密碼輸入錯誤"}), 400

#   "message": "請按照情境提供對應的錯誤訊息")
    except Exception as e:
        return {'error': True, "message": str(e)}
    finally:
        cur.close()
        mydb.close()


# #登出會員
@app.route("/api/user/auth", methods=["DELETE"])
def logout():
    try:
        # 先取得token
        token = request.cookies.get('token')
        response = make_response(jsonify({"ok": True}), 200)
        # 登出成功，從 Cookie 中移除 JWT 加密資訊
        response.set_cookie(key='token', value=token, expires=0, httponly=True)
        return response
    except Exception as e:
        return {'error': True, "message": str(e)}

# 預定行程


@app.route("/api/booking", methods=["GET", "POST", "DELETE"])
def scheduleBooking():
    if request.method == "GET":
        # 看是不是有登入系統
        token = request.cookies.get('token')
        if token is not None:
            # 取得id
            data = jwt.decode(token, "dylanwehelp", algorithms="HS256")
            userId = data["id"]
            # 取得尚未下單預訂行程
            mydb = taipeiPool.get_connection()
            cur = mydb.cursor()
            cur.execute(
                "SELECT spot_info._id,spot_info.name,spot_info.address,image.file,cart.date,cart.time,cart.price,cart.memberID FROM cart_spotInfo join spot_info on cart_spotInfo.spotId=spot_info._id join cart on cart_spotInfo.cartId=cart.id join image on cart_spotInfo.spotId=image._id where cart.memberId = %s LIMIT 1", [userId])
            bookingInfo = cur.fetchone()
            data = {}
            if bookingInfo is not None:
                try:
                    attraction = {}
                    attraction["id"] = bookingInfo[0]
                    attraction["name"] = bookingInfo[1]
                    attraction["address"] = bookingInfo[2]
                    attraction["image"] = "https://"+bookingInfo[3]
                    data["attraction"] = attraction
                    data["date"] = bookingInfo[4].strftime('%Y-%m-%d')
                    data["time"] = bookingInfo[5]
                    data["price"] = int(bookingInfo[6])
                    return jsonify({'data': data}), 200
                except Exception as e:
                    return {'error': True, "message": str(e)}
                finally:
                    cur.close()
                    mydb.close()
            else:
                # 這是沒有資料的
                return jsonify({'data': data}), 200
        else:
            return jsonify({"error": True, "message": "未登入系統，請先登入會員"}), 403

    elif request.method == "POST":
        token = request.cookies.get('token')
        data = jwt.decode(token, "dylanwehelp", algorithms="HS256")
        memberId = data["id"]
        attractionId = request.get_json()["attractionId"]
        date = request.get_json()["date"]
        time = request.get_json()["time"]
        price = request.get_json()["price"]
        if token is not None and len(date) > 0:
            try:
                mydb = taipeiPool.get_connection()
                cur = mydb.cursor()
                cur.execute(
                    "DELETE FROM cart_spotinfo;")
                cur.execute(
                    "DELETE FROM cart;")
            # 建立新的預訂行程
                cur.execute(
                    "INSERT INTO cart(memberId,date,time,price) values(%s,%s,%s,%s);", (memberId, date, time, price))
                cur.execute(
                    "SELECT cart.id FROM cart")
                cartId = (cur.fetchone())[0]
                cur.execute(
                    "INSERT INTO cart_spotinfo(cartId,spotId) values(%s,%s);", (cartId, attractionId))
                mydb.commit()
                return jsonify({"ok": True}), 200
            except Exception as e:
                return {'error': True, "message": str(e)}
            finally:
                cur.close()
                mydb.close()
        elif (token is not None and len(date) == 0):
            return jsonify({"error": True, "message": "預訂失敗，請選擇日期"}), 400
        else:
            return jsonify({"error": True, "message": "未登入系統，請先登入會員"}), 403

    elif request.method == "DELETE":
        token = request.cookies.get('token')
        data = jwt.decode(token, "dylanwehelp", algorithms="HS256")
        # 刪除目前預定的行程
        # return "刪除預訂行程"
        if token is not None:
            try:
                mydb = taipeiPool.get_connection()
                cur = mydb.cursor()
                cur.execute(
                    "DELETE FROM cart_spotinfo;")
                cur.execute(
                    "DELETE FROM cart;")
                mydb.commit()
                return jsonify({"ok": True}), 200
            except Exception as e:
                return {'error': True, "message": str(e)}
        else:
            return jsonify({"error": True, "message": "未登入系統，請先登入會員"}), 403


# 訂單付款api
@app.route("/api/orders", methods=["POST"])
def orders():
    orderInfo = {}
    # 流水編號  日期+顧客id+流水編號
    orderNumber = 1

    token = request.cookies.get('token')
    data = jwt.decode(token, "dylanwehelp", algorithms="HS256")
    memberId = data["id"]
    orderData = request.get_json()
    validate_phone_number_pattern = r"^(\+\d{1,3}|00\d{1,3})\d{6,14}$"
    phoneValidation = re.match(
        validate_phone_number_pattern, orderData["order"]["contact"]["phone"])
    # 使用者id (三碼)
    print(orderData)
    spotId = orderData["order"]["trip"]["id"]
    status = "未付款"
    phone = orderData["order"]["contact"]["phone"]
    date = orderData["order"]["date"]
    time = orderData["order"]["time"]
    price = orderData["order"]["price"]

    # dateForOrderNumber = (orderData["order"]["date"]).replace('-', '')
    now = datetime.now()
    formattedDate = now.strftime('%Y-%m-%d')
    dateForOrderNumber = formattedDate.replace('-', '')
    idForOrderNumber = str(memberId).zfill(4)
    print(orderNumber)
    if (token is not None and not phoneValidation):
        return ({"error": True, "message": "請輸入正確手機格式，包含國碼與號碼"}), 400
    elif token is not None:
        try:
            # 2. 後端建立訂單編號和資料，紀錄訂單付款狀態為【未付款】。
            print("我進來後端")
            mydb = taipeiPool.get_connection()
            cur = mydb.cursor()
            cur.execute(
                "SELECT * FROM order_info where memberId = %s ORDER BY id DESC LIMIT 1;", [memberId])
            info = cur.fetchall()
            print(info)
            if not info:
                serialNumber = str(orderNumber).zfill(3)
                orderNumber = dateForOrderNumber + idForOrderNumber + serialNumber
                cur.execute(
                    "INSERT INTO order_info(memberId,orderNumber,spotId,date,time,price,phone,status) VALUES(%s,%s,%s,%s,%s,%s,%s,%s);", (memberId, int(orderNumber), spotId, date, time, price, phone, status))
                mydb.commit()
                print("沒有訂單資料")
            else:
                serialNumber = str(int((str(info[0][2]))[-3:])+1).zfill(3)
                orderNumber = dateForOrderNumber + idForOrderNumber + serialNumber
                print(serialNumber)
                cur.execute(
                    "INSERT INTO order_info(memberId,orderNumber,spotId,date,time,price,phone,status) VALUES(%s,%s,%s,%s,%s,%s,%s,%s);", (memberId, int(orderNumber), spotId, date, time, price, phone, status))
                mydb.commit()
                print("有訂單資料")

            # 3. 後端呼叫 TapPay 提供的付款 API，提供必要付款資訊，完成付款動作。
            url = 'https://sandbox.tappaysdk.com/tpc/payment/pay-by-prime'
            headers = {"Content-Type": "application/json",
                       "x-api-key": "partner_R8SC0fiXUYHOZKaGIR1S3DooKRoxU6JV9rlfPOlHGjcZT86EP4nnzPxf"}
            postData = {
                "prime": orderData["prime"],
                "partner_key": "partner_R8SC0fiXUYHOZKaGIR1S3DooKRoxU6JV9rlfPOlHGjcZT86EP4nnzPxf",
                "merchant_id": "dylan399_CTBC",
                "details": "Taipei Day Trip",
                "amount": orderData["order"]["price"],
                "cardholder": {
                    "phone_number": orderData["order"]["contact"]["phone"],
                    "name": orderData["order"]["contact"]["name"],
                    "email": orderData["order"]["contact"]["email"]
                },
                "remember": False
            }

            response = requests.post(url, headers=headers, json=postData)
            print("tappay回傳結果")
            print(response)
            print("Status Code", response.status_code)
            print("JSON Response ", response.json())

            if (response.json())["status"] == 0:
                #    4. 付款成功，紀錄付款資訊；將訂單付款狀態改為【已付款】，將訂單編號傳回前端。
                status = "付款成功"
                cur.execute(
                    "UPDATE order_info SET status='已付款' WHERE orderNumber=%s;", [orderNumber])
                mydb.commit()
                payment = {}
                payment["status"] = 1
                payment["message"] = status
                orderInfo["number"] = orderNumber
                orderInfo["payment"] = payment
                cur.execute(
                    "DELETE FROM cart_spotinfo;")
                cur.execute(
                    "DELETE FROM cart;")
                mydb.commit()
                return ({'data': orderInfo}), 200
            else:
                # 5. 付款失敗，紀錄付款資訊；不更動訂單付款狀態，將訂單編號傳遞回前端。
                payment = {}
                payment["status"] = 0
                payment["message"] = status
                orderInfo["number"] = orderNumber
                orderInfo["payment"] = payment
                cur.execute(
                    "DELETE FROM cart_spotinfo;")
                cur.execute(
                    "DELETE FROM cart;")
                mydb.commit()
                return ({'data': orderInfo}), 200
        except Exception as e:
            return {'error': True, "message": str(e)}
        finally:
            cur.close()
            mydb.close()

    else:
        return ({"error": True, "message": "未登入系統，請先登入會員"}), 403


@app.route("/api/orders/<orderNumber>")
def getOrderInfo(orderNumber):
 # 看是不是有登入系統
    token = request.cookies.get('token')
    if token is not None:
        responseData = {}
        attraction = {}
        contact = {}
        trip = {}
        # 取得id
        data = jwt.decode(token, "dylanwehelp", algorithms="HS256")
        memberId = data["id"]
        name = data["name"]
        email = data["email"]
        mydb = taipeiPool.get_connection()
        cur = mydb.cursor(dictionary=True)
        cur.execute(
            "SELECT * FROM order_info JOIN member on order_info.memberId = member.member_id where orderNumber=%s and memberId = %s;", (orderNumber, memberId))
        orderInfoData = cur.fetchone()
        if orderInfoData is not None:
            try:
                spotId = orderInfoData["spotId"]
                cur.execute(
                    "SELECT spot_info.name, spot_info.address, image.file FROM spot_info JOIN image on spot_info._id=image._id WHERE spot_info._id=%s LIMIT 1", [spotId])
                spotInfoData = cur.fetchone()
                print(orderInfoData)
                print(spotInfoData)
                attraction["id"] = spotId
                attraction["name"] = spotInfoData["name"]
                attraction["address"] = spotInfoData["address"]
                attraction["image"] = spotInfoData["file"]
                trip["attraction"] = attraction
                trip["date"] = orderInfoData["date"].strftime('%Y-%m-%d')
                trip["time"] = orderInfoData["time"]
                status = 0 if orderInfoData["status"] == "未付款" else 1
                contact["name"] = name
                contact["email"] = email
                contact["phone"] = orderInfoData["phone"]
                responseData["number"] = orderNumber
                responseData["price"] = orderInfoData["price"]
                responseData["trip"] = trip
                responseData["contact"] = contact
                responseData["status"] = status
                return ({'data': responseData}), 200
            except Exception as e:
                return {'error': True, "message": str(e)}
            finally:
                cur.close()
                mydb.close()
        else:
            cur.close()
            mydb.close()
            return ({'data': responseData}), 200
    else:
        return ({"error": True, "message": "未登入系統，請先登入會員"}), 403


# 會員歷史紀錄api
@app.route("/api/member")
def memberInfo():
 # 看是不是有登入系統
    token = request.cookies.get('token')
    if token is not None:
        # 訂單編號、景點、旅遊日期、時間、建立日期、付款狀態
        responseData = {}
        data = jwt.decode(token, "dylanwehelp", algorithms="HS256")
        memberId = data["id"]
        memberName = data["name"]
        contact = {}
        mydb = taipeiPool.get_connection()
        cur = mydb.cursor(dictionary=True)
        cur.execute(
            "SELECT order_info.orderNumber,spot_info.name,order_info.date,order_info.time,order_info.createdAt,order_info.status FROM order_info JOIN spot_info ON order_info.spotId = spot_info._id  WHERE memberId = %s;", [memberId])
        memberOrderData = cur.fetchall()
        print(memberOrderData)
        print(len(memberOrderData))
        if memberOrderData is not None:
            try:
                # no代表第幾個訂單
                no = 1
                for order in memberOrderData:
                    print(order)
                    datata = {}
                    datata["orderNumber"] = order["orderNumber"]
                    datata["name"] = order["name"]
                    datata["date"] = order["date"].strftime('%Y-%m-%d')
                    datata["time"] = order["time"]
                    datata["createdAt"] = order["createdAt"].strftime(
                        '%Y-%m-%d %H:%M:%S')
                    datata["status"] = order["status"]
                    responseData[f"{no}"] = datata
                    no = no + 1
                contact["name"] = memberName
                responseData["contact"] = contact
                return ({'data': responseData}), 200
            except Exception as e:
                return {'error': True, "message": str(e)}
            finally:
                cur.close()
                mydb.close()
        else:
            cur.close()
            mydb.close()
            return ({'data': responseData}), 200
    else:
        return ({"error": True, "message": "未登入系統，請先登入會員"}), 403


# app.run(host='0.0.0.0', port=3000)
app.run(port=3000)
