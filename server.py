from flask import Flask, render_template, redirect, url_for, request, session
# import the Connector function
from mysqlconnection import MySQLConnector
import os, binascii
import md5
app = Flask(__name__)
app.secret_key = os.urandom(24)
# connect and store the connection in "mysql"; note that you pass the database name to the function
mysql = MySQLConnector(app, 'theWall')
# an example of running a query



@app.route('/')
def index():
    if 'stat' not in session:
        session['stat'] = False
    else:
        print(session['stat'])
    # friends = mysql.query_db("SELECT * FROM friends")
    # all_friends = friends
    return render_template('index.html')

@app.route('/loginpage')
def loginpage():
    if 'stat' not in session:
        session['stat'] = False
    else:
        print(session['stat'])
    return render_template('login.html')

@app.route('/logout')
def logout():
    if session['stat']:
        session['idUser'] = ''
        session['username'] = ''
        session['stat'] = False
    else:
        session['idUser'] = ''
        session['username'] = ''
        session['stat'] = False
    return redirect('/')

@app.route('/register')
def register():
    if 'stat' not in session:
        session['stat'] = False
    else:
        print(session['stat'])
    return render_template('register.html')


@app.route('/registernow', methods=['POST'])
def registernow():
    message = []
    session['checkList'] = [False, False, False, False, False]
    checkFName = request.form['first_name']
    checkLName = request.form['last_name']
    checkEmail = request.form['email']
    checkEmail = checkEmail.lower()
    checkPassword = request.form['password']
    checkCPassword = request.form['confirm']
    if not any(char.isdigit() for char in checkFName):
        session['checkList'][0] = True
    if not any(char.isdigit() for char in checkLName):
        session['checkList'][1] = True
    if '@' in checkEmail and ('.com' in checkEmail or '.org' in checkEmail):
        session['checkList'][2] = True
    else:
        message.append("The fuck bro? A real email. Please, not even a .com? Try harder man.")
    if len(checkPassword) >= 8:
        session['checkList'][3] = True
    else:
        message.append("Ay! sorry about not clarifying this before. But a pass has to be like... at leaster 8 characters... or something.")
    if checkPassword == checkCPassword:
        session['checkList'][4] = True
    else:
        message.append("Hahaha, yeah no worries. I have trouble entering the same thing twice too sometimes, just give in another try, everythings going to be alright. You got this, I beleive in you.")
    print (session['checkList'])
    print("hello9")
    if False in session['checkList']:
        if not session['checkList'][0] or not session['checkList'][1]:
            message.append('Dude... no numbers in Names, come on man. Lets be real for a second here... love ya but... yeah.')
            temp = message[0]
            message[0] = message[len(message) - 1]
            message[len(message) - 1] = temp
        return render_template('register.html', message=message)
    hashed_pw = md5.new(checkPassword).hexdigest()
    query = "INSERT INTO User (first_name, last_name, email, password, created_at, updated_at) VALUES (:first_name, :last_name, :email, :password, NOW(), NOW())"
    data = {
        "first_name": checkFName,
        "last_name": checkLName,
        "email": checkEmail,
        "password": hashed_pw
    }
    mysql.query_db(query, data)
    return render_template('index.html')


@app.route('/login', methods=['POST'])
def login():
    logged_email = request.form['email']
    logged_email = logged_email.lower()
    print(logged_email)
    logged_password = request.form['password']
    logged_password = md5.new(logged_password).hexdigest()
    print(logged_password)
    query = 'SELECT * FROM user WHERE email = :email and password = :password'
    data = {
        'email': logged_email,
        'password': logged_password
    }
    hold = mysql.query_db(query, data)
    if hold != []:
        session['stat'] = True
        print hold[0]['first_name']
        print(hold[0]['idUser'])
        session['username'] = hold[0]['first_name']
        session['idUser'] = hold[0]['idUser']
        return redirect('/wall')
    else:
        message = 'Email or Password was entered incorrectly.'
        return render_template("login.html", message=message)

@app.route('/wall')
def wall():
    print(session['idUser'])
    id = str(session['idUser'])
    query1 = 'Select idPost, message, post.User_idUser, user.first_name from post join user on user.idUser = post.User_idUser;'
    query2 = 'Select * from comment join user on user.idUser = comment.User_idUser;'
    posts = mysql.query_db(query1)
    comments = mysql.query_db(query2)
    print(posts)
    print(comments)
    return render_template('userWall.html', posts=posts, comments=comments)


@app.route('/create_post', methods=['POST'])
def create_post():
    message = request.form['poster']
    if message is not None:
        query = 'INSERT INTO post (message, created_at, updated_at, User_idUser) VALUES (:message, NOW(), NOW(), :id);'
        data = {
            'message': message,
            'id': session['idUser']
        }
        mysql.query_db(query, data)
    return redirect('/wall')


@app.route('/reply', methods=['POST'])
def reply():
    postId = request.form['postID']
    comment = request.form['reply']
    userId = session['idUser']
    print(postId)
    print(userId)
    if comment is not '' and comment is not None:
        query = 'INSERT INTO comment (comment, created_at, updated_at, Post_idPost, User_idUser) VALUES (:comment, NOW(), NOW(), :Post_idPost, :User_idUser);'
        data = {
            'comment': comment,
            'Post_idPost': postId,
            'User_idUser': userId,
        }
        mysql.query_db(query, data)
    print'stop'
    return redirect('/wall')


# @app.route('/friends', methods=['POST'])
# def create():
#     query = "INSERT INTO friends (first_name, last_name, occupation, created_at, updated_at) " \
#             "VALUES (:first_name, :last_name, :occupation, NOW(), NOW())"
#     data = {
#         "first_name": request.form['first_name'],
#         "last_name": request.form['last_name'],
#         "occupation": request.form['occupation']
#     }
#     mysql.query_db(query, data)
#     return redirect('/')


@app.route('/encrypt', methods=['POST'])
def encrypt():
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    occupation = request.form['occupation']
    hashed_name = md5.new(first_name).hexdigest()
    salt = binascii.b2a_hex(os.urandom(10))
    print(salt)
    print(hashed_name)
    return redirect('/')


@app.context_processor  # Start of css buster!
def override_url_for():
    return dict(url_for=dated_url_for)


def dated_url_for(endpoint, **values):
    if endpoint == 'static':
        filename = values.get('filename', None)
        if filename:
            file_path = os.path.join(app.root_path,
                                     endpoint, filename)
            values['q'] = int(os.stat(file_path).st_mtime)
    return url_for(endpoint, **values)


app.run(debug=True)