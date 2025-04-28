# extensions.py
# defines and instantiates database and login management extensions to base flaks library

from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()