from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_restful import Api

db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()
api_ref = Api()
