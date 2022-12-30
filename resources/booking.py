from flask import Flask, Blueprint, request, make_response
from flask.views import MethodView
# from datetime import datetime, timedelta
import datetime
import mysql.connector
import jwt
import os
from dotenv import load_dotenv
import time

load_dotenv()

bookingApi = Blueprint('booking', __name__)

taipeiPool = mysql.connector.pooling.MySQLConnectionPool(
    pool_name="connectionPool",
    pool_size=20,
    pool_reset_session=True,
    host='localhost',
    database=os.getenv('DB_NAME'),
    user=os.getenv('DB_ACCOUNT'),
    password=os.getenv('DB_PW'))


class booking(MethodView):
    def get(self):
        # 看是不是有登入系統
        token = request.cookies.get('token')
        if token is not None:
            # 取得id
            data = jwt.decode(token, os.getenv('JWT_KEY'), algorithms="HS256")
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
                    return ({'data': data}), 200
                except Exception as e:
                    return {'error': True, "message": str(e)}
                finally:
                    cur.close()
                    mydb.close()
            else:
                # 這是沒有資料的
                return ({'data': data}), 200
        else:
            return ({"error": True, "message": "未登入系統，請先登入會員"}), 403

    def post(self):
        token = request.cookies.get('token')
        data = jwt.decode(token, os.getenv('JWT_KEY'), algorithms="HS256")
        memberId = data["id"]
        attractionId = request.get_json()["attractionId"]
        date = request.get_json()["date"]
        time = request.get_json()["time"]
        price = request.get_json()["price"]
        currentDate = datetime.date.today()
        allowedBookingDate = currentDate+datetime.timedelta(days=1)
        if token is not None and len(date) > 0:
           # 將日期文字格式改為datetime.datetime格式
            bookingDate = datetime.datetime.strptime(date, '%Y-%m-%d')
            # 將datetime.datetime格式改為datetime.date
            bookingDate = bookingDate.date()
            print(type(bookingDate))
            if bookingDate >= allowedBookingDate:
                try:
                    mydb = taipeiPool.get_connection()
                    cur = mydb.cursor()
                    cur.execute(
                        "DELETE FROM cart_spotInfo;")
                    cur.execute(
                        "DELETE FROM cart;")
                # 建立新的預訂行程
                    cur.execute(
                        "INSERT INTO cart(memberId,date,time,price) values(%s,%s,%s,%s);", (memberId, date, time, price))
                    cur.execute(
                        "SELECT cart.id FROM cart")
                    cartId = (cur.fetchone())[0]
                    cur.execute(
                        "INSERT INTO cart_spotInfo(cartId,spotId) values(%s,%s);", (cartId, attractionId))
                    mydb.commit()
                    return ({"ok": True}), 200
                except Exception as e:
                    return {'error': True, "message": str(e)}
                finally:
                    cur.close()
                    mydb.close()
            elif (bookingDate == currentDate):
                return ({"error": True, "message": "無法預訂當天日期，請選擇明天開始之日期"}), 400
            elif (bookingDate < currentDate):
                return ({"error": True, "message": "無法選擇過往日期，請選擇明天開始之日期"}), 400

        elif (token is not None and len(date) == 0):
            return ({"error": True, "message": "預訂失敗，請選擇日期"}), 400
        else:
            return ({"error": True, "message": "未登入系統，請先登入會員"}), 403

    def delete(self):
        token = request.cookies.get('token')
        # 刪除目前預定的行程
        # return "刪除預訂行程"
        if token is not None:
            try:
                mydb = taipeiPool.get_connection()
                cur = mydb.cursor()
                cur.execute(
                    "DELETE FROM cart_spotInfo;")
                cur.execute(
                    "DELETE FROM cart;")
                mydb.commit()
                return ({"ok": True}), 200
            except Exception as e:
                return {'error': True, "message": str(e)}
        else:
            return ({"error": True, "message": "未登入系統，請先登入會員"}), 403


bookingApi.add_url_rule(
    '', view_func=booking.as_view('Operation about booking'), methods=['GET', 'DELETE', 'POST']
)
