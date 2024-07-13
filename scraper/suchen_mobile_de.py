from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException

import time
import re


class SuchenMobileDe:
    def __init__(self, url):  # , img_idx
        self.url = url
        # self.img_idx = img_idx
        self.driver = None

    def setup_webdriver(self):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--enable-logging")
        chrome_options.add_argument("--v=1")
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), options=chrome_options
        )

        self.driver.get(self.url)
        self.wait = WebDriverWait(self.driver, 10)

    def click_element_using_javascript(self, XPATH):
        try:
            element = self.wait.until(EC.presence_of_element_located((By.XPATH, XPATH)))
            self.driver.execute_script("arguments[0].click();", element)
        except TimeoutException:
            raise Exception("None of the provided XPaths found an element to click.")

    def extract_number(self, string):
        # Remove any characters that are not digits or a decimal point
        cleaned_string = re.sub(r"[^\d,]", "", string)

        # Convert to int
        cleaned_string = cleaned_string.replace(".", "").replace(",", ".")
        return int(float(cleaned_string))

    def scrape_data(self):
        self.setup_webdriver()
        try:
            # Click the second 'Show all' button
            self.click_element_using_javascript('(//*[@class="link__39Zm5"])[2]')

            # Wait for any dynamic content to load
            time.sleep(2)

            ###############################################################################################################

            # Now that both 'Show all' buttons have been clicked, proceed with scraping

            # Get HTML Script
            try:
                script_element = self.wait.until(
                    EC.presence_of_element_located((By.XPATH, "/html/body/script[2]"))
                )

                HTML_text = script_element.get_attribute("innerHTML")

                keys = [
                    "make",
                    "model",
                    "price",
                    "mileage",
                    "cubicCapacity",
                    "power",
                    "fuel",
                    "transmission",
                    "firstRegistration",
                    "color",
                    "category",
                ]

                data = {}

                for key in keys:
                    match = re.search(r'{}: "(.*?)"'.format(key), HTML_text)
                    if not match:
                        match = re.search(r'"{}": "(.*?)"'.format(key), HTML_text)
                    if match:
                        data[key] = match.group(1)
                    else:
                        data[key] = None

            except TimeoutException:
                print("********** HTML Script Not Found ************")
                return None

            ###############################################################################################################

            # Extract data from the script

            car_title = f"{data['make']} {data['model']}"
            EngineSize = data["cubicCapacity"]

            Car_Shape = data["category"]

            feature_elements = self.driver.find_elements(By.XPATH, '//*[@class="bullet-list"]//p')
            car_features = [feature.text for feature in feature_elements]

            images_index = HTML_text.find("images: [")
            images_index += len("images: [")
            images_end_index = HTML_text.find("]", images_index)
            images_content = HTML_text[images_index:images_end_index]
            urls_strings = re.findall(r'"uri": "([^"]+)"', images_content)

            image_elements = []
            for url in urls_strings:
                url = url.replace("\\", "")
                url = "https://" + url + "?rule=mo-1024.jpg"
                image_elements.append(url)

            car_price = self.extract_number(data["price"].split(" ")[0])
            mileage = data["mileage"] or "0 km"
            fuel = data["fuel"]
            transmission = data["transmission"] or "Automatic"
            power = data["power"]
            color = data["color"]
            firstregistration = data["firstRegistration"].split("/")[-1] if data["firstRegistration"] else None

            return {
                "car_title": car_title,
                "manufacturer_brand": data["make"],
                "model": data["model"],
                "EngineSize": EngineSize,
                "car_features": car_features,
                "car_images": image_elements,
                "car_price": car_price,
                "mileage": mileage,
                "fuel": fuel,
                "transmission": transmission,
                "power": power,
                "color": color,
                "firstregistration": firstregistration,
                "Car_Shape": Car_Shape,
            }
        except Exception as e:
            print(f"An error occurred: {e}")
            return None
        finally:
            self.driver.quit()
