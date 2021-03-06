from datetime import datetime

from app import db
from app.main import bp
from app.main.forms import EditProfileForm, EmptyFollowForm, PostForm, UploadImagesForm
from app.models import User, Post

from flask import render_template, redirect, flash, url_for, request, g, current_app
from flask_babel import get_locale
from flask_babel import gettext as _T
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename

@bp.route("/", methods = ["GET", "POST"])
@bp.route("/index", methods = ["GET", "POST"])
@login_required
def index():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body = form.post.data, author = current_user)
        db.session.add(post)
        db.session.commit()
        flash(_T("Your post has been saved"))

        # Post/Redirect/Get pattern
        # https://en.wikipedia.org/wiki/Post/Redirect/Get
        return redirect(url_for("main.index"))

    # Paginate posts
    # A page can be passed as a request argument
    # Ex. /index?page=3
    page = request.args.get(key = 'page', default = 1, type = int)
    ret_404_on_empty_range = False
    posts = current_user.followed_posts()\
                        .paginate(page, current_app.config['POSTS_PER_PAGE'], ret_404_on_empty_range)

    next_url = url_for("main.index", page = posts.next_num)\
            if posts.has_next else None
    prev_url = url_for("main.index", page = posts.prev_num)\
            if posts.has_prev else None

    return render_template("index.html", title = "Home", form = form,
            posts = posts.items, next_url = next_url, prev_url = prev_url)

# Create a user page
@bp.route("/user/<username>")
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
                .paginate(page, current_app.config['POSTS_PER_PAGE'], ret_404_on_empty_range)

    next_url = url_for("main.user", username = username, page = posts.next_num)\
            if posts.has_next else None
    prev_url = url_for("main.user", username = username, page = posts.prev_num)\
            if posts.has_prev else None

    return render_template("user.html", user = user, form = form,
            posts = posts.items, next_url = next_url, prev_url = prev_url)

@bp.route("/edit_profile", methods = ["GET", "POST"])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        # A POST request is sent when the form is submitted
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash(_T("Your changes have been saved."))
        return redirect(url_for("main.edit_profile"))
    elif request.method == "GET":
        # A GET request is sent when the edit page is accessed
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template("edit_profile.html", title = "Edit Profile", form = form)

# Log user last access time before any request
@bp.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

    g.locale = str(get_locale())

@bp.route("/follow/<username>", methods = ["POST"])
@login_required
def follow(username):
    form = EmptyFollowForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username = username).first()
        if user is None:
            flash(_T("User %(username)s not found.", username = username))
            return redirect(url_for("main.index"))
        if user == current_user:
            flash(_T("You cannot follow yourself!"))
            return redirect(url_for("main.user", username = username))
        current_user.follow(user)
        db.session.commit()
        flash(_T("You are following %(username)s!", username = username))
        return redirect(url_for("main.user", username = username))
    else:
        return redirect(url_for("main.index"))


@bp.route("/unfollow/<username>", methods = ["POST"])
@login_required
def unfollow(username):
    form = EmptyFollowForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username = username).first()
        if user is None:
            flash(_T("User %(username)s not found.", username = username))
            return redirect(url_for("main.index"))
        if user == current_user:
            flash(_T("You cannot unfollow yourself!"))
            return redirect(url_for("main.user", username = username))
        current_user.unfollow(user)
        db.session.commit()
        flash(_T("You are not following %(username)s.", username = username))
        return redirect(url_for("main.user", username = username))
    else:
        return redirect(url_for("main.index"))

@bp.route("/explore")
@login_required
def explore():
    # Paginate posts
    # A page can be passed as a request argument
    # Ex. /index?page=3
    page = request.args.get(key = 'page', default = 1, type = int)
    ret_404_on_empty_range = False
    posts = Post.query.order_by(Post.timestamp.desc())\
            .paginate(page, current_app.config['POSTS_PER_PAGE'], ret_404_on_empty_range)

    next_url = url_for("main.explore", page = posts.next_num)\
            if posts.has_next else None
    prev_url = url_for("main.explore", page = posts.prev_num)\
            if posts.has_prev else None

    return render_template("index.html", title = "Explore", posts = posts.items,
            next_url = next_url, prev_url = prev_url)

@bp.route("/upload", methods = ["GET", "POST"])
@login_required
def upload():
    form = UploadImagesForm()
    if request.method == "POST":
        uploaded_file = request.files['file']
        for uploaded_file in request.files.getlist('file'):
            if uploaded_file.filename != '':
                #uploaded_file.save(uploaded_file.filename)
                print(secure_filename(uploaded_file.filename))

        flash(_T("Your images have been submitted for processing"))

        # Post/Redirect/Get pattern
        # https://en.wikipedia.org/wiki/Post/Redirect/Get
        return redirect(url_for("main.index"))

    return render_template("upload.html", title = "Upload Images", form = form)


