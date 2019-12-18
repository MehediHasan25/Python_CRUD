from flask import Flask, render_template, url_for, flash, redirect, jsonify,session
from flask import request
from passlib.hash import sha256_crypt
from functools import wraps
import gc
import base64
import mysql.connector
app = Flask(__name__)


app.secret_key = 'mykey'

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  passwd="mehedi",
  database="CRUD"
)
mycursor = mydb.cursor()


# -------------------Login Authentication Decorator
def login_required(test):
    @wraps(test)
    def wrap(*args, **kwargs):
        if 'loggedin' and 'user' in session:
            return test(*args, **kwargs)
        else:
            flash('You need to login first.')
            return redirect(url_for('login'))
    return wrap
        
#------------------------Login GET ROUTE

@app.route('/' , methods=['GET'])
def login():
    return render_template('login.html')

#------------------------Login POST ROUTE

@app.route('/auth-account', methods=['POST'])
def authaccount():
    try:
        if request.method == "POST":
            session.pop('user', None)
            session.pop('loggedin', None)
            data= request.form
            userName = data['name']
            password = data['password']
            #cpassword = sha256_crypt.using(rounds=12345).hash(password)
            mycursor = mydb.cursor()
            mycursor.execute('SELECT UserName, Passwrd FROM User WHERE UserName = %s; ', [userName])
            password1 = mycursor.fetchone()[1]
            #print(cpassword)
            #print(password1)
            if sha256_crypt.verify(password, password1) :
                session['loggedin'] = True
                session['user'] = request.form['name']
                return redirect(url_for('index'))
            else:
                return redirect(url_for('login'))
    except Exception as e:
        print("Exception found from authauthentication:" + str(e))
        

#------------------------Index Route = Show all data   
@app.route('/index', methods = ["GET"])
@login_required
def index():
    try:    
        mycursor = mydb.cursor()
        mycursor.execute("SELECT * FROM User")
        myresult = mycursor.fetchall()
        # mycursor.close()


        return render_template('index.html', User=myresult )
    
    except Exception as e:
        print("Exception found from index:" + str(e))


#------------------------Create Route 

@app.route('/create', methods = ["GET","POST"])
@login_required
def create():
    try:
        if request.method == "POST":    
            data = request.form
            userName = data['name']
            fpassword = data['password']
            password = sha256_crypt.hash(fpassword)
            mobile = data['mobile']
            email = data['email']
            userStatus = data['status']
            userType = data['type']
            mycursor = mydb.cursor()
            mycursor.execute("INSERT INTO User (UserName, Passwrd, Email, Mobile, UserStatus, UserType) VALUES (%s, %s, %s, %s, %s, %s)", (userName, password, email, mobile, userStatus, userType )) 
            mydb.commit()
            return redirect(url_for('index'))
        else:
            return render_template('create.html')

    except Exception as e:
        print("Exception found from create:" + str(e))


#------------------------Edit Route

@app.route('/edit/<int:id_data>', methods=['POST', 'GET'])
@login_required
def edit(id_data):
    try:
         mycursor = mydb.cursor()
         mycursor.execute('SELECT *  FROM User where ID= '  +str(id_data)) 
         result = mycursor.fetchall()
         return render_template('edit.html', updata = result)
     
    except Exception as e:
        print("Exception found from edit" + str(e))     
        
        
#------------------------Update Route
            
@app.route('/update', methods=["POST"])
@login_required
def update():
    try:
        if request.method == 'POST':
            data = request.form
            id = data['id']
            userName = data['uname']
            upassword = data['password']
            password = sha256_crypt.hash(upassword)
            mobile = data['mobile']
            email = data['email']
            userStatus = data['status']
            userType = data['type'] 
            mycursor = mydb.cursor()
            mycursor.execute("""
                UPDATE User
                SET UserName=%s, Passwrd=%s, Email=%s, Mobile=%s, UserStatus=%s, UserType=%s
                WHERE ID=%s
                """, (userName, password, email, mobile, userStatus, userType, id)) 
            mydb.commit()
        return redirect(url_for('index'))
    
    except Exception as e:
        print("Exception found from update" + str(e))
        
        
        
#------------------------Delete ROUTE

@app.route('/delete/<int:id_data>' , methods=['GET'])
@login_required
def delete(id_data):
    try:
        mycursor = mydb.cursor()
        mycursor.execute('DELETE FROM User where ID= '  +str(id_data))
        mydb.commit()
        return redirect(url_for('index'))
    
    except Exception as e:
        print("Exception found from delete" + str(e))
        
        
        
#------------------------Logout ROUTE      
        
@app.route('/logout')
@login_required
def logout():
    try:
        session.clear()
        flash("you have to login")
        gc.collect()
        return redirect(url_for('login'))

    except Exception as e:
        print("Exception found from logout" + str(e))
        
        
        

if __name__ == '__main__':
    app.run(debug=True)


