from pymongo import MongoClient
import hashlib
import bcrypt
# JWT 패키지를 사용합니다. (설치해야할 패키지 이름: PyJWT)
import jwt

# 토큰에 만료시간을 줘야하기 때문에, datetime 모듈도 사용합니다.
import datetime

# 회원가입 시엔, 비밀번호를 암호화하여 DB에 저장해두는 게 좋습니다.
# 그렇지 않으면, 개발자(=나)가 회원들의 비밀번호를 볼 수 있으니까요.^^;
import hashlib

from flask import Flask, render_template, jsonify, request, session, redirect, url_for
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta

import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
from collections import OrderedDict

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['UPLOAD_FOLDER'] = "./static/profile_pics"


client = MongoClient('localhost', 27017)


############################loginToken#####################################
db = client.dbsparta
SECRET_KEY = 'book'

books = list(db.book.find({},{'_id' : False}))
my_list = []
for book in books:
    b_category = book['category']
    if b_category not in my_list:
        my_list.append(b_category)
@app.route('/')
def home():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        # user_info = db.users.find_one({"username": payload["id"]})
        username = payload["id"]
        return redirect(url_for("user", username=username))
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))


@app.route('/login')
def login():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        # user_info = db.users.find_one({"username": payload["id"]})
        username = payload["id"]
        return redirect(url_for("user", username=username))
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return render_template('login.html')


@app.route('/user/<username>')
def user(username):
    # 각 사용자의 프로필과 글을 모아볼 수 있는 공간
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        status = (username == payload["id"])  # 내 프로필이면 True, 다른 사람 프로필 페이지면 False

        user_info = db.users.find_one({"username": username}, {"_id": False})
        return render_template('index.html', user_info=user_info, status=status, books=books, my_list=my_list)
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


@app.route('/sign_in', methods=['POST'])
def sign_in():
    # 로그인
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']

    pw_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    result = db.users.find_one({'username': username_receive, 'password': pw_hash})

    if result is not None:
        #클라이언트가 가지고 있는 영수증 내용 작성
        payload = {
            #아이디는 누구
            'id': username_receive,
            #머물수 있는 시간
            'exp': datetime.utcnow() + timedelta(seconds=300)  # 로그인 2분 유지
        }
        #            jsonwebtoken.encode(영수증, 세션 암호화, 토큰의 알고리즘) 디코드하는 이유?
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

        return jsonify({'result': 'success', 'token': token})
    # 찾지 못하면
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})


@app.route('/signup')
def sign_up():
    return render_template('signup.html')


@app.route('/sign_up/save', methods=['POST'])
def sign_up_save():
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']
    password_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    doc = {
        "username": username_receive,                               # 아이디
        "password": password_hash,                                  # 비밀번호
        "profile_name": username_receive,                           # 프로필 이름 기본값은 아이디
        "profile_pic": "",                                          # 프로필 사진 파일 이름
        "profile_pic_real": "profile_pics/profile_placeholder.png", # 프로필 사진 기본 이미지
        "profile_info": ""                                          # 프로필 한 마디
    }
    db.users.insert_one(doc)
    return jsonify({'result': 'success'})


@app.route('/sign_up/check_dup', methods=['POST'])
def check_dup():
    username_receive = request.form['username_give']
    exists = bool(db.users.find_one({"username": username_receive}))

    #ajax response 로 보내질거면 result를 success
    return jsonify({'result': 'success', 'exists': exists})

##############################################################################

##############################booksearchapi###################################
# book의 정보들을 뿌려주는 API
@app.route('/api/books', methods=['GET'])
def show_books():
    books_data = list(db.book.find({}, {'_id':False}))
    return jsonify({'books_data': books_data})


# 검색하기(POST)-카테고리가 있을 때 API
@app.route('/api/search_book/category', methods=['POST'])
def search_book_with_category():
    bookCategory_receive = request.form['bookCategory']
    searchValue_receive = request.form['searchValue']

    category = my_list[int(bookCategory_receive) - 1]
    print(category)

    book_data = list(db.book.find({'category': category}, {'_id': False}))
    print(book_data)

    return jsonify({'msg': ' 저장 ','book_data':book_data,'searchValue_receive':searchValue_receive})


# 검색하기(POST)-카테고리가 없을 때 API
@app.route('/api/search_book', methods=['POST'])
def search_book():
    searchValue_receive = request.form['searchValue']

    book_data = list(db.book.find({}, {'_id': False}))
    print(book_data)


    return jsonify({'msg': ' 저장 ','book_data':book_data,'searchValue_receive':searchValue_receive})
#############################################################################







############################loginSession#####################################
# db = client.accountdata
# app.secret_key = "hello"
# @app.route("/login")
# def home():
#     if "user" in session:
#         return redirect(url_for("user"))
#
#     return render_template("login.html")
#
#
# @app.route("/login", methods=["POST"])
# def login():
#     if request.method == "POST":
#         id_receive = request.form["username"]
#         pass_receive = request.form["pass"]
#         existing_user = db.users.find_one({'id': id_receive})
#
#         if existing_user is not None:
#             if pass_receive == existing_user['pass']:
#                 session["user"] = id_receive
#                 print("login success")
#                 return redirect(url_for("user"))
#             else:
#                 print("invalid password")
#                 return redirect(url_for("user"))
#         else:
#             print("invalid username")
#             return redirect(url_for("user"))
#     else:
#         if "user" in session:
#             return redirect(url_for("user"))
#
#
# @app.route("/user")
# def user():
#     if "user" in session:
#         username = session["user"]
#         return render_template("example.html", data=username)
#     else:
#         return redirect(url_for("login"))
#
#
# @app.route("/logout")
# def logout():
#     #또는 session.clear() 사용도 가능
#     session.pop("user", None)
#     return redirect(url_for("login"))
#
#
# @app.route("/example")
# def ren_ex():
#     # if user in session:
#     #     return
#
#     return render_template("example.html")
#
#
#
#
# @app.route('/signup')
# def signup():
#     return render_template('signup.html')
#
#
# @app.route('/api/signup', methods=['POST', 'GET'])
# def api_signup():
#     if request.method == 'POST':
#         name_receive = request.form['name_give']
#         id_receive = request.form['id_give']
#         pass_receive = request.form['pass_give']
#         # pass_receive = request.form['pass_give'].encode('utf-8')
#         existing_user = db.users.find_one({'id': id_receive})
#
#         #비밀번호 encode 과정
#         pw_hash = hashlib.sha256(pass_receive.encode('utf-8')).hexdigest()
#
#         if existing_user is not None:
#             return jsonify({'check': 1})
#         else:
#             doc = {'name': name_receive, 'id': id_receive, 'pass': pw_hash}
#             db.users.insert_one(doc)
#             return jsonify({'check': 2})
#############################################################################


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
