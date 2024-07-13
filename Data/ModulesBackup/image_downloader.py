import os
import requests
import shutil
from PIL import Image
from model import create_pdf_car_parts

source_folder = "images"  # Replace with the path to your source folder
destination_folder = "images\\car parts"  # Replace with the destination folder

def download_images(image_urls):
    # Create the "images" directory if it doesn't exist
    os.makedirs("images", exist_ok=True)
    
    # Remove all files from the "images" directory
    for filename in os.listdir("images"):
        file_path = os.path.join("images", filename)
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
                    with open(os.path.join("images", f"img-{i}.jpg"), 'wb') as f:
                        shutil.copyfileobj(response.raw, f)
                    print(f"Downloaded image {i+1} out of {len(image_urls)}")
                else:
                    print(f"Failed to download image {i}: HTTP status code {response.status_code}")
        except Exception as e:
            print(f"Failed to download image {i}: {e}")

            
def classify_images():
    # Delete everything in the destination folder
    if os.path.exists(destination_folder):
        shutil.rmtree(destination_folder)
    os.makedirs(destination_folder, exist_ok=True)
    
    for filename in os.listdir(source_folder):
        if filename.endswith((".jpg", ".jpeg", ".png")):
            image_path = os.path.join(source_folder, filename)
            try:
                img = Image.open(image_path)
                predicted_label = create_pdf_car_parts.predict_label(img)  # Correctly call predict_label from the model instance
                # Create a subfolder in the destination folder for each predicted label
                label_folder = os.path.join(destination_folder, predicted_label)
                os.makedirs(label_folder, exist_ok=True)
                # Save the image in the corresponding label folder
                img.save(os.path.join(label_folder, filename))
                print(f"Processed image {filename}: Predicted label - {predicted_label}")
            except Exception as e:
                print(f"Error processing image {filename}: {e}")
