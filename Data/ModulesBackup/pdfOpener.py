import os
import webbrowser

def open_any_pdf_in_browser(folder_path = r'C:\Users\hmaze\Desktop\WebApp'):
    # List all files in the folder
    files = os.listdir(folder_path)
    
    # Look for a PDF file
    pdf_files = [file for file in files if file.lower().endswith('.pdf')]
    
    # Check if any PDF file is found
    if not pdf_files:
        print("No PDF files found in the folder.")
        return
    
    # Open the first PDF file found in the default web browser
    first_pdf_file = pdf_files[0]
    file_path = os.path.join(folder_path, first_pdf_file)
    webbrowser.open_new_tab(f'file://{os.path.abspath(file_path)}')
