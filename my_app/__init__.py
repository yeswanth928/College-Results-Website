from flask import Flask
from flask_mail import Mail
from flask_bootstrap import Bootstrap
from flask_wtf.csrf import CSRFProtect
import os


bootstrap=Bootstrap()
mail=Mail()
csrf=CSRFProtect()

def create_app():
    """Creates the instance of an app."""
    configuration_file=os.getcwd()+'/./configuration.cfg'
    app=Flask(__name__)
    app.config.from_pyfile(configuration_file)
    bootstrap.init_app(app)
    mail.init_app(app)
    from my_app.admin import admin
    app.register_blueprint(admin)
    from my_app.main import main
    app.register_blueprint(main)
    
    return app
