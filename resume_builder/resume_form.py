from flask import request, send_file, render_template
from resume_builder.resume_generator import ResumeGenerator  # Import your PDF generator class/module

def handle_resume_form():
    if request.method == 'POST':
        try:
            # Collect form data from POST request
            user_data = {
                'name': request.form['name'],
                'email': request.form['email'],
                'phone': request.form['phone'],
                'education': request.form['education'],
                'work_experience': request.form.get('work_experience', ''),
                'skills': request.form.get('skills', ''),
            }

            # Generate the PDF resume
            generator = ResumeGenerator(user_data)
            pdf_path = generator.generate_pdf()

            # Return the generated resume as a downloadable file
            return send_file(pdf_path, as_attachment=True)

        except Exception as e:
            print(f"Error: {e}")  # Log the error for debugging
            return "An error occurred while processing your request.", 500

    # If GET request, render the resume form
    return render_template('resume_form.html')
