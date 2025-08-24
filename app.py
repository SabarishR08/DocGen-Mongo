# ---------------- IMPORTS ---------------- #
import os
import base64
import pandas as pd
from datetime import datetime
from dateutil.parser import parse
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, send_file
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, PasswordField
from wtforms.validators import DataRequired
from functools import wraps
from dotenv import load_dotenv
from pymongo import MongoClient
import pdfkit
from docxtpl import DocxTemplate
import requests
from bson.objectid import ObjectId
from jinja2 import Template
import io, zipfile
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# ---------------- ENV ---------------- #
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/docgen")
BREVO_API_KEY = os.getenv("BREVO_API_KEY")
SENDER_NAME = os.getenv("SENDER_NAME")
SENDER_EMAIL = os.getenv("SENDER_EMAIL")

# ---------------- APP INIT ---------------- #
app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "your_secret_key")

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# MongoDB setup
client = MongoClient(MONGO_URI)
db = client.get_database()
candidates_col = db.candidates
templates_col = db.templates
audit_col = db.audit_logs
users_col = db.users

# Folders
GENERATED_PDFS_FOLDER = os.path.join(os.path.dirname(__file__), "generated_pdfs")
UPLOADS_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(GENERATED_PDFS_FOLDER, exist_ok=True)
os.makedirs(UPLOADS_FOLDER, exist_ok=True)

# PDFKit config
# Note: WKHTMLTOPDF_PATH should be configured based on your system.
WKHTMLTOPDF_PATH = os.environ.get("WKHTMLTOPDF_PATH", r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe")
pdfkit_config = pdfkit.configuration(wkhtmltopdf=WKHTMLTOPDF_PATH)

# ---------------- USER MODEL AND ROLE-BASED ACCESS CONTROL ---------------- #
class User(UserMixin):
    def __init__(self, user_id, username, role):
        self.id = user_id
        self.username = username
        self.role = role

    def get_id(self):
        return str(self.id)

@login_manager.user_loader
def load_user(user_id):
    user_data = users_col.find_one({"_id": ObjectId(user_id)})
    if user_data:
        # The user object now includes the role
        return User(user_data["_id"], user_data["username"], user_data.get("role", "staff"))
    return None

# Custom decorators for role-based access control
def role_required(required_roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Check if the user is authenticated and has one of the required roles
            if not current_user.is_authenticated or current_user.role not in required_roles:
                flash("You do not have permission to access this page.", "danger")
                return redirect(url_for('home'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

admin_required = role_required(["admin"])
hr_required = role_required(["admin", "hr"])
staff_required = role_required(["admin", "hr", "staff"])

# ---------------- FORMS ---------------- #
class TemplateForm(FlaskForm):
    name = StringField("Template Name", validators=[DataRequired()])
    type = SelectField(
        "Type",
        choices=[("offer", "Offer Letter"), ("appointment", "Appointment Letter"),
                 ("experience", "Experience Letter"), ("certificate", "Certificate")]
    )
    content = TextAreaField("Template Content", validators=[DataRequired()])

class CandidateForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    role = StringField("Role")
    start_date = StringField("Start Date")
    end_date = StringField("End Date")

# Corrected LoginForm with the 'role' field
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    role = SelectField('Role', choices=[('admin', 'Admin'), ('hr', 'HR'), ('staff', 'Staff')], validators=[DataRequired()])

class CreateUserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    # New field to select the user's role
    role = SelectField('Role', choices=[('admin', 'Admin'), ('hr', 'HR'), ('staff', 'Staff')])

# ---------------- HELPERS ---------------- #
def load_base64_logo():
    logo_path = os.path.join(app.static_folder, "automation_logo.png")
    if not os.path.exists(logo_path):
        return ""
    with open(logo_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

def inline_css(filename="style.css"):
    css_path = os.path.join(app.static_folder, filename)
    if not os.path.exists(css_path):
        return ""
    with open(css_path, "r", encoding="utf-8") as f:
        return f.read()

def ensure_datetime(candidate, field):
    if candidate.get(field):
        if isinstance(candidate[field], str):
            try:
                candidate[field] = parse(candidate[field])
            except ValueError:
                candidate[field] = None

def render_template_content(template_str, candidate):
    context = {
        "name": candidate.get("name", ""),
        "email": candidate.get("email", ""),
        "role": candidate.get("role", ""),
        "start_date": candidate.get("start_date"),
        "end_date": candidate.get("end_date"),
        "date": datetime.today().strftime("%B %d, %Y"),
        "current_year": datetime.today().year,
    }
    jinja_template = Template(template_str)
    return jinja_template.render(**context)

def generate_pdf(candidate, template, filename):
    ensure_datetime(candidate, "start_date")
    ensure_datetime(candidate, "end_date")
    rendered_html = render_template_content(template["content"], candidate)

    html = f"""
    <html>
    <head><style>{inline_css()}</style></head>
    <body>
        <img src="data:image/png;base64,{load_base64_logo()}" style="max-height:60px;"><br><br>
        {rendered_html}
    </body>
    </html>
    """

    filepath = os.path.join(GENERATED_PDFS_FOLDER, filename)
    pdfkit.from_string(html, filepath, configuration=pdfkit_config, options={"enable-local-file-access": None})
    return filename

def generate_docx(candidate, template, filename):
    ensure_datetime(candidate, "start_date")
    ensure_datetime(candidate, "end_date")
    context = {
        "name": candidate["name"],
        "email": candidate["email"],
        "role": candidate.get("role", ""),
        "start_date": candidate.get("start_date"),
        "end_date": candidate.get("end_date"),
        "date": datetime.today().strftime("%B %d, %Y"),
    }

    filepath = os.path.join(GENERATED_PDFS_FOLDER, filename)
    try:
        doc = DocxTemplate(template["content"])
        doc.render(context)
        doc.save(filepath)
    except Exception as e:
        logging.error(f"Error generating DOCX from template. Falling back to simple docx. Exception: {e}")
        from docx import Document
        rendered_text = render_template_content(template["content"], candidate)
        doc = Document()
        doc.add_paragraph(rendered_text)
        doc.save(filepath)
    return filename

def send_email_brevo(to_email, subject, html_content, attachment_path=None):
    url = "https://api.brevo.com/v3/smtp/email"
    payload = {
        "sender": {"name": SENDER_NAME, "email": SENDER_EMAIL},
        "to": [{"email": to_email}],
        "subject": subject,
        "htmlContent": html_content
    }
    if attachment_path:
        with open(attachment_path, "rb") as f:
            payload["attachment"] = [{
                "name": os.path.basename(attachment_path),
                "content": base64.b64encode(f.read()).decode()
            }]
    headers = {"accept": "application/json", "api-key": BREVO_API_KEY, "content-type": "application/json"}
    response = requests.post(url, json=payload, headers=headers)
    return response.status_code in [200, 201]

def log_audit(candidate_id, template_id, action):
    audit_col.insert_one({
        "candidate_id": candidate_id,
        "template_id": template_id,
        "action": action,
        "timestamp": datetime.utcnow(),
        "user_id": str(current_user.id)
    })

# ---------------- ROUTES ---------------- #
@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # Find user by username and password
        user_data = users_col.find_one({"username": form.username.data, "password": form.password.data})
        if user_data:
            # Check if the submitted role matches the role in the database
            if user_data.get('role') == form.role.data:
                # Load user with their role from the database
                user = User(user_data["_id"], user_data["username"], user_data.get("role", "staff"))
                login_user(user)
                flash("Logged in successfully.", "success")
                return redirect(url_for("home"))
            else:
                flash("Invalid username, password, or role combination.", "danger")
        else:
            flash("Invalid username or password.", "danger")
    return render_template("login.html", form=form)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for("login"))

@app.route("/create_user", methods=["GET", "POST"])
@admin_required # Only admins can access this route
def create_user():
    form = CreateUserForm()
    if form.validate_on_submit():
        if users_col.find_one({"username": form.username.data}):
            flash("Username already exists.", "danger")
        else:
            users_col.insert_one({
                "username": form.username.data,
                "password": form.password.data,
                "role": form.role.data # Save the selected role
            })
            flash(f"User '{form.username.data}' created successfully!", "success")
        return redirect(url_for("create_user"))
        
    all_users = list(users_col.find({}))
    return render_template("create_user.html", form=form, users=all_users)

@app.route("/delete_user/<user_id>")
@admin_required # Only admins can access this route
def delete_user(user_id):
    user_to_delete = users_col.find_one({"_id": ObjectId(user_id)})
    if user_to_delete and user_to_delete.get("username") == 'Vignesh R':
        flash("You cannot delete the main admin user.", "danger")
        return redirect(url_for("create_user"))
        
    result = users_col.delete_one({"_id": ObjectId(user_id)})
    if result.deleted_count > 0:
        flash("User deleted successfully!", "success")
    else:
        flash("User not found.", "danger")
    return redirect(url_for("create_user"))

@app.route("/")
@login_required
def home():
    search_query = request.args.get("search", "").strip()
    query = {}
    
    # Staff users can now see all candidates
    if current_user.role == 'staff':
        # Removed the email-based filter for staff
        pass
    elif search_query:
        # HR/Admin can search
        query = {"$or": [
            {"name": {"$regex": search_query, "$options": "i"}},
            {"email": {"$regex": search_query, "$options": "i"}}
        ]}
    
    candidates = list(candidates_col.find(query))
    templates = list(templates_col.find())
    audit_logs_list = list(audit_col.find().sort("timestamp", -1).limit(20))

    for c in candidates:
        ensure_datetime(c, "start_date")
        ensure_datetime(c, "end_date")

    for log in audit_logs_list:
        candidate = candidates_col.find_one({"_id": ObjectId(log.get("candidate_id"))}) if log.get("candidate_id") else None
        template = templates_col.find_one({"_id": ObjectId(log.get("template_id"))}) if log.get("template_id") else None
        log["candidate_name"] = candidate["name"] if candidate else "N/A"
        log["template_name"] = template["name"] if template else "N/A"
        if not isinstance(log.get("timestamp"), datetime):
            log["timestamp"] = datetime.utcnow()

    return render_template("home.html",
                           candidates=candidates,
                           templates=templates,
                           candidate_form=CandidateForm(),
                           audit_logs=audit_logs_list,
                           search_query=search_query)

@app.route("/clear_audit_logs")
@admin_required # Only admins can clear logs
def clear_audit_logs():
    audit_col.delete_many({})
    flash("All audit logs cleared successfully!", "success")
    return redirect(url_for("home"))

@app.route("/bulk_upload", methods=["GET", "POST"])
@hr_required # Admins and HR can bulk upload
def bulk_upload():
    if request.method == "POST":
        file = request.files.get("file")
        if not file:
            flash("No file selected", "danger")
            return redirect(request.url)

        filepath = os.path.join(UPLOADS_FOLDER, file.filename)
        file.save(filepath)

        try:
            df = pd.read_csv(filepath) if file.filename.endswith(".csv") else pd.read_excel(filepath)
            templates = list(templates_col.find())

            for _, row in df.iterrows():
                candidate = {
                    "name": row.get("name"),
                    "email": row.get("email"),
                    "role": row.get("role"),
                    "start_date": row.get("start_date"),
                    "end_date": row.get("end_date"),
                    "documents": []
                }
                inserted = candidates_col.insert_one(candidate)
                candidate_id = inserted.inserted_id

                for template in templates:
                    # Fix: Use a single filename variable
                    filename = f"{template['type']}_{candidate_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
                    
                    pdf_filename = filename + ".pdf"
                    generate_pdf(candidate, template, pdf_filename)
                    candidates_col.update_one(
                        {"_id": candidate_id},
                        {"$push": {"documents": {"file_type": f"{template['type']}_pdf", "file_path": pdf_filename, "template_id": str(template['_id'])}}}
                    )
                    log_audit(str(candidate_id), str(template["_id"]), f"Bulk Generated {template['type'].upper()}_PDF")

                    docx_filename = filename + ".docx"
                    generate_docx(candidate, template, docx_filename)
                    candidates_col.update_one(
                        {"_id": candidate_id},
                        {"$push": {"documents": {"file_type": f"{template['type']}_docx", "file_path": docx_filename, "template_id": str(template['_id'])}}}
                    )
                    log_audit(str(candidate_id), str(template["_id"]), f"Bulk Generated {template['type'].upper()}_DOCX")

            flash("Bulk upload + auto-generation successful!", "success")
        except Exception as e:
            flash(f"Error processing file: {e}", "danger")
        return redirect(url_for("bulk_upload"))
    return render_template("bulk_upload.html")

@app.route("/add_candidate", methods=["POST"])
@hr_required # Admins and HR can add candidates
def add_candidate():
    form = CandidateForm()
    if form.validate_on_submit():
        candidates_col.insert_one({
            "name": form.name.data,
            "email": form.email.data,
            "role": form.role.data,
            "start_date": form.start_date.data,
            "end_date": form.end_date.data,
            "documents": []
        })
        flash(f"Candidate '{form.name.data}' added successfully!", "success")
    else:
        flash("Please fill in required fields", "danger")
    return redirect(url_for("home"))

@app.route("/delete_candidate/<candidate_id>")
@hr_required # Admins and HR can delete candidates
def delete_candidate(candidate_id):
    candidate = candidates_col.find_one({"_id": ObjectId(candidate_id)})
    if candidate:
        log_audit(candidate_id, None, "Deleted Candidate")
        candidates_col.delete_one({"_id": ObjectId(candidate_id)})
        flash("Candidate deleted successfully!", "success")
    else:
        flash("Candidate not found", "danger")
    return redirect(url_for("home"))

@app.route("/templates", methods=["GET", "POST"])
@hr_required # Admins and HR can manage templates
def manage_templates():
    form = TemplateForm()
    if form.validate_on_submit():
        # Check if user has permission to add templates
        if current_user.role not in ["admin", "hr"]:
            flash("You do not have permission to add templates.", "danger")
            return redirect(url_for("manage_templates"))
        templates_col.insert_one({
            "name": form.name.data,
            "type": form.type.data,
            "content": form.content.data,
            "created_at": datetime.utcnow()
        })
        flash("Template created successfully!", "success")
        return redirect(url_for("manage_templates"))
    return render_template("templates.html", templates=list(templates_col.find()), form=form)

@app.route("/edit_template/<id>", methods=["GET", "POST"])
@hr_required # Admins and HR can edit templates
def edit_template(id):
    template = templates_col.find_one({"_id": ObjectId(id)})
    if not template:
        flash("Template not found", "danger")
        return redirect(url_for("manage_templates"))

    form = TemplateForm(obj=template)
    if request.method == "POST" and form.validate_on_submit():
        templates_col.update_one(
            {"_id": ObjectId(id)},
            {"$set": {"name": form.name.data, "type": form.type.data, "content": form.content.data}}
        )
        log_audit(None, id, f"Template edited: {form.name.data}")
        flash("Template updated successfully!", "success")
        return redirect(url_for("manage_templates"))
    return render_template("edit_template.html", form=form, template=template)

@app.route("/delete_template/<id>")
@admin_required # Only admins can delete templates
def delete_template(id):
    template = templates_col.find_one({"_id": ObjectId(id)})
    if not template:
        flash("Template not found", "danger")
    else:
        templates_col.delete_one({"_id": ObjectId(id)})
        log_audit(None, id, f"Template deleted: {template['name']}")
        flash("Template deleted successfully!", "success")
    return redirect(url_for("manage_templates"))

@app.route("/search_candidates", methods=["GET"])
@staff_required # All roles can search/view candidates
def search_candidates():
    query = request.args.get("q", "")
    if current_user.role == 'staff':
        results = candidates_col.find({}) # Staff can view all candidates
    else:
        results = candidates_col.find({"name": {"$regex": query, "$options": "i"}})
    return render_template("search_results.html", results=results, query=query)

@app.route("/generate_document/<candidate_id>/<template_id>/<doc_type>")
@staff_required # Admins, HR, and Staff can now generate documents
def generate_document(candidate_id, template_id, doc_type):
    candidate = candidates_col.find_one({"_id": ObjectId(candidate_id)})
    template = templates_col.find_one({"_id": ObjectId(template_id)})
    if not candidate or not template:
        flash("Candidate or Template not found", "danger")
        return redirect(url_for("home"))
    
    # Use a single variable to store the filename, regardless of type
    filename = f"{doc_type}_{candidate_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"

    if doc_type.endswith("_pdf"):
        filename += ".pdf"
        generate_pdf(candidate, template, filename)
    elif doc_type.endswith("_docx"):
        filename += ".docx"
        generate_docx(candidate, template, filename)
    else:
        flash("Invalid document type", "danger")
        return redirect(url_for("home"))

    candidates_col.update_one(
        {"_id": ObjectId(candidate_id)},
        {"$push": {"documents": {"file_type": doc_type, "file_path": filename, "template_id": str(template["_id"])}}}
    )

    log_audit(candidate_id, template_id, f"Generated {doc_type.upper()}")
    flash(f"{doc_type.upper()} generated successfully!", "success")
    return redirect(url_for("home"))

@app.route("/download/<filename>")
@staff_required # All roles can download documents
def download_generated(filename):
    return send_from_directory(GENERATED_PDFS_FOLDER, filename, as_attachment=True)

@app.route("/send_email/<candidate_id>/<template_id>/<doc_type>")
@staff_required # Admins, HR, and Staff can now send emails
def send_email(candidate_id, template_id, doc_type):
    candidate = candidates_col.find_one({"_id": ObjectId(candidate_id)})
    if not candidate:
        flash("Candidate not found", "danger")
        return redirect(url_for("home"))

    doc_entry = next((d for d in candidate.get("documents", []) if d["file_type"] == doc_type), None)
    if not doc_entry:
        flash(f"No {doc_type.upper()} document found.", "danger")
        return redirect(url_for("home"))

    filepath = os.path.join(GENERATED_PDFS_FOLDER, doc_entry["file_path"])
    success = send_email_brevo(candidate["email"], f"Your {doc_type.upper()}",
                               f"Dear {candidate['name']}, please find attached your {doc_type}.", filepath)
    if success:
        flash(f"{doc_type.upper()} sent successfully to {candidate['email']}", "success")
        log_audit(candidate_id, doc_entry.get("template_id", ""), f"Sent {doc_type.upper()} via email")
    else:
        flash("Failed to send email.", "danger")
    return redirect(url_for("home"))

@app.route("/preview/<candidate_id>/<template_id>")
@staff_required # All roles can preview documents
def preview(candidate_id, template_id):
    candidate = candidates_col.find_one({"_id": ObjectId(candidate_id)})
    template = templates_col.find_one({"_id": ObjectId(template_id)})

    if not candidate or not template:
        flash("Candidate or Template not found", "danger")
        return redirect(url_for("home"))
    
    html = f"""
    <html>
      <head><style>{inline_css()}</style></head>
      <body>
        <img src="data:image/png;base64,{load_base64_logo()}" alt="Logo" style="max-height:60px;"><br><br>
        {render_template_content(template["content"], candidate)}
      </body>
    </html>
    """
    return html

@app.route("/clear_candidates", methods=["POST"])
@admin_required # Only admins can clear all candidates
def clear_candidates():
    try:
        result = candidates_col.delete_many({})
        flash(f"✅ Successfully cleared {result.deleted_count} candidates.", "success")
    except Exception as e:
        flash(f"❌ Error clearing candidates: {str(e)}", "danger")
    return redirect(url_for("home"))

@app.route("/download_all/<candidate_id>")
@staff_required # Admins, HR, and Staff can download all docs for a candidate
def download_all(candidate_id):
    candidate = candidates_col.find_one({"_id": ObjectId(candidate_id)})
    if not candidate:
        flash("Candidate not found", "danger")
        return redirect(url_for("home"))

    mem = io.BytesIO()
    with zipfile.ZipFile(mem, "w", zipfile.ZIP_DEFLATED) as zf:
        for doc in candidate.get("documents", []):
            file_path = os.path.join(GENERATED_PDFS_FOLDER, doc["file_path"])
            if os.path.exists(file_path):
                zf.write(file_path, arcname=doc["file_path"])

    mem.seek(0)
    return send_file(
        mem,
        as_attachment=True,
        download_name=f"{candidate['name']}_documents.zip",
        mimetype="application/zip"
    )

@app.route("/download_all_candidates")
@admin_required # Only admins can download all docs for all candidates
def download_all_candidates():
    candidates = list(candidates_col.find())
    if not candidates:
        flash("No candidates found", "danger")
        return redirect(url_for("home"))

    mem = io.BytesIO()
    with zipfile.ZipFile(mem, "w", zipfile.ZIP_DEFLATED) as zf:
        for candidate in candidates:
            candidate_name = candidate.get("name", f"candidate_{candidate['_id']}")
            for doc in candidate.get("documents", []):
                file_path = os.path.join(GENERATED_PDFS_FOLDER, doc["file_path"])
                if os.path.exists(file_path):
                    zf.write(file_path, arcname=os.path.join(candidate_name, doc["file_path"]))

    mem.seek(0)
    return send_file(
        mem,
        as_attachment=True,
        download_name="all_candidates_documents.zip",
        mimetype="application/zip"
    )

# ---------------- RUN ---------------- #
if __name__ == "__main__":
    # Ensure default admin user exists with 'admin' role
    if not users_col.find_one({"username": "Admin"}):
        users_col.insert_one({
            "username": "Admin",
            "password": "Admin@123",
            "role": "admin"
        })
    app.run(debug=True)
