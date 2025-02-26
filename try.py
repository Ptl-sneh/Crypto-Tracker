import os
import streamlit as st
import mysql.connector
import random
import time
import query as que
import sendemail
import tempfile

class User:
    def __init__(self):
        """Initialize with a database connection and cursor."""
        self.user_id = None
        self.email = None
        self.password = None
        self.role = None

    def login(self, email, password):
        """Authenticate user based on email and password."""
        query = "SELECT user_id, email, password, role FROM users WHERE email=%s AND password=%s;"
        placeholder = (email, password)
        user = que.get_data(query, placeholder)

        if user:
            self.user_id, self.email, self.password, self.role = user
            st.session_state.user_id = self.user_id
            st.session_state.email = self.email
            st.session_state.role = self.role
            st.session_state.is_logged_in = True

            if self.role == "recruiter":
                recruiter_query = "SELECT recruiter_id FROM recruiterprofiles WHERE user_id = %s;"
                recruiter_data = que.get_data(recruiter_query, (self.user_id,))
                if recruiter_data and recruiter_data[0]:
                    st.session_state["recruiter_id"] = recruiter_data[0]
                else:
                    st.warning("Recruiter ID not found. Please complete your recruiter profile.")

            self.go_to_page("done")
            return True
        else:
            st.error("Invalid email or password.")
            return False

    def logout(self):
        """Logout the user by clearing session data."""
        st.session_state.clear()
        st.session_state.is_logged_in = False
        self.go_to_page("form")
        st.success("You have been logged out.")

    def go_to_page(self, page_name):
        """Redirect the user to a specified page."""
        st.session_state.page = page_name
        st.rerun()

    def get_role(self):
        """Get the role of the logged-in user (applicant, recruiter)."""
        return self.role


# Applicant class
class Applicant(User):

    def _init_(self):
        """Initialize the Applicant with inherited User functionality."""
        super()._init_()  # Call the constructor of the parent class

    def view_applicant_profile(self):
        get = """SELECT full_name,university,degree,cgpa,skills,resume FROM applicantProfiles WHERE user_id= %s;"""
        em = (st.session_state.user_id,)
        results = que.get_data(get, em)
        full_name, university, degree, cgpa, skills, resume = results

        st.title("Your Information")
        st.write("Full Name:", full_name)
        st.write("University:", university)
        st.write("Degree:", degree)
        st.write("CGPA:", cgpa)
        st.write("Skills:", skills)
        st.write("Resume:", resume)

        if st.button("Return to Dashboard"):
            self.go_to_page("done")

    def create_applicant_page(self):
        st.title("Create Applicant Profile")
        full_name = st.text_input("Full Name")
        university = st.text_area("University")
        degree = st.text_input("Degree")
        cgpa = st.text_input("CGPA")
        skills = st.text_input("Skills")
        resume = st.text_input("Resume")

        if self.email:
            st.text_input("Email", value=self.email, disabled=True)
        if st.button("Return to Dashboard"):
            self.go_to_page("done")
        if st.button("Submit"):
            if full_name and university and degree and cgpa and skills and resume:
                st.session_state.role = "applicant"
                try:
                    user_id = st.session_state.get("user_id")
                    query = """
                    INSERT INTO applicantprofiles(user_id, full_name, university, degree, cgpa, skills, resume) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """
                    values = (user_id, full_name, university, degree, cgpa, skills, resume)
                    que.update(query, values)
                    st.success("Applicant profile created successfully!")
                    time.sleep(1)
                    self.go_to_page("form")
                except mysql.connector.Error as err:
                    st.error(f"Error creating applicant profile: {err}")
            else:
                st.error("Please fill in all fields.")

    def update_applicant_profile(self):
        st.title("Update Applicant Profile")
        st.write("Form for updating applicant profile goes here.")
        selet_update = st.selectbox('What You want to Update:', options=('Full Name', "University", "Degree", "Cgpa", "Skills", "Resume"))
        if selet_update == "Full Name":
            full_name = st.text_input('Enter Full Name:')
            if st.button("Update"):
                if full_name:
                    query = "UPDATE applicantProfiles SET full_name=%s WHERE user_id=%s"
                    values = (full_name, st.session_state.user_id)
                    que.update(query, values)
                    st.success("Full Name updated successfully!")
                    time.sleep(1)
                    self.go_to_page("update_applicant_profile")
        if selet_update == "University":
            university = st.text_input('Enter University:')
            if st.button("Update"):
                if university:
                    query = "UPDATE applicantProfiles SET university = %s WHERE user_id = %s"
                    values = (university, st.session_state.user_id)
                    que.update(query, values)
                    st.success("University updated successfully!")
                    time.sleep(1)
                    self.go_to_page("update_applicant_profile")
        if selet_update == "Degree":
            deg = st.text_input('Enter Degree:')
            if st.button("Update"):
                if deg:
                    query = "UPDATE applicantProfiles SET degree = %s WHERE user_id = %s"
                    values = (deg, st.session_state.user_id)
                    que.update(query, values)
                    st.success("Degree updated successfully!")
                    time.sleep(1)
                    self.go_to_page("update_applicant_profile")
        if selet_update == "Cgpa":
            cgpa = st.text_input('Enter CGPA:')
            if st.button("Update"):
                if cgpa:
                    query = "UPDATE applicantProfiles SET cgpa = %s WHERE user_id = %s"
                    values = (cgpa, st.session_state.user_id)
                    que.update(query, values)
                    st.success("CGPA updated successfully!")
                    time.sleep(1)
                    self.go_to_page("update_applicant_profile")
        if selet_update == "Skills":
            skill = st.text_input('Enter Skill:')
            if st.button("Update"):
                if skill:
                    query = "UPDATE applicantProfiles SET skills = %s WHERE user_id = %s"
                    values = (skill, st.session_state.user_id)
                    que.update(query, values)
                    st.success("Skills updated successfully!")
                    time.sleep(1)
                    self.go_to_page("update_applicant_profile")
        if selet_update == "Resume":
            pass  
        if st.button("Return to Dashboard"):
            self.go_to_page("done")
            st.success("You have successfully updated your Applicant profile!")
            time.sleep(1)

    def Applicant_dashboard(self):
        st.title("Applicant Dashboard")
        if st.button("Display Profile"):
            self.go_to_page("view_applicant_profile")
        if st.button("Update Profile"):
            self.go_to_page("update_applicant_profile")
        if st.button("View Available Jobs"):
            self.go_to_page("view_apply_for_jobs")
        if st.button("Exit"):
            self.logout()

    def view_apply_for_jobs(self):
    # Fetch all available jobs from the jobs table
        query = "SELECT job_id, job_title, job_description, company_name FROM jobs;"
        jobs = que.get_data_download(query)  # Use get_data_download to fetch all rows

        # Ensure jobs is a list of tuples
        if not jobs:
            print("No jobs available at the moment.")
            return

        print("\nAvailable Jobs:")
        for job in jobs:
            if not isinstance(job, (list, tuple)) or len(job) < 4:
                print("Error: Job data is not in the correct format.")
                return

            print(f"Job ID: {job[0]}, Title: {job[1]}, Description: {job[2]}, Company: {job[3]}")

        # Ask user for job application
        job_id = int(input("\nEnter the Job ID to apply: "))

        # Check if student_id exists in applicantprofiles before inserting
        check_student_query = "SELECT student_id FROM applicantprofiles WHERE student_id = %s"
        student_id = self.student_id
        result = que.get_data(check_student_query, (student_id,))

        if not result:
            print("Error: Student ID not found. Please register first.")
            return

        # Insert into applications table
        insert_query = "INSERT INTO applications (student_id, job_id) VALUES (%s, %s)"
        values = (student_id, job_id)

        try:
            que.update(insert_query, values)
            print("Application submitted successfully!")
        except mysql.connector.errors.IntegrityError:
            print("Error: Unable to apply. Check if the job exists or if you have already applied.")

# Recruiter class and ForgotPassword class remain unchanged (omitted for brevity)
class Recruiter(User):
    def __init__(self):
        super().__init__()

    def recruiter_dashboard(self):
        st.title("Recruiter Dashboard")
        if st.button("View Profile"):
            self.go_to_page("view_recruiter_profile")
        if st.button("Update Profile"):
            self.go_to_page("update_recruiter_profile")
        if st.button("Post Job"):
            self.go_to_page("post_job")
        if st.button("View Applications"):
            self.go_to_page("view_applications")
        if st.button("Shortlist Candidates"):
            self.go_to_page("shortlist_candidates")
        if st.button("Mark Placement"):
            self.go_to_page("mark_placement")
        if st.button("Generate Placement Report"):
            self.go_to_page("generate_report")
        if st.button("Exit"):
            self.logout()

    def create_profile_page(self):
        st.title("Create Recruiter Profile")
        company_name = st.text_input("Company Name")
        company_description = st.text_area("Company Description")
        website_url = st.text_input("Website URL")
        company_email = st.text_input("Company Email")
        company_location = st.text_input("Company Location")
        if self.email:
            st.text_input("Email", value=self.email, disabled=True)
        if st.button("Submit"):
            if company_name and company_email and company_location and company_description and website_url:
                st.session_state.role = "recruiter"
                try:
                    user_id = st.session_state.get("user_id")
                    query = """
                    INSERT INTO recruiterprofiles(user_id, company_name, company_description, website_url, contact_email, company_location) 
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """
                    values = (user_id, company_name, company_description, website_url, company_email, company_location)
                    que.update(query, values)
                    st.success("Recruiter profile created successfully!")
                    time.sleep(1)
                    self.go_to_page("done")
                except mysql.connector.Error as err:
                    st.error(f"Error creating recruiter profile: {err}")
            else:
                st.error("Please fill in all fields.")

    def view_profile_page(self):
        get = """SELECT company_name, company_description, website_url, contact_email, company_location 
                 FROM recruiterprofiles WHERE user_id=%s"""
        em = (st.session_state.user_id,)
        results = que.get_data(get, em)
        company_name, company_description, website_url, contact_email, company_location = results
        st.title("Your Information")
        st.write("Company Name:", company_name)
        st.write("Company Email:", contact_email)
        st.write("Company Location:", company_location)
        st.write("Website URL:", website_url)
        st.write("Company Description:", company_description)
        if st.button("Return to Dashboard"):
            self.go_to_page("done")

    def update_profile_page(self):
        st.title("Update Recruiter Profile")
        st.write("Form for updating recruiter profile goes here.")
        selet_update = st.selectbox('What You want to Update:', options=('Company Name', "Company Email", "Company Location", "Company Description", "Website url"))
        if selet_update == "Company Name":
            company_name = st.text_input('Enter Company Name:')
            if st.button("Update"):
                if company_name:
                    user_id = st.session_state.get("user_id")
                    query = "UPDATE recruiterprofiles SET company_name = %s WHERE user_id = %s"
                    values = (company_name, user_id)
                    que.update(query, values)
                    st.success("Company Name updated successfully!")
                    time.sleep(1)
                    self.go_to_page("update_recruiter_profile")
        if selet_update == "Company Email":
            contact_email = st.text_input('Enter Company Email:')
            if st.button("Update"):
                if contact_email:
                    user_id = st.session_state.get("user_id")
                    query = "UPDATE recruiterprofiles SET contact_email = %s WHERE user_id = %s"
                    values = (contact_email, user_id)
                    que.update(query, values)
                    st.success("Company Email updated successfully!")
                    time.sleep(1)
                    self.go_to_page("update_recruiter_profile")
        if selet_update == "Company Location":
            compney_location = st.text_input('Enter Company Location:')
            if st.button("Update"):
                if compney_location:
                    user_id = st.session_state.get("user_id")
                    query = "UPDATE recruiterprofiles SET company_location = %s WHERE user_id = %s"
                    values = (compney_location, user_id)
                    que.update(query, values)
                    st.success("Company Location updated successfully!")
                    time.sleep(1)
                    self.go_to_page("update_recruiter_profile")
        if selet_update == "Company Description":
            company_description = st.text_input('Enter Company Description:')
            if st.button("Update"):
                if company_description:
                    user_id = st.session_state.get("user_id")
                    query = "UPDATE recruiterprofiles SET company_description = %s WHERE user_id = %s"
                    values = (company_description, user_id)
                    que.update(query, values)
                    st.success("Company Description updated successfully!")
                    time.sleep(1)
                    self.go_to_page("update_recruiter_profile")
        if selet_update == "Website url":
            website_url = st.text_input('Enter Website url:')
            if st.button("Update"):
                if website_url:
                    user_id = st.session_state.get("user_id")
                    query = "UPDATE recruiterprofiles SET website_url = %s WHERE user_id = %s"
                    values = (website_url, user_id)
                    que.update(query, values)
                    st.success("Website url updated successfully!")
                    time.sleep(1)
                    self.go_to_page("update_recruiter_profile")
        if st.button("Return to Dashboard"):
            self.go_to_page("done")
            st.success("You have successfully updated your recruiter profile!")
            time.sleep(1)

    def ensure_recruiter_id(self):
        if "recruiter_id" not in st.session_state:
            st.session_state["recruiter_id"] = None

    def post_job_page(self):
        st.title("Post Job")
        Recruiter.ensure_recruiter_id(self)
        recruiter_id = st.session_state.get("recruiter_id")
        if not recruiter_id:
            st.error("Error: Recruiter ID not found. Please log in again.")
            return
        job_title = st.text_input("Job Title")
        job_description = st.text_area("Job Description")
        job_type = st.text_input("Job Type")
        location = st.text_input("Location")
        salary_range = st.text_input("Salary Range")
        required_skills = st.text_input("Required Skills")
        experience_level = st.text_input("Experience Level")
        education_requirements = st.text_input("Education Requirements")
        application_deadline = st.date_input("Application Deadline")
        contact_email = st.text_input("Contact Email")
        job_benefits = st.text_area("Job Benefits")
        number_of_openings = st.number_input("Number of Openings", min_value=1, step=1)
        industry_domain = st.text_input("Industry/Domain")
        job_file_data = None
        if st.button("Submit Job"):
            if all([
                job_title, job_description, job_type, location, salary_range,
                required_skills, experience_level, education_requirements,
                str(application_deadline), contact_email, job_benefits,
                number_of_openings, industry_domain
            ]):
                from datetime import datetime, timedelta
                created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                ends_at = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S")
                job_file_content = (
                    f"Job Title: {job_title}\n"
                    f"Job Description: {job_description}\n"
                    f"Job Type: {job_type}\n"
                    f"Location: {location}\n"
                    f"Salary Range: {salary_range}\n"
                    f"Required Skills: {required_skills}\n"
                    f"Experience Level: {experience_level}\n"
                    f"Education Requirements: {education_requirements}\n"
                    f"Application Deadline: {application_deadline}\n"
                    f"Contact Email: {contact_email}\n"
                    f"Job Benefits: {job_benefits}\n"
                    f"Number of Openings: {number_of_openings}\n"
                    f"Industry/Domain: {industry_domain}\n"
                    f"Created At: {created_at}\n"
                    f"Ends At: {ends_at}\n"
                )
                with tempfile.NamedTemporaryFile(delete=False, mode="w", suffix=".txt") as temp_file:
                    temp_file.write(job_file_content)
                    temp_file_path = temp_file.name
                with open(temp_file_path, "rb") as file:
                    job_file_data = file.read()
                try:
                    query = """
                    INSERT INTO jobs (
                        recruiter_id, job_title, job_description, job_type, location, salary_range,
                        required_skills, experience_level, education_requirements, application_deadline,
                        contact_email, job_benefits, number_of_openings, industry_domain, created_at, ends_at, job_file
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    values = (
                        recruiter_id,
                        job_title,
                        job_description,
                        job_type,
                        location,
                        salary_range,
                        required_skills,
                        experience_level,
                        education_requirements,
                        application_deadline,
                        contact_email,
                        job_benefits,
                        number_of_openings,
                        industry_domain,
                        created_at,
                        ends_at,
                        job_file_data
                    )
                    que.update(query, values)
                    st.success("Job posted successfully!")
                except mysql.connector.Error as err:
                    st.error(f"Error submitting job: {err}")
                os.remove(temp_file_path)
            else:
                st.error("Please fill in all required fields.")
        if job_file_data:
            st.download_button(
                label="Download Job File",
                data=job_file_data,
                file_name=f"{job_title}.txt",
                mime="text/plain",
            )
        if st.button("Go to Dashboard"):
            self.go_to_page("done")

    def view_applications_page(self):
        st.title("View Job Applications")
        
        # Ensure recruiter_id is available from session_state.
        recruiter_id = st.session_state.get("recruiter_id")
        st.write(recruiter_id)
        if not recruiter_id:
            st.error("Recruiter ID not found. Please log in again.")
            if st.button("Go to Dashboard"):
                self.go_to_page("done")
            return

        # Query to fetch all applications for jobs posted by this recruiter.
        # Adjust the join queries as needed according to your schema.
        query = """
            SELECT
                a.application_id,
                j.job_id,
                j.job_title,
                ap.full_name,
                ap.university,
                ap.degree,
                ap.cgpa,
                ap.skills,
                u.email,
                a.status
            FROM applications a
            JOIN jobs j ON a.job_id = j.job_id
            JOIN applicantprofiles ap ON a.student_id = ap.user_id
            JOIN users u ON ap.user_id = u.user_id
            WHERE j.recruiter_id = %s;
        """
        # Use your helper function to fetch multiple rows.
        applications = que.get_data_download(query, (recruiter_id,))
        
        if not applications:
            st.info("No applications found for your posted jobs.")
            if st.button("Go to Dashboard"):
                self.go_to_page("done")
            return

        # Prepare a mapping of application IDs to a detailed label.
        app_options = {}
        for app in applications:
            # Unpack the columns from the query result
            (application_id, job_id, job_title, full_name, university,
             degree, cgpa, skills, email, status) = app

            label = (f"App ID: {application_id} | Job: {job_title} | "
                     f"Name: {full_name} | Email: {email} | "
                     f"University: {university} | Degree: {degree} | "
                     f"CGPA: {cgpa} | Skills: {skills} | Status: {status}")
            app_options[application_id] = label

        # Display the applications in a table for a quick overview.
        # You can use st.table with a list of dicts.
        table_data = [
            {
                "Application ID": app[0],
                "Job ID": app[1],
                "Job Title": app[2],
                "Applicant Name": app[3],
                "University": app[4],
                "Degree": app[5],
                "CGPA": app[6],
                "Skills": app[7],
                "Email": app[8],
                "Status": app[9]
            }
            for app in applications
        ]
        st.table(table_data)
        
        # Allow the recruiter to select which applications to shortlist.
        selected_app_ids = st.multiselect(
            "Select applications to shortlist",
            options=list(app_options.keys()),
            format_func=lambda app_id: app_options[app_id]
        )

        if st.button("Shortlist Selected"):
            if not selected_app_ids:
                st.warning("No applications selected. Please select at least one application.")
                if st.button("Return to Dashboard"):
                    self.go_to_page("done")
            else:
                update_query = "UPDATE applications SET status = 'shortlisted' WHERE application_id = %s"
                success_count = 0
                for app_id in selected_app_ids:
                    try:
                        que.update(update_query, (app_id,))
                        success_count += 1
                    except Exception as e:
                        st.error(f"Error updating application {app_id}: {e}")
                        if st.button("Go to Dashboard"):
                             self.go_to_page("done")
                if success_count:
                    st.success(f"{success_count} application(s) have been shortlisted.")
                # Optionally, refresh the page to show updated status.
                self.go_to_page("view_applications")
        
        if st.button("Return to Dashboard"):
            self.go_to_page("done")

class ForgotPassword(User):
    def __init__(self):
        super().__init__()

    def send_otp(self, email):
        user = que.get_data("SELECT email FROM users WHERE email=%s;", (email,))
        if user:
            otp = random.randint(100000, 999999)
            st.session_state.otp = otp
            st.session_state.otp_email = email
            sendemail.send(email, "Forgot password", f"Your otp {otp}")
            st.info(f"OTP sent to {email}: {otp}")
        else:
            st.error("Email not found in the database.")
            if st.button("Return to Dashboard"):
                self.go_to_page("form")

    def verify_otp(self, entered_otp):
        if str(st.session_state.otp) == entered_otp:
            st.success("OTP verified successfully. You can reset your password.")
            return True
        else:
            st.error("Invalid OTP. Please try again.")
            return False

def main():
    user = User()
    recruiter = Recruiter()
    forgot_password = ForgotPassword()
    applicant = Applicant()

    if "page" not in st.session_state:
        st.session_state.page = "form"

    if st.session_state.page == "form":
        st.title("Login Page")
        email = st.text_input("Enter Your E-Mail:")
        password1 = st.text_input("Enter Your Password:", type="password")
        if st.button("Submit"):
            if user.login(email, password1):
                st.success("Login successful!")
        if st.button("Forget Password"):
            st.session_state.page = "forgot_password"
            st.rerun()
        if st.button("Create New Account"):
            st.session_state.page = "create_new_account"
            st.rerun()

    elif st.session_state.page == "done":
        st.title("Welcome!")
        role = st.session_state.role
        print(st.session_state.role)
        if role == "recruiter":
            recruiter.recruiter_dashboard()
        elif role == "applicant":
            st.write("Welcome, Applicant! Access your dashboard below.")
            applicant.Applicant_dashboard()
        elif role == "admin":
            st.write("Welcome, Admin! Manage the platform here.")

    elif st.session_state.page == "create_new_account":
        st.title("Create New Account")
        user_role = st.radio("Select your role:", ["Applicant", "Recruiter"])
        print(user_role)
        create_email = st.text_input("Enter Email:")
        create_password = st.text_input("Enter Password:", type="password")
        create_confirm_password = st.text_input("Confirm Password:", type="password")
        if st.button("Submit"):
            if create_password == create_confirm_password and create_password != "":
                existing_user = que.get_data("SELECT email FROM users WHERE email=%s;", (create_email,))
                if existing_user:
                    st.error("Email already exists. Please use a different email.")
                else:
                    insert_query = """INSERT INTO users (email, password, role) VALUES (%s, %s, %s)"""
                    values = (create_email, create_password, user_role)
                    user_id = que.update(insert_query, values, return_last_insert_id=True)
                    st.session_state.user_id = user_id
                    st.success("Account created successfully!")
                    if user_role == 'Recruiter':
                        user.go_to_page("create_recruiter_profile")
                    elif user_role == 'Applicant':
                        user.go_to_page("create_applicant_profile")
            else:
                st.error("Passwords do not match or are empty. Please try again.")
        elif st.button('Back'):
            user.go_to_page('form')
            st.rerun()

    elif st.session_state.page == "forgot_password":
        st.title("Forgot Password")
        f_email = st.text_input("Enter Email-id:")
        if st.button("Send OTP"):
            forgot_password.send_otp(f_email)
        if "otp" in st.session_state:
            entered_otp = st.text_input("Enter OTP:")
            if st.button("Verify OTP"):
                if forgot_password.verify_otp(entered_otp):
                    st.session_state.page = "reset_password"
                    st.rerun()

    elif st.session_state.page == "reset_password":
        st.title("Reset Password")
        new_password = st.text_input("Enter New Password:", type="password")
        confirm_password = st.text_input("Confirm New Password:", type="password")
        if st.button("Submit"):
            if new_password == confirm_password:
                que.update("UPDATE users SET password=%s WHERE email=%s;", (new_password, st.session_state.otp_email))
                st.success("Password reset successfully. Please log in.")
                user.go_to_page("form")
            else:
                st.error("Passwords do not match. Please try again.")

    # applicant pages
    elif st.session_state.page == "create_applicant_profile":
        applicant.create_applicant_page()
    elif st.session_state.page == "view_applicant_profile":
        applicant.view_applicant_profile()
    elif st.session_state.page == "update_applicant_profile":
        applicant.update_applicant_profile()
    elif st.session_state.page == "view_apply_for_jobs":
        applicant.view_apply_for_jobs()
    elif st.session_state.page == "applied_job_status":
        applicant.create_applicant_page()

    # recruiter pages
    elif st.session_state.page == "create_recruiter_profile":
        recruiter.create_profile_page()
    elif st.session_state.page == "view_recruiter_profile":
        recruiter.view_profile_page()
    elif st.session_state.page == "update_recruiter_profile":
        recruiter.update_profile_page()
    elif st.session_state.page == "post_job":
        recruiter.post_job_page()
    elif st.session_state.page == "view_applications":
        recruiter.view_applications_page()
    elif st.session_state.page == "shortlist_candidates":
        recruiter.shortlist_candidates_page()
    elif st.session_state.page == "mark_placement":
        recruiter.mark_placement_page()
    elif st.session_state.page == "generate_report":
        recruiter.generate_report_page()


if __name__ == "__main__":
    main()
