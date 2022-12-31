from flask import Flask, Blueprint, request, make_response
from flask.views import MethodView
from datetime import datetime, timedelta
import mysql.connector
import jwt
import re
import os
from dotenv import load_dotenv

load_dotenv()

userApi = Blueprint('user', __name__)

taipeiPool = mysql.connector.pooling.MySQLConnectionPool(
    pool_name="connectionPool",
    pool_size=20,
    pool_reset_session=True,
    host='localhost',
    database=os.getenv('DB_NAME'),
    user=os.getenv('DB_ACCOUNT'),
    password=os.getenv('DB_PW')
)


class user(MethodView):

    def get(self):
        # 取得當前登入的會員資訊
        # 12/29 增加手機、大頭貼位置、大頭貼名字
        # 取得目前在瀏覽器的token
        token = request.cookies.get('token')
        mydb = taipeiPool.get_connection()
        cur = mydb.cursor(dictionary=True)
        try:
            data = jwt.decode(token, os.getenv('JWT_KEY'), algorithms="HS256")
            cur.execute(
                "SELECT avator_url, avator_name,phone,email from member WHERE name =%s;", [data["name"]])
            info = cur.fetchone()
            data["email"] = info["email"]
            data["avatorUrl"] = info["avator_url"]
            data["avatorName"] = info["avator_name"]
            data["phone"] = info["phone"]
            return ({'data': data}), 200
        except Exception as e:
            return {'error': True, "message": str(e)}
        finally:
            cur.close()
            mydb.close()
    # 登入會員

    def put(self):
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
                    payload=payload_data, key=os.getenv('JWT_KEY'), algorithm="HS256")
                # 登入成功，使用 JWT 加密資訊並存放到 Cookie 中，保存七天
                response = make_response(({"ok": True}), 200)
                response.set_cookie(key='token', value=encoded_jwt,
                                    expires=exp_epoc_time, httponly=True)
                return response
            else:
                return ({"error": True, "message": "帳號或密碼輸入錯誤"}), 400
        except Exception as e:
            return {'error': True, "message": str(e)}
        finally:
            cur.close()
            mydb.close()
    # 登出會員

    def delete(self):
        try:
            # 先取得token
            token = request.cookies.get('token')
            response = make_response(({"ok": True}), 200)
            # 登出成功，從 Cookie 中移除 JWT 加密資訊
            response.set_cookie(key='token', value=token,
                                expires=0, httponly=True)
            return response
        except Exception as e:
            return {'error': True, "message": str(e)}


class userSignup(MethodView):

    def post(self):
        mydb = taipeiPool.get_connection()
        cur = mydb.cursor()
        inputName = request.get_json()["name"]
        inputEmail = request.get_json()["email"]
        inputPassword = request.get_json()["password"]
        validatedMail = isValidMail(inputEmail)
        validatedPwd = isValidPwd(inputPassword)
        if validatedMail and validatedPwd:
            cur.execute(
                "SELECT member_id,name,email,password FROM member WHERE email=%s", [inputEmail])
            memberInfo = cur.fetchone()
            try:
                if memberInfo is not None:
                    return ({"error": True, "message": "註冊失敗，此信箱已被使用"}), 400
                else:
                    cur.execute("INSERT INTO member(name,email,password) VALUES(%s,%s,%s)",
                                (inputName, inputEmail, inputPassword))
                    mydb.commit()
                    return ({'ok': True})
            except Exception as e:
                return {'error': True, "message": str(e)}
            finally:
                cur.close()
                mydb.close()
        elif validatedPwd and not validatedMail:
            return ({"error": True, "message": "信箱格式錯誤"}), 400
        elif not validatedPwd and validatedMail:
            return ({"error": True, "message": "密碼至少4位數，且包含至少一個數字與一個英文字母"}), 400
        else:
            return ({"error": True, "message": "密碼與信箱格式錯誤"}), 400


class userOrder(MethodView):
    def get(self):
        # 看是不是有登入系統
        token = request.cookies.get('token')
        if token is not None:
            # 訂單編號、景點、旅遊日期、時間、建立日期、付款狀態
            responseData = {}
            data = jwt.decode(token, os.getenv('JWT_KEY'), algorithms="HS256")
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


def isValidMail(email):
    emailRegex = re.compile(
        r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
    if re.fullmatch(emailRegex, email):
        return True
    else:
        print("Invalid email")


def isValidPwd(password):
    pwdRegex = re.compile(
        r'^(?=.*[0-9])(?=.*[a-zA-Z]).{4,}$')
    if re.fullmatch(pwdRegex, password):
        return True
    else:
        return False


userApi.add_url_rule(
    '', view_func=userSignup.as_view('userSignup'), methods=['POST'])

userApi.add_url_rule(
    '/auth', view_func=user.as_view('Operation about user'), methods=['GET', 'DELETE', 'PUT'])

userApi.add_url_rule(
    '/order', view_func=userOrder.as_view('user all orders'))
