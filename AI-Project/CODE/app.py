import docx2txt
from pyresparser import ResumeParser
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer
from flask import Flask,render_template,request,redirect,url_for,flash,session
import mysql.connector
import pandas as pd
db=mysql.connector.connect(user="root",password="",port='3306',database='resume')
cur=db.cursor()
from flask_mail import *
app=Flask(__name__)
app.secret_key="CBJcb786874wrf78chdchsdcv"
import requests
import os
import csv
import docx2txt
import spacy
import random
from pyresparser import ResumeParser
from PyPDF2 import PdfReader  

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/about")
def about():
    return render_template('about.html')


@app.route("/signup")
def signup():
    return render_template('registration.html')


@app.route('/login',methods=['POST','GET'])
def login():
    if request.method=='POST':
        useremail=request.form['useremail']
        session['useremail']=useremail
        userpassword=request.form['userpassword']
        sql="select * from user where useremail='%s' and userpassword='%s'"%(useremail,userpassword)
        cur.execute(sql)
        data=cur.fetchall()
        db.commit()
        if data ==[]:
            msg="user Credentials Are not valid"
            return render_template("login.html",name=msg)
        else:
            return render_template("Upload.html",myname=data[0][1])
    return render_template('login.html')

@app.route('/register',methods=["POST","GET"])
def registration():
    if request.method=='POST':
        username=request.form['username']
        useremail = request.form['useremail']
        userpassword = request.form['userpassword']
        conpassword = request.form['conpassword']
        Age = request.form['Age']
        address = request.form['address']
        contact = request.form['contact']
        if userpassword == conpassword:
            sql="select * from user where useremail='%s' and userpassword='%s'"%(useremail,userpassword)
            cur.execute(sql)
            data=cur.fetchall()
            db.commit()
            print(data)
            if data==[]:
                sql = "insert into user(Username,Useremail,Userpassword,Age,Address,Contact)values(%s,%s,%s,%s,%s,%s)"
                val=(username,useremail,userpassword,Age,address,contact)
                cur.execute(sql,val)
                db.commit()
                flash("Registered successfully","success")
                return render_template("login.html")
            else:
                flash("Details are invalid","warning")
                return render_template("registration.html")
        else:
            flash("Password doesn't match", "warning")
            return render_template("registration.html")
    return render_template('registration.html')

@app.route('/upload',methods=["POST","GET"])
def upload():
    return render_template('upload.html')

# Define a function to read job details with skills from a CSV file
def read_job_details_from_csv():
    csv_file_path = "job_details.csv"  # Specify the path to your CSV file
    job_details = []
    with open(csv_file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            job_details.append(row)
    return job_details

# Define the list of job positions
job_positions = [
    "Software Engineer",
    "Data Analyst",
    "Web Developer",
    "Digital Marketing Specialist",
    "Graphic Designer",
    "Product Manager",
    "UX/UI Designer",
    "Business Analyst",
    "Sales Manager",
    "Human Resources Manager",
    "Project Manager",
    "Accountant",
    "Marketing Manager",
    "Network Administrator",
    "Data Scientist",
    "Data Engineer",
    "System Engineer",
    "Operational Manager",
    "Performance Analyst",
    "Team Lead",
    "Manager"
]

# # Route for the registration form
# @app.route('/load', methods=["POST", "GET"])
# def load():
#     if request.method == 'POST':
#         # Handle form submission
#         files1 = request.files['resume']
#         selected_job_position = request.form['job_position']

#         # Get the file extension
#         file_extension = files1.filename.split('.')[-1]

#         if file_extension == 'docx':
#             # Process DOCX file
#             resume_text = docx2txt.process(files1)
#         elif file_extension == 'pdf':
#             # Process PDF file using PdfReader
#             pdf_reader = PdfReader(files1)
#             resume_text = ''
#             for page in pdf_reader.pages:
#                 resume_text += page.extract_text()

#         # Read job details from CSV
#         job_details = read_job_details_from_csv()

#         # Find the selected job position's required skills
#         target_job_skills = None
#         for job in job_details:
#             if job['Job Position'] == selected_job_position:
#                 target_job_skills = job['Skills'].split(',')

#         if not target_job_skills:
#             return "Selected job position not found in job details CSV."

#         # Extract skills from the resume text
#         user_skills = extract_skills_from_text(resume_text)

#         # Find missing skills for the selected job position
#         missing_skills = [skill for skill in target_job_skills if skill not in user_skills]

#         # Render the "load" page with results
#         return render_template('load.html', user_skills=user_skills,
#                                target_job_skills=target_job_skills, missing_skills=missing_skills,
#                                job_positions=job_positions, selected_job_position=selected_job_position)

#     # Render the "load" page with job position dropdown options
#     return render_template('load.html', job_positions=job_positions)


# # Define a function to extract skills from text 
# def extract_skills_from_text(text):
#     return [skill.strip() for skill in text.split(',')]

@app.route('/load', methods=["POST", "GET"])
def load():
    if request.method == 'POST':
        files1 = request.files['resume']
        selected_job_position = request.form['job_position']

        # Save the uploaded file temporarily
        temp_file_path = "temp_resume." + files1.filename.split('.')[-1]
        files1.save(temp_file_path)

        # Use ResumeParser to extract skills
        resume_data = ResumeParser(temp_file_path).get_extracted_data()
        user_skills = resume_data.get('skills', [])

        # Remove the temporary file
        os.remove(temp_file_path)

        # Read job details from CSV
        job_details = read_job_details_from_csv()

        # Find the selected job position's required skills
        target_job_skills = None
        for job in job_details:
            if job['Job Position'] == selected_job_position:
                target_job_skills = job['Skills'].split(',')

        if not target_job_skills:
            return "Selected job position not found in job details CSV."

        # Find missing skills for the selected job position
        missing_skills = [skill for skill in target_job_skills if skill not in user_skills]

        # Render the "load" page with results
        return render_template('load.html', user_skills=user_skills,
                               target_job_skills=target_job_skills, missing_skills=missing_skills,
                               job_positions=job_positions, selected_job_position=selected_job_position)

    # Render the "load" page with job position dropdown options
    return render_template('load.html', job_positions=job_positions)
 

if __name__ == '__main__':
    app.run(debug=True)