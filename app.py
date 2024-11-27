'''
MIT License

Copyright (c) 2023 Shonil B, Akshada M, Rutuja R, Sakshi B

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''
import os
from flask import Flask,json, request, render_template, make_response, redirect,url_for,send_from_directory, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField 
from wtforms.validators import InputRequired, Length, ValidationError, DataRequired, EqualTo, Regexp
from werkzeug.utils import redirect
from Controller.send_email import *
from Controller.send_profile import *
from Controller.ResumeParser import *
from Utils.jobprofileutils import *
import os
from flask import send_file, current_app as app
from Controller.chat_gpt_pipeline import pdf_to_text,chatgpt
from Controller.data import data, upcoming_events, profile
from Controller.send_email import *
from dbutils import add_job, create_tables, add_client, delete_job_application_by_company ,find_user, get_job_applications, get_job_applications_by_status, update_job_application_by_id
from login_utils import login_user
import requests

from resume_builder.resume_generator import ResumeGenerator

from flask import request, render_template, redirect, url_for
from werkzeug.utils import secure_filename
import os
from Utils.resume_scrapper import scrape_resume
#from Utils.gpt_api import get_gpt_suggestions

UPLOAD_FOLDER = 'uploaded_resumes'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)
# api = Api(app)
bcrypt = Bcrypt(app)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database.db"  # SQLite URI
app.config['SECRET_KEY'] = 'thisisasecretkey'
db = SQLAlchemy(app)
database = "database.db"
"""
CREATE TABLE client (
    id INTEGER NOT NULL,
    name VARCHAR(20) NOT NULL,
    username VARCHAR(20) NOT NULL UNIQUE,
    password VARCHAR(80) NOT NULL,
    usertype VARCHAR(20) NOT NULL,
    PRIMARY KEY (id)
);
"""
create_tables(database)

# class Client(db.Model,UserMixin):
#     __tablename__ = 'client'
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(20), nullable=False)
#     username = db.Column(db.String(20), nullable=False, unique=True)
#     password = db.Column(db.String(80), nullable=False)
#     usertype = db.Column(db.String(20), nullable=False)

def validate_username(form, field):
        user = find_user(field.data,database)
        print("user--->",user)
        if user:
            raise ValidationError('Username already exists')

def validate_confirm_password(form, field):
        if str(field.data) != str(form.password.data):
            raise ValidationError('Passwords do not match')

class RegisterForm(FlaskForm):
    username = StringField(validators=[
                           InputRequired(), Length(min=4, max=20), validate_username],render_kw={"placeholder": "Username"})
    

    name = StringField(validators=[
                             InputRequired()],render_kw={"placeholder": "Name"})
    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20), Regexp('(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%#*?&])[A-Za-z\d@$!%*?&]+',message='Password should contain atleast one letter, number and special character')],render_kw={"placeholder": "Password"})
    confirm_password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20), validate_confirm_password],render_kw={"placeholder": "Confirm Password"})
    usertype = SelectField(render_kw={"placeholder": "Usertype"}, choices=[('admin', 'Admin'), ('student', 'Student')])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    username = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})

    usertype = SelectField(validators=[
                             InputRequired()], render_kw={"placeholder": "Usertype"}, choices=[('admin', 'Admin'), ('student', 'Student')])

    submit = SubmitField('Login')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/logout',methods=['GET', 'POST'])
def logout():
    session['type'] = ''
    session['user_id'] = None
    return redirect(url_for('login'))


@app.route('/login',methods=['GET', 'POST'])
def login():
    form = LoginForm() 
    if form.validate_on_submit():
        print("Form is valid")
        user = find_user(str(form.username.data),database)
        if user:
            if bcrypt.check_password_hash(user[3], form.password.data):
                if form.usertype.data == user[4]:
                    login_user(app,user)
                    if user[4] == 'admin':
                        return redirect(url_for('admin', data=user[2]))
                    elif user[4] == 'student':
                        return redirect(url_for('student', data=user[2]))
                    else:
                        pass
                else:
                    form.usertype.errors.append("Invalid credentials")
            else:
                form.password.errors.append("Invalid credentials")
        else:
            form.username.errors.append("User does not exist")
    else:
        print("Form errors:", form.errors)
    return render_template('login.html',form = form)

@app.route('/signup',methods=['GET', 'POST'])
def signup():
    form = RegisterForm()
    if form.validate_on_submit():
        print("Form is valid")
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_client = [form.name.data,form.username.data, hashed_password, form.usertype.data]
        add_client(new_client,database)
        return redirect(url_for('login'))
    else:
        print("Form errors:", form.errors)

    return render_template('signup.html',form = form)

@app.route('/admin',methods=['GET', 'POST'])
def admin():
    data_received = request.args.get('data')
    user = find_user(str(data_received),database)
    ##Add query
    return render_template('admin_landing.html', user=user)


@app.route('/student',methods=['GET', 'POST'])
def student():
    data_received = request.args.get('data')
    user = find_user(str(data_received),database)


    jobapplications = get_job_applications(database)
    return render_template('home.html', user=user, jobapplications=jobapplications)

@app.route('/student/<status>', methods=['GET', 'POST'])
def get_job_application_status(status):
    data_received = request.args.get('data')
    user = find_user(str(data_received), database)

    if status:
        job_applications = get_job_applications_by_status(database, status)
    else:
        job_applications = get_job_applications(database)

    return render_template('home.html', user=user, jobapplications=job_applications)


@app.route("/admin/send_email", methods=['GET','POST'])
def send_email():
    comments = request.form['comment']
    email = 'elliotanderson506@gmail.com'
    s_comment_email(email,comments)
    return make_response(render_template('admin_landing.html'), 200,{'Content-Type': 'text/html'})

@app.route("/admin/render_resume")
def tos():
    workingdir = os.path.abspath(os.getcwd())
    filepath = workingdir + '/static/files/'
    return send_from_directory(filepath, 'resume2.pdf')

@app.route("/add_job_application", methods=['POST'])
def add_job_application():
    if request.method == 'POST':
        company = request.form['company']
        location = request.form['location']
        jobposition = request.form['jobposition']
        salary = request.form['salary']
        status = request.form['status']
        user_id = request.form['user_id']

        job_data = [company, location, jobposition, salary, status]
        # Perform actions with the form data, for instance, saving to the database
        add_job(job_data,database)

        flash('Job Application Added!')
        # Redirect to a success page or any relevant route after successful job addition
        return redirect(url_for('student', data=user_id))

@app.route('/student/update_job_application',methods=['GET','POST'])
def update_job_application():
    if request.method == 'POST':
        company = request.form['company']
        location = request.form['location']
        jobposition = request.form['jobposition']
        salary = request.form['salary']
        status = request.form['status']
        user_id = request.form['user_id']

        # Perform the update operation
        update_job_application_by_id( company, location, jobposition, salary, status, database)  # Replace this with your method to update the job

        flash('Job Application Updated!')
        # Redirect to a success page or any relevant route after successful job update
        return redirect(url_for('student', data=user_id))

@app.route('/student/delete_job_application/<company>', methods=['POST'])
def delete_job_application(company):
    if request.method == 'POST':
        user_id = request.form['user_id']
        # Perform the deletion operation
        delete_job_application_by_company(company,database)  # Using the function to delete by company name

        flash('Job Application Deleted!')
        # Redirect to a success page or any relevant route after successful deletion
        return redirect(url_for('student', data=user_id))  # Redirect to the student page or your desired route

@app.route('/student/add_New',methods=['GET','POST'])
def add_New():
    company_name = request.form['fullname']
    location = request.form['location_text']
    Job_Profile = request.form['text']
    salary = request.form['sal']
    user = request.form['user']
    password = request.form['pass']
    email = request.form['user_email']
    sec_question = request.form['starting_date']
    sec_answer = request.form['starting_date']
    notes = request.form['notes']
    date_applied = request.form['starting_date']

    s_email(company_name,location, Job_Profile,salary, user,password,email,sec_question,sec_answer,notes,date_applied)
    return render_template('home.html', data=data, upcoming_events=upcoming_events, user=user)

@app.route('/student/send_Profile',methods=['GET','POST'])
def send_Profile():
    emailID = request.form['emailID']
    s_profile(data,upcoming_events, profile,emailID)

    print("Email Notification Sent")
    '''data_received = request.args.get('data')
    print('data_receivedddd->>>> ', data_received)
    user = find_user(str(data_received))
    print('Userrrrrr', user)'''
    user_id = request.form['user_id']
    user = request.form['user_id']
    print('==================================================================', user)
    
    user = find_user(str(user),database)

    data_received = request.args.get('data')
    user = find_user(str(data_received),database)

    return render_template('home.html', data=data, upcoming_events=upcoming_events, user=user)


skills_list = [
    'Python', 'Java', 'SQL', 'AWS', 'Azure', 'JavaScript', 'HTML', 'CSS', 
    'Machine Learning', 'Data Analysis', 'Git', 'Docker', 'Kubernetes', 
    'Linux', 'C++', 'C#', 'Flask', 'Django', 'React', 'Node.js'
]
def extract_skills(job_description):
    job_description = job_description.lower()
    found_skills = []
    
    for skill in skills_list:
        if re.search(r'\b' + re.escape(skill.lower()) + r'\b', job_description):
            found_skills.append(skill)
    
    return found_skills

@app.route('/student/job_profile_analyze', methods=['GET', 'POST'])
def job_profile_analyze():
    skills_text = ""
    job_profile = ""

    if request.method == "POST":
        job_profile = request.form.get("job_profile", "")
        skills = extract_skills(job_profile)
        skills_text = ", ".join(skills) if skills else "No skills found."

    return render_template("job_profile_analyze.html", job_profile=job_profile, skills_text=skills_text)

filename=""
@app.route("/student/upload", methods=['POST'])
def upload():
    APP_ROOT = os.path.dirname(os.path.abspath(__file__))
    target = os.path.join(APP_ROOT, 'Controller\\resume\\')

    if not os.path.isdir(target):
        os.mkdir(target)
    if len(os.listdir(target)) != 0:
        os.remove(target + os.listdir(target)[0])

    for file in request.files.getlist("file"):
        filename = file.filename
        destination = "/".join([target, filename])
        file.save(destination)

    user = request.form['user_id']
    
    user = find_user(str(user),database)
    print('Userrrrrr', user)


    return render_template("home.html", data=data, upcoming_events=upcoming_events, user=user)

@app.route('/student/analyze_resume', methods=['GET'])
def view_ResumeAna():
    return render_template('resume_analyzer.html')

@app.route('/student/companiesList', methods=['GET'])
def view_companies_list():
    return render_template('companies_list.html')


@app.route('/student/analyze_resume', methods=['POST'])
def analyze_resume():
    jobtext = request.form['jobtext']
    os.chdir(os.getcwd()+"/Controller/resume/")
    output = resume_analyzer(jobtext, str(os.listdir(os.getcwd())[0]))
    os.chdir("..")
    os.chdir("..")
    return render_template('resume_analyzer.html', data = output)

@app.route("/student/display/", methods=['POST','GET'])
def display():
    path = os.getcwd()+"/Controller/resume/"
    filename = os.listdir(path)
    if filename:
        return send_file(path+str(filename[0]),as_attachment=True)
    else:
        user = request.form['user_id']
        user = find_user(str(user),database)
        return render_template('home.html', user=user, data=data, upcoming_events=upcoming_events)



# @app.route('/student/chat_gpt_analyzer/', methods=['GET'])
# def chat_gpt_analyzer():
#     files = os.listdir(os.getcwd()+'/Controller/resume')
#     pdf_path = os.getcwd()+'//Controller/resume/'+files[0]
#     text_path = os.getcwd()+'//Controller/resume_txt/'+files[0][:-3]+'txt'
#     with open(text_path, 'w'):
#         pass
#     pdf_to_text(pdf_path, text_path)
#     suggestions = chatgpt(text_path)
#     flag = 0
#     final_sugges_send = []
#     final_sugges = ""

#     # Initialize an empty string to store the result
#     result_string = ""

#     # Iterate through each character in the original string
#     for char in suggestions:
#         # If the character is not a newline character, add it to the result string
#         if char != '\n':
#             final_sugges += char
#     sections = final_sugges.split("Section")
#     for section in sections:
#         section = section.strip()  # Remove leading and trailing whitespace
#         # if section:  # Check if the section is not empty (e.g., due to leading/trailing "Section")
#         #     print("Section:", section)
#     sections = sections[1:]
#     section_names = ['Education', 'Experience','Skills', 'Projects']
#     sections[0] = sections[0][3:]
#     sections[1] = sections[1][3:]
#     sections[2] = sections[2][3:]
#     sections[3] = sections[3][3:]
#     return render_template('chat_gpt_analyzer.html', suggestions=sections, pdf_path=pdf_path, section_names = section_names)

@app.route('/student/job_search')
def job_search():
    return render_template('job_search.html')

@app.route('/student/leave_review')
def leave_review():
    return render_template('leave_review.html')

@app.route('/student/networking_contacts')
def networking_contacts():
    return render_template('networking_contacts.html')

@app.route('/student/job_search/result', methods=['POST'])
def search():
    job_role = request.form['job_role']
    min_salary = request.form['minSalary']
    location = request.form['location']
    max_salary = request.form['maxSalary']

    adzuna_url = f"https://api.adzuna.com/v1/api/jobs/gb/search/1?app_id=a3ccdd4c&app_key=9528003d5f2bda2be5e19dd645326cda&what_phrase={job_role}&where={location}&salary_min={min_salary}&salary_max={max_salary}"
    try:
        response = requests.get(adzuna_url)
        if response.status_code == 200:
            data = response.json()
            jobs = data.get('results', [])
            return render_template('job_search_results.html', jobs=jobs)
        else:
            return "Error fetching job listings"
    except requests.RequestException as e:
        return f"Error: {e}"

def load_resources():
    # Use the directory of this file to construct the path to resource.json
    resource_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'resource.json')
    with open(resource_path) as f:
        resources = json.load(f)
    return resources
    
@app.route('/interview-prep')
def interview_prep():
    resources = load_resources()
    return render_template('interview_prep.html', resources=resources)

@app.route('/download/<int:resource_id>')
def download_pdf(resource_id):  
    resources = load_resources()
    resource = next((res for res in resources if res["id"] == resource_id), None)
    if resource and "pdf" in resource:
        return send_file(resource["pdf"], as_attachment=True)
    return "File not found", 404


@app.route('/student/make_resume', methods=['GET', 'POST'])
def make_resume():
    if request.method == 'POST':
        # Collect form data
        user_data = {
            'name': request.form.get('name'),
            'email': request.form.get('email'),
            'phone': request.form.get('phone'),
            'education': request.form.get('education'),
            'work_experience': request.form.get('work_experience'),
            'skills': request.form.get('skills'),
        }

        # Generate the resume PDF
        generator = ResumeGenerator(user_data)
        resume_path = generator.generate_pdf()

        # Return the generated resume as a downloadable file
        return send_file(resume_path, as_attachment=True)

    # Render the resume form for GET requests
    return render_template('resume_form.html')


# @app.route('/student/maybe_do_this', methods=['GET', 'POST'])
# def maybe_do_this():
#     if request.method == 'POST':
#         try:
#             # Get form data
#             job_name = request.form['job_name']
#             job_description = request.form['job_description']

#             # Save uploaded resume
#             resume_file = request.files['resume']
#             resume_path = os.path.join(UPLOAD_FOLDER, secure_filename(resume_file.filename))
#             resume_file.save(resume_path)

#             # Scrape resume content
#             resume_content = scrape_resume(resume_path)

#             # Send data to GPT API
#             suggestions = get_gpt_suggestions(job_name, job_description, resume_content)

#             # Render suggestions
#             return render_template('suggestions.html', suggestions=suggestions)

#         except Exception as e:
#             print(f"Error: {e}")
#             return "An error occurred while processing your request.", 500

    # Render the form for GET request
    #return render_template('maybe_do_this.html')


if __name__ == '__main__':
    app.run(debug=True)
