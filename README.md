# dicom_converter
Converts all images in the input folder (including subfolders) to DICOM format and saves them in the output folder.

> [!NOTE]  
> The user **must** define `input_folder` and `output_folder` in line 94 and 95 before running the script.

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
│   ├── 9fd72aeb-cb5f-4bcb-8e91-6d50a1bc19d1.dcm
│   ├── 3bcf1a3e-4b7d-4766-a645-320e92c95d48.dcm
├── Subfolder2
│   ├── 1a73aefd-87b8-490a-85c1-d2f43456d92b.dcm
├── 4ad1e741-134d-4e12-9a4e-8e07d61e84d7.dcm
```

## Required imports
os, pydicom, pydicom.dataset import Dataset, pydicom.uid import generate_uid, PIL import Image, numpy as np, uuid
