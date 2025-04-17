# db.py

#we might just need to restructure this file to have our extensions
#ie this file might just define the db, login/session mgmt modules
#
import os
import pymysql
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
