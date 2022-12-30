from flask import Flask, Blueprint, request, make_response
from flask.views import MethodView
from datetime import datetime, timedelta
import mysql.connector
import jwt
import re
import requests
import os
from dotenv import load_dotenv

load_dotenv()

orderApi = Blueprint('order', __name__)

taipeiPool = mysql.connector.pooling.MySQLConnectionPool(
    pool_name="connectionPool",
    pool_size=20,
    pool_reset_session=True,
    host='localhost',
    database=os.getenv('DB_NAME'),
    user=os.getenv('DB_ACCOUNT'),
    password=os.getenv('DB_PW'))


class order(MethodView):
    def get(self, orderNumber):
        token = request.cookies.get('token')
        if token is not None:
            responseData = {}
            attraction = {}
            contact = {}
            trip = {}
            # 取得id
            data = jwt.decode(token, os.getenv('JWT_KEY'), algorithms="HS256")
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

    def post(self):
        orderInfo = {}
        # 流水編號  日期+顧客id+流水編號
        orderNumber = 1

        token = request.cookies.get('token')
        data = jwt.decode(token, os.getenv('JWT_KEY'), algorithms="HS256")
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
                           "x-api-key": os.getenv('PARTNER_KEY')}
                postData = {
                    "prime": orderData["prime"],
                    "partner_key": os.getenv('PARTNER_KEY'),
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
                        "DELETE FROM cart_spotInfo;")
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
                        "DELETE FROM cart_spotInfo;")
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


orderApi.add_url_rule(
    '/order/<orderNumber>', view_func=order.as_view('Specific ordr info'))
orderApi.add_url_rule(
    '/orders/', view_func=order.as_view('Add new add'), methods=['POST'])
# attractionApi.add_url_rule(
#     '/attractions', defaults={'id': None}, view_func=attractionList.as_view('All tourist spots'))
