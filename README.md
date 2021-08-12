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
HTML, CSS, JavaScript and JQuery as frontend(Refered Bootstrap and Google Searches).

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
