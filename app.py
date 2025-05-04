# intialize app with extensions
import os
from dotenv import load_dotenv
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from extensions import db, login_manager
from models import User, Guestbook, Message
from routes import register_blueprints
from google.cloud.sql.connector import Connector

#load relevant credentials from our env files
load_dotenv()

# initialize the app
app = Flask(__name__, template_folder='templates')

# import and register blueprints (app routes)
register_blueprints(app)

# initialize app with extensions
# initialize login management module with app
# login manager instance must come first due to db module initialization with app context
login_manager.init_app(app)
login_manager.login_view = 'routes.login' #defines login route

# define user loader mechanism for login manager
@login_manager.user_loader
def load_user(user_id):
    # use the database model to get the id for users
    # since the user_id is just the primary key of our user table, use it in the query for the user
    return User.query.get(int(user_id))

# set the secret key for the sessions
# secret key is a series of random bytes, store in an env file for confidentiality.
app.secret_key = os.getenv('SESSION_MGMT_BYTES').encode('utf-8')

#pull database credentials from the .env file
db_user = os.getenv('DB_USER')
db_pass = os.getenv('DB_PASS')
db_name = os.getenv('DB_NAME')
db_host = os.getenv('DB_HOST')
db_connection_name = os.getenv('DB_CONNECTION_NAME')
unix_socket_path = f'/cloudsql/{db_connection_name}'

#instantiate a google cloud connector
connector = Connector()

#turn off extra sqlalchemy warnings
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
#configure sqlalchemy to to use mysql
app.config['SQLALCHEMY_DATABASE_URI']= 'mysql+pymysql://'
#override the default sqlalchemy engine options to connect to the cloud SQL instance
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    #lambda function returns a new connector
    "creator": lambda: connector.connect(
        f"{db_connection_name}",
        "pymysql",
        user=f'{db_user}',
        password=f'{db_pass}',
        db=f'{db_name}',
        ip_type="public"
    )
}

# initialize database module with app
db.init_app(app)  

# use create_all() to create the models and tables after defining them.
with app.app_context():
    db.create_all()

# tears down database connections when the app shuts down
@app.teardown_appcontext
def shutdown_session(exception=None):
    db.session.remove()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port="8080")
