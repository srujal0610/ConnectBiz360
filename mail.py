import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Flask, render_template, request, redirect, url_for
app = Flask(__name__)


@app.route('/')
def front():
    return render_template('index.html')


@app.route('/graphhsy',methods=['GET','POST'])
def mail():

    smtp_port = 587
    smtp_server = "smtp.gmail.com"

    my_email = "vyomdummy123@gmail.com"
    to_email = "rishitlunia123@gmail.com"
    password = "kexndlggwymjmaoq"

    # Create a MIMEText object for the email content
    subject = "Subject: HAPPY BIRTHDAY"
    body = "HAPPPPPPYYYYYYYY BIRTHDAYYYYYYYYYYY!"
    message = MIMEMultipart()
    message["From"] = my_email
    message["To"] = to_email
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))

    simple_email_context = ssl.create_default_context()

    try:
        print("Connecting to server")
        connection = smtplib.SMTP(smtp_server, smtp_port)
        connection.starttls(context=simple_email_context)
        connection.login(my_email, password)
        print("Connected to server:- ")
        print()
        print(f"Sending mail to: {to_email}")
        connection.sendmail(my_email, to_email, message.as_string())
        print(f"Mail sent to: {to_email}")

    except Exception as e:
        print(e)

    finally:
        connection.close()

    return("Mail sent successfully")

if __name__ == '__main__':
    app.run(debug=True)
