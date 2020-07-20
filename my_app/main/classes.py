#This file contains decorators,classes,functions that will be used by rest of the app.

from flask import request,session,redirect,render_template,url_for,current_app
from wtforms import StringField,PasswordField,FileField,SubmitField
from wtforms.validators import DataRequired,Regexp,Length,Email,EqualTo
from flask_wtf.file import FileAllowed,FileRequired
from flask_wtf import FlaskForm
from flask_mail import Message
from threading import Thread
from functools import wraps
import mysql.connector
from .. import mail
from . import main


def check_login(func):
    @wraps(func)
    def wrapper(*args,**kwargs):
        """Used to check if a user is logged in.
        
        If the user is logged in it just return the function.
        Else the user is redirected to login page.
        """
        if ('name' not in session) or (session.get('name', None) == None):
            return redirect(url_for('main.login_user'))
        return func(*args, **kwargs)      
    return wrapper 

 
class DBcursor:
    """This class is used to make querying database easier.This is a Context Manager.
    
    Context managers allow you to allocate and release resources precisely when you want to.
    """
    def __init__(self,**dbcon: dict) -> None:
        self.dbdet = dbcon

    def __enter__(self) -> 'cursor':
        self.conn = mysql.connector.connect(**self.dbdet)
        self.cursor = self.conn.cursor()
        return self.cursor

    def __exit__(self,exc_type,exc_value,exc_trace) -> None:
        self.conn.commit()
        self.cursor.close()
        self.conn.close()

class LoginForm(FlaskForm):
    """This class is used to generate a login form as the name suggests."""
    style_dict = {"class": "text-center", "style": "background-color: #0095ff; color: azure; margin: auto;" }
    user_na = StringField('Enter Your Registration Number', validators = [DataRequired('This Field is necessary'), Length(min = 8, max = 8, message = 'Enter a valid registration number')])
    user_psw = PasswordField('Enter your Password', validators = [DataRequired()])
    submit = SubmitField('Submit',render_kw=style_dict)

class ForgotPasword(FlaskForm):
    """This class is used to when users forget their passwords."""
    style_dict = {"class": "text-center", "style": "background-color: #0095ff; color: azure; margin: auto;" }
    user_na = StringField('Enter Your Registration Number', validators = [DataRequired('This Field is necessary'), Length(min = 8, max = 8, message = 'Enter a valid registration number')])
    submit = SubmitField('Submit',render_kw=style_dict)

class MailForm(FlaskForm):  
    """This MailForm class is used to generate a form that is used to update user mail id. And it uses email validator."""

    new_mail = StringField("Enter the new mail address", validators = [Email(message = "Enter a valid email id", check_deliverability = True), DataRequired("Email feild cannot be empty")])
    user_psw = PasswordField("Enter your account Password",validators = [DataRequired("Password is required")])
    submit = SubmitField("Submit")

class PhoneForm(FlaskForm):
    """This PhoneForm class is used to generate a from that is used to update user phone number.It takes a 10 digit phone number only."""

    new_phone = StringField("Enter your phone number", validators = [DataRequired("This field is necessary"), Regexp(regex=r'^[0-9]{10}$', message="Enter a valid phone number")])
    user_psw = PasswordField("Enter your account Password", validators = [DataRequired("Password is required")])
    submit = SubmitField("Submit")

class PasswordForm(FlaskForm):
    """This PasswordForm class is used to generate a form that is used to update the password of the user.
    
    It imposes certain restrictions such as length of the new password.
    """
    new_pass = PasswordField("Enter your New Password", validators = [DataRequired("This field is necessary"), Length(min = 8, max = 20)])
    re_pass = PasswordField("Repeat Password", validators = [DataRequired("This field is necessary"), EqualTo('new_pass', message = "Entered Passwords doesn't match")])
    user_psw = PasswordField("Enter your current password", validators = [DataRequired("This field is necessary")])
    submit = SubmitField("Submit")

class ImageForm(FlaskForm):
    """This ImageForm class is used to generate a form that is used to update the user profile pic.And only jpg,jpeg,png images are allowed to be uploaded."""

    photo = FileField('Choose the image', validators = [FileRequired("An image is required to upload"), FileAllowed(['jpg','jpeg','png','JPG','PNG','JPEG'])])
    submit = SubmitField("Upload")


def sendmail_asynchroously(to:list,subject:str,message:str,template=None,*args,**kwargs):
    """sendmail_asynchronously function is used to send a mail to the user asynchronously whenever required."""

    msg = Message(subject = subject, body = message, recipients = to, sender = current_app.config['MAIL_USERNAME'])
    if template != None:
        msg.html = template
    thr = Thread(target = async_process, args = [current_app._get_current_object(), msg])
    thr.start()
    return thr


def async_process(app, msg):
    with app.app_context():
        mail.send(msg)