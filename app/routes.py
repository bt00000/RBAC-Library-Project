from flask import render_template, redirect, url_for, flash, request, session
from functools import wraps
from . import app, db, bcrypt
from .models import User, Role, Book, Borrow
from datetime import datetime

def role_required(*roles):
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            if not session.get('logged_in') or 'user_id' not in session:
                flash('You need to be logged in to view this page.', 'danger')
                return redirect(url_for('login', next=request.url))
            user = User.query.get(session['user_id'])
            if user.role.name not in roles:
                flash('You do not have permission to view this page.', 'danger')
                return redirect(url_for('home'))
            return fn(*args, **kwargs)
        return decorated_view
    return wrapper

@app.route('/')
def home():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    role = session.get('role', '')
    if role == 'Administrator':
        return redirect(url_for('admin'))
    elif role == 'Librarian':
        return redirect(url_for('librarian_dashboard'))
    elif role == 'Student':
        return redirect(url_for('student_dashboard'))
    else:
        return redirect(url_for('login'))  # Redirect to login if the role is not recognized


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        role_name = request.form.get('role', 'Student')  # Default role is 'Student'

        if role_name == 'Administrator' and session.get('role') != 'Administrator':
            flash('Unauthorized role selection.', 'danger')
            return redirect(url_for('register'))

        role = Role.query.filter_by(name=role_name).first()
        if not role:
            flash(f'Role {role_name} not found. Please contact the administrator.', 'danger')
            return redirect(url_for('register'))

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(username=username, email=email, password_hash=hashed_password, role=role)
        db.session.add(user)
        db.session.commit()
        flash('Account created successfully! Please login.', 'success')
        return redirect(url_for('login'))
    roles = Role.query.all()
    return render_template('register.html', roles=roles)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'logged_in' in session and session['logged_in']:
        return redirect(url_for('home'))

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()

        if user and bcrypt.check_password_hash(user.password_hash, password):
            session['logged_in'] = True
            session['user_id'] = user.id
            session['role'] = user.role.name
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password.', 'danger')

    return render_template('login.html')

#Admin Dashboard
@app.route('/admin')
@role_required('Administrator')
def admin():
    users = User.query.all()
    return render_template('admin.html', users=users)

@app.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
@role_required('Administrator')
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    if request.method == 'POST':
        old_role = user.role.name
        new_role_name = request.form['role']
        user.username = request.form['username']
        user.email = request.form['email']
        user.role_id = Role.query.filter_by(name=new_role_name).first().id
        db.session.commit()
        flash('User updated successfully!', 'success')
        
        # Check if the role has changed and if it's the current user
        if old_role != new_role_name and user_id == session.get('user_id'):
            return logout()  # Logout if the role of the logged-in user is changed

        return redirect(url_for('admin'))
    roles = Role.query.all()
    return render_template('edit_user.html', user=user, roles=roles)

@app.route('/delete_user/<int:user_id>', methods=['POST'])
@role_required('Administrator')
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    current_user_id = session.get('user_id')  # Get current user's ID

    db.session.delete(user)
    db.session.commit()

    if user_id == current_user_id:  # Check if the deleted user is the current user
        return logout()  # Call the logout function

    flash('User deleted successfully.', 'success')
    return redirect(url_for('admin'))

@app.route('/admin/add_user_form')
@role_required('Administrator')
def add_user_form():
    roles = Role.query.all()
    return render_template('add_user_form.html', roles=roles)

@app.route('/admin/add_user', methods=['POST'])
@role_required('Administrator')
def add_user():
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']
    role_id = request.form['role']
    
    user = User.query.filter_by(email=email).first()
    if user:
        flash('Email already in use.', 'danger')
        return redirect(url_for('add_user_form'))

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    new_user = User(username=username, email=email, password_hash=hashed_password, role_id=role_id)
    db.session.add(new_user)
    db.session.commit()
    flash('User added successfully.', 'success')
    return redirect(url_for('admin'))

#Librarian Dashboard
@app.route('/librarian_dashboard')
@role_required('Librarian')
def librarian_dashboard():
    books = Book.query.all()  # Fetch all books from the database
    
    # Initialize a dictionary to store borrow details
    borrow_details = {}
    
    # Iterate over all books to check their availability and fetch borrow details if they are checked out
    for book in books:
        if not book.is_available:
            borrow = Borrow.query.filter_by(book_id=book.id).order_by(Borrow.borrow_date.desc()).first()
            if borrow:
                borrow_details[book.id] = borrow
    
    # Pass books and their borrow details to the template
    return render_template('librarian_dashboard.html', books=books, borrow_details=borrow_details)

@app.route('/librarian/add_book', methods=['GET', 'POST'])
@role_required('Librarian')
def add_book():
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        isbn = request.form['isbn']
        book = Book(title=title, author=author, isbn=isbn)
        db.session.add(book)
        db.session.commit()
        flash('Book added successfully!', 'success')
        return redirect(url_for('librarian_dashboard'))
    return render_template('add_book.html')

@app.route('/delete_book/<int:book_id>', methods=['POST'])
@role_required('Librarian')
def delete_book(book_id):
    book = Book.query.get_or_404(book_id)
    # Make sure to handle associated Borrow records or other dependencies before deleting
    db.session.delete(book)
    db.session.commit()
    flash('Book deleted successfully!', 'success')
    return redirect(url_for('librarian_dashboard'))


@app.route('/return_book/<int:borrow_id>', methods=['POST'], endpoint='return_book_librarian')
@role_required('Librarian')
def return_book(borrow_id):
    borrow = Borrow.query.get_or_404(borrow_id)
    borrow.book.is_available = True
    db.session.commit()
    flash('Book returned successfully!', 'success')
    return redirect(url_for('librarian_dashboard'))

@app.route('/approve_return/<int:borrow_id>', methods=['POST'])
@role_required('Librarian')
def approve_return(borrow_id):
    borrow = Borrow.query.get_or_404(borrow_id)
    if borrow.return_requested:
        borrow.book.is_available = True
        borrow.return_date = datetime.utcnow()
        borrow.return_requested = False
        db.session.commit()
        flash('Return approved. Book is now available.', 'success')
    else:
        flash('No return requested for this book.', 'danger')
    return redirect(url_for('librarian_dashboard'))

#Student Dashboard
@app.route('/student_dashboard')
@role_required('Student')
def student_dashboard():
    books = Book.query.all()
    borrow_details = {}

    # Collect borrow details for each book
    for book in books:
        borrow = Borrow.query.filter_by(book_id=book.id).order_by(Borrow.borrow_date.desc()).first()
        if borrow:
            borrow_details[book.id] = borrow

    return render_template('student_dashboard.html', books=books, borrow_details=borrow_details)


@app.route('/borrow_book/<int:book_id>', methods=['POST'])
@role_required('Student')
def borrow_book(book_id):
    book = Book.query.get_or_404(book_id)
    if book.is_available:
        new_borrow = Borrow(user_id=session['user_id'], book_id=book.id)
        book.is_available = False  # Mark the book as borrowed
        db.session.add(new_borrow)
        db.session.commit()
        flash('You have successfully borrowed the book.', 'success')
    else:
        flash('This book is currently unavailable.', 'danger')
    return redirect(url_for('student_dashboard'))

@app.route('/return_book/<int:borrow_id>', methods=['POST'])
@role_required('Student')
def return_book(borrow_id):
    borrow = Borrow.query.get_or_404(borrow_id)
    borrow.return_date = datetime.utcnow()
    borrow.book.is_available = True  # Mark the book as available
    db.session.commit()
    flash('Book returned successfully.', 'success')
    return redirect(url_for('student_dashboard'))

@app.route('/request_return/<int:borrow_id>', methods=['POST'])
@role_required('Student')
def request_return(borrow_id):
    borrow = Borrow.query.get_or_404(borrow_id)
    if borrow.user_id == session['user_id'] and not borrow.return_requested:
        borrow.return_requested = True
        db.session.commit()
        flash('Return requested. Please wait for librarian approval.', 'success')
    else:
        flash('You have already requested a return for this book.', 'danger')
    return redirect(url_for('student_dashboard'))

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('user_id', None)
    session.pop('role', None)  # Also clear the role from the session
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))