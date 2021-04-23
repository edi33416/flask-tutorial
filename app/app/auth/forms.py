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

class ResetPasswordRequestForm(FlaskForm):
    email = StringField(_LT("Email"), validators=[DataRequired(), Email()])
    submit = SubmitField(_LT("Request Password Reset"))

class ResetPasswordForm(FlaskForm):
    password = PasswordField(_LT("Password"), validators = [DataRequired()])
    password2 = PasswordField(_LT("Repeat Password"),
            validators = [DataRequired(), EqualTo("password")])

    submit = SubmitField(_LT("Reset Password"))
