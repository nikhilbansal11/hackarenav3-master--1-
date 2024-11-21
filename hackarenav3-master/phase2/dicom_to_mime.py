import os
import pydicom
from PIL import Image
import numpy as np
# import pyheif
import imageio.v3 as iio

# Function to read a DICOM file and convert it to a numpy array
def read_dicom_to_image_array(dicom_path):
    dicom_data = pydicom.dcmread(dicom_path)
    image_array = dicom_data.pixel_array
    normalized_image = (image_array - np.min(image_array)) / (np.max(image_array) - np.min(image_array)) * 255
    return Image.fromarray(normalized_image.astype('uint8'))

# Function to save the image in different formats
def save_image_in_formats(image, output_dir, file_base_name):
    formats = {
       "PNG": "image/png",
        "JPEG": "image/jpeg",
        "WEBP": "image/webp",
    }
    
    results = {}
    for format_name, mime_type in formats.items():
        output_path = os.path.join(output_dir, f"{file_base_name}.{format_name.lower()}")
        if format_name in ["HEIC", "HEIF"]:
            # Save HEIC/HEIF using imageio
            iio.imwrite(output_path, image, plugin="pillow")
        else:
            image.save(output_path, format_name)
        results[format_name] = os.stat(output_path).st_size
    return results


# Function to compare file sizes
def compare_results(results):
    print("File Size Comparison:")
    for format_name, file_size in results.items():
        print(f"{format_name}: {file_size / 1024:.2f} KB")

# Main function
def main(dicom_path, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    image = read_dicom_to_image_array(dicom_path)
    file_base_name = os.path.splitext(os.path.basename(dicom_path))[0]
    
    results = save_image_in_formats(image, output_dir, file_base_name)
    compare_results(results)

# Example usage
dicom_file_path = r"C:\Users\Admin\Downloads\hackarenav3-master (1)\hackarenav3-master\phase2\ID_000229f2a.dcm"  # Replace with your DICOM file path
output_directory = r"C:\Users\Admin\Downloads\hackarenav3-master (1)\hackarenav3-master\phase2"  # Replace with your output directory path
main(dicom_file_path, output_directory)


# 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