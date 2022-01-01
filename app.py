# Import all the necessary modules here
from flask import Flask, render_template, abort, request, redirect, session, send_file, url_for
from flask_pymongo import PyMongo
from cfg import config
from utils import get_random_string
from werkzeug.utils import secure_filename
import json
import math
import os
from hashlib import sha256
from datetime import datetime
from bson import ObjectId

app = Flask(__name__)
app.secret_key = b'delph@!#78d%'
# Set configurations for flask environment
app.config["MONGO_URI"] = config['mongo_uri']
app.config["UPLOAD_FOLDER"] = 'uploads'
app.config["MAX_CONTENT_LENGTH"] = 1024 * 1024 *10
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
    try:
        if session['redirectPage'] is None:
            session['redirectPage'] = '/main'
    except KeyError:
        session['redirectPage'] = '/main'
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
    error = ''
    if 'error' in session:
        error = session['error']
        session.pop('error', None)

    success = ''
    if 'fileDeleted' in session:
        success = session['fileDeleted']
        session.pop('fileDeleted', None) 

    if not 'userToken' in session:
        session['error'] = 'You must login to access this page'
        session['redirectPage'] = '/main'
        return redirect('/login')

    token_document = mongo.db.user_tokens.find_one({
        'sessionHash': session['userToken']
    })
    if token_document is None:
        session.pop('userToken', None)
        session['error'] = 'You must login again to access this page'
        session['redirectPage'] = '/main'
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
    return render_template('files.html', title='ShareBytes | Store and Share your file anyone, anywhere', user=user, uploadedFiles=uploaded_files_for_display, fileCount=file_count, error=error, success=success)

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
        if session['redirectPage'] == '/main':
            return redirect('/main')
        else:
            path = session['redirectPage']
            session['redirectPage'] = '/main'
            return redirect(path)

@app.route('/logout')
def logout():
    session.pop('userToken', None)
    session['registerSuccess'] = 'You are now logged out.'
    return redirect('/login')

def validateFileType(filename):
    ALLOWED_EXTENSIONS = ['jpg', 'jpeg', 'png', 'gif', 'svg']
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/handle_file_upload', methods=['POST'])
def handleFileUpload():
    if request.method == 'POST':
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


        if 'uploaded_file' not in request.files:
            session['error'] = 'No file uploaded!'
            return redirect('/main')
        uploaded_file = request.files['uploaded_file']
        print(uploaded_file)

        if uploaded_file.filename == '':
            session['error'] = 'No file selected!'
            return redirect('/main')

        if not validateFileType(uploaded_file.filename):
            session['error'] = 'File type not supported currently!'
            return redirect('/main')


        filename = secure_filename(uploaded_file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        uploaded_file.save(filepath)
        extension = uploaded_file.filename.rsplit('.', 1)[1].lower()
        size = os.stat(filepath).st_size

        result = mongo.db.files.insert_one({
            'userId': token_document['userID'],
            'originalFileName': uploaded_file.filename,
            'fileType': extension,
            'fileSize': size,
            'fileHash': sha256(uploaded_file.read()).hexdigest(),
            'filePath': filepath,
            'isActive': True,
            'createdAt': datetime.utcnow(),
            'updatedAt': datetime.utcnow()
        })

        return redirect('/main')

@app.errorhandler(413)
def too_large(e):
    session['error'] = 'File size is too large. Max file size supported is {0} MB'.format(app.config["MAX_CONTENT_LENGTH"])
    return redirect('/main')

@app.route('/download/<fileId>/<fileNameSlugified>', methods=["GET"])
def showDownloadPage(fileId, fileNameSlugified):
    if not 'userToken' in session:
        session['error'] = 'You must login to access this page'
        session['redirectPage'] = '/download/' + fileId + '/' + fileNameSlugified
        return redirect('/login')

    token_document = mongo.db.user_tokens.find_one({
        'sessionHash': session['userToken']
    })
    if token_document is None:
        session.pop('userToken', None)
        session['error'] = 'You must login again to access this page'
        return redirect('/login')

    userId = token_document['userID']
    users = mongo.db.users.find_one({
        '_id': userId
    })

    file_object = None
    file_object = mongo.db.files.find_one({
        '_id': ObjectId(fileId),
        'isActive': True
    })
    if file_object is None:
        return abort(404)

    file_object['fileSize'] = get_converted_file_size(file_object['fileSize'])
    current_time = datetime.utcnow()
    date_diff = current_time - file_object['createdAt']
    file_object['createdAt'] = str(date_diff.days) + ' days ago' if date_diff.days < 31 else file_object['createdAt'].strftime("%Y-%m-%d")
        

    return render_template('download.html', title='ShareBytes | Download Your File', user=users['email'], file=file_object)

@app.route('/download-file/<fileId>', methods=['GET'])
def downloadFile(fileId):
    if not 'userToken' in session:
        session['error'] = 'You must login to access this page'
        session['redirectPage'] = '/download-file/' + fileId
        return redirect('/login')

    token_document = mongo.db.user_tokens.find_one({
        'sessionHash': session['userToken']
    })
    if token_document is None:
        session.pop('userToken', None)
        session['error'] = 'You must login again to access this page'
        return redirect('/login')

    file_object = None
    file_object = mongo.db.files.find_one({
        '_id': ObjectId(fileId),
        'isActive': True
    })
    if file_object is None:
        return abort(404)

    path = file_object['filePath']
    try:
        return send_file(path, as_attachment=True)
    except FileNotFoundError:
        return abort(404)

@app.errorhandler(404)
def fileNotFound(e):
    return render_template('404.html', title='ShareBytes | 404 Page Not Found')

@app.route('/handle-delete/<id>')
def handleDelete(id):
    print(id)
    print(ObjectId(id))
    post = mongo.db.files.update({
        '_id': ObjectId(id)
    }, {
        'isActive': False
    })
    session['fileDeleted'] = 'The selected file has ben deleted!'
    return redirect('/main')

@app.route('/subscribe-to-newsletter',methods=['GET', 'POST'])
def addEmailToNewsletterList():
    if request.method == 'POST':
        email = request.json['newsletterEmail']
        print(email)
        token_document = mongo.db.newsletter.find_one({
            'email': email
        })
        if token_document is not None:
            return json.dumps({'message': 'Email Already Subscribed'})
        result = mongo.db.newsletter.insert_one({
            'email': email
        })
        return json.dumps({'message': 'Subscribed To The Newsletter'})

@app.route('/download-desktop-app')
def downloadDesktopApp():
    back = ''
    try:
        back = request.referrer
        if back is None:
            raise Exception
    except:
        back = 'http://localhost:5000'
    return render_template('desktop_app.html', title='ShareBytes | Desktop App Coming Soon', back=back)

@app.route('/contact')
def contact():
    message = ''
    # Add any message if any
    if 'contact_us_success' in session:
        message = session['contact_us_success']
        session.pop('contact_us_success', None)
    return render_template('contact_us.html', title='ShareBytes | Contact Us', message=message)

@app.route('/get-contact-details', methods=['POST'])
def getContactDetails():
    if request.method == 'POST':
        name = request.form['contact-name'].strip()
        email = request.form['contact-email'].strip()
        message = request.form['contact-message'].strip()
        print(name, message, email)
        result = mongo.db.contact_us_details.insert_one({
            'name': name,
            'email': email,
            'message': message,
            'createdAt': datetime.utcnow()
        })
        session['contact_us_success'] = 'Your message is sent. You\'ll soon be contacted by our team.' 
        return redirect('contact')

@app.route('/help-forum')
def helpForum():
    all_posts = mongo.db.posts.find({})
    return render_template('help_forum.html', title='ShareBytes | Help Forum', posts=all_posts)

@app.route('/post/<id>')
def post(id):
    if not 'userToken' in session:
        session['error'] = 'You must login to access this page'
        session['redirectPage'] = '/post/' + id
        return redirect('/login')

    try: 
        fetch_post = mongo.db.posts.find_one({
            '_id': ObjectId(id)
        })
    except:
        abort(404)

    if fetch_post is not None:
        fetch_post['postedAt'] = fetch_post['postedAt'].strftime('%b %d %Y %I:%M%p')
        for item in fetch_post['comments']:
            item['postedAt'] = item['postedAt'].strftime('%b %d %Y %I:%M%p')
        fetch_post['totalAnswers'] = len(fetch_post['comments'])
    else:
        fetch_post = []
        return abort(404)
    return render_template('post.html', title='ShareBytes | View post', post=fetch_post, user=session['user'])

@app.route('/ask-question')
def question():
    if not 'userToken' in session:
        session['error'] = 'You must login to access this page'
        session['redirectPage'] = '/ask-question'
        return redirect('/login')

    token_document = mongo.db.user_tokens.find_one({
        'sessionHash': session['userToken']
    })
    if token_document is None:
        session.pop('userToken', None)
        session['error'] = 'You must login again to access this page'
        return redirect('/login')

    userId = token_document['userID']
    users = mongo.db.users.find_one({
        '_id': userId
    })
    return render_template('question.html', title='ShareBytes | Ask your question', user=users['email'])

@app.route('/post-question', methods=['POST'])
def addQuestion():
    if request.method == 'POST':
        question = request.form['question']
        description = request.form['description']
        result = mongo.db.posts.insert_one({
            'question': question,
            'description': description,
            'user': session['user'],
            'deleted': 0,
            'comments': [],
            'postedAt': datetime.utcnow(),
        })
        return redirect(url_for('post', id=result.inserted_id))

@app.route('/add-comment/<id>', methods=['POST'])
def addComment(id):
    if request.method == 'POST':
        comment = request.form['comment']
        post = mongo.db.posts.update({
            '_id': ObjectId(id)
        }, {
            '$push': {
                'comments': {
                    'message': comment,
                    'postedBy': session['user'],
                    'postedAt': datetime.utcnow()
                }
            }
        })
        return redirect(url_for('post', id=ObjectId(id)))

@app.route('/blog')
def blog():
    post = mongo.db.all_blogs.find({})
    return render_template('blog.html', title='ShareBytes | Blog', blogs=post)

@app.route('/blog-post/<id>')
def blogPost(id):
    blog = mongo.db.blog.find_one({
        '_id': ObjectId(id)
    })
    title = 'ShareBytes | ' + blog['title']
    blog['content'] = blog['content'].split('\n')
    return render_template('blog_post.html', title=title, blog=blog)

if __name__ == '__main__':
    app.run(debug=True) # Debug set to True for development purpose