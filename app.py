# app.py

import os
from dotenv import load_dotenv
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from db import db, login_manager
from routes import routes
from google.cloud.sql.connector import Connector

# initialize the app
app = Flask(__name__)

#load the db credentials from our env files
load_dotenv()

db_user = os.getenv('DB_USER')
db_pass = os.getenv('DB_PASS')
db_name = os.getenv('DB_NAME')
db_host = os.getenv('DB_HOST')
db_connection_name = os.getenv('DB_CONNECTION_NAME')
unix_socket_path = f'/cloudsql/{db_connection_name}'

#instantiate a google cloud connector
connector = Connector()

#turn off extra warnings
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
#configure the sqlalchemy to to use mysql
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

# initialize app with extensions
db.init_app(app)  
#login_manager.init_app(app)

#defining a model does not create it in the database.
#need to use create_all() to create the models and tables after defining them.
with app.app_context():
    db.create_all()

# import and register blueprints (routes)
app.register_blueprint(routes)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port="8080")
