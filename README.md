# comppy
## Overview
This script is designed to process microscopy images. The script first finds all images in the input folder that match a given well number, filters out the green channel images, and performs some intensity rescaling. The user can then select regions to crop by clicking on the displayed image. The cropped images and their composites are then saved to the specified output folder, with a unique folder name.

## Requirements
- Python 3
- Numpy, Skimage, Matplotlib, Glob, Logging, Subprocess, Datetime and Random libraries
- git installed and added to path
- Some input images to process

## Running the script
To run the script clone the repository.
You will need to provide the plate_id, well number and protein name and channel.

## Input and Output
The script takes all images in the input folder as input and expects them to be in a certain format.
The output images will be in the output folder, with a unique folder name generated from the input parameters.

## Known Issues and Future Improvements
Please note that this script needs some further development and testing before it can be considered for use. 
