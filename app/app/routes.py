from datetime import datetime

from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm
from app.models import User

from flask import render_template, redirect, flash, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse

@app.route('/')
@app.route("/index")
@login_required
def index():
    user = { "username": "Edi" }
    posts = [
            { "author": { "username": "Aaa"},
               "body": "Bla bla"
            },
            { "author": { "username": "Baa"},
               "body": "Bla bla bla"
            }]

    return render_template("index.html", title="Test", posts=posts)

@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash("Invalit username or password")
            return redirect(url_for("login"))

        # Login user in Flask-Login
        login_user(user, remember=form.remember_me.data)

        # If the user was redirected to the login page from a protected one
        # we must redirect to the initial page after a login
        next_page = request.args.get("next")
        # Ensure next_page is not empty or it's a local page, not a different site
        if not next_page or url_parse(next_page).netloc != "":
            next_page = url_for("index")
        return redirect(next_page)

    return render_template("login.html", title="Sign In", form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))

@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    form = RegistrationForm()

    if form.validate_on_submit():
        user = User(username = form.username.data, email = form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Congrats! You've logged in")
        return redirect(url_for("login"))

    return render_template("register.html", form = form)

# Create a user page
@app.route("/user/<username>")
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = [
        {"author": user, "body": "Test post #1"},
        {"author": user, "body": "Test post #2"}
    ]
    return render_template("user.html", user=user, posts=posts)

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        # A POST request is sent when the form is submitted
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        # A GET request is sent when the edit page is accessed
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile',
            form=form)

# Log user last access time before any request
@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
