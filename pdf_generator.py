from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime
from helper import extract_numeric_value, resize_and_format_image, define_classe, translate
from model import create_pdf_car_parts
from googletrans import Translator

import math
import os


####################################################################################################################
####################################################################################################################


class PdfGenerator:
    def __init__(
            self, api_data, input_data, selected_language, use_manual_data, title, **kwargs
    ):
        # Global Variables
        self.api_data = api_data
        self.input_data = input_data
        self.selected_language = selected_language
        self.use_manual_data = use_manual_data
        self.img_root_path = "images"
        self.title = title
        self.kwargs = kwargs
        quotation_num = self.input_data.get("quotation_num")


        # Define All Pages Size
        self.pdf_filename = self._generate_pdf_filename()
        self.page_width, self.page_height = 2481, 3508
        directory_path = f"PDFS/{quotation_num}/"
        pdf_path = f"{directory_path}/{self.pdf_filename}"
# Create the directory
        os.makedirs(directory_path, exist_ok=True)

        self.c = canvas.Canvas(
            pdf_path, pagesize=(self.page_width, self.page_height)
        )
        self._register_fonts()

        ####################################################################################################################
        ####################################################################################################################

    # Global Helper Functions

    def create_images(self):
        image_paths = [
            f"{self.img_root_path}/{i}"
            for i in os.listdir("images")
            if "main" not in i and i.endswith(".jpg")
        ]

        return image_paths

    def _generate_pdf_filename(self):
        model = self.api_data.get("model", "NA")
        manufacturer_brand = self.api_data.get("manufacturer_brand", "NA")
        purchaser_name = self.input_data.get("purchaser_name", "NA").replace(" ", "")
        index = self.input_data.get("Index", 0)
        date = datetime.today().strftime("%d.%m.%Y")
        return f"Export Offer-GO_00{index}-{purchaser_name}-{manufacturer_brand}-{model}-{date}.pdf"

    def _register_fonts(self):
        fonts = [
            ("AktivGrotesk-Regular", "AktivGrotesk-Regular.ttf"),
            ("AktivGrotesk-Medium", "AktivGrotesk-Medium.ttf"),
            ("AktivGrotesk-MediumItalic", "AktivGrotesk-MediumItalic.ttf"),
            ("AktivGrotesk-Bold", "AktivGrotesk-Bold.ttf"),
        ]
        for font_name, font_file in fonts:
            pdfmetrics.registerFont(TTFont(font_name, f"./Assets/{font_file}"))

    def add_car_specs(
            self, specs, x1, y1, x2, y2, font_name="AktivGrotesk-Regular", font_size=22
    ):
        # Maximum number of elements per column
        max_elements_per_column = 15
        # Calculate the number of columns needed
        num_columns = math.ceil(len(specs) / max_elements_per_column)
        # Define column width
        column_width = ((x2 - x1) / num_columns) + 30
        # Set font for drawing the specs
        self.c.setFont(font_name, font_size)
        # Calculate line height based on font size
        line_height = font_size * 1.9  # Adjust line height as needed

        # Loop through the list and draw each spec
        for column_number in range(num_columns):
            # Calculate the starting x position for the current column
            x_position = x1 + column_number * column_width
            # Start at the top of the column
            y_position = y1

            # Get the subset of specs for the current column
            start_index = column_number * max_elements_per_column
            end_index = start_index + max_elements_per_column
            column_specs = specs[start_index:end_index]

            # Draw each spec in the column
            for spec in column_specs:
                self.c.drawString(x_position, y_position, "• " + spec)
                # Move to the next line
                y_position -= line_height

        ####################################################################################################################
        ####################################################################################################################

    def generate_pdf(self):

        # Color Of PDF
        self.c.setFillColorRGB(0, 0, 0)

        ####################################################################################################################

        ###### Page 1 ######

        # Background Of The First Page
        self.c.drawImage(
            "./Assets/Page_1.jpg", 0, 0, width=self.page_width, height=self.page_height
        )

        ####################################################################################################################

        # Seler & Client Info

        # Font
        self.c.setFont("AktivGrotesk-Regular", 26)

        # Quotation Number
        quotation_num = self.input_data.get("quotation_num", "")
        self.c.drawString(575, self.page_height - 175, f"{quotation_num}")

        # Seller Data (Name - Phone - Email)
        seller_name = self.input_data.get("seller_name", "Mr.")
        seller_phone = self.input_data.get("seller_phone", "xxxxxxxxxxx")

        self.c.drawString(105, self.page_height - 265, f"{seller_name}")
        self.c.drawString(105, self.page_height - 300, f"{seller_phone}")

        # Client Data (Name - Phone - Email)
        self.c.drawString(890, self.page_height - 230, f"Client Name:")

        Gender = self.input_data.get("Gender", 0)
        gender_title = self.input_data.get("gender_title")
        purchaser_name = self.input_data.get("purchaser_name", "(PURCHASER NAME)")
        purchaser_phone = self.input_data.get("purchaser_phone", "(PHONE NO)")
        purchaser_email = self.input_data.get("purchaser_email", "")

        self.c.drawString(
            890, self.page_height - 260, f"{gender_title} {purchaser_name}"
        )
        self.c.drawString(890, self.page_height - 290, f"{purchaser_phone}")
        self.c.drawString(890, self.page_height - 320, f"{purchaser_email}")

        ####################################################################################################################

        # Car Title
        self.c.setFont("AktivGrotesk-MediumItalic", 80)
        car_title = self.api_data.get("car_title", "NA")
        title = self.title
        if title:
            print_title = title
        else:
            print_title = car_title
        self.c.drawString(760, self.page_height - 620, f"{print_title}")

        ####################################################################################################################

        # Car Images
        image_paths = self.create_images()

        create_pdf_car_parts.process_images(image_paths)

        selected_images_from_folder = define_classe(f"./images/car parts")

        # Left part - first image
        image1_x1, image1_y1 = 93, 689
        image1_x2, image1_y2 = 1237, 1589

        image1_path = (
            f"./images/car parts/{selected_images_from_folder['Full front view']}"
        )
        image1_path = resize_and_format_image(image1_path, 93, 689, 1237, 1589)
        self.c.drawImage(
            image1_path,
            image1_x1,
            self.page_height - image1_y2,
            width=image1_x2 - image1_x1,
            height=(image1_y2 - image1_y1) - 66,
        )

        # Right part - Second image
        image2_x1, image2_y1 = 1241, 689
        image2_x2, image2_y2 = 2385, 1589

        image2_path = f"./images/car parts/{selected_images_from_folder['Back view']}"

        image2_path = resize_and_format_image(image2_path, 1241, 689, 2385, 1589)

        self.c.drawImage(
            image2_path,
            image2_x1,
            self.page_height - image2_y2,
            width=image2_x2 - image2_x1,
            height=(image2_y2 - image2_y1) - 66,
        )

        ####################################################################################################################

        # Car Info
        self.c.setFont("AktivGrotesk-Regular", 45)
        translator = Translator()
        manufacturer_brand, firstregistration, fuel, transmission, model, mileage, color, power, translated_car_specs, car_shape = translate(
            self.api_data, self.selected_language, translator)

        ## Left Info
        self.c.drawString(640, self.page_height - 1750, manufacturer_brand)
        self.c.drawString(640, self.page_height - 1805, firstregistration)
        self.c.drawString(640, self.page_height - 1865, fuel)
        self.c.drawString(640, self.page_height - 1928, transmission)

        ## Right Info
        self.c.drawString(1785, self.page_height - 1750, model)
        self.c.drawString(1785, self.page_height - 1805, mileage)
        self.c.drawString(1785, self.page_height - 1865, color)
        self.c.drawString(1785, self.page_height - 1928, power)

        ####################################################################################################################

        self.add_car_specs(
            translated_car_specs,
            125,
            self.page_height - 2160,
            2240,
            self.page_height - 2760,
        )

        ####################################################################################################################

        # Financial Offer

        # Car Type or Customs Option
        Customs_option = self.input_data.get("Customs_option", 0)

        # Car Net Price
        gross = self.api_data.get("car_price", 0)
        car_net_price = float(gross) / 1.19

        # Euro Rate
        euroRate = self.input_data.get("euroRate")

        # Engine Size
        Engin_CC = self.api_data.get("EngineSize")
        if Engin_CC is None and fuel == "Electrical":
            Engin_CC = "Electrical"
        elif Engin_CC is None and fuel != "Electrical":
            Engin_CC = 0
        print("\nEngin_CC : ", Engin_CC)

        if Engin_CC != "Electrical":
            if Engin_CC == 0:
                stripped = 0
            else:
                stripped = extract_numeric_value(Engin_CC)
                print("\nstripped", stripped)
            if int(stripped) <= 1600:
                Engin_CC = str("upto 1600cc")
            elif 1600 < int(stripped) <= 2000:
                Engin_CC = str("1600-2000cc")
            elif int(stripped) > 2000:
                Engin_CC = str("more than 2000cc")

        # Country Of Origin
        Eur1 = self.input_data.get("Eur1", 0)

        # Germany Shipping & Egyptian Customs Calculations
        Germany_Shipping = self.input_data.get("Germany_Shipping", 0)
        Egyptian_Customs = self.input_data.get("Egyptian_Customs", 0)



        Egyptian_Customs = round(Egyptian_Customs)

        # Custom clearance fees (€)
        Port_Customs_Fees = self.input_data.get("Port_Customs_Fees", 0)

        print("***************")
        print(
            "car_net_price,Germany_Shipping,Port_Customs_Fees,Egyptian_Customs,euroRate"
        )
        print(
            car_net_price,
            Germany_Shipping,
            Port_Customs_Fees,
            Egyptian_Customs,
            euroRate,
        )
        print("***************")

        # Go Fees ($) & Customs Calculation

        Fees = self.input_data.get("G&O_Fees", 0)


        if Customs_option == "Used Car":
            # 1
            GOFees = (
                             ((car_net_price + Germany_Shipping + Port_Customs_Fees) * euroRate)
                             + Egyptian_Customs
                     ) * (Fees / 100)

            # 2
            customs = round(Port_Customs_Fees * euroRate) + Egyptian_Customs

        else:
            # 1
            GOFees = (
                             (
                                     (car_net_price + Germany_Shipping + Port_Customs_Fees)
                                     + (car_net_price * (Egyptian_Customs / 100))
                             )
                             * (Fees / 100)
                     ) * euroRate

            # 2
            customs = round(
                ((car_net_price * (Egyptian_Customs / 100)) + Port_Customs_Fees)
                * euroRate
            )

        print(f"GOFees {GOFees}")

        # Car Cost In Alexandria For Both New & Used
        Car_Cost_till_reaching_Alexandria = round(
            ((car_net_price + Germany_Shipping) * euroRate) + GOFees
        )

        # Total Contract
        if self.input_data.get("egyptian_pound"):
            Total_Contract_Amount = round(
                (Car_Cost_till_reaching_Alexandria + customs) * self.input_data.get("dollar_rate"))
            Car_Cost_till_reaching_Alexandria = round(
                Car_Cost_till_reaching_Alexandria * self.input_data.get("dollar_rate"))
            customs = round(customs * self.input_data.get("dollar_rate"))
        else:
            Total_Contract_Amount = round(Car_Cost_till_reaching_Alexandria + customs)

        # Formatted Numbers
        cost_till = Car_Cost_till_reaching_Alexandria

        Car_Cost_till_reaching_Alexandria = "{:,}".format(
            Car_Cost_till_reaching_Alexandria
        )

        cust = customs

        customs = "{:,}".format(customs)

        Total_Contract_Amount = "{:,}".format(Total_Contract_Amount)

        ## Get Destination City
        self.c.setFont("AktivGrotesk-Regular", 40)

        destination_city = self.input_data.get("destination_city", "Alexandria")
        self.c.drawString(
            150, self.page_height - 3081, f"Total Car cost till {destination_city} port"
        )
        self.c.drawString(150, self.page_height - 3152, "Estimated Customs")

        ## Total Car Cost Till Alexandria Port & Estimated Customs
        if self.input_data.get("egyptian_pound"):
            self.c.setFont("AktivGrotesk-Regular", 45)
            self.c.drawString(
                895, self.page_height - 3081, f"{Car_Cost_till_reaching_Alexandria} EGP"
            )

            self.c.drawString(895, self.page_height - 3152, f"{customs} EGP")

            ## Total Contract
            self.c.setFont("AktivGrotesk-Medium", 90)
            self.c.drawString(1750, self.page_height - 3097, f"{Total_Contract_Amount} EGP")

        else:
            self.c.setFont("AktivGrotesk-Regular", 45)
            self.c.drawString(
                895, self.page_height - 3081, f"{Car_Cost_till_reaching_Alexandria} USD"
            )

            self.c.drawString(895, self.page_height - 3152, f"{customs} USD")

            ## Total Contract
            self.c.setFont("AktivGrotesk-Medium", 90)
            self.c.drawString(1850, self.page_height - 3097, f"{Total_Contract_Amount} USD")

        self.c.showPage()

        ####################################################################################################################
        ####################################################################################################################

        ###### Page 2 ######
        # Background Of The Second Page
        self.c.drawImage(
            "./Assets/Page_2.jpg", 0, 0, width=self.page_width, height=self.page_height
        )

        # Draw the images on the second page at the specified positions

        # Image 1

        image_path1 = f"./images/car parts/{selected_images_from_folder['Interior'][0]}"

        image_path1 = resize_and_format_image(image_path1, 270, 448, 1229, 928)

        self.c.drawImage(
            image_path1,
            270,
            self.page_height - 928,
            width=1229 - 270,
            height=928 - 448,
        )

        # Image 2
        image_path2 = f"./images/car parts/{selected_images_from_folder['Interior'][1]}"

        image_path2 = resize_and_format_image(image_path2, 1251, 448, 2210, 928)

        self.c.drawImage(
            image_path2,
            1251,
            self.page_height - 928,
            width=2210 - 1251,
            height=928 - 448,
        )

        # Image 3

        image_path3 = f"./images/car parts/{selected_images_from_folder['Interior'][2]}"

        image_path3 = resize_and_format_image(image_path3, 500, 977, 1979, 1719)

        self.c.drawImage(
            image_path3,
            500,
            self.page_height - 1719,
            width=1979 - 500,
            height=1719 - 977,
        )

        # Image 4

        image_path4 = f"./images/car parts/{selected_images_from_folder['Interior'][3]}"

        image_path4 = resize_and_format_image(image_path4, 270, 1768, 1229, 2248)

        self.c.drawImage(
            image_path4,
            270,
            self.page_height - 2248,
            width=1229 - 270,
            height=2248 - 1768,
        )

        # Image 5

        image_path5 = f"./images/car parts/{selected_images_from_folder['Interior'][4]}"

        image_path5 = resize_and_format_image(image_path5, 1251, 1768, 2210, 2248)

        self.c.drawImage(
            image_path5,
            1251,
            self.page_height - 2248,
            width=2210 - 1251,
            height=2248 - 1768,
        )

        self.c.showPage()

        ####################################################################################################################
        ####################################################################################################################

        ###### Page 3 ######
        # Background Of The Third Page
        self.c.drawImage(
            "./Assets/Page_3.jpg", 0, 0, width=self.page_width, height=self.page_height
        )

        self.c.showPage()

        ####################################################################################################################
        ####################################################################################################################
        car_dict = {
            "car_title": car_title,
            "manufacturer_brand": manufacturer_brand,
            "model": model,
            "EngineSize": Engin_CC,
            "car_price": gross,
            "car_features": translated_car_specs,
            "mileage": mileage,
            "fuel": fuel,
            "transmission": transmission,
            "power": power,
            "color": color,
            "firstregistration": firstregistration,
            "car_shape": car_shape,
        }

        self.c.save()
        return cost_till, cust, car_dict
