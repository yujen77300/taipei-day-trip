from flask import Flask, Blueprint, request
from flask.views import MethodView
import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

attractionApi = Blueprint('attraction', __name__)


taipeiPool = mysql.connector.pooling.MySQLConnectionPool(
    pool_name="connectionPool",
    pool_size=20,
    pool_reset_session=True,
    host='localhost',
    database=os.getenv('DB_NAME'),
    user=os.getenv('DB_ACCOUNT'),
    password=os.getenv('DB_PW'))


class attractionCategory(MethodView):
    def get(self):
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
            return ({'data': categories})
        except Exception as e:
            return {'error': True, "message": str(e)}
        finally:
            cur.close()
            mydb.close()


class attractionList(MethodView):
    def get(self, id):
        if id is None:
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
                imgCursor.execute(
                    "SELECT file FROM image WHERE _id=%s", [i[0]])
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
                return ({'nextpage': nextpage, "data": spotInfoWithKey})
            except Exception as e:
                return {'error': True, "message": str(e)}
        else:
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
                    imgCursor.execute(
                        "SELECT file FROM image WHERE _id=%s", [id])
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
                    return ({"data": spot})
                else:
                    return ({"error": True, "message": "請輸入正確景點編號"})
            except Exception as e:
                return {'error': True, "message": str(e)}
            finally:
                imgCursor.close()
                mydb.close()


attractionApi.add_url_rule(
    '/categories', view_func=attractionCategory.as_view('Categories of all tourist spots'))
attractionApi.add_url_rule(
    '/attractions', defaults={'id': None}, view_func=attractionList.as_view('All tourist spots'))
attractionApi.add_url_rule(
    '/attraction/<id>', view_func=attractionList.as_view('Specific tourist spot'))
