#example of a flask applet
from flask import Flask, render_template
import os
#Flask constructor takes the name of the current module as the argument
app = Flask(__name__)

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

