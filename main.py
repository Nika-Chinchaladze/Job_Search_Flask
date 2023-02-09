from flask import Flask, render_template, redirect, url_for, request, flash, abort, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_required, login_user, logout_user, current_user
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from uuid import uuid1
from functools import wraps
import os
from datetime import date
from gmail_class import SendEmail

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("MY_SECRET_KEY")
# =================================== UPLOAD FILES SECTION =================================== #
UPLOAD_FOLDER = "static/files"
ALLOWED_EXTENSIONS = ['pdf', 'png', 'jpg', 'jpeg']
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


def allowed_file(filename):
    control = str(filename.lower())
    if control[control.rfind(".")+1:] in ALLOWED_EXTENSIONS:
        return True
    else:
        return False


# =================================== PREPARE SQL DATABASE =================================== #
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///myJobs.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


class Users(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String, unique=True, nullable=False)
    user_email = db.Column(db.String, unique=True, nullable=False)
    user_password = db.Column(db.String, nullable=False)
    user_type = db.Column(db.String, nullable=False)
    user_image = db.Column(db.String, nullable=False)


class Jobs(db.Model):
    __tablename__ = "jobs"
    id = db.Column(db.Integer, primary_key=True)
    job_title = db.Column(db.String, nullable=False)
    job_category = db.Column(db.String, nullable=False)
    job_location = db.Column(db.String, nullable=False)
    job_description = db.Column(db.String, nullable=False)
    published_date = db.Column(db.String, nullable=False)
    expired_date = db.Column(db.String, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)


class Questions(db.Model):
    __tablename__ = "questions"
    id = db.Column(db.Integer, primary_key=True)
    question_body = db.Column(db.String, unique=True, nullable=False)
    question_answer = db.Column(db.String, nullable=True)


class Applicants(db.Model):
    __tablename__ = "applicants"
    id = db.Column(db.Integer, primary_key=True)
    applicant_name = db.Column(db.String, nullable=False)
    applicant_email = db.Column(db.String, nullable=False)
    applicant_phone = db.Column(db.String, nullable=False)
    applicant_resume = db.Column(db.String, nullable=False)
    provider_email = db.Column(db.String, db.ForeignKey("users.user_email"), nullable=False)
    provided_job = db.Column(db.String, nullable=False)


# =================================== FLASK LOGIN MANAGER =================================== #
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return Users.query.filter_by(id=user_id).first()


# =================================== GENERAL ROUTES SECTION =================================== #
@app.route("/", methods=["GET", "POST"])
def home_page():
    available_providers_list = Users.query.all()
    if request.method == "POST":
        desired_location = request.form.get("placeSelect")
        desired_category = request.form.get("typeSelect")
        desired_skill = request.form.get("jNameSkill")
        desired_jobs_list = None

        if desired_location != "any" and desired_category != "all" and desired_skill != "":
            desired_jobs_list = db.session.query(Users, Jobs).join(Jobs).filter(
                Jobs.job_location == desired_location,
                Jobs.job_category == desired_category,
                Jobs.job_title.like(f"%{desired_skill}%")
            ).all()
        elif desired_location != "any" and desired_category != "all" and desired_skill == "":
            desired_jobs_list = db.session.query(Users, Jobs).join(Jobs).filter(
                Jobs.job_location == desired_location,
                Jobs.job_category == desired_category
            ).all()
        elif desired_location != "any" and desired_category == "all" and desired_skill == "":
            desired_jobs_list = db.session.query(Users, Jobs).join(Jobs).filter(
                Jobs.job_location == desired_location
            ).all()
        elif desired_location == "any" and desired_category != "all" and desired_skill == "":
            desired_jobs_list = db.session.query(Users, Jobs).join(Jobs).filter(
                Jobs.job_category == desired_category
            ).all()
        elif desired_location == "any" and desired_category == "all" and desired_skill != "":
            desired_jobs_list = db.session.query(Users, Jobs).join(Jobs).filter(
                Jobs.job_title.like(f"%{desired_skill}%")
            ).all()
        elif desired_location != "any" and desired_category == "all" and desired_skill != "":
            desired_jobs_list = db.session.query(Users, Jobs).join(Jobs).filter(
                Jobs.job_location == desired_location,
                Jobs.job_title.like(f"%{desired_skill}%")
            ).all()
        elif desired_location == "any" and desired_category != "all" and desired_skill != "":
            desired_jobs_list = db.session.query(Users, Jobs).join(Jobs).filter(
                Jobs.job_category == desired_category,
                Jobs.job_title.like(f"%{desired_skill}%")
            ).all()
        elif desired_location != "any" or desired_category != "all" or desired_skill != "":
            desired_jobs_list = db.session.query(Users, Jobs).join(Jobs).filter(
                (Jobs.job_location == desired_location) |
                (Jobs.job_category == desired_category) |
                (Jobs.job_title.like(f"%{desired_skill}%"))
            ).all()
        return render_template("index.html",
                               logged_in=current_user.is_authenticated,
                               job_list=desired_jobs_list,
                               provider_list=available_providers_list
                               )

    available_jobs_list = db.session.query(Users, Jobs).join(Jobs).all()
    return render_template("index.html",
                           logged_in=current_user.is_authenticated,
                           present_user=current_user,
                           job_list=available_jobs_list,
                           provider_list=available_providers_list
                           )


@app.route("/about")
def about_page():
    return render_template("about.html",
                           logged_in=current_user.is_authenticated,
                           present_user=current_user
                           )


@app.route("/contact", methods=["GET", "POST"])
def contact_page():
    if request.method == "POST":
        send_tool = SendEmail(
            receiver=request.form.get("email"),
            subject=request.form.get("fullname"),
            body=request.form.get("textArea")
        )
        send_tool.send_mail()
        flash("EMAIL HAS BEEN SENT SUCCESSFULLY!")
        return redirect(url_for("contact_page"))
    return render_template("contact.html",
                           logged_in=current_user.is_authenticated,
                           present_user=current_user
                           )


@app.route("/job", methods=["GET", "POST"])
def job_page():
    if request.method == "POST":
        file = request.files["user_pdf"]
        if file.filename == "":
            return "No Selected File"

        if allowed_file(file.filename):
            pdf_file = secure_filename(file.filename)
            pdf_random_name = str(uuid1()) + "_" + pdf_file
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], pdf_random_name))
            new_applicant = Applicants(
                applicant_name=request.form.get("user_name"),
                applicant_email=request.form.get("email"),
                applicant_phone=request.form.get("phone"),
                applicant_resume=pdf_random_name,
                provider_email=request.form.get("jobProviderNameHold"),
                provided_job=request.form.get("jobProvidedHeadHold")
            )
            db.session.add(new_applicant)
            db.session.commit()
            flash("CONGRATULATIONS - YOUR APPLICATION HAS BEEN SENT SUCCESSFULLY - "
                  "SEARCH FOR ANOTHER OPPORTUNITIES HERE!")
            return redirect(url_for("home_page"))

    job_id = request.args.get("id")
    chosen_job = db.session.query(Users, Jobs).join(Jobs).filter(Jobs.id == job_id).first()
    return render_template("job.html",
                           logged_in=current_user.is_authenticated,
                           present_user=current_user,
                           job=chosen_job
                           )


@app.route("/provider")
def provider_page():
    user_id = request.args.get("id")
    chosen_provider = db.session.query(Users, Jobs).join(Jobs).filter(Jobs.user_id == user_id).all()
    return render_template("provider.html",
                           logged_in=current_user.is_authenticated,
                           present_user=current_user,
                           provider_list=chosen_provider
                           )


# =================================== CRUD OPERATIONS SECTION =================================== #
@app.route("/add", methods=["GET", "POST"])
@login_required
def add_page():
    if request.method == "POST":
        current_date = str(date.today())
        new_job = Jobs(
            job_title=request.form.get("jobtitle"),
            job_category=request.form.get("jobtype"),
            job_location=request.form.get("jobplace"),
            job_description=request.form.get("addArea2"),
            published_date=current_date,
            expired_date=request.form.get("jobdate"),
            user_id=current_user.id
        )
        db.session.add(new_job)
        db.session.commit()
        return redirect(url_for("personal_page"))
    return render_template("add.html",
                           logged_in=current_user.is_authenticated,
                           present_user=current_user
                           )


@app.route("/edit", methods=["GET", "POST"])
@login_required
def edit_page():
    if request.method == "POST":
        current_job = Jobs.query.filter_by(id=request.form.get("holdJobId")).first()
        current_job.job_title = request.form.get("jobtitle")
        current_job.job_category = request.form.get("jobtype")
        current_job.job_location = request.form.get("jobplace")
        current_job.job_description = request.form.get("addArea2")
        current_job.expired_date = request.form.get("jobdate")
        db.session.commit()
        return redirect(url_for("personal_page"))
    chosen_job = Jobs.query.filter_by(id=request.args.get("id")).first()
    return render_template("edit.html",
                           job=chosen_job,
                           logged_in=current_user.is_authenticated,
                           present_user=current_user
                           )


@app.route("/delete")
@login_required
def delete_page():
    chosen_job = Jobs.query.filter_by(id=request.args.get("id")).first()
    db.session.delete(chosen_job)
    db.session.commit()
    return redirect(url_for("personal_page"))


# =================================== USER AUTHENTICATION SECTION =================================== #
@app.route("/register", methods=["GET", "POST"])
def register_page():
    if request.method == "POST":
        file = request.files["user_img"]
        if file.filename == "":
            return "No Selected File"

        check_email = Users.query.filter_by(user_email=request.form.get("user_email")).first()
        check_name = Users.query.filter_by(user_name=request.form.get("user_name")).first()
        if check_email is None and check_name is None:
            if allowed_file(file.filename):
                img_file = secure_filename(file.filename)
                img_random_name = str(uuid1()) + "_" + img_file
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], img_random_name))
                new_user = Users(
                    user_name=request.form.get("user_name"),
                    user_email=request.form.get("user_email"),
                    user_password=generate_password_hash(
                        request.form.get("loginPassword"),
                        method='pbkdf2:sha1',
                        salt_length=8
                    ),
                    user_type=request.form.get("user_type"),
                    user_image=img_random_name
                )
                db.session.add(new_user)
                db.session.commit()
                login_user(new_user)
                return redirect(url_for("personal_page"))
        elif check_name:
            flash("Use Another UserName!")
            return redirect(url_for("register_page"))
        else:
            flash("User Already Exists with That Email - Try to Sign In or use Another One!")
            return redirect(url_for("register_page"))
    return render_template("register.html",
                           logged_in=current_user.is_authenticated,
                           present_user=current_user
                           )


@app.route("/login", methods=["GET", "POST"])
def login_page():
    if request.method == "POST":
        present_user = Users.query.filter_by(user_email=request.form.get("user_name")).first()
        if present_user is not None:
            if check_password_hash(pwhash=present_user.user_password, password=request.form.get("loginPassword")):
                login_user(present_user)
                return redirect(url_for("personal_page"))
            else:
                flash("INCORRECT PASSWORD")
                return redirect(url_for("login_page"))
        else:
            flash("INCORRECT EMAIL")
            return redirect(url_for("login_page"))
    return render_template("login.html",
                           logged_in=current_user.is_authenticated,
                           present_user=current_user
                           )


@app.route("/logout")
@login_required
def logout_page():
    logout_user()
    return redirect(url_for("home_page"))


@app.route("/ask", methods=["GET", "POST"])
def ask_page():
    if request.method == "POST":
        answer_question = request.form.get("answerTextArea")
        check_question = Questions.query.filter_by(question_body=request.form.get("textArea")).first()
        if not check_question and request.form.get("textArea") is not None:
            new_question = Questions(
                question_body=request.form.get("textArea"),
                question_answer="Not Answered Yet"
            )
            db.session.add(new_question)
            db.session.commit()
            return redirect(url_for("ask_page"))
        elif answer_question is not None and len(answer_question) > 0:
            update_question = Questions.query.filter_by(id=request.form.get("hiddenQuestionID")).first()
            update_question.question_answer = answer_question
            db.session.commit()
            return redirect(url_for("ask_page"))
        else:
            flash("QUESTION ALREADY EXISTS HERE - CHECK MORE CAREFULLY!")
            return redirect(url_for("ask_page"))
    question_data = Questions.query.all()
    return render_template("ask.html",
                           logged_in=current_user.is_authenticated,
                           question_list=question_data,
                           present_user=current_user
                           )


@app.route("/personal")
@login_required
def personal_page():
    excepted_applications = db.session.query(Applicants).filter(Applicants.provider_email ==
                                                                current_user.user_email).all()
    present_user = Users.query.filter_by(id=current_user.id).first()
    my_jobs = Jobs.query.filter_by(user_id=current_user.id).all()
    return render_template("personal.html",
                           user=present_user,
                           job_list=my_jobs,
                           logged_in=current_user.is_authenticated,
                           present_user=current_user,
                           applications_list=excepted_applications
                           )


@app.route("/resume")
@login_required
def resume_page():
    pdf_name = request.args.get("name")
    return send_from_directory("static", f"files/{pdf_name}")


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
