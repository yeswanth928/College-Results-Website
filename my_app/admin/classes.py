from flask import current_app,session,redirect,url_for
from my_app.main.classes import DBcursor
from functools import wraps
from flask_wtf import FlaskForm
from wtforms import FileField,SubmitField,StringField
from wtforms.validators import DataRequired
from flask_wtf.file import FileRequired,FileAllowed
from my_app import main


def check_admin(func):
    @wraps(func)
    def wrapper(*args,**kargs):
        """Used to check if an user is Admin"""

        if session.get('admin',False):
            return func(*args,**kargs)
        return redirect(url_for('main.logout'))
    return wrapper

class MarksExcel(FlaskForm):
    """This MarksExcel class is used to generate a form that is used to update students marks.And only xls, xlsx, xlsm and xlsb files are allowed to be uploaded."""

    excel = FileField('Choose the Excel file.', validators = [FileRequired("An image is required to upload"), FileAllowed(['xls', 'xlsx', 'xlsb', 'xlsm'])])
    submit = SubmitField("Upload")

class MarksUpdate(FlaskForm):
    """This MarksUpdate form is used to update students grade if there's any mistake after entering their grade in database."""

    reg = StringField("Registration Number", validators = [DataRequired('This feild is necessary.')])
    sem = StringField("Sem", validators = [DataRequired('This field is neceessary.')])
    sub_code = StringField("Subject Code", validators = [DataRequired('This feild is necessary.')])
    grade = StringField("Grade", validators = [DataRequired('This feild is necessary.')])
    credit = StringField("Credits", validators = [DataRequired('This feild is necessary.')])
    submit = SubmitField('Submit')