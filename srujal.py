import logging
import os
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from flask import Flask, render_template, request
import mysql.connector

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def mail():
    return render_template('index.html')

@app.route('/mailhsy', methods=['POST'])
def mailhsy():
    compname = 'TCS'
    smtp_port = 587
    smtp_server = "smtp.gmail.com"
    my_email = "vyomdummy123@gmail.com"  # Replace with your email address
    password = "kexndlggwymjmaoq"  # Replace with your email password

    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="1234",
        database="vyom",
        auth_plugin='mysql_native_password'
    )
    cursor = conn.cursor()

    cursor.execute("SELECT email FROM compdata WHERE CompanyName = %s", (compname,))
    user = cursor.fetchone()

    if user is None:
        return "Recipient email not found in the database."

    to_email = user[0]

    # Ensure the 'uploads' directory exists
    uploads_dir = os.path.join(app.instance_path, 'uploads')
    os.makedirs(uploads_dir, exist_ok=True)

    attachment_path = None  # Initialize attachment path to None

    if 'attachment' in request.files:
        attachment = request.files['attachment']
        if attachment.filename != '':
            attachment_path = os.path.join(uploads_dir, attachment.filename)
            attachment.save(attachment_path)

    # Create a MIMEText object for the email content
    subject = request.form['Subject']

    # Predefined message with the corrected variable
    predefined_message = f"This company named {compname} wants to collaborate with you {to_email}."

    # Custom message from the sender
    custom_message = request.form.get('message')

    full_message = f"{predefined_message}\n\nCustom Message:\n{custom_message}"

    message = MIMEMultipart()
    message["From"] = my_email
    message["To"] = to_email
    message["Subject"] = subject
    message.attach(MIMEText(full_message, "plain"))

    # Attach the file if it exists
    if attachment_path:
        with open(attachment_path, "rb") as attachment_file:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment_file.read())
            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition",
                f"attachment; filename= {os.path.basename(attachment_path)}",
            )
            message.attach(part)

    simple_email_context = ssl.create_default_context()

    try:
        connection = smtplib.SMTP(smtp_server, smtp_port)
        connection.starttls(context=simple_email_context)
        connection.login(my_email, password)
        connection.sendmail(my_email, to_email, message.as_string())
    except Exception as e:
        return f"Error sending email: {str(e)}"
    finally:
        connection.quit()

    # If an attachment was added, remove the file
    if attachment_path and os.path.exists(attachment_path):
        os.remove(attachment_path)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
