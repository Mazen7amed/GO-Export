from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time
import requests
from bs4 import BeautifulSoup
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


def scrape_navigation_tabs(vin):
    """Scrape navigation tabs from mb.vin."""
    # Set up the WebDriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)

    url1 = ""
    url2 = ""

    try:
        # Open the website
        driver.get("https://mb.vin/")

        # Locate the VIN input field and enter the VIN
        vin_input = driver.find_element(By.CLASS_NAME, "form-control")
        vin_input.send_keys(vin)

        # Wait for 20 seconds for CAPTCHA to be solved manually
        print("Waiting for 15 seconds for CAPTCHA to be solved manually...")
        time.sleep(15)

        # Locate and click the submit button
        submit_button = driver.find_element(
            By.CSS_SELECTOR, "button.btn.btn-primary.btn-lg"
        )
        submit_button.click()

        # Wait for the results to load
        driver.implicitly_wait(10)

        # Find the navigation tabs container
        nav_tabs = driver.find_element(By.ID, "nav-tab")

        # Extract URLs and text from navigation tabs
        nav_links = nav_tabs.find_elements(By.CLASS_NAME, "nav-link")
        if len(nav_links) >= 2:
            url1 = nav_links[0].get_attribute("href")
            url2 = nav_links[1].get_attribute("href")

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        # Close the driver
        driver.quit()

    return url1, url2


def scrape_vehicle_info_and_options(vehicle_url, options_url, quotation_num):
    """Scrape vehicle information and options from the provided URLs and generate a multi-page PDF."""
    output_pdf = f"PDFS/{quotation_num}/vehicle_info.pdf"

    # Function to scrape vehicle information
    def scrape_vehicle_info(url):
        # Send a GET request to the URL
        response = requests.get(url)

        if response.status_code == 200:
            # Parse the HTML content
            soup = BeautifulSoup(response.content, 'html.parser')

            # Find the table element
            table = soup.find('div', class_='table-responsive').find('table')

            # Initialize a dictionary to store vehicle information
            vehicle_info = {
                "VIN": None,
                "Order": None,
                "Engine": None,
                "Transmission": None,
                "Color": None,
                "Upholstery": None,
                "Production": None,
                "Manufacturer": None,
                "Delivery Date": None
            }

            # Extract data from the table
            rows = table.find_all('tr')
            for row in rows:
                th = row.find('th')
                td = row.find('td')
                if th and td:
                    key = th.text.strip().rstrip(':')  # Remove trailing colon
                    if key in vehicle_info:
                        vehicle_info[key] = td.text.strip()

            return vehicle_info

        else:
            print(f"Failed to retrieve vehicle data. Status code: {response.status_code}")
            return None

    # Function to scrape options information
    def scrape_options_table(url):
        # Send a GET request to the URL
        response = requests.get(url)

        if response.status_code == 200:
            # Parse the HTML content
            soup = BeautifulSoup(response.content, 'html.parser')

            # Find the table element
            table = soup.find('div', class_='table-responsive').find('table')

            # Initialize a dictionary to store options
            options = {}

            # Extract data from the table
            rows = table.find_all('tr')
            for row in rows:
                # Find td elements
                tds = row.find_all('td')
                if len(tds) == 2:  # Ensure we have two columns (image and description)
                    description = tds[1].get_text(separator='\n').strip() if tds[1] else None
                    if description:
                        # Extract option code from the description
                        option_code = tds[1].find('b').get_text().strip() if tds[1].find('b') else None
                        if option_code:
                            options[option_code] = description

            options = {key: value.split('\n')[1] if '\n' in value else value for key, value in options.items()}
            return options

        else:
            print(f"Failed to retrieve options data. Status code: {response.status_code}")
            return None

    # Function to generate PDF
    def generate_pdf(vehicle_info, options, output_pdf):
        c = canvas.Canvas(output_pdf, pagesize=letter)
        c.setLineWidth(.3)
        c.setFont('Helvetica', 12)

        # Generate vehicle information page
        c.drawString(100, 750, "Vehicle Information:")
        y_position = 730
        for key, value in vehicle_info.items():
            if value:  # Check if value is not None or empty
                if y_position < 50:
                    c.showPage()
                    c.drawString(100, 750, "Vehicle Information (continued):")
                    y_position = 730
                y_position -= 20
                c.drawString(120, y_position, f"{key}: {value}")

        c.showPage()

        # Generate options page
        c.drawString(100, 750, "Options:")
        y_position = 730
        for key, value in options.items():
            if y_position < 50:
                c.showPage()
                c.drawString(100, 750, "Options (continued):")
                y_position = 730
            y_position -= 20
            c.drawString(120, y_position, f"{key}: {value}")

        c.save()

    # Scrape vehicle information
    vehicle_info = scrape_vehicle_info(vehicle_url)

    # Scrape options information
    options = scrape_options_table(options_url)

    # Generate PDF
    if vehicle_info and options:
        generate_pdf(vehicle_info, options, output_pdf)
    else:
        print("Failed to generate PDF. Check data retrieval.")
