from flask import Flask, Blueprint, request, make_response
from flask.views import MethodView
from datetime import datetime, timedelta
import mysql.connector
import jwt
import os
from dotenv import load_dotenv
import boto3
from werkzeug.utils import secure_filename

load_dotenv()

uploadImgApi = Blueprint('loadImg', __name__)

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


class uploadAvator(MethodView):
    def post(self):
        avatorInfo = {}
        token = request.cookies.get('token')
        data = jwt.decode(token, os.getenv('JWT_KEY'), algorithms="HS256")
        if token is not None:
            img = request.files['form']
            # img 是 < FileStorage: 'logo.png' ('image/png') >
            if img.filename == "":
                return ({"error": True, "message": "Please select a file"}), 400
            if img:
                try:
                    # 文件名進行安全清理，確保它們不包含任何不安全字符
                    filename = secure_filename(img.filename)
                    img.save(filename)
                    s3.upload_file(
                        Bucket=BUCKET_NAME,
                        Filename=filename,
                        Key=filename
                    )
                    urlWithkey = s3.generate_presigned_url(
                        ClientMethod='get_object',
                        Params={
                            'Bucket': BUCKET_NAME,  # 代表 S3 bucket 的名稱
                            'Key': filename  # 代表檔案在 S3 中的路徑
                        }
                    )
                    url = (urlWithkey.split('?'))[0]
                    # 將檔案公開讀取
                    s3.put_object_acl(
                        Bucket=BUCKET_NAME,  # 代表 S3 bucket 的名稱
                        Key=filename,  # 代表檔案在 S3 中的路徑
                        ACL='public-read'  # 代表檔案的 ACL
                    )
                    avatorInfo["userId"] = data["id"]
                    avatorInfo["name"] = data["name"]
                    avatorInfo["fileName"] = filename
                    avatorInfo["avatorUrl"] = url
                    return ({"data": avatorInfo}), 200
                except Exception as e:
                    return {'error': True, "message": str(e)}
            else:
                return ({"error": True, "message": "未登入系統，請先登入會員"}), 403


uploadImgApi.add_url_rule(
    '/avator', view_func=uploadAvator.as_view('Operation about avator'), methods=['POST'])
