from flask_babel import lazy_gettext as _LT
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length
from app.models import User

class LoginForm(FlaskForm):
    username = StringField(_LT("Username"), validators = [DataRequired()])
    password = PasswordField(_LT("Password"), validators = [DataRequired()])
    remember_me = BooleanField(_LT("Remember Me"))
    submit = SubmitField(_LT("Sign In"))

class RegistrationForm(FlaskForm):
    username = StringField(_LT("Username"), validators = [DataRequired()])
    email = StringField(_LT("Email"), validators = [DataRequired(), Email()])
    password = PasswordField(_LT("Password"), validators = [DataRequired()])
    password2 = PasswordField(_LT("Repeat Password"),
            validators = [DataRequired(), EqualTo("password")])

    submit = SubmitField(_LT("Register"))

    def validate_username(self, username):
        user = User.query.filter_by(username = username.data).first()
        if user is not None:
            raise ValidationError(_LT("Username is already taken"))

    def validate_email(self, email):
        user = User.query.filter_by(email = email.data).first()
        if user is not None:
            raise ValidationError(_LT("Email is already in use"))

class EditProfileForm(FlaskForm):
    username = StringField(_LT("Username"), validators=[DataRequired()])
    about_me = TextAreaField(_LT("About me"), validators=[Length(min=0, max=140)])
    submit = SubmitField(_LT("Submit"))

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        # Validation must not fail when user doesn't change username
        if username.data == self.original_username:
            return

        user = User.query.filter_by(username = username.data).first()
        if user is not None:
            raise ValidationError("Username is already taken")

class EmptyFollowForm(FlaskForm):
    """
    Because the follow and unfollow actions introduce changes in the application,
    we to implement them as POST requests, which are triggered from the web browser
    as a result of submitting a web form. It would be easier to implement these routes
    as GET requests, but then they could be exploited in CSRF attacks. Because GET
    requests are harder to protect against CSRF, they should only be used on actions
    that do not introduce state changes. Implementing these as a result of a form
    submission is better because then a CSRF token can be added to the form.
    """
    submit = SubmitField(_LT("Submit"))

class PostForm(FlaskForm):
    post = TextAreaField(_LT("Say something:"), validators = [DataRequired(), Length(min = 1, max = 140)])
    submit = SubmitField(_LT("Submit"))

class ResetPasswordRequestForm(FlaskForm):
    email = StringField(_LT("Email"), validators=[DataRequired(), Email()])
    submit = SubmitField(_LT("Request Password Reset"))

class ResetPasswordForm(FlaskForm):
    password = PasswordField(_LT("Password"), validators = [DataRequired()])
    password2 = PasswordField(_LT("Repeat Password"),
            validators = [DataRequired(), EqualTo("password")])

    submit = SubmitField(_LT("Reset Password"))

