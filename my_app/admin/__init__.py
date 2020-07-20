from flask import Blueprint
admin=Blueprint('admin',__name__,template_folder="/./templates")
from my_app.main.classes import check_login
from . import views