from pdf2image import convert_from_path
import os

# Function to convert PDF to PNG
def pdf_to_png(pdf_path, output_folder):
    # Convert PDF to list of images
    images = convert_from_path(pdf_path)
    
    # Save images as PNG files
    for i, image in enumerate(images):
        # Create a subfolder for each PDF file
        pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
        pdf_output_folder = os.path.join(output_folder, pdf_name)
        if not os.path.exists(pdf_output_folder):
            os.makedirs(pdf_output_folder)
        
        output_path = os.path.join(pdf_output_folder, f"page_{i+1}.png")
        image.save(output_path, 'PNG')
        print(f"Saved: {output_path}")

# Function to process all PDFs in a folder
def convert_pdfs_to_png(input_folder, output_folder):
    # Create output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Iterate through all files in the input folder
    for filename in os.listdir(input_folder):
        if filename.lower().endswith('.pdf'):
            pdf_path = os.path.join(input_folder, filename)
            pdf_to_png(pdf_path, output_folder)

