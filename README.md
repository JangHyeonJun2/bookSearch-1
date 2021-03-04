[TOC]



# 27조 프로젝트 : 책다나와(BookSearch)

## 프로젝트 설명

- 로그인이 필요한 페이지이며 로그인 화면으로 부터 시작한다.스크래핑으로 책 정보들을 스크래핑하여 DB에 저장하고 메인페이지에서 DB에 저장된 책 정보들을 보여준다.
- 검색을하여 원하는 책 정보들을 검색할 수 있고 카테고리를 설정할 수 있게하여 사용자들의 검색 효율을 높였다.
- 프로젝트 URL
  - http://15.164.94.216:5000/

-------

## 와이어프레임

- 메인페이지

  [![15.jpg](https://i.postimg.cc/63JqnxQn/15.jpg)](https://postimg.cc/8F4Tg3Mz)

- 로그인 페이지

  [![16.jpg](https://i.postimg.cc/QM5xXYqt/16.jpg)](https://postimg.cc/TydX09FM)

- 회원가입 페이지

  [![17.jpg](https://i.postimg.cc/6Qst1LNN/17.jpg)](https://postimg.cc/HrtqrMxS)



-----------

## DB구성

- 메인페이지 책 정보

| _id  |    img    |  title  |       url       |  category   |
| :--: | :-------: | :-----: | :-------------: | :---------: |
|  -   | 책 이미지 | 책 제목 | 책 구매하기 url | 책 카테고리 |



- 로그인 User 정보

| -id  |   Id   |   password   |
| :--: | :----: | :----------: |
|  -   | UserId | UserPassword |

------------



## 기능 소개

- 검색

  - 책 정보들을 스크래핑을 하여 json형태로 DB에 책 정보들을 저장.
  - 저장된 정보들을 카테고리와 검색 문자열로 책 정보들을 간추린다.

  ```python
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
  ```

  - 사용자가 카테고리를 사용하였을 때는 Client부분에서 카테고리와 사용자가 검색한 문자열을 가져와야합니다.  가져온 카테고리를 DB에서 같은 카테고리를 비교하여 책 정보 리스트를 뽑아냅니다. 이렇게 뽑아낸 책 정보와 사용자 검색 문자열을 Client에 다시 보내주게 됩니다. 

  ```python
  # 검색하기(POST)-카테고리가 없을 때 API
  @app.route('/api/search_book', methods=['POST'])
  def search_book():
      searchValue_receive = request.form['searchValue']
  
      book_data = list(db.book.find({}, {'_id': False}))
      return jsonify({'msg': ' 저장 ','book_data':book_data,'searchValue_receive':searchValue_receive})
  ```

  - 사용자가 카테고리를 선택하지 않고 검색만 할 때는 검색 문자열과 모든 책 정보들을 Client로 보내준다.
  - **`검색을 백엔드쪽에서 검색 정보와 카테고리 정보들을 받고 처리를 하여 처리된 정보들을 Client로 보내주려고 하였지만 정확히 구현 되지않아서 필수 정보들만 Client에 보내서 프론트에서 처리하게 하였다. 이런점은 다시 고쳐야겠다`**.

- Jinja2를 이용해서 카테고리 보여주기

  ```python
  books = list(db.book.find({},{'_id' : False}))
  my_list = []
  for book in books:
      b_category = book['category']
      if b_category not in my_list:
          my_list.append(b_category)
  ```

  - DB에 저장된 정보들을 보면 카테고리가 중복된게 많다. 어찌보면 당연하다. 같은 카테고리를 가지게 되어 카테고리별로 정보를 보여줘야하니깐..! 하지만 Client에서 **Select html** 문법에서는 중복된 카테고리를 제거해서 카테고리를 보여줘야한다. 예를 들면 (소설,어린이,여행,...,)  그래서 위에 코드처럼 중복을 제거해서 list에 담게 하였다. 이렇게 담은 my_list는 "/"주소로 메인페이지가 띄어질때 

    ```python
    @app.route('/')
    def home():
        return render_template('index.html', books=books, my_list=my_list)
    ```

    render_template로 return 시켜준다.

    ```html
    <select id="book-category" class="form-select" aria-label="Default select example">
                <option selected>카테고리</option>
                {% for category in my_list %}
                    <option value="{{ loop.index }} ">{{ category }}</option>
                {% endfor %}
    </select>
    ```

    이렇게 html select 문법에서 jinja2를 이용해서 my_list의 값들을 받아서 option에 뿌려줄 수 있다.



## 쿠키와 세션

#### 들어가기전에

- 인증을 먼저 알고가자!
  - 인증은 **Front-end** 관점에서 봤을 때 사용자의 로그인, 회원가입과 같이 사용자의 도입부분을 가리키곤한다. 반면 **Back-end** 관점에서 봤을 때는 모든 API 요청에 대해 사용자를 확인하는 작업이다.
  - 사용자A와 사용자 B가 앱을 사용한다고 가정하자. 두 사용자는 기본적을로 정보가 다르고 보유하고 있는 컨텐츠도 다르다. 따라서 서버에서는 A,B가 요청을 보냈을 때 누구의 요청인지를 정확히 알아야한다. 만일 그렇지 않다면 자신의 정보가 타인에게 유출되는 최악의 상황이 발생한다. 그렇기에 **앱(Front-end)** 에서는 자신이 누구인지를 알만한 단서를 서버에 보내야 하며, **서버(Back-end)** 는 그 단서를 파악해 각 요청에 맞는 데이터를 뿌려주게 된다.

- 쿠키와 세션 방식

  [![2021-03-04-10-38-05.png](https://i.postimg.cc/L40jGrYF/2021-03-04-10-38-05.png)](https://postimg.cc/K4BKMpD0)

  - **Session/Cookie** 방식의 인증은 기본적으로 세션 저장소를 필요로 합니다.(Redis를 많이 사용). 세션 저장소는 로그인을 했을 때 사용자의 정보를 저장하고 열쇠가 되는 세션 ID값을 만든다. 그리고 HTTP헤더에 실어 사용자에게 돌려보낸다.그러면 사용자는 쿠키로 보관하고 있다 인증이 필요한 요청에 쿠키(Session ID)를 넣어 보낸다. 웹 서버에서는 세션 저장소에 쿠키(Session ID)를 받고 저장되어 있는 정보와 매칭을 시켜 인증을 완료한다.
  - **Session**은 서버에서 가지고 있는 정보이다. Cookie는 사용자에게 발급된 세션을 열기 위한 열쇠(Session ID)를 의미한다. 만약 쿠키만으로 인증을 사용한다는 말은 서버의 지원은 사용 x , 이는 즉 Client가 인증 정보를 책임지게 된다. 그렇게 되면 HTTP요청을 탈취당할 경우 다 털리게 된다.따라서 보안과는 상관없는 단순한 장바구니나 자동로그인 설정은 유용하게 쓰인다. 





## JWT란?

- **Session/Cookie** 와 함께 모바일과 웹의 인증을 책임지는 대표주자이다. JWT는 Json Web Token의 약자로 인증에 필요한 정보들을 암호화시킨 토큰을 뜻한다. 위의 Session/Cookie 방식과 유사하게 사용자는 Access Token(JWT 토큰)을 HTTP 헤더에 실어 서버로 보내게 된다.

  [![2021-03-04-11-00-42.png](https://i.postimg.cc/RVZGr7V2/2021-03-04-11-00-42.png)](https://postimg.cc/rz75xt49)

- 토큰을 만들기 위해서는 크게 3가지 Header, Payload, Verify Signature가 필요하다.

  - Header : 위 3가지 정보를 암호화할 방식(alg), 타입(type) 등이 들어간다.
  - Payload : 서버에서 보낼 데이터가 들어간다. 일반적으로 유저의 고유 ID값, 유효기간이 들어갑니다.
  - Verify Signature : Base64 방식으로 인코딩한 Header, Payload 그리고 SECRET KEY를 더한 후 서명된다.
  - **최종적인 결과 : Encoded Header + "." + Encoded Payload + "." + Verify Signatur**e<br>Header, Payload는 인코딩될 뿐(16진수로 변경), 따로 암호화되지 않습니다. 따라서 JWT 토큰에서 Header, Payload는 누구나 디코딩하여 확인할 수 있습니다. 여기서 누구나 디코딩할 수 있다는 말은 Payload에는 유저의 중요한 정보(비밀번호)가 들어가면 쉽게 노출될 수 있다는 말이 됩니다. <br>**하지만 Verify Signature는 SECRET KEY를 알지 못하면 복호화할 수 없습니다.**

- JWT 순서

  [![2021-03-04-11-05-49.png](https://i.postimg.cc/DwdzqX1y/2021-03-04-11-05-49.png)](
