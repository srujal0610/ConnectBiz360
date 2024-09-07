from flask import jsonify
import logging
import datetime
from flask import flash
import csv
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from flask import Flask, render_template, request, redirect, url_for
from bs4 import BeautifulSoup
import requests
import mysql.connector
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from flask import Flask, render_template, request, redirect, url_for
from bs4 import BeautifulSoup
import requests
import mysql.connector
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import csv
import datetime
import plotly.graph_objects as go
import pandas as pd
import os
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from flask import Flask, render_template, request, redirect, url_for
app = Flask(__name__)
app.secret_key = 'vyom1410'
# For simplicity, using dictionaries to store user and company data
users = {}
companies = {}
# CSV_FOLDER = "company_data"
# app.config["CSV_FOLDER"] = CSV_FOLDER

# # Initialize logging
# logging.basicConfig(filename='web_scraping.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


@app.route('/', methods=['GET', 'POST'])
def front():
    return render_template('Login.html')


@app.route('/return', methods=['GET', 'POST'])
def mainpage():

    return render_template('frontpage_v.html')


@app.route('/about', methods=['GET', 'POST'])
def about():
    return render_template('about.html')


def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="1234",
            database="vyom",
            auth_plugin='mysql_native_password'
        )
        if conn.is_connected():
            print("Connected to MySQL database")
            return conn
    except Exception as e:
        print(f"Error", e)


@app.route('/Login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()

        # Perform a query to check if the username and password exist in the database
        cursor.execute(
            "SELECT * FROM signup WHERE email = %s AND password = %s", (username, password))
        user = cursor.fetchone()

        if user:
            # User exists in the database, you can redirect to a success page or perform other actions
            return redirect(url_for('success'))
        else:
            # User does not exist or the password is incorrect
            return "Invalid username or password"

        conn.close()

    return render_template('Login.html')


@app.route('/signup', methods=['GET', 'POST'])
def register():
    message = ""
    if request.method == 'POST':
        companyName = request.form['companyName']
        domain = request.form['domain']
        description = request.form['description']
        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO signup (companyName, domain, description, email, password) VALUES (%s,%s, %s, %s, %s)",
                       (companyName, domain, description, email, password))
        conn.commit()
        conn.close()

        message = "Data inserted successfully!"

    return render_template('signUp.html', message=message)


@app.route('/logsin', methods=['GET', 'POST'])
def logsin():
    return render_template('signup.html')


@app.route('/signlog', methods=['GET', 'POST'])
def sinlog():
    return render_template('Login.html')


@app.route('/success')
def success():
    return render_template('frontpage_v.html')


def scrap(company):
    # Create a folder to store CSV files
    csv_folder = "company_data"
    if not os.path.exists(csv_folder):
        os.makedirs(csv_folder)

    # Calculate the current date
    current_date = datetime.datetime.now()
    # Calculate the period1 parameter for the URL
    # Subtract 365 days for one year
    period1 = int((current_date - datetime.timedelta(days=365)).timestamp())
    # Use the current date as period2 (today)
    period2 = int(current_date.timestamp())

    base_url = "https://finance.yahoo.com/quote/TSLA/history?period1={}&period2={}&interval=1d&filter=history&frequency=1d&includeAdjustedClose=true"
    try:
        # Create ChromeOptions and set headless mode
        chrome_options = Options()
        chrome_options.add_argument("--headless")

        # Set up the Chrome driver with the options
        driver = webdriver.Chrome(options=chrome_options)
        # Set up the Chrome driver (you need to have the Chrome driver executable in the same directory or in PATH)
        # driver = webdriver.Chrome()

        # Format the URL
        url = base_url.format(period1, period2).replace("TSLA", company)
        logging.info("Generated URL for one year of data: %s", url)
        logging.info("Opening the URL: %s", url)
        driver.get(url)

        driver.implicitly_wait(10)
        logging.info("Dynamic content loaded")

        # Get the page source after dynamic content is loaded
        page_source = driver.page_source

        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(page_source, 'html.parser')

        # Find the historical data table element
        table = soup.find('table', {'class': 'W(100%)'})

        # Extract table data
        table_data = []
        for row in table.find_all('tr'):

            # Check if the row contains a dividend entry, and set the flag to skip the next row
            if "Dividend" in row.get_text():
                continue
            if "dividend" in row.get_text():
                continue

            row_data = []
            for cell in row.find_all(['th', 'td']):
                row_data.append(cell.get_text(strip=True))
            if row_data:
                table_data.append(row_data)

        csv_file_path = os.path.join(csv_folder, f"{company}.csv")
        with open(csv_file_path, mode='w', newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            for row in table_data:
                csv_writer.writerow(row)

        logging.info(
            f"Data written to CSV file for {company}: {csv_file_path}")

        # Load the data from the CSV file
        with open(csv_file_path, mode='r', newline='') as csv_file:
            csv_reader = csv.reader(csv_file)
            data = list(csv_reader)

        # Reverse the order of rows (excluding the header if present)
        header = data[0]  # Store the header row
        data = data[1:]   # Exclude the header row
        data.reverse()    # Reverse the order of rows

        # Write the inverted data back to the same CSV file
        with open(csv_file_path, mode='w', newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            if header:
                csv_writer.writerow(header)  # Write the header row back
            csv_writer.writerows(data)

        logging.info(f"Data in the CSV file for {company} has been inverted.")

    except (TimeoutException, NoSuchElementException) as e:
        logging.error(f"An exception occurred for {company}: {str(e)}")

    finally:
        try:
            # Close the web driver
            driver.quit()
            logging.info("Web driver closed")
        except NameError:
            pass


@app.route('/commonmail', methods=['GET', 'POST'])
def commonmail(companyname):
    compname = companyname
    smtp_port = 587
    smtp_server = "smtp.gmail.com"
    my_email = "connectbiz360@gmail.com"  # Replace with your email address
    password = "lyzpcczoqkeansss"  # Replace with your email password

    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="1234",
        database="vyom",
        auth_plugin='mysql_native_password'
    )
    cursor = conn.cursor()
    cursor.execute(
        "SELECT email FROM compdata WHERE CompanyName = %s", (compname,))
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
    predefined_message = f"Greetings from ConnectBiz360 a company wants to collaborate with you."

    # Custom message from the sender
    custom_message = request.form.get('message')

    full_message = f"{predefined_message}\n\n{custom_message}"

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

    return render_template('frontpage_v.html')


# ***********************BACKEND FOR HSY*******************************
@app.route('/graphhsy', methods=['GET', 'POST'])
def graphhsy():
    scrap('HSY')
    df = pd.read_csv("company_data/HSY.csv")

    # Create a Plotly figure
    fig = go.Figure()

    # Add line chart trace
    fig.add_trace(go.Scatter(x=df['Date'], y=df['Close*'],
                  mode='lines', name='Line Chart', line=dict(color='red')))

    # Add bar graph trace
    fig.add_trace(go.Scatter(x=df['Date'], y=df['Close*'],
                  mode='markers', name='Bar Graph', marker=dict(color='blue')))

    # Update the layout
    fig.update_xaxes(title_text='Date')
    fig.update_yaxes(title_text='Closing Value')

    # Update the main layout (optional)
    fig.update_layout(
        title_text="Stock Trends - HERSHEYS",
        showlegend=True,  # Display the legend
    )

    # Show the figure
    fig.show()

    return render_template('frontpage_v.html')


@app.route("/volhsy", methods=['GET', 'POST'])
def volhsy():
    scrap('HSY')
    df = pd.read_csv("company_data/HSY.csv")
    print("loaded")
    fig = go.Figure(data=[go.Candlestick(x=df['Date'],
                                         open=df['Open'],
                                         high=df['High'],
                                         low=df['Low'],
                                         close=df['Close*'])])

    fig.update_xaxes(title_text='Date')
    fig.update_yaxes(title_text='Volume Range')
    fig.update_layout(
        title_text="Volume Trends - HERSHEYS",
        showlegend=True,  # Display the legend
    )
    fig.show()

    return render_template('frontpage_v.html')


@app.route('/mail', methods=['GET', 'POST'])
def mail():
    return render_template('index.html')


@app.route('/b1', methods=['GET', 'POST'])
def hsyb():
    # button_name = request.args.get('button', 'Connect')  # Get the button name from the URL parameter
    action_url = url_for('mailhsy')
    return render_template('index.html', action_url=action_url)


@app.route('/mailhsy', methods=['POST'])
def mailhsy():
    commonmail('HSY')  # rishit
    return render_template('frontpage_v.html')


# BACKEND FOR NVDA
@app.route('/graphnvda', methods=['GET', 'POST'])
def graphnvda():
    # Load your dataset
    scrap('NVDA')
    df = pd.read_csv("company_data/NVDA.csv")

    # Create a Plotly figure
    fig = go.Figure()

    # Add line chart trace
    fig.add_trace(go.Scatter(x=df['Date'], y=df['Close*'],
                  mode='lines', name='Line Chart', line=dict(color='red')))

    # Add bar graph trace
    fig.add_trace(go.Scatter(x=df['Date'], y=df['Close*'],
                  mode='markers', name='Bar Graph', marker=dict(color='blue')))

    # Update the layout
    fig.update_xaxes(title_text='Date')
    fig.update_yaxes(title_text='Closing Value')

    # Update the main layout (optional)
    fig.update_layout(
        title_text="Stock Trends - NVDIA",
        showlegend=True,  # Display the legend
    )

    # Show the figure
    fig.show()

    return render_template('frontpage_v.html')


@app.route("/volnvda", methods=['GET', 'POST'])
def volnvda():
    scrap('NVDA')
    df = pd.read_csv("company_data/NVDA.csv")
    print("loaded")
    fig = go.Figure(data=[go.Candlestick(x=df['Date'],
                                         open=df['Open'],
                                         high=df['High'],
                                         low=df['Low'],
                                         close=df['Close*'])])

    fig.update_xaxes(title_text='Date')
    fig.update_yaxes(title_text='Volume Range')
    fig.update_layout(
        title_text="Volume Trends - NVIDIA",
        showlegend=True,  # Display the legend
    )
    fig.show()

    return render_template('frontpage_v.html')


@app.route('/b2', methods=['GET', 'POST'])
def nvdab():
    # button_name = request.args.get('button', 'Connect')  # Get the button name from the URL parameter
    action_url = url_for('mailnvda')
    return render_template('index.html', action_url=action_url)


@app.route('/mailnvda', methods=['POST'])
def mailnvda():
    commonmail('NVDA')  # rishit
    return render_template('frontpage_v.html')


# BACKEND FOR JPM


@app.route('/graphjpm', methods=['GET', 'POST'])
def graphjpm():
    # Load your dataset
    scrap('JPM')
    df = pd.read_csv("company_data/JPM.csv")

    # Create a Plotly figure
    fig = go.Figure()

    # Add line chart trace
    fig.add_trace(go.Scatter(x=df['Date'], y=df['Close*'],
                  mode='lines', name='Line Chart', line=dict(color='red')))

    # Add bar graph trace
    fig.add_trace(go.Scatter(x=df['Date'], y=df['Close*'],
                  mode='markers', name='Bar Graph', marker=dict(color='blue')))

    # Update the layout
    fig.update_xaxes(title_text='Date')
    fig.update_yaxes(title_text='Closing Value')

    # Update the main layout (optional)
    fig.update_layout(
        title_text="Stock Trends - JP MORGAN",
        showlegend=True,  # Display the legend
    )

    # Show the figure
    fig.show()

    return render_template('frontpage_v.html')


@app.route("/voljpm", methods=['GET', 'POST'])
def voljpm():
    scrap('JPM')
    df = pd.read_csv("company_data/JPM.csv")
    print("loaded")
    fig = go.Figure(data=[go.Candlestick(x=df['Date'],
                                         open=df['Open'],
                                         high=df['High'],
                                         low=df['Low'],
                                         close=df['Close*'])])

    fig.update_xaxes(title_text='Date')
    fig.update_yaxes(title_text='Volume Range')
    fig.update_layout(
        title_text="Volume Trends - JP MORGAN",
        showlegend=True,  # Display the legend
    )
    fig.show()

    return render_template('frontpage_v.html')


@app.route('/b3', methods=['GET', 'POST'])
def jpmb():
    # button_name = request.args.get('button', 'Connect')  # Get the button name from the URL parameter
    action_url = url_for('mailjpm')
    return render_template('index.html', action_url=action_url)


@app.route('/mailjpm', methods=['POST'])
def mailjpm():
    commonmail('JPM')  # rishit
    return render_template('frontpage_v.html')


# BACKEND FOR RVPH
@app.route('/graphrvph', methods=['GET', 'POST'])
def graphrvph():
    # Load your dataset
    scrap('RVPH')
    df = pd.read_csv("company_data/RVPH.csv")

    # Create a Plotly figure
    fig = go.Figure()

    # Add line chart trace
    fig.add_trace(go.Scatter(x=df['Date'], y=df['Close*'],
                  mode='lines', name='Line Chart', line=dict(color='red')))

    # Add bar graph trace
    fig.add_trace(go.Scatter(x=df['Date'], y=df['Close*'],
                  mode='markers', name='Bar Graph', marker=dict(color='blue')))

    # Update the layout
    fig.update_xaxes(title_text='Date')
    fig.update_yaxes(title_text='Closing Value')

    # Update the main layout (optional)
    fig.update_layout(
        title_text="Stock Trends - REVIVA PHARMA",
        showlegend=True,  # Display the legend
    )

    # Show the figure
    fig.show()

    return render_template('frontpage_v.html')


@app.route("/volrvph", methods=['GET', 'POST'])
def volrvph():
    scrap('RVPH')
    df = pd.read_csv("company_data/RVPH.csv")
    print("loaded")
    fig = go.Figure(data=[go.Candlestick(x=df['Date'],
                                         open=df['Open'],
                                         high=df['High'],
                                         low=df['Low'],
                                         close=df['Close*'])])

    fig.update_xaxes(title_text='Date')
    fig.update_yaxes(title_text='Volume Range')
    fig.update_layout(
        title_text="Volume Trends - REVIVA PHARMA",
        showlegend=True,  # Display the legend
    )
    fig.show()

    return render_template('frontpage_v.html')


@app.route('/b4', methods=['GET', 'POST'])
def rvphb():
    # button_name = request.args.get('button', 'Connect')  # Get the button name from the URL parameter
    action_url = url_for('mailrvph')
    return render_template('index.html', action_url=action_url)


@app.route('/mailrvph', methods=['POST'])
def mailrvph():
    commonmail('RVH')  # rishit
    return render_template('frontpage_v.html')


# BACKEND FOR HYMTF
@app.route('/graphhymtf', methods=['GET', 'POST'])
def graphhymtf():
    # Load your dataset
    scrap('HYMTF')
    df = pd.read_csv("company_data/HYMTF.csv")

    # Create a Plotly figure
    fig = go.Figure()

    # Add line chart trace
    fig.add_trace(go.Scatter(x=df['Date'], y=df['Close*'],
                  mode='lines', name='Line Chart', line=dict(color='red')))

    # Add bar graph trace
    fig.add_trace(go.Scatter(x=df['Date'], y=df['Close*'],
                  mode='markers', name='Bar Graph', marker=dict(color='blue')))

    # Update the layout
    fig.update_xaxes(title_text='Date')
    fig.update_yaxes(title_text='Closing Value')

    # Update the main layout (optional)
    fig.update_layout(
        title_text="Stock Trends - HYUNDAI MOTOR",
        showlegend=True,  # Display the legend
    )

    # Show the figure
    fig.show()

    return render_template('frontpage_v.html')


@app.route("/volhymtf", methods=['GET', 'POST'])
def volhymtf():
    scrap('HYMTF')
    df = pd.read_csv("company_data/HYMTF.csv")
    print("loaded")
    fig = go.Figure(data=[go.Candlestick(x=df['Date'],
                                         open=df['Open'],
                                         high=df['High'],
                                         low=df['Low'],
                                         close=df['Close*'])])

    fig.update_xaxes(title_text='Date')
    fig.update_yaxes(title_text='Volume Range')
    fig.update_layout(
        title_text="Volume Trends - HYUNDAI",
        showlegend=True,  # Display the legend
    )
    fig.show()

    return render_template('frontpage_v.html')


@app.route('/b5', methods=['GET', 'POST'])
def hynb():
    # button_name = request.args.get('button', 'Connect')  # Get the button name from the URL parameter
    action_url = url_for('mailhyn')
    return render_template('index.html', action_url=action_url)


@app.route('/mailhyn', methods=['POST'])
def mailhyn():
    commonmail('HYN')  # rishit
    return render_template('frontpage_v.html')


# BACKEND FOR SHELL
@app.route('/graphshell', methods=['GET', 'POST'])
def graphshell():
    # Load your dataset
    scrap('SHEL')
    df = pd.read_csv("company_data/SHEL.csv")

    # Create a Plotly figure
    fig = go.Figure()

    # Add line chart trace
    fig.add_trace(go.Scatter(x=df['Date'], y=df['Close*'],
                  mode='lines', name='Line Chart', line=dict(color='red')))

    # Add bar graph trace
    fig.add_trace(go.Scatter(x=df['Date'], y=df['Close*'],
                  mode='markers', name='Bar Graph', marker=dict(color='blue')))

    # Update the layout
    fig.update_xaxes(title_text='Date')
    fig.update_yaxes(title_text='Closing Value')

    # Update the main layout (optional)
    fig.update_layout(
        title_text="Stock Trends - SHELL",
        showlegend=True,  # Display the legend
    )

    # Show the figure
    fig.show()

    return render_template('frontpage_v.html')


@app.route("/volshell", methods=['GET', 'POST'])
def volshell():
    scrap('SHEL')
    df = pd.read_csv("company_data/SHEL.csv")
    print("loaded")
    fig = go.Figure(data=[go.Candlestick(x=df['Date'],
                                         open=df['Open'],
                                         high=df['High'],
                                         low=df['Low'],
                                         close=df['Close*'])])

    fig.update_xaxes(title_text='Date')
    fig.update_yaxes(title_text='Volume Range')
    fig.update_layout(
        title_text="Volume Trends - SHELL",
        showlegend=True,  # Display the legend
    )
    fig.show()

    return render_template('frontpage_v.html')


@app.route('/b6', methods=['GET', 'POST'])
def shelb():
    # button_name = request.args.get('button', 'Connect')  # Get the button name from the URL parameter
    action_url = url_for('mailshel')
    return render_template('index.html', action_url=action_url)


@app.route('/mailshel', methods=['POST'])
def mailshel():
    commonmail('SHELL')  # rishit
    return render_template('frontpage_v.html')


@app.route('/contact')
def index():
    return render_template('contact.html')


@app.route('/submit', methods=['POST'])
def submit_form():
    company_name = request.form.get('companyName')
    phone_number = request.form.get('phoneNumber')
    gst_number = request.form.get('gstNumber')
    registration_number = request.form.get('registrationNumber')

    with open('contact_details.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([company_name, phone_number,
                        gst_number, registration_number])

    response_data = {'message': 'Details submitted successfully'}
    return jsonify(response_data)
    # flash('Details submitted successfully', 'success')
    return redirect(url_for('index'))


# Create a route to log out and delete all CSV files
@app.route('/logout', methods=['GET'])
def logout():
    CSV_FOLDER = "company_data"
    app.config["CSV_FOLDER"] = CSV_FOLDER
    # Delete all CSV files in the folder
    for filename in os.listdir(app.config["CSV_FOLDER"]):
        file_path = os.path.join(app.config["CSV_FOLDER"], filename)
        print(file_path)
        try:
            if os.path.isfile(file_path):
                logging.info("file deleted")  # Corrected to lowercase "info"
                print("file deleted")
                os.unlink(file_path)
        except Exception as e:
            logging.error(
                "An exception occurred while deleting files: %s", str(e))

    # Redirect back to the main page
    return render_template('Login.html')


if __name__ == '__main__':
    app.run(debug=True)
