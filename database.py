import base64
from datetime import datetime
import json
import os
import pickle
import mysql.connector
import bcrypt

# Define the connection details
USERNAME = "root"
PASSWORD = ""
DATABASE = "g&o"


# Function to establish a connection to the MySQL database
def get_db_connection():
    return mysql.connector.connect(
        host="localhost", user=USERNAME, password=PASSWORD, database=DATABASE
    )


def insert(cost, customs, car_dict, input_data):
    global db_connection
    try:
        db_connection = get_db_connection()
        with db_connection.cursor() as cursor:
            user_id = input_data.get("user_id")

            cust_name = input_data.get("purchaser_name")
            cust_phone = input_data.get("purchaser_phone")
            cust_email = input_data.get("purchaser_email")
            cust_gender = input_data.get("Gender")

            car_title = car_dict.get("car_title")
            manufacturer_brand = car_dict.get("manufacturer_brand")
            model = car_dict.get("model")
            EngineSize = car_dict.get("EngineSize")
            car_features = car_dict.get("car_features")
            car_features_json = json.dumps(car_features)

            car_price = car_dict.get("car_price")
            mileage = car_dict.get("mileage")
            fuel = car_dict.get("fuel")
            transmission = car_dict.get("transmission")
            power = car_dict.get("power")
            color = car_dict.get("color")
            firstregistration = car_dict.get("firstregistration")

            quotation_num = input_data.get("quotation_num")
            car_images_folder = (
                "images"
            )

            # List of image files, excluding directories
            image_files = [
                file
                for file in os.listdir(car_images_folder)
                if os.path.isfile(os.path.join(car_images_folder, file))
            ]

            # List to hold all binary image data
            images_data = []
            for image_file in image_files:
                image_path = os.path.join(car_images_folder, image_file)

                # Read the image file
                with open(image_path, "rb") as file:
                    binary_data = file.read()
                    images_data.append(binary_data)

            serialized_images = pickle.dumps(images_data)

            # Insert data into Customers table
            cursor.execute(
                "INSERT INTO Customers (Name, Phone, Email, Gender) VALUES (%s, %s, %s, %s)",
                (cust_name, cust_phone, cust_email, cust_gender),
            )
            cust_id = cursor.lastrowid

            # Insert data into Car_Details table
            cursor.execute(
                "INSERT INTO Car_Details (car_title, manufacturer_brand, model, EngineSize, "
                "car_price, car_features, Car_Images, mileage, fuel, transmission, power, color, First_Registration) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (
                    car_title,
                    manufacturer_brand,
                    model,
                    EngineSize,
                    car_price,
                    car_features_json,
                    serialized_images,
                    mileage,
                    fuel,
                    transmission,
                    power,
                    color,
                    firstregistration,
                ),
            )
            car_id = cursor.lastrowid

            germany_shipping = input_data.get("Germany_Shipping")
            port_custom_fees = input_data.get("Port_Customs_Fees")
            g_o_fees = input_data.get("G&O_Fees")
            euro_rate = input_data.get("euroRate")
            cost_till_port = cost
            customs = customs
            total_contract = cost + customs
            index_ = input_data.get("Index")
            date = datetime.today().strftime("%d.%m.%Y")

            with open(
                    f"PDFS/{quotation_num}/Export Offer-GO_00{index_}-{cust_name}-{manufacturer_brand}-{model}-{date}.pdf",
                    "rb",
            ) as file:
                pdf_data = file.read()
            encoded_pdf = base64.b64encode(pdf_data)
            # Insert data into Quotation table
            cursor.execute(
                "INSERT INTO quotations (Quot_num, Germany_Shipping, Port_Custom_Fees, "
                "G_O_Fees, Euro_Rate, Cost_Till_Port, Customs, Total_Contract, Index_, PDF,Cust_ID, Car_Details_ID, user_id) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (
                    quotation_num,
                    germany_shipping,
                    port_custom_fees,
                    g_o_fees,
                    euro_rate,
                    cost_till_port,
                    customs,
                    total_contract,
                    index_,
                    encoded_pdf,
                    cust_id,
                    car_id,
                    user_id
                ),
            )

            # Commit changes
            db_connection.commit()
    except Exception as e:
        # Log the exception (or handle it accordingly)
        print(f"An error occurred: {e}")
    finally:
        if db_connection.is_connected():
            db_connection.close()


def check_login(username, password):
    global db_connection
    try:
        db_connection = get_db_connection()
        with db_connection.cursor() as cursor:
            cursor.execute(
                "SELECT user_id,Phone_Number ,Password,User_Type FROM users WHERE Name = %s",
                (username,)
            )
            result = cursor.fetchone()

            if result is not None:
                user_id, phone, db_password, user_type = result
                if bcrypt.checkpw(password.encode("utf-8"), db_password.encode("utf-8")):
                    return user_type, phone, user_id
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    finally:
        if 'db_connection' in globals() and db_connection.is_connected():
            db_connection.close()


def get_count(username):
    global db_connection
    try:
        db_connection = get_db_connection()
        with db_connection.cursor() as cursor:
            cursor.execute(
                "SELECT quotation_count FROM users WHERE Name = %s",
                (username,)
            )
            result = cursor.fetchone()

            if result is not None:
                return result[0]
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    finally:
        if 'db_connection' in globals() and db_connection.is_connected():
            db_connection.close()


def get_costs():
    global db_connection
    try:
        db_connection = get_db_connection()
        with db_connection.cursor() as cursor:
            cursor.execute("SELECT * FROM costs LIMIT 1")
            costs = cursor.fetchone()
            if costs is not None:
                week_no, go_fees_percent, germany_shipping, custom_fees = costs
                return week_no, go_fees_percent, germany_shipping, custom_fees
            return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    finally:
        if 'db_connection' in globals() and db_connection.is_connected():
            db_connection.close()
