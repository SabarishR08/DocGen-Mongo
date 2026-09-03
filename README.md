# DocGen Mongo

![License](https://img.shields.io/badge/license-MIT-green) ![Language](https://img.shields.io/badge/language-Python-informational)


## 📌 Overview

DocGen-Mongo is a Flask + MongoDB powered automation system for generating professional HR documents such as offer, appointment, and experience letters, along with certificates. It supports reusable templates, bulk CSV/Excel uploads, role-based access, audit logging, email integration, and PDF/DOCX export.

## 🏗️ Architecture

```text
Browser / UI
     │   HTTP
     ▼
Flask app
```

## 🧰 Tech Stack

- **Language:** Python
- **Backend:** Flask

## 🚀 Getting Started

### Prerequisites

- Python 3.10+

### 1. Clone

```bash
git clone https://github.com/SabarishR08/DocGen-Mongo.git
cd DocGen-Mongo
```

### 2. Install dependencies

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 4. Run

```bash
python app.py
```


---

An automated system for generating professional documents using MongoDB.

DocGen-Mongo streamlines the creation of offer letters, appointment letters, experience letters, and certificates. Templates, audit logs, and metadata are stored in MongoDB for a secure, auditable workflow.

## 🎯 Core features

- **Template management:** Store customizable templates with placeholders (e.g. `{{name}}`, `{{date}}`).
- **Single & bulk generation:** Generate individual documents or upload a CSV/Excel file to create many documents at once.
- **Preview before export:** Review generated documents before downloading.
- **Export options:** Download documents as PDF or DOCX.
- **Role-based access control:** Admin, HR, and Staff roles with distinct privileges.
- **Comprehensive audit trail:** Tracks who generated a document and when.
- **Email integration (optional):** Send documents via the Brevo API.

## 📂 Project structure

```
DocGen-Mongo/
│  .env
│  app.py
│  requirements.txt
│  reset_admin.py
│
├── generated_pdfs/
├── static/
│   └── style.css
│
├── templates/
│   ├── alerts.html
│   ├── Appointment Letter.html
│   ├── bulk_upload.html
│   ├── certificate_template.html
│   ├── create_user.html
│   ├── edit_template.html
│   ├── Experience Letter.html
│   ├── home.html
│   ├── login.html
│   ├── navbar.html
│   ├── Offer Letter.html
│   ├── offer_letter.html
│   ├── preview.html
│   └── templates.html
│
└── uploads/
    └── Bulk_upload_test.csv

__pycache__/
```

## ⚡ Installation & setup

Follow these steps to run the project locally.

### 1. Clone the repository

```
git clone https://github.com/SabarishR08/DocGen-Mongo.git
cd DocGen-Mongo
```

### 2. Install requirements

```
pip install -r requirements.txt
```

### 3. Set up MongoDB

You can run MongoDB locally or use MongoDB Atlas (cloud-based). Create a `.env` file in the project root with these variables:

```
MONGO_URI=mongodb://localhost:27017/docgen
BREVO_API_KEY=your_api_key_here
SENDER_NAME="Prompt Lord"
SENDER_EMAIL=sabarish.edu2024@gmail.com
```

Note: ensure the database name `docgen` exists or MongoDB will auto-create it when the app first runs.

### 4. Run the application

```
python app.py
```

The app will be available at `http://127.0.0.1:5000/`.

### 5. Reset admin (optional)

To reset the default admin account, run:

```
python reset_admin.py
```

Default Login:

- **Username:** `Admin`
- **Password:** `Admin@123`

⚠️ Important: change the default password after first login.

## 👨‍💻 Author & contact

This project was developed as part of the AICTE Internship – Python Full Stack Development.

- **Author:** Sabarish R
- **Email:** `sabarish.edu2024@gmail.com`
- **LinkedIn:** https://www.linkedin.com/in/sabarishr08/

---

## 📄 License

[MIT](LICENSE) — © 2026 Sabarish R.
