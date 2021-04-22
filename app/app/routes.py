from datetime import datetime

from app import app, db
from app.email import send_password_reset_email
from app.forms import (LoginForm, RegistrationForm, EditProfileForm, EmptyFollowForm,
        PostForm, ResetPasswordRequestForm, ResetPasswordForm)
from app.models import User, Post

from flask import render_template, redirect, flash, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse

@app.route("/", methods = ["GET", "POST"])
@app.route("/index", methods = ["GET", "POST"])
@login_required
def index():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body = form.post.data, author = current_user)
        db.session.add(post)
        db.session.commit()
        flash("Your post has been saved")

        # Post/Redirect/Get pattern
        # https://en.wikipedia.org/wiki/Post/Redirect/Get
        return redirect(url_for("index"))

    # Paginate posts
    # A page can be passed as a request argument
    # Ex. /index?page=3
    page = request.args.get(key = 'page', default = 1, type = int)
    ret_404_on_empty_range = False
    posts = current_user.followed_posts().paginate(page, app.config['POSTS_PER_PAGE'], ret_404_on_empty_range)

    next_url = url_for("index", page = posts.next_num)\
            if posts.has_next else None
    prev_url = url_for("index", page = posts.prev_num)\
            if posts.has_prev else None

    return render_template("index.html", title = "Home", form = form,
            posts = posts.items, next_url = next_url, prev_url = prev_url)

@app.route("/login", methods = ["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username = form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash("Invalit username or password")
            return redirect(url_for("login"))

        # Login user in Flask-Login
        login_user(user, remember = form.remember_me.data)

        # If the user was redirected to the login page from a protected one
        # we must redirect to the initial page after a login
        next_page = request.args.get("next")
        # Ensure next_page is not empty or it's a local page, not a different site
        if not next_page or url_parse(next_page).netloc != "":
            next_page = url_for("index")
        return redirect(next_page)

    return render_template("login.html", title = "Sign In", form = form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))

@app.route("/register", methods = ["GET", "POST"])
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

@app.route("/reset_password_request", methods = ["GET", "POST"])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data).first()
        if user:
            send_password_reset_email(user)

        flash("Check your email for the instructions to reset your password")
        return redirect(url_for("login"))

    return render_template("reset_password_request.html",
            title = "Reset Password", form = form)

@app.route("/reset_password/<token>", methods = ["GET", "POST"])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for("index"))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash("Your password has been reset.")
        return redirect(url_for("login"))

    return render_template("reset_password.html", form = form)

# Create a user page
@app.route("/user/<username>")
@login_required
def user(username):
    form = EmptyFollowForm()
    user = User.query.filter_by(username = username).first_or_404()

    # Paginate posts
    # A page can be passed as a request argument
    # Ex. /index?page=3
    page = request.args.get(key = 'page', default = 1, type = int)
    ret_404_on_empty_range = False
    posts = user.posts.order_by(Post.timestamp.desc())\
                .paginate(page, app.config['POSTS_PER_PAGE'], ret_404_on_empty_range)

    next_url = url_for("user", username = username, page = posts.next_num)\
            if posts.has_next else None
    prev_url = url_for("user", username = username, page = posts.prev_num)\
            if posts.has_prev else None

    return render_template("user.html", user = user, form = form,
            posts = posts.items, next_url = next_url, prev_url = prev_url)

@app.route("/edit_profile", methods = ["GET", "POST"])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        # A POST request is sent when the form is submitted
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash("Your changes have been saved.")
        return redirect(url_for("edit_profile"))
    elif request.method == "GET":
        # A GET request is sent when the edit page is accessed
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template("edit_profile.html", title = "Edit Profile", form = form)

# Log user last access time before any request
@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@app.route("/follow/<username>", methods = ["POST"])
@login_required
def follow(username):
    form = EmptyFollowForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username = username).first()
        if user is None:
            flash("User {} not found.".format(username))
            return redirect(url_for("index"))
        if user == current_user:
            flash("You cannot follow yourself!")
            return redirect(url_for("user", username = username))
        current_user.follow(user)
        db.session.commit()
        flash("You are following {}!".format(username))
        return redirect(url_for("user", username = username))
    else:
        return redirect(url_for("index"))


@app.route("/unfollow/<username>", methods = ["POST"])
@login_required
def unfollow(username):
    form = EmptyFollowForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username = username).first()
        if user is None:
            flash("User {} not found.".format(username))
            return redirect(url_for("index"))
        if user == current_user:
            flash("You cannot unfollow yourself!")
            return redirect(url_for("user", username = username))
        current_user.unfollow(user)
        db.session.commit()
        flash("You are not following {}.".format(username))
        return redirect(url_for("user", username = username))
    else:
        return redirect(url_for("index"))

@app.route("/explore")
@login_required
def explore():
    # Paginate posts
    # A page can be passed as a request argument
    # Ex. /index?page=3
    page = request.args.get(key = 'page', default = 1, type = int)
    ret_404_on_empty_range = False
    posts = Post.query.order_by(Post.timestamp.desc())\
            .paginate(page, app.config['POSTS_PER_PAGE'], ret_404_on_empty_range)

    next_url = url_for("explore", page = posts.next_num)\
            if posts.has_next else None
    prev_url = url_for("explore", page = posts.prev_num)\
            if posts.has_prev else None

    return render_template("index.html", title = "Explore", posts = posts.items,
            next_url = next_url, prev_url = prev_url)





