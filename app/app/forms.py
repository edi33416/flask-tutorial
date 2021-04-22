from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length
from app.models import User

class LoginForm(FlaskForm):
    username = StringField("Username", validators = [DataRequired()])
    password = PasswordField("Password", validators = [DataRequired()])
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("Sign In")

class RegistrationForm(FlaskForm):
    username = StringField("Username", validators = [DataRequired()])
    email = StringField("Email", validators = [DataRequired(), Email()])
    password = PasswordField("Password", validators = [DataRequired()])
    password2 = PasswordField("Repeat Password",
            validators = [DataRequired(), EqualTo("password")])

    submit = SubmitField("Register")

    def validate_username(self, username):
        user = User.query.filter_by(username = username.data).first()
        if user is not None:
            raise ValidationError("Username is already taken")

    def validate_email(self, email):
        user = User.query.filter_by(email = email.data).first()
        if user is not None:
            raise ValidationError("Email is already in use")

class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    about_me = TextAreaField('About me', validators=[Length(min=0, max=140)])
    submit = SubmitField('Submit')

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
    submit = SubmitField('Submit')

