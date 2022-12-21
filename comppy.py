import glob
import os
from skimage import io
from skimage import exposure
from matplotlib import pyplot as plt
import numpy as np
import logging
import subprocess
from datetime import datetime

logging.basicConfig(level=logging.INFO)
i_path = 'input/*'
# todo: plateid
well = input('well number(format B08):')
protein = input('protein(format N_D377Y):')
date = datetime.now().strftime('%Y%m%d')
folder = '_'.join([protein,
                   well,
                   date,
                   subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).decode('ascii').strip()  # git hash
                   ])
os.mkdir('output/' + folder)

well_list = []
green_list = []

for i in glob.glob(i_path):
    filename = str(i).split('\\')[-1]
    if well in filename.split('_')[1]:
        well_list.append(filename)

for i in well_list:
    if '2' in i.split('_')[-1][1]:  # channel
        # print(i)
        green_list.append(i)


def get_list_of_files(path, pattern_to_search):
    list_of_files = []
    for file in glob.glob(path):
        if pattern_to_search in file:
            list_of_files.append(file)
    return list_of_files


for i in green_list:
    print(i)
    im = io.imread('input/' + i)
    fov = '_'.join(i.split('_')[:3]) + '_'
    g_perc = np.percentile(im, 99.95)
    g_contr = exposure.rescale_intensity(im, in_range=(50, g_perc))
    mng = plt.get_current_fig_manager()  # to get fullscreen image
    mng.window.state('zoomed')  # to get fullscreen image
    plt.imshow(g_contr)
    x = plt.ginput(2, mouse_add=1, mouse_stop=3)  # 1 for left click, 2 for right
    print(x)
    plt.close()

    # todo: try instead of if + logging
    if x:
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

        for channel in get_list_of_files(i_path, fov):
            im = io.imread(channel)
            crop = im[(center_x - int(crop_size / 2)):(center_x + int(crop_size / 2)),
                   (center_y - int(crop_size / 2)):(center_y + int(crop_size / 2))]

            plt.imshow(crop)
            plt.waitforbuttonpress(timeout=0.5)
            plt.close()

            # Contrast stretching
            perc = np.percentile(crop, 99.5)
            contr = exposure.rescale_intensity(crop, in_range=(90, perc))  # or crop.max()?

            plt.imshow(contr, cmap='gray')
            plt.waitforbuttonpress(timeout=1)
            plt.close()
    # to get pseudocolors convert to RGP via appropriate LUT then sum.
