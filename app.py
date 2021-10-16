# Import all the necessary modules here
from flask import Flask, render_template, abort
from flask_pymongo import PyMongo
from cfg import config
import json

app = Flask(__name__)
# Set configurations for flask environment
app.config["MONGO_URI"] = config['mongo_uri']
mongo = PyMongo(app)

# Displays index page
@app.route('/')
def index():
    # user_documents = mongo.db.users.find({})
    # print(user_documents)

    # user_documents = list(user_documents)
    # print(user_documents)
    return render_template('index.html', title='ShareBytes | Store and Share Your File With Anyone, Anywhere')

# Displays login page
@app.route('/login')
def login():
    return 'Login'

# Displays register page
@app.route('/get-started')
def signup():
    return 'Get Started'

if __name__ == '__main__':
    app.run(debug=True) # Debug set to True for development purpose