import glob
from skimage import io
from skimage import exposure
from matplotlib import pyplot as plt
import numpy as np


i_path = 'input/*'
well = input('well number:')
well_list = []
green_list = []

for i in glob.glob(i_path):
    filename = str(i).split('\\')[-1]
    if well in filename.split('_')[1]:
        well_list.append(filename)

for i in well_list:
    if '2' in i.split('_')[-1][1]:  # channel
        #print(i)
        green_list.append(i)

for i in green_list:
    print(i)
    im = io.imread('input/' + i)
    mng = plt.get_current_fig_manager()  # to get fullscreen image
    mng.window.state('zoomed')  # to get fullscreen image
    plt.imshow(im)
    x = plt.ginput(2, mouse_add=1, mouse_stop=3)  # 1 for left click, 2 for right
    print(x)
    plt.close()

    # having two clicks to set square we need to get min and max for x and y
    min_x = min(int(x[0][1]), int(x[1][1]))
    max_x = max(int(x[0][1]), int(x[1][1]))
    min_y = min(int(x[0][0]), int(x[1][0]))
    max_y = max(int(x[0][0]), int(x[1][0]))

    center_x = min_x + int((max_x - min_x) / 2)
    center_y = min_y + int((max_y - min_y) / 2)

    diff_x = max_x - min_x
    diff_y = max_y - min_y

    crop_size = max(diff_x, diff_y)

    crop = im[(center_x - int(crop_size / 2)):(center_x + int(crop_size / 2)),
           (center_y - int(crop_size / 2)):(center_y + int(crop_size / 2))]

    plt.imshow(crop)
    plt.waitforbuttonpress(timeout=1)
    plt.close()

    # Contrast stretching
    perc = np.percentile(crop, 99.5)
    contr = exposure.rescale_intensity(crop, in_range=(110, perc))  # or crop.max()?

    plt.imshow(contr, cmap='gray')
    plt.waitforbuttonpress(timeout=1)
    plt.close()

    # to get pseudocolors convert to RGP via appropriate LUT then sum.

