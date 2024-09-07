# pip install selenium
# pip install bs4

import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import csv
import datetime
# from selenium.webdriver.common.by import By


logging.basicConfig(filename='web_scraping.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
# logging.info("Name: Ronit Shah, Roll_no: 21BCP321")
try:
    # Create ChromeOptions and set headless mode
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    
    # Set up the Chrome driver with the options
    driver = webdriver.Chrome(options=chrome_options)
    # Set up the Chrome driver (you need to have the Chrome driver executable in the same directory or in PATH)
    # driver = webdriver.Chrome()
    base_url = "https://finance.yahoo.com/quote/TSLA/history?period1={}&period2={}&interval=1d&filter=history&frequency=1d&includeAdjustedClose=true"

    # Calculate the current date
    current_date = datetime.datetime.now()

    # Calculate the period1 parameter for the URL
    period1 = int((current_date - datetime.timedelta(days=365)).timestamp())  # Subtract 365 days for one year

    # Use the current date as period2 (today)
    period2 = int(current_date.timestamp())

    # Format the URL
    url = base_url.format(period1, period2)
    logging.info("Generated URL for one year of data: %s", url)
    
    # url = "https://finance.yahoo.com/quote/TSLA/history?period1=1664955538&period2=1696491538&interval=1d&filter=history&frequency=1d&includeAdjustedClose=true"
    # url = "https://finance.yahoo.com/quote/HSY/history?period1=1665339865&period2=1696875865&interval=1d&filter=history&frequency=1d&includeAdjustedClose=true"
    # url = "https://finance.yahoo.com/quote/JPM/history?period1=1664958115&period2=1696494115&interval=1d&filter=history&frequency=1d&includeAdjustedClose=true"
    # url = "https://finance.yahoo.com/quote/NVDA/history?period1=1664958502&period2=1696494502&interval=1d&filter=history&frequency=1d&includeAdjustedClose=true"
    # url = "https://finance.yahoo.com/quote/RVPH/history?period1=1664958749&period2=1696494749&interval=1d&filter=history&frequency=1d&includeAdjustedClose=true"
    # url = "https://finance.yahoo.com/quote/HYMTF/history?period1=1664958894&period2=1696494894&interval=1d&filter=history&frequency=1d&includeAdjustedClose=true"
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
    

    csv_file_path = "HSY1.csv"
    with open(csv_file_path, mode='w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        for row in table_data:
            csv_writer.writerow(row)

    logging.info("Data written to CSV file: %s", csv_file_path)

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

    logging.info("Data in the CSV file has been inverted.")


except ( TimeoutException, NoSuchElementException) as e:
    logging.error("An exception occurred: %s", str(e))
    
finally:
    try:
        # Close the web driver
        driver.quit()
        logging.info("Web driver closed")
    except NameError:
        pass