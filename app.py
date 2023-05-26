from flask import Flask, render_template, request, redirect, url_for, flash, session
from functools import wraps
from werkzeug.utils import secure_filename
import threading
import os
import mysql.connector
from flask_mysqldb import MySQL
import random
import uuid
from werkzeug.routing import UUIDConverter



app = Flask(__name__, template_folder='templates')
app.secret_key = "secret_key"

app.url_map.converters['uuid'] = UUIDConverter

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'password'
app.config['MYSQL_DB'] = 'lcu_database'


mysql = MySQL(app)

def query_db(matric_no):
    cursor = mysql.connection.cursor()
    query = "SELECT passkey FROM Students WHERE matric_no= %s"
    cursor.execute(query, (matric_no,))
    result = cursor.fetchone()
    cursor.close()
    if result:
        return result[0]
    else:
        return None

def query_db_otp(otp):
    cursor = mysql.connection.cursor()
    query = "SELECT passkey FROM otp WHERE passkey = %s"  # Specify the column name in the WHERE clause
    cursor.execute(query, (otp,))
    result = cursor.fetchone()
    cursor.close()
    if result:
        return result[0]
    else:
        return None

def save_user(first_name, last_name, matric_no, passkey, department, phone_number):
    cursor = mysql.connection.cursor()
    query = "INSERT INTO Students (first_name, last_name, matric_no, passkey, department, phone_number) VALUES (%s, %s, %s, %s, %s, %s)"
    cursor.execute(query, (first_name, last_name, matric_no, passkey, department, phone_number))
    mysql.connection.commit()
    user_id = cursor.lastrowid
    cursor.close()
    return user_id

# Set up file upload folder
app.config['UPLOAD_FOLDER'] = 'uploads'

# Set up allowed file types
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt'}

# Check if a file is an allowed file type
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Check if user is logged in
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Homepage
@app.route('/')
@login_required
def admin_index():
    document_id = get_document_id()
    return render_template('admin_index.html',  document_id=document_id)

@app.route('/user_index')
@login_required
def user_index():
    return render_template('user_index.html')

@app.route('/documents/<int:document_id>')
def document_route(document_id):
    # Retrieve the document with the given document_id from your data source
    document = get_document_by_id(document_id)

    # Check if the document exists
    if document is None:
        return "Document not found"

    # Process the document or perform any necessary operations
    # ...

    # Return a response or render a template with the document information
    return render_template('document.html', document=document)

@app.route('/some_route')
def some_route():
    # Get the document_id from your data source
    document_id = "123"  # Example document_id as a string

    # Convert the document_id to an integer
    try:
        document_id = int(document_id)
    except ValueError:
        # Handle the case where document_id is not a valid integer
        return "Invalid document_id"

    # Validate the document_id if necessary
    # ...

    # Pass the corrected document_id to url_for
    document_url = url_for('document_route', document_id=1234)

    # Use the generated URL as needed
    # ...

    return "Success"

# Login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if 'otp' in request.form:
            # Handle OTP submission
            otp = request.form['otp']
            # Process OTP here
            stored_otp = query_db_otp(otp)
            if stored_otp is not None:
                return redirect(url_for('register'))
            else:
                flash('Invalid OTP')
        else:
            # Handle username and password submission
            matric_no = request.form['username']
            passkey = request.form['password']
            stored_password = query_db(matric_no)
            # Process username and password here
            if matric_no == 'admin' and passkey == 'admin':
                session['username'] = matric_no
                return redirect(url_for('admin_index'))
            elif stored_password is not None and stored_password == passkey:
                session['username'] = matric_no
                return redirect(url_for('user_index'))
            else:
                flash('Invalid username or password')

    # Display login form
    return render_template('login.html')


# Logout
@app.route('/logout')
@login_required
def logout():
    session.pop('matric_no', None)
    return redirect(url_for('login'))

#Register 
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        first_name = request.form["first-name"]
        last_name = request.form["last-name"]
        matric_no = request.form["matric-no"]
        passkey = request.form["password"]
        confirm_password = request.form["confirm-password"]
        department = request.form["department"]
        phone_number = request.form["phone-number"]

        if passkey != confirm_password:
            flash("Passwords do not match.")
        else:
            user_id = save_user(first_name, last_name, matric_no, passkey, department, phone_number)
            session['matric_no'] = matric_no
            return redirect(url_for('login'))
    return render_template('registeration_user.html')

#Upload Document
@app.route('/upload_document', methods=['GET', 'POST'])
def upload_document():
    if request.method == 'POST':
        # Get the uploaded file
        file = request.files['file']
        
        # Check if a file was selected
        if file.filename == '':
            return "No file selected"  
        
        # Get the filename and extension
        filename = secure_filename(file.filename)
        extension = os.path.splitext(filename)[1]
        
        # Generate a unique filename
        unique_filename = str(uuid.uuid4()) + extension
        
        # Construct the file path
        location = os.path.join('C:/Users/danie/Documents/GitHub/Student Electronic Document Manager/files/', unique_filename)
        
        try:
            # Save the file to the specified location
            file.save(location)
            
            # Get other form data
            title = request.form['title']
            description = request.form['description']
            access_type = request.form['access-type']
            
            # Save the data to the database
            cursor = db.cursor()
            sql = "INSERT INTO documents (title, description, access_type, filename) VALUES (%s, %s, %s, %s)"
            values = (title, description, access_type, unique_filename)
            cursor.execute(sql, values)
            db.commit()
            cursor.close()
            
            # Redirect to a success page
            return render_template('upload_success.html')
        except Exception as e:
            # Handle any exceptions that occur during file saving or database operations
            return "An error occurred: " + str(e)
    
    return render_template('upload_document.html')


# Route to render the "Download Document" page
@app.route('/download_document/<int:document_id>')
def download_document(document_id):
    # Establish a connection to the MySQL database
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    # Fetch the document from the database
    query = "SELECT * FROM documents WHERE id = %s"
    cursor.execute(query, (document_id,))
    document = cursor.fetchone()

    # Close the database connection
    cursor.close()
    conn.close()

    # Get the file path of the document
    file_path = document['file_path']

    return send_file(file_path, as_attachment=True)



# Route to render the "Edit Document" page
@app.route('/edit_document')
def edit_document():
    # Establish a connection to the MySQL database
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    # Fetch documents from the database
    query = "SELECT * FROM documents"
    cursor.execute(query)
    documents = cursor.fetchall()

    # Close the database connection
    cursor.close()
    conn.close()

    return render_template('edit_document.html', documents=documents)



@app.route('/delete_document/<int:document_id>', methods=['GET', 'POST'])
def delete_document(document_id):
    # Delete the document from the database
    delete_query = "DELETE FROM documents WHERE id = %s"
    db_cursor.execute(delete_query, (document_id,))
    db_connection.commit()

    return redirect(url_for('delete_document'))


# User management
@app.route("/user_management")
def user_management():
    # Fetch all user data from the database
    cursor = mysql.connection.cursor()
    query = "SELECT * FROM Students"
    cursor .execute(query)
    users = cursor.fetchall()
    cursor.close()
    return render_template('user_management.html', Users=users)

# Add user
@app.route('/add_user', methods=['GET', 'POST'])
@login_required
def add_user():
    if request.method == 'POST':
        session['matric_number'] = request.form['matric-number']
        return redirect(url_for('generate_otp'))
    else:
        return render_template('add_user.html')

@app.route('/generate_otp', methods=['POST'])
@login_required
def generate_otp():
    matric_number = request.form.get('matric-number')
    
    if matric_number:
        otp = random.randint(100000, 999999)
        
        # Store the OTP and matric number in the database
        # (Make sure to have a table named 'otp' with 'passkey' and 'matric_no' columns)
        cursor = mysql.connection.cursor()
        query = "INSERT INTO otp (matric_no, passkey) VALUES (%s, %s)"
        cursor.execute(query, (matric_number, otp))
        mysql.connection.commit()
        cursor.close()
        
        flash('User added successfully')
        return render_template('generate_otp.html', otp=otp, matric_number=matric_number)
    else:
        flash('Matric number not found')
        return redirect(url_for('add_user'))



    
# Route for the Edit User page
@app.route('/edit_user', methods=['GET', 'POST'])
@app.route('/edit_user', methods=['GET', 'POST'])
def edit_user():
    if request.method == 'POST':
        user_id = request.form['user_id']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        department = request.form['department']
        phone_number = request.form['phone_number']
        
        # Update the user's details in the database
        cursor = mysql.connection.cursor()
        query = "UPDATE Students SET first_name = %s, last_name = %s, department = %s, phone_number = %s WHERE id = %s"
        cursor.execute(query, (first_name, last_name, department, phone_number, user_id))
        mysql.connection.commit()
        cursor.close()
        
        flash('User details updated successfully')
        return redirect(url_for('edit_user'))
    else:
        # Retrieve all users from the database
        cursor = mysql.connection.cursor()
        query = "SELECT * FROM Students"
        cursor.execute(query)
        users = cursor.fetchall()
        cursor.close()
        
        return render_template('edit_user.html', users=users)


# Route for the Delete User page
@app.route('/delete_user', methods=['GET', 'POST'])
def delete_user():
    if request.method == 'POST':
        if 'delete_selected' in request.form:
            selected_users = request.form.getlist('selected_users')
            
            # Delete the selected users from the database
            cursor = mysql.connection.cursor()
            for user_id in selected_users:
                query = "DELETE FROM Students WHERE id = %s"
                cursor.execute(query, (user_id,))
            mysql.connection.commit()
            cursor.close()
            
            flash('Selected users deleted successfully')
        elif 'delete_all' in request.form:
            # Delete all users from the database
            cursor = mysql.connection.cursor()
            query = "DELETE FROM Students"
            cursor.execute(query)
            mysql.connection.commit()
            cursor.close()
            
            flash('All users deleted successfully')
        
        return redirect(url_for('delete_user'))
    else:
        # Retrieve all users from the database
        cursor = mysql.connection.cursor()
        query = "SELECT * FROM Students"
        cursor.execute(query)
        users = cursor.fetchall()
        cursor.close()
        
        return render_template('delete_user.html', users=users)

#manage logs
@app.route('/manage_logs')
@login_required
def manage_logs():
    log_file = 'app.log'  # Specify the path to your log file

    # Read log file and retrieve log entries
    logs = []
    with open(log_file, 'r') as file:
        for line in file:
            log_entry = line.strip()
            logs.append(log_entry)

    # Reverse the order of logs to display the latest first
    logs.reverse()

    return render_template('manage_logs.html', logs=logs)

@app.route('/send_document', methods=['GET', 'POST'])
@login_required
def send_document():
    if request.method == 'POST':
        # Get the uploaded file
        file = request.files['file']

        # Check if a file was selected
        if file.filename == '':
            flash('No file selected')
            return redirect(url_for('send_document'))

        # Get the filename and extension
        filename = secure_filename(file.filename)
        extension = os.path.splitext(filename)[1]

        # Generate a unique filename
        unique_filename = str(uuid.uuid4()) + extension

        # Construct the file path
        location = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)

        try:
            # Save the file to the specified location
            file.save(location)

            # Get other form data
            recipient = request.form['recipient']
            title = request.form['title']
            description = request.form['description']

            # Save the data to the database
            cursor = mysql.connection.cursor()
            query = "INSERT INTO documents (title, description, filename) VALUES (%s, %s, %s)"
            values = (title, description, unique_filename)
            cursor.execute(query, values)
            document_id = cursor.lastrowid

            # Save the document recipient to the database
            query = "INSERT INTO document_recipients (document_id, recipient) VALUES (%s, %s)"
            values = (document_id, recipient)
            cursor.execute(query, values)

            mysql.connection.commit()
            cursor.close()

            # Redirect to a success page
            flash('Document sent successfully')
            return redirect(url_for('send_document'))
        except Exception as e:
            # Handle any exceptions that occur during file saving or database operations
            flash('An error occurred: ' + str(e))
            return redirect(url_for('send_document'))

    return render_template('send_document.html')


@app.route('/quick_search', methods=['GET', 'POST'])
@login_required
def quick_search():
    if request.method == 'POST':
        keyword = request.form['keyword']
        results = quick_search(keyword)
        return render_template('search_results.html', results=results)
    else:
        return render_template('quick_search.html')


@app.route('/profile')
@login_required
def profile():
    pass


# Download document
@app.route('/download/<filename>')
@login_required
def download(filename):
    path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    return send_file(path, as_attachment=True)

# Generate unique document ID
def get_document_id():
    return str(uuid.uuid4())


    
if __name__ == '__main__':
    app.run(debug=True)








print('             ~lyon98.dbios')
