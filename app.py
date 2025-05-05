import os
import zipfile
import io
from flask import Flask, request, render_template, redirect, url_for, session, flash, jsonify,send_file
from werkzeug.utils import secure_filename
import pytesseract
from PIL import Image
from ocr_pdf import extract_text_from_pdf  # Import the PDF processing function
import mysql.connector
import json
from nlp import compute_similarity
from db import get_student_courses, get_prereqs_for_program 
from export import generate_csv_for_student, generate_xlsx_for_student

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
        cursor = connection.cursor(buffered=True, dictionary=True)
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


@app.route('/teacherdashboard')
def teacherdashboard():
    # Check if the user is logged in
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('teacherdashboard.html')

@app.route('/upload_file', methods=['POST'])
def upload_file():
    connection = get_db_connection()

    if 'file' not in request.files:
        flash("No file uploaded.", "error")
        return redirect(request.url)

    file = request.files['file']
    if file.filename == '':
        flash("No selected file.", "error")
        return redirect(request.url)

    try:
        cursor = connection.cursor(buffered=True)

        student_id = request.form.get("student_id")
        student_name = request.form.get("student_name")

        filename = f"{student_id}.pdf"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        if file.filename.lower().endswith('.pdf'):
            text = extract_text_from_pdf(file_path)
        else:
            text = extract_text_from_image(file_path)

        result_dict = json.loads(text)
        structured_data = result_dict.get("structured_data_processed", {})

        if not isinstance(structured_data, dict):
            flash("Invalid file format. Please try again.", "error")
            return redirect(url_for('teacherdashboard'))

        # Check if student exists

        cursor.execute("SELECT idStudent FROM student WHERE idStudent = %s", (student_id,))
        existing_student = cursor.fetchone()

        if not existing_student:
            student_insert_query = "INSERT INTO student (idStudent, student_name) VALUES (%s, %s)"
            cursor.execute(student_insert_query, (student_id, student_name))

        # Insert Courses & Transcripts
        for page, courses in structured_data.items():
            semester = "Unknown"
            academic_year = "Unknown"

            for course in courses:
                course_code = course.get("Course Code", "N/A")
                description = course.get("Description", "N/A")
                grade = course.get("Grade", "N/A")
                units = course.get("Units", "0")

                # Ensure course exists in the courses table
                course_query = """
                    INSERT INTO courses (course_code, description) 
                    VALUES (%s, %s) 
                    ON DUPLICATE KEY UPDATE description = VALUES(description)
                """
                cursor.execute(course_query, (course_code, description))

                cursor.execute("SELECT id FROM courses WHERE course_code = %s", (course_code,))
                course_id = cursor.fetchone()[0]
                # Insert transcript data linking student to course
                transcript_query = """
                    INSERT INTO transcripts (student_id, semester, academic_year, course_id, grade, units)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
                cursor.execute(transcript_query, (student_id, semester, academic_year, course_id, grade, units))


        connection.commit()
        flash(f"Student {student_name} (ID: {student_id}) added successfully!", "success")
        return redirect(url_for('teacher_dashboard'))

    except mysql.connector.Error as err:
        print(f"❌ 1 MySQL Error: {err}")
        flash("An error occurred while processing the data. Please try again.", "error")
        connection.rollback()
        return redirect(url_for('teacher_dashboard'))

    finally:
        try:
            if 'cursor' in locals():
                cursor.close()
            if 'connection' in locals() and connection.is_connected():
                connection.close()
        except Exception as e:
            print(f"⚠️ Cleanup Error: {e}")
            
@app.route('/result_page/<student_id>')
def result_page(student_id):
    pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{student_id}.pdf")  # Ensure correct folder

    if not os.path.exists(pdf_path):
        flash("TOR not found for this student.")
        return redirect(url_for('teacher_dashboard'))

    extracted_text = extract_text_from_pdf(pdf_path)  # Extract text from PDF
    result_dict = json.loads(extracted_text)  # Attempt JSON parsing
    # 🔹 Ensure JSON parsing is safe
    try:
        structured_data_processed = result_dict.get("structured_data_processed", {})  # ✅ Fix variable name
    except (json.JSONDecodeError, TypeError):
        structured_data_processed = {}  # Set as empty dictionary instead of None
    print(result_dict.get("raw_text", ""))
    return render_template(
        'result.html',
        student_id=student_id,
        raw_text= result_dict.get("raw_text", ""), 
        processed_text= result_dict.get("processed_text", ""),  # Ensure `processed_text` is passed
        structured_data_processed=structured_data_processed  # ✅ Now correctly passed
    )


@app.route('/view_courses/<student_id>')
def view_courses(student_id):
    connection = get_db_connection()
    program = request.args.get("program")  # <-- gets ?program=PhD from the URL)
    try:
        cursor = connection.cursor(buffered=True, dictionary=True)
        query = """
            SELECT t.id, t.semester, t.academic_year, 
                   c.course_code, c.description, t.grade, t.units
            FROM transcripts t
            JOIN courses c ON t.course_id = c.id
            WHERE t.student_id = %s;
        """
        cursor.execute(query, (student_id,))
        courses = cursor.fetchall()
    
        query = "SELECT student_name FROM student WHERE idStudent = %s"
        cursor.execute(query, (student_id,))
        student_name = cursor.fetchone()  # Fetch all students


        if not courses:
            flash("No courses found for this student.", "error")
            return redirect(url_for('teacher_dashboard'))  

        return render_template('view_courses.html', student_id=student_id,student_name=student_name , courses=courses, program=program)

    except mysql.connector.Error as err:
        print(f"❌ 2 MySQL Error: {err}")
        flash("Error fetching data from database.", "error")
        return redirect(url_for('teacher_dashboard'))

    finally:
        cursor.close()
        connection.close()

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

    cursor = connection.cursor(buffered=True, dictionary=True)  # Use dictionary cursor
    query = "SELECT idStudent, student_name FROM student"
    cursor.execute(query)
    students = cursor.fetchall()  # Fetch all students
    cursor.close()
    connection.close()

    return render_template('teacherdashboard.html', students=students or [])

@app.route('/redirect_program', methods=['POST'])
def redirect_program():
    program = request.form.get('program')
    print(program)
    student_id = request.form.get('student_id')  # Get student ID from form input
    print("STUDENT ID:", student_id)
    if program == 'phd':  
        return redirect(url_for('compare_courses', program= program, student_id=student_id))
    elif program == 'ms':
        return redirect(url_for('compare_courses', program = program, student_id = student_id))
    elif program == 'bioinformatics':
        return redirect(url_for('compare_courses', program = program, student_id = student_id))
    else:
        flash("Invalid selection. Please choose a valid program.")
        return redirect(url_for('teacher_dashboard'))

@app.route('/add_prereq', methods=['POST'])
def add_prereq():
    program = request.form['program']
    course_code = request.form['course_code']
    description = request.form['description']

    connection = get_db_connection()
    cursor = connection.cursor()
    
    query = "INSERT INTO prereqs (program, course_code, description) VALUES (%s, %s, %s)"
    cursor.execute(query, (program, course_code, description))
    
    connection.commit()
    cursor.close()
    connection.close()
    
    flash("Prerequisite added successfully!", "success")
    return redirect(url_for('manage_prereqs'))  # Redirect to admin page

@app.route('/remove_student/<student_id>', methods=['POST'])
def remove_student(student_id):
    connection = get_db_connection()
    if not connection:
        flash("Database connection failed.", "error")
        return redirect(url_for('teacher_dashboard'))

    try:
        cursor = connection.cursor()

        # Delete only the student from the student table
        cursor.execute("DELETE FROM transcripts WHERE student_id = %s", (student_id,))
        cursor.execute("DELETE FROM student WHERE idStudent = %s", (student_id,))
        
        connection.commit()
        flash("Student removed successfully.", "success")
    
    except mysql.connector.Error as err:
        print(f"❌ MySQL Error: {err}")
        flash("Error deleting student. Please try again.", "error")
        connection.rollback()
    
    finally:
        cursor.close()
        connection.close()

    return redirect(url_for('teacher_dashboard'))

@app.route('/compare_courses', methods=['GET','POST'])
def compare_courses():
    student_id = request.args.get("student_id")
    program = request.args.get("program")  # Get desired program
    taken_courses = get_student_courses(student_id)
    prereqs = get_prereqs_for_program(program)
    matched_results = compute_similarity(taken_courses, prereqs)
    return render_template("matched_courses.html", results = matched_results, student_id=student_id)
    

@app.route('/export_files', methods=['POST'])
def export_files():
    student_ids = request.form.getlist('selected_students')
    export_format = request.form.get('export_format')

    if not student_ids:
        flash("Please select at least one student.")
        return redirect(url_for('teacher_dashboard'))

    if export_format not in ['csv', 'xlsx']:
        flash("Please select a valid export format.")
        return redirect(url_for('teacher_dashboard'))

    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, 'w') as zipf:
        for student_id in student_ids:
            program = request.form.get(f'program_{student_id}')
            taken_courses = get_student_courses(student_id)
            prereqs = get_prereqs_for_program(program)
            matched_results = compute_similarity(taken_courses, prereqs)

            filename = f'student_{student_id}_export.{export_format}'

            if export_format == 'csv':
                csv_file = generate_csv_for_student(student_id, matched_results)
                zipf.writestr(filename, csv_file.read())

            elif export_format == 'xlsx':
                output = io.BytesIO()
                wb = generate_xlsx_for_student(student_id, matched_results)
                wb.save(output)
                output.seek(0)
                zipf.writestr(filename, output.read())

    zip_buffer.seek(0)
    return send_file(
        zip_buffer,
        mimetype='application/zip',
        as_attachment=True,
        download_name=f'matched_exports_{export_format}.zip'
    )

@app.route('/save_courses', methods=['POST'])
def save_courses():
    data = request.get_json()
    student_id = data['student_id']
    courses = data['courses']
    connection = get_db_connection()
    cursor = connection.cursor()

    # AVOUD DUPLICATES
    unique_course_updates = {}
    for course in courses:
        course_id = course['id']  
        if course_id not in unique_course_updates:
            unique_course_updates[course_id] = {
                'course_code': course['course_code'],
                'description': course['description']
            }

    try:
        for course_id, info in unique_course_updates.items():
            cursor.execute("""
                UPDATE courses
                SET course_code = %s, description = %s
                WHERE id = %s
            """, (info['course_code'], info['description'], course_id))

        for course in courses:
            transcript_id = course['id']  # This should refer to the transcript row ID
            cursor.execute("""
                UPDATE transcripts
                SET grade = %s, units = %s
                WHERE id = %s AND student_id = %s
            """, (course['grade'], course['units'], transcript_id, student_id))

        connection.commit()
        return jsonify({'message': 'Courses updated successfully!'}), 200

    except Exception as e:
        print("Error updating:", e)
        return jsonify({'message': 'Failed to update courses.'}), 500

    finally:
        cursor.close()
        connection.close()

@app.route('/delete_course/<int:transcript_id>', methods=['DELETE'])
def delete_course(transcript_id):
    connection = get_db_connection()
    if not connection:
        return jsonify(success=False, message="DB connection failed")

    try:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM transcripts WHERE id = %s", (transcript_id,))
        connection.commit()
        return jsonify(success=True)
    except Exception as e:
        print("Delete error:", e)
        return jsonify(success=False, message="DB error")
    finally:
        cursor.close()
        connection.close()

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
