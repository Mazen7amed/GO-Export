import os
import random
import re
import shutil
import subprocess
import sys
import time
import requests
import pathlib
import tempfile
from PIL import Image
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from tenacity import retry, stop_after_attempt, wait_fixed
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
from model import create_pdf_car_parts



def image_output(images_index):
    if ":" in images_index:
        st, end = images_index.split(":")
        return [i for i in range(int(st), int(end) + 1)]

    else:
        return re.findall("[\.,-]?(\d+)", images_index)


def domain_detector(ad_link):
    if re.search(".*?(mobile\.de)/", ad_link):
        return "SuchenMobileDe"

    elif re.search(".*?(autoscout24\.de)/", ad_link):
        return "AutoScout24De"


def price_format(price):
    price = str(price)
    decimal = ""
    if "." in price:
        decimal = f'.{price.split(".")[-1]}'
        price = price.split(".")[0]

    if 2 < len(price) <= 6:
        return f"{price[:-3]},{price[-3:]}" + decimal
    elif len(price) > 6:
        return f"{price[:-6]},{price[-6:-3]},{price[-3:]}" + decimal
    else:
        return price


def remove_white_spaces(input_string):
    return re.sub(r"\s+", " ", input_string).strip()


def remove_unicode_char(input_string):
    """
    This function takes string as an input, and return strings after removing unicode character
    """
    return ("".join([i if ord(i) < 128 else " " for i in input_string])).strip()


def extract_number_only(input_string):
    numbers = re.findall(r"\d+(?:\.\d+)?", input_string)
    if numbers:
        return numbers
    else:
        return 0
    # return (''.join(filter(lambda i: i.isdigit(), remove_white_spaces(input_string)))).strip()


def summation(numbers):
    summ = 0
    for num in numbers:
        summ += float(num)

    return summ


def calculate_percentage(percent, num):
    return round(float(percent) / 100 * float(num), 5)


def list2table(list_data):
    out_put = []
    if len(list_data) % 2 == 0:
        for i in range(0, len(list_data), 2):
            out_put.append([list_data[i], list_data[i + 1]])
    else:
        for i in range(0, len(list_data) - 1, 2):
            out_put.append([list_data[i], list_data[i + 1]])
        out_put.append([list_data[-1], ""])

    return out_put


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def extract_numeric_value(text):
    text = text.replace(".", ",")
    # Use regular expression to find a sequence of digits with optional comma, followed by optional space and "cc", "cm³", or "ccm" at the end of the string
    match = re.search(r"(\d{1,3}(?:,\d{3})|\d+)\s?(cc|cm³|ccm)?$", text, re.IGNORECASE)

    if match:
        number_str = match.group(1).replace(
            ",", ""
        )  # Remove comma from the matched string
        number = int(number_str)
        return number
    else:
        return None


# Function to calculate new dimensions preserving the aspect ratio
def calculate_new_dimensions(image_path, target_width, target_height):
    image = Image.open(image_path)
    original_width, original_height = image.size
    width_ratio = target_width / original_width
    height_ratio = target_height / original_height
    ratio = min(width_ratio, height_ratio)
    return int(original_width * ratio), int(original_height * ratio)


def get_resource_path(filename):
    """Get the absolute path to a resource file, accounting for PyInstaller temp path."""
    if hasattr(sys, "_MEIPASS"):
        # Running as bundled executable (PyInstaller)
        return os.path.join(sys._MEIPASS, filename)
    else:
        # Running as script (development environment)
        return os.path.join(os.path.abspath("."), filename)


def resize_and_format_image(image_path, x1, y1, x2, y2):
    # Calculate target dimensions
    target_width = x2 - x1
    target_height = y2 - y1

    # Assuming get_resource_path is a function you have that determines the output path
    output_path = get_resource_path(image_path)

    with Image.open(image_path) as image:
        # Resize the image to fill the target area (this may change the aspect ratio)
        resized_image = image.resize((target_width, target_height), Image.LANCZOS)

        # Save the resized image
        resized_image.save(output_path)

    return output_path


def define_classe(folder_path):
    image_files = [
        f
        for f in os.listdir(folder_path)
        if os.path.isfile(os.path.join(folder_path, f)) and f.endswith(".jpg")
    ]

    # Classify images into classes based on the file naming convention
    images_classes = {}
    for image_file in image_files:
        # Extract the class name from the filename

        class_name = image_file.split("_img")[0]

        if class_name in images_classes:
            images_classes[class_name].append(image_file)
        else:
            images_classes[class_name] = [image_file]

    # Sort images in each class
    images_classes = {
        category: sorted(images, key=lambda x: int(x.split("-")[-1].split(".")[0]))
        for category, images in images_classes.items()
    }

    # Randomly select an image from each class
    selected_images_from_folder = {}
    for class_name, images in images_classes.items():
        if class_name == "Interior":
            selected_images_from_folder[class_name] = random.sample(images, 5)
        else:
            if len(images) > 1:
                selected_images_from_folder[class_name] = images[1]
            else:
                selected_images_from_folder[class_name] = images[0]

    return selected_images_from_folder


def translate_text(text, src, dest, translator):
    translated = translator.translate(text, src=src, dest=dest).text
    return translated


@retry(stop=stop_after_attempt(3), wait=wait_fixed(3))
def safe_translate_text(text, src, dest, translator):
    return translate_text(text, src, dest, translator)


def translate(api_data, selected_language, translator):
    manufacturer_brand = api_data.get("manufacturer_brand", "Not Provided")

    if selected_language != "de":
        firstregistration = safe_translate_text(
            api_data.get("firstregistration", "Not Provided"),
            src="de",
            dest=selected_language,
            translator=translator,
        )
        fuel = safe_translate_text(
            api_data.get("fuel", "Not Provided"),
            src="de",
            dest=selected_language,
            translator=translator,
        )
        transmission = safe_translate_text(
            api_data.get("transmission", "Not Provided"),
            src="de",
            dest=selected_language,
            translator=translator,
        )
        model = api_data.get("model", "Not Provided")
        mileage = safe_translate_text(
            api_data.get("mileage", "Not Provided"),
            src="de",
            dest=selected_language,
            translator=translator,
        )
        color = safe_translate_text(
            api_data.get("color", "Not Provided"),
            src="de",
            dest=selected_language,
            translator=translator,
        )
        power = safe_translate_text(
            api_data.get("power", "Not Provided"),
            src="de",
            dest=selected_language,
            translator=translator,
        )
        car_shape = safe_translate_text(
            api_data.get("Car_Shape", "Not Provided"),
            src="de",
            dest=selected_language,
            translator=translator,
        )
    else:
        firstregistration = api_data.get("firstregistration", "Not Provided")
        fuel = api_data.get("fuel", "Not Provided")
        transmission = api_data.get("transmission", "Not Provided")
        model = api_data.get("model", "Not Provided")
        mileage = api_data.get("mileage", "Not Provided")
        color = api_data.get("color", "Not Provided")
        power = api_data.get("power", "Not Provided")
        car_shape = api_data.get("Car_Shape", "Not Provided")

    car_specs = api_data.get("car_features", [])

    if selected_language != "de":
        translated_car_specs = []
        for feature in car_specs:
            if feature.lower() == "abs":
                translated_car_specs.append(feature)
            else:
                translation = safe_translate_text(
                    feature, src="de", dest=selected_language, translator=translator
                )
                translated_car_specs.append(translation)
    else:
        translated_car_specs = car_specs

    translated_car_specs = [
        item
        for sublist in translated_car_specs
        for item in (sublist if isinstance(sublist, list) else [sublist])
    ]

    return (
        manufacturer_brand,
        firstregistration,
        fuel,
        transmission,
        model,
        mileage,
        color,
        power,
        translated_car_specs,
        car_shape,
    )


def download_images(image_urls, source_folder="images"):
    # Create the source directory if it doesn't exist
    os.makedirs(source_folder, exist_ok=True)

    # Remove all files from the source directory
    for filename in os.listdir(source_folder):
        file_path = os.path.join(source_folder, filename)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
        except Exception as e:
            print(f"Failed to delete {file_path}: {e}")

    # Download new images
    for i, url in enumerate(image_urls):
        try:
            with requests.get(url, stream=True) as response:
                if response.status_code == 200:
                    with open(os.path.join(source_folder, f"img-{i}.jpg"), "wb") as f:
                        shutil.copyfileobj(response.raw, f)
                    print(f"Downloaded image {i + 1} out of {len(image_urls)}")
                else:
                    print(
                        f"Failed to download image {i + 1}: HTTP status code {response.status_code}"
                    )
        except Exception as e:
            print(f"Failed to download image {i}: {e}")


def classify_images(source_folder="images", destination_folder="images\\car parts"):
    # Delete everything in the destination folder
    if os.path.exists(destination_folder):
        shutil.rmtree(destination_folder)
    os.makedirs(destination_folder, exist_ok=True)

    # Classify the downloaded images
    for filename in os.listdir(source_folder):
        if filename.endswith((".jpg", ".jpeg", ".png")):
            image_path = os.path.join(source_folder, filename)
            try:
                img = Image.open(image_path)
                predicted_label = create_pdf_car_parts.predict_label(img)
                # Create a subfolder in the destination folder for each predicted label
                label_folder = os.path.join(destination_folder, predicted_label)
                os.makedirs(label_folder, exist_ok=True)
                # Save the image in the corresponding label folder
                img.save(os.path.join(label_folder, filename))
                print(
                    f"Processed image {filename}: Predicted label - {predicted_label}"
                )
            except Exception as e:
                print(f"Error processing image {filename}: {e}")


def move_pdf(index, purchaser_name, quotation_num, api_data):
    manufacturer_brand = api_data.get("manufacturer_brand", "")
    model = api_data.get("model", "")
    date = datetime.today().strftime("%d.%m.%Y")  # Format date as DD.MM.YYYY

    # Get the directory of the current script
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Construct file names
    car_pdf = f"Export Offer-GO_00{int(index)}-{purchaser_name}-{manufacturer_brand}-{model}-{date}.pdf"
    # Create subfolder path
    subfolder_path = os.path.join(current_dir, "PDFS", quotation_num)
    try:
        # Create the subfolder if it doesn't exist
        os.makedirs(subfolder_path, exist_ok=True)

        # Move car_pdf if it exists
        car_pdf_path = os.path.join(current_dir, car_pdf)
        if os.path.exists(car_pdf_path):
            shutil.move(car_pdf_path, os.path.join(subfolder_path, car_pdf))
            print(f"{car_pdf} moved to {subfolder_path}")
        else:
            print(f"{car_pdf} does not exist.")

    except FileNotFoundError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Unexpected error occurred: {e}")


def count_files_in_folder():
    """
    Count the number of files in a folder.

    Parameters:
    folder_path (str): The path to the folder.

    Returns:
    int: The number of files in the folder.
    """
    folders = ["Full front view", "Back view", "Interior"]
    for folder in folders:
        folder_path = f"images/car parts/{folder}"
        # List all files in the folder
        files = os.listdir(folder_path)
        # Count the number of files
        num_files = [len(files)]
    return sum(num_files)


def move_images(quotation_num):
    """
    Moves all files from the source directory to the destination directory.
    If the destination directory already exists, it deletes it first.

    Args:
        quotation_num (str): Quotation number used for creating the destination directory.
    """
    source_dir = "images"
    destination_dir = f"Saved_images/{quotation_num}"

    # Check if destination directory exists
    if os.path.exists(destination_dir):
        try:
            # Delete existing destination directory and its contents
            shutil.rmtree(destination_dir)
            print(f"Deleted existing directory: {destination_dir}")
        except Exception as e:
            print(f"Error deleting existing directory {destination_dir}: {e}")

    # Create destination directory
    try:
        os.makedirs(destination_dir)
        print(f"Created new directory: {destination_dir}")
    except Exception as e:
        print(f"Error creating directory {destination_dir}: {e}")

    # List all files in the source directory
    files = os.listdir(source_dir)

    # Move each file to the destination directory
    for file_name in files:
        # Construct full file paths
        source_file = os.path.join(source_dir, file_name)
        destination_file = os.path.join(destination_dir, file_name)

        try:
            # Move file
            shutil.move(source_file, destination_file)
            print(f"Moved {file_name} to {destination_dir}")
        except Exception as e:
            print(f"Error moving file {file_name}: {e}")



def generate_car_parts_pdf(quotation_num):
    main_dir = pathlib.Path(f'images/car parts')
    subfolders = [
        "Full front view",
        "Back view",
        "Interior",
        "Wheel",
        "Headlight",
        "Trunk",
        "Side view",
        "Engine",
    ]

    # Create PDF directory if it doesn't exist
    pdf_dir = pathlib.Path(f'PDFS/{quotation_num}')
    pdf_dir.mkdir(parents=True, exist_ok=True)

    # List to store image objects
    images_list = []

    # Loop through each subfolder
    for subfolder in subfolders:
        subfolder_path = main_dir / subfolder

        # Check if the subfolder exists
        if subfolder_path.exists():
            print(f"Processing subfolder: {subfolder}")

            # List all image files in the subfolder
            image_files = list(subfolder_path.glob('*.[pj][npvai][meg]*'))

            if not image_files:
                print(f"No images found in subfolder '{subfolder}'.")

            # Load images and append to images_list
            for image_file in image_files:
                try:
                    img = Image.open(image_file)
                    images_list.append(img)
                    print(f"Loaded image: {image_file}")
                except Exception as e:
                    print(f"Error loading image '{image_file}': {e}")
        else:
            print(f"Subfolder '{subfolder}' does not exist. Skipping...")

    # Create a PDF using reportlab
    def create_pdf(images, output_filename):
        c = canvas.Canvas(str(output_filename), pagesize=letter)
        width, height = letter

        # Define margins and image size
        margin = 50
        img_width = width - 2 * margin
        img_height = height - 2 * margin

        # Calculate positions for images
        y_position = height - margin
        for img in images:
            img_width, img_height = img.size
            aspect_ratio = img_width / img_height

            # Check if image fits on the page
            if img_height > height - 2 * margin or img_width > width - 2 * margin:
                img_width = width - 2 * margin
                img_height = img_width / aspect_ratio

            # Save image to a temporary file
            with tempfile.NamedTemporaryFile(delete=False) as tmpfile:
                img.save(tmpfile.name, format='JPEG')

                # Draw image on canvas
                c.drawImage(tmpfile.name, margin, y_position - img_height, width=img_width, height=img_height)

            y_position -= img_height + margin

            # Add a page break if there's space left
            if y_position - img_height <= margin:
                c.showPage()
                y_position = height - margin

        # Save the PDF file
        c.save()

        print(f"PDF created: {output_filename}")

    # Generate PDF with the list of images
    output_pdf = pathlib.Path(f'PDFS/{quotation_num}/Image.pdf')
    create_pdf(images_list, output_pdf)



def sanitize_filename(vin):
    """Sanitize VIN for use as a filename by removing non-alphanumeric characters."""
    return re.sub(r"\W+", "_", vin)


def create_pdf(car_details, save_folder):
    """Create a PDF file with the car details."""
    vin = car_details["VIN"]
    pdf_filename = f"vehicle_info_{sanitize_filename(vin)}.pdf"
    pdf_filepath = os.path.join(save_folder, pdf_filename).replace("\\", "/")

    # Ensure the save directory exists
    os.makedirs(save_folder, exist_ok=True)

    c = canvas.Canvas(pdf_filepath, pagesize=letter)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(100, 750, "Vehicle Information")
    c.setFont("Helvetica", 12)

    # Write details to PDF, excluding lines with unwanted text
    y_position = 720
    unwanted_texts = ["Donate to mb.vin", "Get a car", "Show mileage"]
    for key, value in car_details.items():
        if not any(unwanted_text in value for unwanted_text in unwanted_texts):
            c.drawString(100, y_position, f"{key}: {value}")
            y_position -= 20

    c.save()
    print(f"Vehicle information saved to {pdf_filepath}")
    return pdf_filepath


def open_pdf_files(quotation_num):
    quotation_num = quotation_num
    folder_path = f"PDFS/{quotation_num}"

    # Check if the folder exists
    if not os.path.exists(folder_path):
        print(f"Folder {folder_path} does not exist.")
        return

    try:
        # List all files in the folder
        files = os.listdir(folder_path)

        # Filter PDF files
        pdf_files = [file for file in files if file.lower().endswith(".pdf")]

        if not pdf_files:
            print(f"No PDF files found in {folder_path}")
            return

        # Open each PDF file using default PDF viewer
        for pdf_file in pdf_files:
            file_path = os.path.join(folder_path, pdf_file)

            # Platform-specific command to open PDF file
            if os.name == "nt":  # Windows
                subprocess.run(["start", "", file_path], shell=True)
            elif os.name == "posix":  # Linux, macOS
                subprocess.run(["xdg-open", file_path])
            else:
                print(
                    f"Unsupported OS: {os.name}. Cannot open PDF files automatically."
                )

    except Exception as e:
        print(f"Error: {e}")
