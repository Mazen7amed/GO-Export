import mysql.connector
import base64
import os
import pickle

# Define the connection details
URL = "jdbc:mysql://localhost:3306/pdf-generator"
USERNAME = "root"
PASSWORD = ""

# Establish a connection to your MySQL database
db_connection = mysql.connector.connect(
    host="localhost",
    user=USERNAME,
    password=PASSWORD,
    database="pdf-generator"
)


with open('PDFS/Export Offer-GO_001-AhmedKhaled-Kia-Sportage-02.06.2024.pdf', 'rb') as file:
    pdf_data = file.read()

# Encode the PDF file
encoded_pdf = base64.b64encode(pdf_data)


# Create a cursor object to execute SQL queries
# Create a cursor object
cursor = db_connection.cursor()

# Folder containing the car images
car_images_folder = "images"

# List of image files
image_files = os.listdir(car_images_folder)

# List to hold all binary image data
images_data = []

for image_file in image_files:
    image_path = os.path.join(car_images_folder, image_file)

    # Read the image file
    with open(image_path, 'rb') as file:
        binary_data = file.read()
        images_data.append(binary_data)

# Serialize the list of images into a single binary object
serialized_images = pickle.dumps(images_data)


# Sample data to insert
employee_data = ("John Doe", "1234567890")
customer_data = ("Jane Smith", "0987654321", "jane@example.com", "Female")
car_data = ("Toyota Camry", "Toyota", "Camry", "2.5L", "Automatic", "Black")

# Insert data into Employees table
cursor.execute("INSERT INTO Employees (Name, Phone) VALUES (%s, %s)", employee_data)
emp_id = cursor.lastrowid  # Get the last inserted employee ID

# Insert data into Customers table
cursor.execute("INSERT INTO Customers (Name, Phone, Email, Gender) VALUES (%s, %s, %s, %s)", customer_data)
cust_id = cursor.lastrowid  # Get the last inserted customer ID

# Insert data into Car_Details table
cursor.execute("INSERT INTO Car_Details (car_title, manufacturer_brand, model, EngineSize, transmission, color) VALUES (%s, %s, %s, %s, %s, %s)", car_data)
car_id = cursor.lastrowid  # Get the last inserted car ID

# Insert data into Quotations table
quot_data = (5, "Germany", 100.0, 50.0, 75.0, 1.2, 0.8, 3000.0, 500.0, 5000.0, 1, encoded_pdf, emp_id, cust_id, car_id)
cursor.execute("INSERT INTO Quotations (No_Of_Weeks, Country_Of_Origin, Germany_Shipping, Port_Custom_Fees, G_O_Fees, Dollar_Rate, Euro_Rate, Cost_Till_Port, Customs, Total_Contract, Index_, PDF, Emp_ID, Cust_ID, Car_Details_ID) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", quot_data)

# Commit changes and close connection
db_connection.commit()
cursor.close()
db_connection.close()
