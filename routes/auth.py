from flask import Blueprint, render_template, redirect, request, flash
from flask_login import login_user, logout_user
from models import User
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db

auth_bp = Blueprint("auth", __name__)

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return render_template('signup.html')
    form_data = request.form.to_dict()
    if User.query.filter_by(email=form_data['email']).first():
        flash('User already exists with current email.', 'error')
        return redirect('/signup')
    hashed_pw = generate_password_hash(form_data['password_hash'])
    user = User(first_name=form_data['first_name'], last_name=form_data['last_name'],
                email=form_data['email'], password_hash=hashed_pw)
    db.session.add(user)
    db.session.commit()
    flash("Account was successfully created!", "success")
    return redirect('/login')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('signin.html')
    form_data = request.form.to_dict()
    user = User.query.filter_by(email=form_data['email']).first()
    if not user or not check_password_hash(user.password_hash, form_data['password']):
        flash('Invalid credentials.', 'error')
        return redirect('/login')
    login_user(user)
    flash("Successfully logged in!", "success")
    return redirect('/')

@auth_bp.route('/logout')
def logout():
    logout_user()
    flash("Successfully logged out.", "success")
    return redirect('/login')
