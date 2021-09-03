# Social Media App
Application where user can post, chat and make friends.

# Live Demo Hosted on Heroku(Might take time to load up initially as it is hosted on Free Account)
- Any data you provide on website is not secure, so avoid using personal data.
- https://flaskteststore2021.herokuapp.com/
- id: test_user10	 password: test_user10@test.com
- id: test_user11	 password: test_user11@test.com

# Description
This application was build for learning purpose.
Its an application developed using Flask and PostgreSQL(Provided by Heroku) as backend.
HTML, CSS, JavaScript and jQuery as frontend(Referred Bootstrap and Google Searches).

# Application Funcationality
- Register
- Login
- Logout
- Home page
- User can Post
- User can check own friend list
- User can check friend request received
- User can response to those request
- User can search People 
- User can send request to People
- User can Remove people from friend list
- User can chat with friend(Without any delay considering good network and no delay in server response)
- User can check friend post

# Database Design
- user Table
  | Field         | Type          | Key           |
  | ------------- | ------------- | ------------- |
  | user_id       | Int           | PK            |
  | User_name     | varchar       |               |
  | user_email_id | varchar       |               |
  | user_password | varchar       |               |
  | user_status   | varchar       |               |
  
- relation Table
  | Field              | Type          | Key           |
  | ------------------ | ------------- | ------------- |
  | relation_id        | Int           | PK            |
  | mutual_id          | varchar       |               |
  | relation_user_id_1 | Int           | FK(user)      |
  | relation_user_id_2 | Int           | FK(user)      |
  | relation_status    | varchar       |               |
  
- request Table
  | Field                | Type          | Key           |
  | -------------------- | ------------- | ------------- |
  | request_id           | Int           | PK            |
  | request_from_user_id | Int           | FK(user)      |
  | request_to_user_id   | Int           | FK(user)      |
  | request_status       | varchar       |               |
  
- message Table
  | Field                | Type          | Key           |
  | -------------------- | ------------- | ------------- |
  | message_id           | Int           | PK            |
  | mutual_id            | varchar       |               |
  | message_from_user_id | Int           | FK(user)      |
  | message_to_user_id   | Int           | FK(user)      |
  | message              | Text          |               |
  | message_status       | varchar       |               |
  
- post Table
  | Field             | Type          | Key           |
  | ----------------- | ------------- | ------------- |
  | post_id           | Int           | PK            |
  | post_from_user_id | Int           | FK(user)      |
  | post              | varchar       |               |


# Screenshot

- Login Page

  ![alt text](https://github.com/TheLastJediCoder/Social_Media_App_Public/blob/master/static/Login%20Page.png?raw=true)
  
- Login Page

  ![alt text](https://github.com/TheLastJediCoder/Social_Media_App_Public/blob/master/static/Register.png?raw=true)

- User Home Page

  ![alt text](https://github.com/TheLastJediCoder/Social_Media_App_Public/blob/master/static/User%20Home%20Page.png?raw=true)
  
- Search Page

  ![alt text](https://github.com/TheLastJediCoder/Social_Media_App_Public/blob/master/static/Find%20Friend.png?raw=true)
  
- Friend List Page

  ![alt text](https://github.com/TheLastJediCoder/Social_Media_App_Public/blob/master/static/Friend%20List.png?raw=true)
  
- Friend/Chat Page

  ![alt text](https://github.com/TheLastJediCoder/Social_Media_App_Public/blob/master/static/Chat.png?raw=true)
  

# Requirements
- bidict==0.21.2
- cachelib==0.2.0
- cffi==1.14.6
- click==8.0.1
- colorama==0.4.4
- dnspython==1.16.0
- eventlet==0.30.2
- Flask==2.0.1
- Flask-Session==0.4.0
- Flask-SocketIO==5.1.0
- Flask-SQLAlchemy==2.5.1
- gevent==21.1.2
- gevent-websocket==0.10.1
- greenlet==1.1.0
- gunicorn==20.1.0
- itsdangerous==2.0.1
- Jinja2==3.0.1
- MarkupSafe==2.0.1
- psycopg2==2.9.1
- pycparser==2.20
- python-engineio==4.2.0
- python-socketio==5.3.0
- six==1.16.0
- SQLAlchemy==1.4.21
- Werkzeug==2.0.1
- zope.event==4.5.0
- zope.interface==5.4.0

