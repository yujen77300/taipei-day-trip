from flask import Flask, Blueprint, request, make_response
from flask.views import MethodView
from datetime import datetime, timedelta
import mysql.connector
import jwt
import os
import re
from dotenv import load_dotenv
import boto3
from werkzeug.utils import secure_filename

load_dotenv()

editAllInfoApi = Blueprint('editAllInfo', __name__)

# email和圖片、電話更新用patch

taipeiPool = mysql.connector.pooling.MySQLConnectionPool(
    pool_name="connectionPool",
    pool_size=20,
    pool_reset_session=True,
    host='localhost',
    database=os.getenv('DB_NAME'),
    user=os.getenv('DB_ACCOUNT'),
    password=os.getenv('DB_PW')
)

s3 = boto3.resource('s3')

s3 = boto3.client(
    "s3",
    region_name=os.getenv('AWS_REGION_NAME'),
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
)
BUCKET_NAME = os.getenv('AWS_BUCKET_NAME')


class editInfo(MethodView):
    def patch(self):
        token = request.cookies.get('token')
        mydb = taipeiPool.get_connection()
        cur = mydb.cursor(dictionary=True)
        tokenData = jwt.decode(token, os.getenv('JWT_KEY'), algorithms="HS256")
        if token is not None:
            try:
                data = request.get_json()
                print("測試測試")
                print(data)
                userName = data["userName"]
                email = data["email"]
                phone = data["phone"]
                avatorUrl = data["avatorUrl"]
                avatorName = data["avatorName"]
                print(avatorName)
                print(avatorUrl)
                cur.execute(
                    "UPDATE member SET phone=%s WHERE name=%s", (phone, userName))
                cur.execute(
                    "SELECT avator_name FROM member WHERE name=%s", [userName])
                info = cur.fetchone()
                originAvator = info["avator_name"]
                print("原本的圖片")
                print(originAvator)
                if email != tokenData["email"]:
                    cur.execute(
                        "UPDATE member SET email=%s WHERE name=%s", (email, userName))
                if avatorName != originAvator:
                    print("近來更改圖片")
                    cur.execute(
                        "UPDATE member SET avator_url=%s,avator_name=%s WHERE name=%s", (avatorUrl, avatorName, userName))
                mydb.commit()
                return {"ok": True}, 200
            except Exception as e:
                return {'error': True, "message": str(e)}
            finally:
                cur.close()
                mydb.close()
        else:
            return ({"error": True, "message": "未登入系統，請先登入會員"}), 403


class editPwd(MethodView):
    def patch(self):
        token = request.cookies.get('token')
        mydb = taipeiPool.get_connection()
        cur = mydb.cursor(dictionary=True)
        tokenData = jwt.decode(token, os.getenv('JWT_KEY'), algorithms="HS256")
        if token is not None:
            try:
                data = request.get_json()
                print("測試測試")
                print(data)
                print(tokenData["name"])
                cur.execute(
                    "SELECT password FROM member WHERE name=%s", [tokenData["name"]])
                info = cur.fetchone()

                if info["password"] == data["oldPwd"]:
                    if data["newPwd"] == data["repeatPwd"]:
                        if data["newPwd"] != data["oldPwd"]:
                            if isValidPwd(data["newPwd"]):
                                cur.execute(
                                    "UPDATE member SET password=%s WHERE name=%s", (
                                        data["newPwd"], tokenData["name"]))
                                mydb.commit()
                                return {"ok": True}, 200
                            else:
                                return {'error': True, "message": "密碼至少4位數，且包含至少一個數字與一個英文字母"}, 400
                        else:
                            return {'error': True, "message": "新的密碼不可與上一次密碼相同"}, 400
                    else:
                        return {'error': True, "message": "新的密碼與確認密碼不一致"}, 400
                else:
                    return {'error': True, "message": "輸入的現在密碼與原本密碼不一致"}, 400
            except Exception as e:
                return {'error': True, "message": str(e)}
            finally:
                cur.close()
                mydb.close()
        else:
            return ({"error": True, "message": "未登入系統，請先登入會員"}), 403


def isValidPwd(password):
    pwdRegex = re.compile(
        r'^(?=.*[0-9])(?=.*[a-zA-Z]).{4,}$')
    if re.fullmatch(pwdRegex, password):
        return True
    else:
        return False


editAllInfoApi.add_url_rule(
    '/info', view_func=editInfo.as_view('Operation about editing info'), methods=['PATCH'])

editAllInfoApi.add_url_rule(
    '/password', view_func=editPwd.as_view('Operation about editing password'), methods=['PATCH'])
