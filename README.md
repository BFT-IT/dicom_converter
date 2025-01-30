# dicom_converter
Converts all images in the input folder (including subfolders) to DICOM format and saves them in the output folder.

> [!NOTE]  
> The user **must** define `input_folder` and `output_folder` in line 94 and 95 before running the script.
> If the series is a computer tomography the original filenames of the files must be in numeric order for the scrolling to work. slice_001.jpg, slice_002.jpg for example.
> The parent folder of the images is acknowledged as a series

> ## Args
>
> - input_folder (str): Path to the folder containing images.
> - output_folder (str): Path to the folder to save DICOM files.

## The structure of the input folder
```
input_folder
├── Subfolder1
│   ├── image1.jpg
│   ├── image2.png
├── Subfolder2
│   ├── image3.bmp
├── image4.jpg

```

## The structure of the output folder
```
output_folder
├── Subfolder1
│   ├── image1.dcm
│   ├── image2.dcm
├── Subfolder2
│   ├── image3.dcm
├── image4.dcm
```

## Required imports
os, pydicom, pydicom.dataset import Dataset, pydicom.uid import generate_uid, PIL import Image, numpy as np, uuid
