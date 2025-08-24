# 📄 DocGen-Mongo

## 🚀 Project Overview
**DocGen-Mongo** is a system to automate the generation of **offer letters, appointment letters, experience letters, and certificates**.  
It uses **MongoDB** to store templates, audit logs, and metadata of generated documents, ensuring a seamless and secure document management workflow.  

This project is part of the **AICTE Internship – Learnzo Python with Django Full Stack Web Development** assignment.  

---

## 🎯 Core Features
- 📑 **Template Management** → Store templates with placeholders (e.g., `{{name}}`, `{{date}}`) in MongoDB.  
- 👥 **Single & Bulk Generation** → Upload CSV/Excel and generate multiple documents at once.  
- 👀 **Preview before Download** → Check formatting before exporting.  
- 📂 **Export Options** → Download documents in **PDF/DOCX** format.  
- 🛡 **Role-Based Access** → Admin / HR / Staff login with different privileges.  
- 📜 **Audit Trail** → Tracks who generated what and when.  
- 📧 **Email Integration (Optional)** → Send documents directly via email using Brevo API.  

---

## 📂 Project Structure

```bash
DocGen-Mongo/  
│   .env  
│   app.py  
│   requirements.txt  
│   reset_admin.py  
│
├───generated_pdfs/  
├───static/  
│       style.css  
│
├───templates/  
│       alerts.html  
│       Appointment Letter.html  
│       bulk_upload.html  
│       certificate_template.html  
│       create_user.html  
│       edit_template.html  
│       Experience Letter.html  
│       home.html  
│       login.html  
│       navbar.html  
│       Offer Letter.html  
│       offer_letter.html  
│       preview.html  
│       templates.html  
│
├───uploads/  
│       Bulk_upload_test.csv  
│
└───__pycache__/  
        config.cpython-313.pyc  
        forms.cpython-313.pyc  
        models.cpython-313.pyc  

---

##⚡ Installation & Setup
# 1️⃣ Clone the Repository
```bash
git clone https://github.com/your-username/DocGen-Mongo.git
cd DocGen-Mongo

# 2️⃣ Install Requirements
```bash
pip install -r requirements.txt

# 3️⃣ Set Up MongoDB
```bash
# Install & run MongoDB locally OR use MongoDB Atlas
# Create a .env file in the project root and add:
MONGO_URI=mongodb://localhost:27017/docgen
BREVO_API_KEY=your_api_key_here
SENDER_NAME=Prompt Lord
SENDER_EMAIL=sabarish.edu2024@gmail.com

# 4️⃣ Run the App
```bash
python app.py
# 👉 App will be available at: http://127.0.0.1:5000/

# 5️⃣ Reset Admin (if needed)
```bash
python reset_admin.py
# Default Admin → username: Admin | password: Admin@123
# ⚠️ Change the password after first login for security

---

## ​​​ Author & Contact
- **Author:** Sabarish R  
- 📧 **Email:** [sabarish.edu2024@gmail.com](mailto:sabarish.edu2024@gmail.com)  
- 🔗 **LinkedIn:** [linkedin.com/in/sabarishr08](https://www.linkedin.com/in/sabarishr08/)  
