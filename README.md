# Library RBAC System

A web-based Role-Based Access Control (RBAC) system built with **Python**, **Flask**, and **MySQL** for managing users, books, and permissions for a Library.

## Features

- Role-based dashboards for **Admin**, **Librarian**, and **Student**
- Secure user **registration**, **login**, and **logout**
- **Password hashing** with bcrypt and salting
- **Admin** can add/edit/delete users and assign roles
- **Librarian** can add/delete books, approve returns
- **Students** can borrow books and request returns
- MySQL database integration with Flask

## Tech Stack

- Python
- Flask
- MySQL
- Flask-Login
- Bcrypt

## Role Permissions

| Role        | Permissions                              |
|-------------|-------------------------------------------|
| Admin       | AddUser, DeleteUser, UpdatePermissions    |
| Librarian   | AddBook, DeleteBook, ReturnBook           |
| Student     | BorrowBook, SearchBook, ReturnBook        |

## Installation

```bash
git clone https://github.com/bt00000/RBAC-Library-Project.git
cd RBAC-Library-Project-main
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt  # or install manually:
pip install flask flask-mysqldb flask-login bcrypt
```

## Configuration

Edit `config.py`:

```python
MYSQL_HOST = 'localhost'
MYSQL_USER = 'your_mysql_user'
MYSQL_PASSWORD = 'your_mysql_password'
MYSQL_DB = 'your_db_name'
```

Create the required MySQL tables (ask me for schema if missing).

## Run the App

```bash
python run.py
```

Visit: [http://127.0.0.1:5000](http://127.0.0.1:5000)

## Full Report Avaliable Here:
https://docs.google.com/document/d/1TWibdhpdTEB0i6JS0GgT1x9waJ6dzoi6V1Vu3vXoalg/edit?tab=t.0

## Use Cases

- Students can borrow and return books
- Librarians manage inventory
- Admins manage users and roles

## Security

- Passwords are hashed with `bcrypt` + salt
- Session-based authentication
- Role-based route protection using decorators
