import mysql.connector

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

def get_student_courses(student_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    query = """
    SELECT c.course_code, c.description 
    FROM transcripts t
    JOIN courses c ON t.course_id = c.id
    WHERE t.student_id = %s
    """
    cursor.execute(query, (student_id,))
    taken_courses = cursor.fetchall()

    cursor.close()
    connection.close()
    return taken_courses


def get_prereqs_for_program(program):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    query = """
    SELECT prereq_course_code, description 
    FROM prereqs 
    WHERE program = %s
    """
    cursor.execute(query, (program,))
    prereqs = cursor.fetchall()

    cursor.close()
    connection.close()
    return prereqs
