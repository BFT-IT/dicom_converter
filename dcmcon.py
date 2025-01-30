import os
import pydicom
from pydicom.dataset import Dataset
from pydicom.uid import generate_uid
from PIL import Image
import numpy as np
import re  # For sorting filenames numerically

def convert_images_to_dicom(input_folder, output_folder):
    os.makedirs(output_folder, exist_ok=True)
    supported_extensions = {".png", ".bmp", ".jpg", ".jpeg", ".tiff"}

    series_uid_map = {}  # Store SeriesInstanceUID per folder
    study_uid = generate_uid()  # Keep the Study UID the same for all slices

    for root, _, files in os.walk(input_folder):
        # Sort files numerically if filenames contain numbers (e.g., slice_1.tiff, slice_2.tiff)
        files = sorted(files, key=lambda x: int(re.search(r"\d+", x).group()) if re.search(r"\d+", x) else x)

        patient_name = os.path.basename(os.path.normpath(root))

        # Assign a SeriesInstanceUID for the folder
        if patient_name not in series_uid_map:
            series_uid_map[patient_name] = generate_uid()

        series_uid = series_uid_map[patient_name]

        # Iterate through files and assign InstanceNumber & SliceLocation
        for instance_number, file_name in enumerate(files, start=1):
            if any(file_name.lower().endswith(ext) for ext in supported_extensions):
                image_path = os.path.join(root, file_name)
                try:
                    img = Image.open(image_path)
                    width, height = img.size
                    print(f"Processing: {image_path} | Format: {img.format}, Mode: {img.mode}, Size: {width}x{height}")

                    # Handle different image modes
                    if img.mode == "I;16":
                        img = img.point(lambda i: i * (255 / 65535))
                        img = img.convert("L")
                    elif img.mode == "P":
                        img = img.convert("RGB")
                    elif img.mode in ["CMYK", "RGBA"]:
                        img = img.convert("RGB")
                    elif img.mode == "L":
                        img = img.convert("L")

                    np_frame = np.array(img)
                    output_file_name = file_name.rsplit(".", 1)[0]

                    # Create DICOM dataset
                    ds = Dataset()
                    ds.file_meta = Dataset()
                    ds.file_meta.TransferSyntaxUID = pydicom.uid.ExplicitVRLittleEndian
                    ds.file_meta.MediaStorageSOPClassUID = "1.2.840.10008.5.1.4.1.1.2"  # CT Image Storage
                    ds.file_meta.MediaStorageSOPInstanceUID = generate_uid()
                    ds.file_meta.ImplementationClassUID = generate_uid()

                    # Assign Patient & Study details
                    ds.PatientName = patient_name
                    ds.Rows = height
                    ds.Columns = width
                    ds.StudyInstanceUID = study_uid
                    ds.SeriesInstanceUID = series_uid
                    ds.SOPInstanceUID = generate_uid()

                    # Set slice order properties
                    ds.InstanceNumber = instance_number  # Ensures correct scrolling order
                    ds.SliceLocation = float(instance_number)  # Helps viewers order slices spatially

                    # Optional: Image Position (important for 3D reconstruction in some viewers)
                    ds.ImagePositionPatient = [0, 0, instance_number * 1.5]  # Arbitrary slice spacing

                    # Set Photometric Interpretation
                    if img.mode in ["RGB", "RGBA"]:
                        ds.PhotometricInterpretation = "RGB"
                        ds.SamplesPerPixel = 3
                    else:
                        ds.PhotometricInterpretation = "MONOCHROME2"
                        ds.SamplesPerPixel = 1

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

                    ds.PixelRepresentation = 0
                    ds.PlanarConfiguration = 0
                    ds.NumberOfFrames = 1

                    # Maintain folder structure in output
                    relative_path = os.path.relpath(root, input_folder)
                    output_subfolder = os.path.join(output_folder, relative_path)
                    os.makedirs(output_subfolder, exist_ok=True)

                    dicom_filename = os.path.join(output_subfolder, f"{output_file_name}.dcm")
                    ds.save_as(dicom_filename, write_like_original=False)
                    print(f"Saved DICOM: {dicom_filename} (InstanceNumber: {instance_number})")

                except Exception as e:
                    print(f"Error processing {image_path}: {e}")

if __name__ == "__main__":
    input_folder = r"C:\Temp\Images"
    output_folder = r"C:\Temp\DICOM"
    convert_images_to_dicom(input_folder, output_folder)
