import os
from flask import Flask, request, render_template, redirect, url_for, session, flash, jsonify
from werkzeug.utils import secure_filename
import pytesseract
from PIL import Image
from ocr_pdf import extract_text_from_pdf  # Import the PDF processing function
import mysql.connector
import json

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = "C:/Users/yanni/OneDrive/Desktop/2nd Sem Year 3/CS192/CS192/uploads" #Specify folder directory
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Limit file size to 16 MB

app.secret_key = "my_secret_key" 

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host="localhost",  # Replace with  DB host
            user="root",  # Replace with MySQL username
            password="password",  # Replace with your MySQL password
            database="cs191"
        )
        return connection
    except mysql.connector.Error as err:
        print(f"Database connection error: {err}")
        return None

# Ensure upload folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

@app.route('/')
def login():
    return render_template('login_page.html')

@app.route('/login', methods=['POST'])
def login_post():
    email = request.form['email']
    password = request.form['password']
    
    connection = get_db_connection()

    
    if email == "teacher@up.edu.ph" and password == "pass":
        session['user'] = email # Store user in session
        return redirect(url_for('teacher_dashboard'))

    if not connection:
        flash('Database connection failed. Please try again later.')
        return redirect(url_for('login'))
    
    try:
        cursor = connection.cursor(dictionary=True)
        query = "SELECT * FROM student WHERE email = %s AND password = %s"
        cursor.execute(query, (email, password))
        user = cursor.fetchone()        #fetches result of execute query

        if user:                        #if user is in the database/ already signed up 
            session['user'] = user['email']
            # session['role'] = user['role']
            # if user['role'] == 'student':
            return redirect(url_for('status')) #redirect to status page
            # elif user['role'] == 'teacher':
            #     return redirect(url_for('teacherdashboard'))
        else:
            flash('Invalid credentials. Please try again.')
            return redirect(url_for('login'))
    finally:
        cursor.close()
        connection.close()



@app.route('/TOR_page')
def TOR_page():
    # Check if the user is logged in
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('TOR_page.html')

@app.route('/teacherdashboard')
def teacherdashboard():
    # Check if the user is logged in
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('teacherdashboard.html')

@app.route('/status')
def status():
    return render_template('status.html')

@app.route('/upload_file', methods=['POST'])
def upload_file():
    connection = get_db_connection()
    cursor = connection.cursor()

    if 'file' not in request.files:
        flash("No file uploaded.")
        return redirect(request.url)

    file = request.files['file']
    if file.filename == '':
        flash("No selected file.")
        return redirect(request.url)

    try:
        # Secure and save the file
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Extract text based on file type
        if file.filename.lower().endswith('.pdf'):
            text = extract_text_from_pdf(file_path)
        else:
            text = extract_text_from_image(file_path)

        # Remove file after processing
        os.remove(file_path)
        
        # Parse extracted text as JSON
        result_dict = json.loads(text)
        structured_data = result_dict.get("structured_data_processed", {})

        # 🔹 Insert Courses into `courses` Table
        for page, data in structured_data.items():
            if isinstance(data, list) and len(data) > 0:
                data = data[0]  # Extract first dictionary from the list

            semester = data.get("Semester", "Unknown")
            academic_year = data.get("Academic Year", "Unknown")

            for course in data.get("Courses", []):  # Ensure "Courses" exists
                course_code = course.get("Course Code", "N/A")
                description = course.get("Description", "N/A")
                grade = course.get("Grade", "N/A")
                units = course.get("Units", "N/A")

                course_query = """
                    INSERT INTO courses (semester, academic_year, course_code, description, grade, units)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
                cursor.execute(course_query, (semester, academic_year, course_code, description, grade, units))

        # ✅ Commit changes before returning
        connection.commit()
        cursor.close()
        connection.close()

        return render_template('result.html',
                               processed_text=result_dict.get("processed_text", ""),
                               structured_data_processed=structured_data)

    except mysql.connector.Error as err:
        print(f"❌ MySQL Error: {err}")
        flash("An error occurred while processing the data. Please try again.")
        connection.rollback()  # Rollback in case of error
        return redirect(url_for('TOR_page'))

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


@app.route('/generate_plan/<student_id>')
def generate_plan(student_id):
    pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{student_id}.pdf")  # Ensure correct folder

    if not os.path.exists(pdf_path):
        flash("TOR not found for this student.")
        return redirect(url_for('teacher_dashboard'))

    extracted_text = extract_text_from_pdf(pdf_path)  # Use existing function
    return render_template('result.html',  extracted_text=extracted_text)

@app.route('/student_info')
def student_info():
   # Fetch the student's information from the database or session
    user = session.get('user')  # Assuming the user's ID is stored in the session
    print(user)
    if not user:
        flash("You need to log in to view your information.")
        return redirect(url_for('login'))

    connection = get_db_connection()
    cursor = connection.cursor()

    # Query the database for student information
    cursor.execute("SELECT * FROM student WHERE email = %s", (user,))
    student_data = cursor.fetchone()

    if not student_data:
        flash("Student information not found.")
        return redirect(url_for(''))  # Redirect to the setup flow if info is missing

    # Pass the retrieved data to the template
    return render_template('student_info.html', student_info=student_data)

@app.route('/teacher_dashboard')
def teacher_dashboard():
    user = session.get('user')
    if not user:
        flash("You need to log in to view this page.")
        return redirect(url_for('login'))

    connection = get_db_connection()
    if not connection:
        flash("Database connection failed.")
        return redirect(url_for('login'))

    cursor = connection.cursor(dictionary=True)  # Use dictionary cursor
    query = "SELECT idStudent, first_name, last_name FROM student"
    cursor.execute(query)
    students = cursor.fetchall()  # Fetch all students

    cursor.close()
    connection.close()

    return render_template('teacherdashboard.html', students=students or [])

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

@app.errorhandler(404)
def not_found(error=None):
    message = {
        'status' : 404,
        'message' : 'Not Found: ' + request.url,
    }
    resp = jsonify(message)
    resp.status_code = 404

    return resp 

if __name__ == '__main__':
    app.run(debug=True)