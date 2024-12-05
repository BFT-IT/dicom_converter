import os
import pydicom
from pydicom.dataset import Dataset
from pydicom.uid import generate_uid
from PIL import Image
import numpy as np
import uuid

def convert_images_to_dicom(input_folder, output_folder):
    """
    Converts all images in the input folder (including subfolders) to DICOM format
    and saves them in the output folder.

    Args:
        input_folder (str): Path to the folder containing images.
        output_folder (str): Path to the folder to save DICOM files.
    """
    # Create the output folder if it doesn't already exist
    os.makedirs(output_folder, exist_ok=True)

    # Supported image file extensions
    supported_extensions = {".png", ".bmp", ".jpg", ".jpeg", ".tiff"}

    # Traverse through all subfolders and files in the input folder
    for root, _, files in os.walk(input_folder):
        for file_name in files:
            # Check if the current file has a supported image format
            if any(file_name.lower().endswith(ext) for ext in supported_extensions):
                image_path = os.path.join(root, file_name)
                try:
                    # Load the image using PIL
                    img = Image.open(image_path)
                    width, height = img.size  # Get image dimensions
                    print(f"Processing: {image_path} | Format: {img.format}, Size: {width}x{height}")

                    # Convert to RGB mode if the image format requires it
                    if img.format in ["PNG", "BMP", "TIFF"]:
                        img = img.convert("RGB")

                    # Convert image data to a NumPy array for DICOM PixelData
                    if img.mode == "L":  # Grayscale image
                        np_frame = np.array(img, dtype=np.uint8)
                    elif img.mode in ["RGBA", "RGB"]:  # Color image
                        np_frame = np.array(img.getdata(), dtype=np.uint8).reshape(height, width, -1)
                    else:
                        # Skip unsupported image modes
                        print(f"Skipping {image_path}: Unsupported image mode {img.mode}")
                        continue

                    # Create a new DICOM dataset
                    ds = Dataset()
                    ds.file_meta = Dataset()
                    ds.file_meta.TransferSyntaxUID = pydicom.uid.ExplicitVRLittleEndian
                    ds.file_meta.MediaStorageSOPClassUID = "1.2.840.10008.5.1.4.1.1.1.1"  # Secondary capture image storage
                    ds.file_meta.MediaStorageSOPInstanceUID = generate_uid()
                    ds.file_meta.ImplementationClassUID = generate_uid()

                    # Populate required DICOM attributes
                    ds.PatientName = "ConvertedImage"  # Placeholder patient name
                    ds.Rows = height
                    ds.Columns = width
                    ds.PhotometricInterpretation = "RGB" if img.mode in ["RGBA", "RGB"] else "MONOCHROME2"
                    ds.SamplesPerPixel = 3 if img.mode in ["RGBA", "RGB"] else 1
                    ds.BitsStored = 8  # 8 bits per pixel
                    ds.BitsAllocated = 8
                    ds.HighBit = 7  # Most significant bit (0-indexed)
                    ds.PixelRepresentation = 0  # Unsigned integer
                    ds.PlanarConfiguration = 0  # Pixel data stored by pixel
                    ds.NumberOfFrames = 1  # Single frame
                    ds.PixelData = np_frame.tobytes()  # Set the pixel data

                    # Add unique identifiers for the DICOM file
                    ds.SOPClassUID = generate_uid()
                    ds.SOPInstanceUID = generate_uid()
                    ds.StudyInstanceUID = generate_uid()
                    ds.SeriesInstanceUID = generate_uid()

                    # Generate a relative output path to maintain folder structure
                    relative_path = os.path.relpath(root, input_folder)
                    output_subfolder = os.path.join(output_folder, relative_path)
                    os.makedirs(output_subfolder, exist_ok=True)

                    # Save the DICOM file with a unique name
                    dicom_filename = os.path.join(output_subfolder, str(uuid.uuid4()) + ".dcm")
                    ds.save_as(dicom_filename, write_like_original=False)
                    print(f"Saved DICOM: {dicom_filename}")

                except Exception as e:
                    # Catch and log any errors that occur during the conversion process
                    print(f"Error processing {image_path}: {e}")

if __name__ == "__main__":
    # Define input and output folder paths (update paths as needed)
    input_folder = r"C:\Temp\Images"  # Path to folder containing images
    output_folder = r"C:\Temp\DICOM"  # Path to folder for saving DICOM files

    # Convert all images in the input folder to DICOM format
    convert_images_to_dicom(input_folder, output_folder)
