# **DocGen-Mongo**

An automated system for generating professional documents with MongoDB.

DocGen-Mongo is a robust solution designed to streamline the generation of **offer letters, appointment letters, experience letters, and certificates**. Leveraging MongoDB for secure storage of templates, audit logs, and metadata, this project ensures a seamless and efficient document management workflow.

## **🎯 Core Features**

* Template Management  
  Store customizable templates with placeholders (e.g., {{name}}, {{date}}) directly in MongoDB.  
* Single & Bulk Generation  
  Generate individual documents or upload a CSV/Excel file to generate multiple documents at once.  
* Preview before Download  
  Review and confirm document formatting before exporting.  
* Export Options  
  Easily download generated documents in popular formats such as PDF/DOCX.  
* Role-Based Access Control  
  Secure the application with distinct privileges for Admin, HR, and Staff users.  
* Comprehensive Audit Trail  
  Automatically tracks document generation details, including who generated a document and when.  
* Email Integration (Optional)  
  Directly send documents via email using the Brevo API.

## **📂 Project Structure**

DocGen-Mongo/  
│   .env  
│   app.py  
│   requirements.txt  
│   reset\_admin.py  
│  
├───generated\_pdfs/  
├───static/  
│   └───style.css  
│  
├───templates/  
│   ├───alerts.html  
│   ├───Appointment Letter.html  
│   ├───bulk\_upload.html  
│   ├───certificate\_template.html  
│   ├───create\_user.html  
│   ├───edit\_template.html  
│   ├───Experience Letter.html  
│   ├───home.html  
│   ├───login.html  
│   ├───navbar.html  
│   ├───Offer Letter.html  
│   ├───offer\_letter.html  
│   ├───preview.html  
│   └───templates.html  
│  
├───uploads/  
│   └───Bulk\_upload\_test.csv  
│  
└───\_\_pycache\_\_/

## **⚡ Installation & Setup**

Follow these steps to get the project up and running on your local machine.

### **1️⃣ Clone the Repository**

git clone \[https://github.com/your-username/DocGen-Mongo.git\](https://github.com/your-username/DocGen-Mongo.git)  
cd DocGen-Mongo

### **2️⃣ Install Requirements**

pip install \-r requirements.txt

### **3️⃣ Set Up MongoDB**

You can either install and run MongoDB locally or use a cloud service like MongoDB Atlas. Once your MongoDB instance is running, create a .env file in the project root and add your configuration details.

MONGO\_URI=mongodb://localhost:27017/docgen  
BREVO\_API\_KEY=your\_api\_key\_here  
SENDER\_NAME=Prompt Lord  
SENDER\_EMAIL=sabarish.edu2024@gmail.com

### **4️⃣ Run the Application**

python app.py

The application will be available at: http://127.0.0.1:5000/

### **5️⃣ Reset Admin (if needed)**

To reset the default admin account, you can run the following command:

python reset\_admin.py

The default credentials will be:

* **Username:** Admin  
* **Password:** Admin@123

⚠️ **Important:** For security, please change the password immediately after your first login.

## **👨‍💻 Author & Contact**

This project was developed as part of the **AICTE Internship – Learnzo Python with Django Full Stack Web Development** assignment.

* **Author:** Sabarish R  
* **Email:** sabarish.edu2024@gmail.com  
* **LinkedIn:** [linkedin.com/in/sabarishr08](https://www.linkedin.com/in/sabarishr08/)