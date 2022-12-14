import glob
from skimage import io
from matplotlib import pyplot as plt

i_path = 'input/*'

for i in glob.glob(i_path):
    filename = str(i).split('\\')[-1]
    channel = filename.split('_')[-1][1]
    print(filename + channel)
    im = io.imread(i)
    mng = plt.get_current_fig_manager()  # to get fullscreen image
    mng.window.state('zoomed')  # to get fullscreen image
    plt.imshow(im)
    x = plt.ginput(2)
    print(x)
    plt.close()

    # having two clicks to set square we need to get min and max for x and y
    min_x = min(int(x[0][1]), int(x[1][1]))
    max_x = max(int(x[0][1]), int(x[1][1]))
    min_y = min(int(x[0][0]), int(x[1][0]))
    max_y = max(int(x[0][0]), int(x[1][0]))

    center_x = min_x + int((max_x - min_x) / 2)
    center_y = min_y + int((max_y - min_y) / 2)

    print('cx'+str(center_x))
    print('cy' + str(center_y))

    diff_x = max_x - min_x
    diff_y = max_y - min_y

    print('dx'+str(diff_x))
    print('dy' + str(diff_y))


    crop_size = max(diff_x, diff_y)
    print(crop_size)


    crop = im[(center_x - int(crop_size / 2)):(center_x + int(crop_size / 2)),
              (center_y - int(crop_size / 2)):(center_y + int(crop_size / 2))]
    print(crop.shape)

    plt.imshow(crop)
    plt.waitforbuttonpress(timeout=5)
    plt.close()

    break
'''
    plt.imshow(im)
    plt.annotate('yay!', x[0])
    plt.waitforbuttonpress(timeout=5)

    plt.show()
    plt.close()
'''
