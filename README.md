
# ShareBytes

**ShareBytes** is a web based file sharing application. Being a web app, you can share your files from a Windows device to any Android, iOS or any other device having a web browser. 

The web app is secured through a login/register feature. They have to login before accessing the file sharing features of this application. After logging in, users can see all the files they have uploaded previously. They can also upload new files in the application. 
After uploading a file, each file will have a permanent link, which can be shared by the user to other people. Any person whether logged in or not can download the file from the link shared by that user.

Maximum size limit for individual file in 10 MB. Supported file types includes jpg, jpeg, png, gif and svg currently. If a user uploads any file that is not included in the mentioned file types and the uploaded file size is above the max file size then the app will reject the file. The application also has a support help forum where new users can ask their doubts and other active users can answer.

**Tech Stack Used:** HTML5, CSS, JavaScript, Bootstrapp 5, Flask  
**DataBase Used:** MongoDB  
**Vector Illustrations:** All vector illustrations used in this project are taken from [undraw.co](https://undraw.co/)  
**Company Logos** used in the app are taken from [Wikimedia](https://commons.wikimedia.org/)  

## Steps to run the app locally
* Install your desired version of [Python](https://www.python.org/downloads/) on your local system if not installed already.
* Install [PIP(Preferred Installer Program)](https://www.liquidweb.com/kb/install-pip-windows/). Though in newer versions, PIP is already installed.
* Install Python Virtual Environment by using the below command:
    > pip install virtualenv  
* Open command prompt (or terminal) and change the current working directory to location where you want to clone the repository.
* Then type: git clone [https://github.com/OptimalLearner/ShareBytes.git](https://github.com/OptimalLearner/ShareBytes.git)
* If the clone was successfully completed then a new sub directory may appear with the same name as the repository. Now change the currently directory to the new sub directory.
* Create and activate a virtualenv by using the following commands:
    > virtualenv venv  
    > venv/Scripts/activate
* Install all the dependencies required to run the app:
    > $ pip install -r requirements.txt
* Create a .env file in the root directory and copy the contents of env.sample file to the newly created .env file. Replace 'YOUR_EMAIL_ADDRESS' to your actual email address and 'YOUR_EMAIL_PASSWORD' to the password of the entered email address. This email and password are required for the functionality of reset password.
* Now run the app by using the below command:
    > python app.py
