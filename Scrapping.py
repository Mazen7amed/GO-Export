from helper import domain_detector
from scraper.suchen_mobile_de import SuchenMobileDe
from readScrapy import run_spider, get_scraped_data


#{purchaser_name, purchaser_email, purchaser_phone, Gender, quotation_num, ad_link, Eur1, car_date, destination_city, Index}

def scrap_Car_Data(url):
    message = ""
    api_data = None

    if url:
        domain = domain_detector(url)
        if domain == "SuchenMobileDe":
            mobile_de_scraper = SuchenMobileDe(url)
            api_data = mobile_de_scraper.scrape_data()
        else:
            run_spider(url)
            api_data = get_scraped_data()

        if not api_data:
            message = f"Error: No data retrieved."
    else:
        message = "Error: Please provide a valid URL."
    return api_data, message
