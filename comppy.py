import glob
import os
from skimage import io
from skimage import exposure
from matplotlib import pyplot as plt
import numpy as np
import logging
import subprocess
from datetime import datetime
import random
import string

i_path = 'input/*'

plate_id = 'plid' + input('plate_id:')
well = input('well number:')
protein = input('protein:')
date = datetime.now().strftime('%Y%m%d')
git_hash = 'git_' + subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).decode('ascii').strip()
random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))

# in tuple, [0] is background, and [1] is np.percentile!!!
min_max_histo = [(110, 99.9),
                 (100, 99.0),
                 (200, 99.9),
                 (200, 98.5),
                 ]

folder = '_'.join([protein,
                   plate_id,
                   well,
                   git_hash,
                   ])
os.makedirs('output/' + folder, exist_ok=True)

well_list = []
green_list = []

for i in glob.glob(i_path):
    filename = str(i).split('\\')[-1]
    if well in filename.split('_')[1]:
        well_list.append(filename)

if not well_list:
    logging.info('no files for this well')

for i in well_list:
    if '2' in i.split('_')[-1][1]:  # channel
        # print(i)
        green_list.append(i)


def get_list_of_files(path, pattern_to_search):
    list_of_files = []
    for file in glob.glob(path):
        if pattern_to_search in file:
            list_of_files.append(file)
    list_of_files.sort()
    return list_of_files


for i in green_list:
    logging.basicConfig(level=logging.INFO, filename=('output' + ('/' + folder) * 2 + '.log'))
    logging.info(i)
    im = io.imread('input/' + i)
    fov = '_'.join(i.split('_')[:3]) + '_'
    g_perc = np.percentile(im, 99.95)
    g_contr = exposure.rescale_intensity(im, in_range=(50, g_perc))
    mng = plt.get_current_fig_manager()  # to get fullscreen image
    mng.window.state('zoomed')  # to get fullscreen image
    plt.imshow(g_contr)
    x = plt.ginput(2, mouse_add=1, mouse_stop=3)  # 1 for left click, 2 for right
    plt.close()

    try:
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

        for ch_number, channel in enumerate(get_list_of_files(i_path, fov)):  # todo:

            im = io.imread(channel)
            crop = im[(center_x - int(crop_size / 2)):(center_x + int(crop_size / 2)),
                      (center_y - int(crop_size / 2)):(center_y + int(crop_size / 2))]

            plt.imshow(crop)
            plt.waitforbuttonpress(timeout=0.5)
            plt.close()

            # Contrast stretching
            contr = exposure.rescale_intensity(crop, in_range=(min_max_histo[ch_number][0],
                                           np.percentile(crop, min_max_histo[ch_number][1])))

            plt.imshow(contr, cmap='gray')
            plt.waitforbuttonpress(timeout=1)
            plt.close()

            filename = '_'.join([protein,
                                 plate_id,
                                 well,
                                 random_str,
                                 ])

    except Exception:
        logging.info('no proper input coordinates for cropping')

    # to get pseudocolors convert to RGP via appropriate LUT then sum.
