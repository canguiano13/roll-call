# app.py

import os
from flask import Flask, render_template
from db import get_messages

app = Flask(__name__)

@app.route('/')
def index():
    try:
        data = get_messages()
    except Exception as e:
        app.logger.error("Error fetching messages: %s", e)
        return "An error occurred while fetching data.", 500
    return render_template('testhome.html', data=data)

@app.route('/signin')
def signin():
    return render_template('signin.html')

@app.route('/createEvent')
def create_event():
    return render_template('createEvent.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
