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


# todo: save originals (separate folder)
# todo: make composite if right click on crop that was shown
# todo: scalebar (thickness and xy according to crop size)
# todo: gaussian blur on green channel to denoise? 0.9
# to get pseudocolors convert to RGB via appropriate LUT then sum.

def random_str():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))


def get_list_of_files(path, pattern_to_search):
    list_of_files = []
    for file in glob.glob(path):
        if pattern_to_search in file:
            list_of_files.append(file)
    list_of_files.sort()
    return list_of_files


def to_cmyk(arr, color='k'):
    arr = arr.astype('float32') / arr.astype('float32').max()
    a = arr
    b = np.zeros(a.shape, dtype='float32')
    if color == 'c':
        order = [b, a, a]
    elif color == 'm':
        order = [a, b, a]
    elif color == 'y':
        order = [a, a, b]
    else:
        order = [a, a, a]

    return np.stack(order, axis=2)


def scalebar(image):
    # Scale bar, 10 microns (10/0.335=30pxs)
    height = image.shape[0]
    width = image.shape[0]
    region_height = int(height * 0.02)
    region_width = 30
    start_x = int(height * 0.95) - region_height
    start_y = int(width * 0.95) - region_width
    region = image[start_x:start_x + region_height, start_y:start_y + region_width, :]
    region[:, :] = 1


i_path = 'input/*'

plate_id = 'plid' + input('plate_id:')
well = input('well number:')
protein = input('protein:')
date = datetime.now().strftime('%Y%m%d')
git_hash = 'git_' + subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).decode('ascii').strip()

# in tuple, [0] is background, and [1] is np.percentile!!!
min_max_histo = [(110, 99.9, 'dapi'),
                 (95, 99.5, '2dab'),
                 (200, 99.9, 'phal'),
                 (200, 98.5, 'cona'),
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

for i in green_list:
    logging.basicConfig(level=logging.INFO, filename=('output' + ('/' + folder) * 2 + '.log'))
    logging.info(i)
    im = io.imread('input/' + i)
    fov = '_'.join(i.split('_')[:3]) + '_'
    g_perc = np.percentile(im, 99.95)
    g_contr = exposure.rescale_intensity(im, in_range=(100, g_perc))
    x = ['dummy']  # to iterate through list, later x = input

    while x:
        try:
            mng = plt.get_current_fig_manager()  # to get fullscreen image
            mng.window.state('zoomed')  # to get fullscreen image
            plt.imshow(g_contr)
            x = plt.ginput(2, mouse_add=1, mouse_stop=3, timeout=60)  # 1 for left click, 3 for right
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

            plt.figure(figsize=(12.5, 12.5), dpi=300)

            channels = []
            rand_str = random_str()  # every crop has its own unique identifier (all channels have the same)
            for ch_number, channel in enumerate(get_list_of_files(i_path, fov)):
                im = io.imread(channel)
                crop = im[(center_x - int(crop_size / 2)):(center_x + int(crop_size / 2)),
                       (center_y - int(crop_size / 2)):(center_y + int(crop_size / 2))]

                # plt.imshow(crop)
                # plt.waitforbuttonpress(timeout=0.5)
                # plt.close()

                # Contrast stretching
                contr = exposure.rescale_intensity(crop, in_range=(min_max_histo[ch_number][0],
                                                                   np.percentile(crop, min_max_histo[ch_number][1])))
                channels.append(contr)
                plt.subplot(1, 5, (ch_number + 1))
                plt.imshow(contr, cmap='gray')
                plt.axis('off')
                # plt.waitforbuttonpress(timeout=0.5)
                # plt.close()

                filename = '_'.join([protein,
                                     plate_id,
                                     well,
                                     channel.split('_')[2],  # fov according filename from MD Nano imager
                                     min_max_histo[ch_number][2],  # channel / dye
                                     rand_str,
                                     ]) + '.tiff'
                plt.imsave(('output/' + (folder + '/') + filename), contr, cmap='gray')
                logging.info('written to file ' + ('output/' + (folder + '/') + filename))
            c_channels = [to_cmyk(channels[0]) * .8,
                          to_cmyk(channels[1], 'y'),
                          to_cmyk(channels[2], 'c') / 0.8,
                          to_cmyk(channels[3], 'm') * .95]
            norm = (np.sum(c_channels, axis=0) / np.sum(c_channels, axis=0).max()) / 0.55  # first normalized, then br
            scalebar(norm)

            plt.subplot(1, 5, 5)
            plt.imshow(norm)
            plt.axis('off')

            # to get more than 1 crop from an image
            plt.tight_layout(pad=0.5)
            composite_name = '_'.join([protein,
                                       plate_id,
                                       well,
                                       'cmyk',
                                       rand_str,
                                       ]) + '.tiff'
            plt.savefig(('output/' + (folder + '/') + composite_name), bbox_inches='tight')
            logging.info('written to file ' + ('output/' + (folder + '/') + composite_name))
            mng = plt.get_current_fig_manager()  # to get fullscreen image
            mng.window.state('zoomed')  # to get fullscreen image
            plt.show()
            plt.waitforbuttonpress(timeout=10)
            plt.close()

        except Exception:
            logging.info('no (more) proper input coordinates for cropping')
    #break  # remove before flight!
