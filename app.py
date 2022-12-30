from flask import *
from flask import request
import boto3
from werkzeug.utils import secure_filename
from resources.attraction import attractionApi
from resources.user import userApi
from resources.booking import bookingApi
from resources.order import orderApi
from resources.upload import uploadImgApi
from resources.edit import editAllInfoApi

app = Flask(
    __name__,
    static_folder="public",
    static_url_path="/"
)
app.config["JSON_AS_ASCII"] = False
app.config["TEMPLATES_AUTO_RELOAD"] = True
# Json檔案不要按照字母順序
app.config['JSON_SORT_KEYS'] = False

# s3 = boto3.resource('s3')

# s3 = boto3.client(
#     "s3",
#     regio_name="ap-northeast-1",
#     aws_access_key_id="AKIAS6XPTNST3CQDB6MV",
#     aws_secret_access_key="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"
# )
# BUCKET_NAME = "taipeidaytrip-dylan"
# print("測試s3")
# print(dir(s3))
# response = s3.list_buckets()
# print(response['Buckets'])
# s3.put_object_acl(
#     Bucket=BUCKET_NAME,  # 代表 S3 bucket 的名稱
#     Key='logo.png',  # 代表檔案在 S3 中的路徑
#     ACL='public-read'  # 代表檔案的 ACL
# )
# s3.delete_object(
#     Bucket=BUCKET_NAME,  # 代表 S3 bucket 的名稱
#     Key="logo123.png"  # 代表檔案
# )
# Pages


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/attraction/<id>")
def attractionnn(id):
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


# @app.route("/api/member/upload", methods=["POST"])
# def upload():
    # img = request.files['form']
    # # img 是 < FileStorage: 'logo.png' ('image/png') >
    # if img.filename == "":
    #     return ({"error": True, "message": "Please select a file"}), 400
    # if img:
    #     try:
    #         # 文件名進行安全清理，以確保它們不包含任何不安全字符
    #         filename = secure_filename(img.filename)
    #         img.save(filename)
    #         s3.upload_file(
    #             Bucket=BUCKET_NAME,
    #             Filename=filename,
    #             Key=filename
    #         )
    #         url = s3.generate_presigned_url(
    #             ClientMethod='get_object',
    #             Params={
    #                 'Bucket': BUCKET_NAME,  # 代表 S3 bucket 的名稱
    #                 'Key': filename  # 代表檔案在 S3 中的路徑
    #             }
    #         )
    #         print(url)
    #         return ({"ok": True}), 200
    #     except Exception as e:
    #         return {'error': True, "message": str(e)}

    # else:
    #     return ({"ok": True}), 200
        # return redirect("/")




app.register_blueprint(attractionApi, url_prefix='/api')
app.register_blueprint(userApi, url_prefix='/api/user')
app.register_blueprint(bookingApi, url_prefix='/api/booking')
app.register_blueprint(orderApi, url_prefix='/api')
app.register_blueprint(uploadImgApi, url_prefix='/api/upload')
app.register_blueprint(editAllInfoApi, url_prefix='/api/edit')

# app.run(port=3000)
app.run(host='0.0.0.0', port=3000)
