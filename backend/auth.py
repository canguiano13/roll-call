from flask import Blueprint, render_template, redirect, request, flash
from flask_login import login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash

from models import User
from extensions import db


auth = Blueprint("auth", __name__)

#handle creation of new accounts
@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    #render frontend template for GET requests
    if request.method == 'GET':
        return render_template('signup.html')
    form_data = request.form.to_dict()
    #validate uniqueness of user using email
    if User.query.filter_by(email=form_data['email']).first():
        flash('User already exists with current email.', 'error')
        return redirect('/signup')
    #hash the password so it is not stored in plaintext
    #werkzeug has a built-in hash password function! no external libs needed :)
    hashed_pw = generate_password_hash(form_data['password_hash'])
    #instantiate new user using ORM model
    user = User(first_name=form_data['first_name'], last_name=form_data['last_name'],
                email=form_data['email'], password_hash=hashed_pw)
    #commit to database
    db.session.add(user)
    db.session.commit()
    #display success message on next page
    flash("Account was successfully created!", "success")
    return redirect('/login')

@auth.route('/login', methods=['GET', 'POST'])
def login():
    #render frontend template for GET requests
    if request.method == 'GET':
        return render_template('signin.html')
    #retrieve form data
    form_data = request.form.to_dict()
    #fetch the user from the database
    user = User.query.filter_by(email=form_data['email']).first()
    #validate user existence 
    if not user:
        flash("Account does not exist.", 'error')
        return redirect('/login')
    #validate login credentials
    if not check_password_hash(user.password_hash, form_data['password']):
        flash('Invalid credentials. Please try again.', 'error')
        return redirect('/login')
    #log in using flask-loginmanager function
    login_user(user)
    #display success message on next page
    flash("Successfully logged in!", "success")
    return redirect('/')

@auth.route('/logout')
def logout():
    #logout using sql-loginmanager function
    logout_user()
    #display success message on next page
    flash("Successfully logged out.", "success")
    return redirect('/login')
