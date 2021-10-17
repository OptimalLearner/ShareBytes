# Import all the necessary modules here
from flask import Flask, render_template, abort, request, redirect, session
from flask_pymongo import PyMongo
from cfg import config
import json
from hashlib import sha256
from datetime import datetime

app = Flask(__name__)
app.secret_key = b'delph@!#78d%'
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
    alertMesage = ''
    # Add success message if any
    if 'registerSuccess' in session:
        alertMesage = session['registerSuccess']
        session.pop('registerSuccess', None)
    session.pop('value', None)
    return render_template('login.html', title='ShareBytes | Login', alertMesage=alertMesage)

# Displays register page
@app.route('/get-started')
def register():
    error = ''
    default_form_values = ''
    # Add error message if any
    if 'error' in session:
        error = session['error']
        session.pop('error', None)
    # Add existing form field values if any
    if 'value' in session:
        default_form_values = session['value']
        session.pop('value', None)
    return render_template('register.html', title='ShareBytes | Getting Started', error=error, value=default_form_values)

@app.route('/handle-register', methods=['POST'])
def handleRegister():
    if request.method == 'POST':
        name = request.form['register-name'].strip()
        email = request.form['register-email'].strip()
        password = request.form['register-password'].strip()
        confirm_password = request.form['register-confirm-password'].strip()
        session['value'] = [name, email, password, confirm_password]
        # Check if name is empty
        if not len(name) > 0:
            session['error'] = 'Name is required'
            return redirect('/get-started')
        # Check if email is empty
        if not len(email) > 0:
            session['error'] = 'Email is required'
            return redirect('/get-started')
        # Check if email is valid
        if not ('@' in email and '.' in email and email[0]!='@' and email[-1]!='@' and email[0]!='.' and email[-1]!='.'):
            session['error'] = 'Email is invalid'
            return redirect('/get-started')
        # Check if password is empty
        if not len(password) > 0:
            session['error'] = 'Password is required'
            return redirect('/get-started')
        # Check if confirm password is empty
        if not len(confirm_password) > 0:
            session['error'] = 'Confirm Password is required'
            return redirect('/get-started')
        # Check if password and confirm password match
        if password != confirm_password:
            session['error'] = 'Confirm Password should match the Password'
            return redirect('/get-started')

        # Check if user email already exists in database
        existing_user_count = mongo.db.users.count_documents({ 'email': email })
        if existing_user_count > 0:
            session['error'] = 'Email already exists'
            return redirect('/get-started')
        
        # Create a new user record in the database
        password = sha256(password.encode('utf-8')).hexdigest()
        result = mongo.db.users.insert_one({
            'name': name,
            'email': email,
            'password': password,
            'lastLoginDate': None,
            'createdAt': datetime.utcnow(),
            'updatedAt': datetime.utcnow()
        })
        # Registration Successful
        session['registerSuccess'] = 'Your user account is ready. You can log in now.'
        return redirect('/login')
    session['error'] = 'Invalid Request'
    return redirect('/get-started')

if __name__ == '__main__':
    app.run(debug=True) # Debug set to True for development purpose