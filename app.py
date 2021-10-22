# Import all the necessary modules here
from flask import Flask, render_template, abort, request, redirect, session
from flask_pymongo import PyMongo
from cfg import config
from utils import get_random_string
import json
import math
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
    # Redirect to main page if already logged in
    if 'userToken' in session:
        return redirect('/main')

    alertMesage = ''
    # Add success message if any
    if 'registerSuccess' in session:
        alertMesage = session['registerSuccess']
        session.pop('registerSuccess', None)

    error = ''
    # Add error message if any
    if 'error' in session:
        error = session['error']
        session.pop('error', None)

    session.pop('value', None)
    return render_template('login.html', title='ShareBytes | Login', alertMesage=alertMesage, error=error)

# Displays register page
@app.route('/get-started')
def register():
    # Redirect to main page if already logged in
    if 'userToken' in session:
        return redirect('/main')

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

def get_converted_file_size(size_bytes):
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return "{0} {1}".format(s, size_name[i])

# Displays the main page after successful login
@app.route('/main')
def main():
    if not 'userToken' in session:
        session['error'] = 'You must login to access this page'
        return redirect('/login')

    token_document = mongo.db.user_tokens.find_one({
        'sessionHash': session['userToken']
    })
    if token_document is None:
        session.pop('userToken', None)
        session['error'] = 'You must login again to access this page'
        return redirect('/login')

    user_id = token_document['userID']

    uploaded_files = mongo.db.files.find({
        'userId': user_id,
        'isActive': True
    }).sort('createdAt', -1)

    uploaded_files_for_display = []
    for file in uploaded_files:
        current_time = datetime.utcnow()
        date_diff = current_time - file['createdAt']
        file['formattedTime'] = str(date_diff.days) + ' days ago' if date_diff.days < 31 else file['createdAt'].strftime("%Y-%m-%d")
        file['fileSize'] = get_converted_file_size(file['fileSize'])
        uploaded_files_for_display.append(file)

    file_count = uploaded_files.count()
    user = session['user']
    return render_template('files.html', title='ShareBytes | Store and Share your file anyone, anywhere', user=user, uploadedFiles=uploaded_files_for_display, fileCount=file_count)

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

@app.route('/check-login', methods=['POST'])
def checkLogin():
    if request.method == 'POST':
        email = request.form['login-email'].strip()
        password = request.form['login-password'].strip()
        # Check if email is empty
        if not len(email) > 0:
            session['error'] = 'Email is required'
            return redirect('/login')
        # Check if password is empty
        if not len(password) > 0:
            session['error'] = 'Password is required'
            return redirect('/login')
        # Check if email present in database
        user_document = mongo.db.users.find_one({ 'email': email })
        if user_document is None:
            session['error'] = 'No account exists with this email address'
            return redirect('/login')
        # Check if password hash matches
        password_hash = sha256(password.encode('utf-8')).hexdigest()
        if user_document['password'] != password_hash:
            session['error'] = 'Password does not match'
            return redirect('/login')

        # Generate token and save it in session
        random_string = get_random_string()
        randomSessionHash = sha256(random_string.encode('utf-8')).hexdigest()
        token_object = mongo.db.user_tokens.insert_one({
            'userID': user_document['_id'],
            'sessionHash': randomSessionHash,
            'createdAt': datetime.utcnow()
        })

        session['userToken'] = randomSessionHash
        session['user'] = email
        return redirect('/main')

@app.route('/logout')
def logout():
    session.pop('userToken', None)
    session['registerSuccess'] = 'You are now logged out.'
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True) # Debug set to True for development purpose