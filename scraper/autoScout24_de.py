import json
import re

import scrapy

from helper import price_format, remove_unicode_char, extract_number_only


class AutoScout24De(scrapy.Spider):
    def __init__(self, urls, *args, **kwargs):  # , img_idx
        super().__init__(*args, **kwargs)
        self.start_urls = urls
        # self.img_idx = img_idx

    name = "autoScout24_de"
    allowed_domains = ["autoScout24.de"]

    def parse(self, response, **kwargs):
        print("Parsing response...")
        # All Scraped Data
        car_maker_path = response.xpath('//script[@id="__NEXT_DATA__"]/text()').get()
        car_maker_json = json.loads(car_maker_path)["props"]["pageProps"][
            "listingDetails"
        ]
        # ******************************************************************************************* #

        # Car Id - Manufacturer Brand - Model
        manufacturer_brand = car_maker_json["vehicle"]["make"]
        model = car_maker_json["vehicle"]["model"]

        car_title = f"{manufacturer_brand} {model}"

        # ******************************************************************************************* #

        # Engine Size
        EngineSize = car_maker_json["vehicle"]["displacementInCCM"]

        # ******************************************************************************************* #

        # Car Features
        car_features = response.xpath(
            '//div[contains(@class, "ExpandableDetailsSection_childContainer__FBt_o")]//li/text()'
        ).getall()

        # ******************************************************************************************* #

        # Car Shape
        body_shape_value = response.xpath(
            f'//dt[contains(@class, "DataGrid_defaultDtStyle__soJ6R") and text()="Karosserieform"]/following-sibling::dd[contains(@class, "DataGrid_defaultDdStyle__3IYpG") and contains(@class, "DataGrid_fontBold__RqU01")]/text()'
        ).get()

        # ******************************************************************************************* #
        # Car Images
        car_images = car_maker_json["images"]
        # selected_images = [car_images[int(i) - 1] for i in self.img_idx]

        # ******************************************************************************************* #

        # Car Price
        car_price = car_maker_json["prices"]["public"]["priceRaw"]

        # ******************************************************************************************* #

        # Car Specifications
        if car_maker_json["vehicle"]["mileageInKm"] == None:
            mileage = "0 km"
        else:
            mileage = car_maker_json["vehicle"]["mileageInKm"]

        fuel = car_maker_json["vehicle"]["fuelCategory"]["formatted"]

        # transmission = car_maker_json["vehicle"]["transmissionType"]
        if car_maker_json["vehicle"]["transmissionType"] == None:
            transmission = "Automatic"
        else:
            transmission = car_maker_json["vehicle"]["transmissionType"]
        power = f"{car_maker_json['vehicle']['rawPowerInKw']}/{car_maker_json['vehicle']['rawPowerInHp']}"
        color = car_maker_json["vehicle"]["bodyColor"]

        firstregistration = car_maker_json["vehicle"]["firstRegistrationDate"]
        if firstregistration:
            firstregistration = firstregistration.split("/")[1]

        # ******************************************************************************************* #

        yield {
            "car_title": car_title,
            "manufacturer_brand": manufacturer_brand,
            "model": model,
            "EngineSize": EngineSize,
            "car_features": car_features,
            "car_images": car_images,
            "car_price": car_price,
            "mileage": mileage,
            "fuel": fuel,
            "transmission": transmission,
            "power": power,
            "color": color,
            "firstregistration": firstregistration,
            "Car_Shape" : body_shape_value,
            # "car_specifications": [
            #     ["Herstellermarke:", manufacturer_brand],
            #     ["Fahrzeugtyp:", model],
            #     ["Laufleistung (km):", mileage],
            #     ["Motorart:", fuel],
            #     ["Getriebeart:", transmission],
            #     ["Leistung KW/PS:", power],
            #     ["Lackierung:", color],
            #     ["Erstzulassung:", firstregistration],
            # ],
        }
