import requests
import random
from bs4 import BeautifulSoup
from readScrapy import run_spider, get_scraped_data, SaveDataPipeline


def car_images(manufacturer_brand, model, color):
    # Construct the URL based on the provided parameters

    manufacturer_brand = manufacturer_brand.lower().replace(" ", "-")
    model = model.lower().replace(" ", "-")
    color = color.lower().replace(" ", "-")

    url = f"https://www.autoscout24.de/lst/{manufacturer_brand}/{model}/bc_{color}?atype=C&cy=D&damaged_listing=exclude&desc=0&ocs_listing=include&powertype=kw&search_id=mbb2mv9nca&sort=standard&source=detailsearch"

    try:
        # Fetch the webpage
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.text
    except requests.RequestException as e:
        print(f"Error fetching the webpage: {e}")
        return []

    # Parse the webpage content
    soup = BeautifulSoup(data, 'html.parser')
    containers = soup.find_all("div", class_="ListItem_wrapper__TxHWu")

    # Extract car links from the containers
    car_data = []
    for container in containers[0:3]:
        a_tag = container.find("div", class_="ListItem_header__J6xlG ListItem_header_new_design__Rvyv_").find("a",
                                                                                                              class_="ListItem_title__ndA4s ListItem_title_new_design__QIU2b Link_link__Ajn7I")
        if a_tag:
            link = a_tag.get('href')
            if link:
                full_link = "https://www.autoscout24.de" + link
                run_spider(full_link)
                car_data.append(get_scraped_data())

    # Use the external spider to scrape data from each car link

    # Extract image URLs from the car data
    images = []
    for car in car_data:
        img_list = car.get("car_images", [])
        images.extend(img_list)
    images = random.sample(images, min(30, len(images)))

    return images
