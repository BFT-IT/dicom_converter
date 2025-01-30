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
    os.makedirs(output_folder, exist_ok=True)  # Ensure output folder exists

    supported_extensions = {".png", ".bmp", ".jpg", ".jpeg", ".tiff"}  # Supported formats

    for root, _, files in os.walk(input_folder):
        for file_name in files:
            if any(file_name.lower().endswith(ext) for ext in supported_extensions):
                image_path = os.path.join(root, file_name)
                try:
                    img = Image.open(image_path)
                    width, height = img.size
                    print(f"Processing: {image_path} | Format: {img.format}, Mode: {img.mode}, Size: {width}x{height}")

                    # Handle different image modes
                    if img.mode == "I;16":  # 16-bit grayscale TIFF
                        img = img.point(lambda i: i * (255 / 65535))  # Normalize to 8-bit
                        img = img.convert("L")
                    elif img.mode == "P":  # Indexed color
                        img = img.convert("RGB")
                    elif img.mode in ["CMYK", "RGBA"]:  # CMYK or has alpha
                        img = img.convert("RGB")
                    elif img.mode == "L":  # Ensure grayscale images remain MONOCHROME2
                        img = img.convert("L")

                    # Convert image to NumPy array
                    np_frame = np.array(img)

                    # Extract file name without extension
                    output_file_name = file_name.rsplit(".", 1)[0]

                    # Create a new DICOM dataset
                    ds = Dataset()
                    ds.file_meta = Dataset()
                    ds.file_meta.TransferSyntaxUID = pydicom.uid.ExplicitVRLittleEndian
                    ds.file_meta.MediaStorageSOPClassUID = "1.2.840.10008.5.1.4.1.1.1.1"  # Secondary capture image storage
                    ds.file_meta.MediaStorageSOPInstanceUID = generate_uid()
                    ds.file_meta.ImplementationClassUID = generate_uid()

                    # Populate required DICOM attributes
                    patient_name = os.path.basename(os.path.normpath(root))
                    ds.PatientName = patient_name  # Placeholder patient name
                    ds.Rows = height
                    ds.Columns = width

                    # Set Photometric Interpretation
                    if img.mode in ["RGB", "RGBA"]:
                        ds.PhotometricInterpretation = "RGB"
                        ds.SamplesPerPixel = 3
                    else:
                        ds.PhotometricInterpretation = "MONOCHROME2"
                        ds.SamplesPerPixel = 1

                    # Handle 16-bit TIFF correctly
                    if img.mode == "I;16":
                        ds.BitsStored = 16
                        ds.BitsAllocated = 16
                        ds.HighBit = 15
                        ds.PixelData = np_frame.astype(np.uint16).tobytes()
                    else:
                        ds.BitsStored = 8
                        ds.BitsAllocated = 8
                        ds.HighBit = 7
                        ds.PixelData = np_frame.astype(np.uint8).tobytes()

                    ds.PixelRepresentation = 0  # Unsigned integer
                    ds.PlanarConfiguration = 0  # Pixel data stored by pixel
                    ds.NumberOfFrames = 1  # Single frame

                    # Add unique identifiers
                    ds.SOPClassUID = generate_uid()
                    ds.SOPInstanceUID = generate_uid()
                    ds.StudyInstanceUID = generate_uid()
                    ds.SeriesInstanceUID = generate_uid()

                    # Maintain folder structure in output
                    relative_path = os.path.relpath(root, input_folder)
                    output_subfolder = os.path.join(output_folder, relative_path)
                    os.makedirs(output_subfolder, exist_ok=True)

                    # Save the DICOM file
                    dicom_filename = os.path.join(output_subfolder, f"{output_file_name}.dcm")
                    ds.save_as(dicom_filename, write_like_original=False)
                    print(f"Saved DICOM: {dicom_filename}")

                except Exception as e:
                    print(f"Error processing {image_path}: {e}")


if __name__ == "__main__":
    input_folder = r"C:\\Temp\\Images"  # Path to folder containing images
    output_folder = r"C:\\Temp\\DICOM"  # Path to folder for saving DICOM files

    convert_images_to_dicom(input_folder, output_folder)