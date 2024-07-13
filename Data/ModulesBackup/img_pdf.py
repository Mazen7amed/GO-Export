import os
from PIL import Image
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


def create_pdf_from_images(quotation_num):
    folder_path = f"Saved_images/{quotation_num}"
    output_pdf = "Images.pdf"

    # Create a canvas object with letter size (8.5x11 inches)
    c = canvas.Canvas(output_pdf, pagesize=letter)

    # Get a list of image files in the folder
    image_files = [
        f
        for f in os.listdir(folder_path)
        if f.lower().endswith((".jpg", ".png", ".jpeg"))
    ]

    # Loop through each image file
    for image_file in image_files:
        image_path = os.path.join(folder_path, image_file)
        img = Image.open(image_path)
        width, height = img.size
        max_width = 500  # Adjust this value as needed
        max_height = 700  # Adjust this value as needed

        # Resize the image if necessary
        if width > max_width or height > max_height:
            ratio = min(max_width / width, max_height / height)
            width = int(width * ratio)
            height = int(height * ratio)

        # Calculate the position to center the image horizontally
        x = (letter[0] - width) / 2
        y = (
            letter[1] - height - 50
        )  # Adjust this value to control the vertical position

        # Draw the image on the canvas
        c.drawImage(image_path, x, y, width, height)

        # Add a new page for the next image
        c.showPage()

    # Save the PDF
    c.save()
