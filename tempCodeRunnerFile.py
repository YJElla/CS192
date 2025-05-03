
@app.route('/export_csv', methods=['POST'])
def export_csv():
    student_ids = request.form.getlist('selected_students')
    if not student_ids:
        flash("Please select at least one student.")
        return redirect(url_for('teacher_dashboard'))

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zipf:
        for student_id in student_ids:
            program = request.form.get(f'program_{student_id}')
            taken_courses = get_student_courses(student_id)
            prereqs = get_prereqs_for_program(program)
            matched_results = compute_similarity(taken_courses, prereqs)
            csv_file = generate_csv_for_student(student_id, matched_results)
            zipf.writestr(f'student_{student_id}_export.csv', csv_file.read())

    zip_buffer.seek(0)
    return send_file(
        zip_buffer,
        mimetype='application/zip',
        as_attachment=True,
        download_name='matched_exports.zip'
    )