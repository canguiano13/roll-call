#example of a flask applet
from flask import Flask, render_template
from dotenv import load_dotenv
import os
import sqlalchemy

#Load the environment variables from the .env file
load_dotenv()

#Flask constructor takes the name of the current module as the argument
app = Flask(__name__)

#Initialize the database connection
def init_db():
    db_config = {
        'pool_size': 5,
        'max_overflow': 2,
        'pool_timeout': 30,
        'pool_recycle': 1800,
    }
    return init_unix_connection_engine(db_config)

def init_unix_connection_engine(db_config):
    pool = sqlalchemy.create_engine(
        sqlalchemy.engine.url.URL(
            drivername="postgresql+pg8000",
            host="localhost", 
            port=5432,
            username=os.environ.get("CLOUD_SQL_USERNAME"),
            password=os.environ.get("CLOUD_SQL_PASSWORD"),
            database=os.environ.get("CLOUD_SQL_DATABASE"),
            query={"unix_socket": "/cloudsql/{}".format(os.environ.get("CLOUD_SQL_CONNECTION_NAME"))},
        ),
        **db_config
    )
    pool.dialect.description_encoding = None
    return pool

db = init_db()


#route() decorator tells the app which URL should call the below function
@app.route("/")
def hello_world():
    return "Hello, World."

#can also add variables into the route. it will build the URL dynamically
@app.route("/hello/<name>")
def hello_name(name):
    return f"Hello {name}!"

#flask can also render HTML templates
@app.route("/test")
def html_test():
    return render_template('test.html')
  
#main can act as a driver
if __name__ == "__main__":
    #runs the app listening on all hosts on port 8080
    app.run(debug=True, host="0.0.0.0", port=8080)