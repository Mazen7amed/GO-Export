from helper import domain_detector
from scraper.suchen_mobile_de import SuchenMobileDe
from Data.ModulesBackup.use_manual_scrapper import car_images, run_spider, get_scraped_data
import pandas as pd
import numpy as np


def scrap_Car_Data(file, use_manual):
    message = ""
    # Process the file if it exists and use_manual is False
    if file and not use_manual:
        df = pd.read_excel(file)
        df = df.replace(np.nan, "Not Provided")
        excel_data = df.to_dict(orient="records").pop()
        url = excel_data.get("ad_link")

        if excel_data.get("ad_link"):
            url = excel_data.get("ad_link")
            domain = domain_detector(url)

            if domain == "SuchenMobileDe":
                mobile_de_scraper = SuchenMobileDe(url)
                api_data = mobile_de_scraper.scrape_data()
            else:
                run_spider(url)
                api_data = get_scraped_data()
            message = ""

        else:
            api_data = None
            excel_data = None
            message = "Error In Retrieving Car Link. Please Check The Uploaded Excel File."



    # Process the file if use_manual is True
    elif file and use_manual:
        df = pd.read_excel(file)
        df = df.replace(np.nan, "Not Provided")
        if len(df.columns) != 19:
            message = "Error In Retrieving Manual Data. Please Check The Uploaded Excel File."
            api_data = None
            excel_data = None
        else:
            excel_data = {
                "purchaser_name": df["purchaser_name"][0],
                "Index": df["Index"][0],
                "quotation_num": df["quotation_num"][0],
                "Gender": df["Gender"][0],
                "gender_title": "Mr." if df["Gender"][0] == "Male" else "Ms.",
                "purchaser_phone": df["purchaser_phone"][0],
                "purchaser_email": df["purchaser_email"][0],
                "Customs_option": df["Customs_option"][0],
                "Egyptian_Customs": df["Egyptian_Customs"][0],
                "destination_city": df["destination_city"][0],
            }

            car_specifications = {
                key: value for key, value in
                zip(df["car_specifications_key"].values.tolist(), df["car_specifications_value"].values.tolist())
            }

            api_data = {
                "car_title": f"{car_specifications.get('Manufacturer Brand')} {car_specifications.get('Model')}",
                "manufacturer_brand": car_specifications.get("Manufacturer Brand"),
                "model": car_specifications.get("Model"),
                "EngineSize": df["EngineSize"][0],
                "car_features": df["car_features"].values.tolist(),
                "car_images": car_images(car_specifications.get("Manufacturer Brand"), car_specifications.get("Model"),
                                         car_specifications.get("Color")),
                "car_price": df["car_price"][0],
                "mileage": car_specifications.get("Mileage"),
                "fuel": car_specifications.get("Fuel"),
                "transmission": car_specifications.get("Transmission"),
                "power": car_specifications.get("Power"),
                "color": car_specifications.get("Color"),
                "firstregistration": car_specifications.get("First Registration"),
            }
    return api_data, excel_data, message
