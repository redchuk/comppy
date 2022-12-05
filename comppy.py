import glob
from skimage import io
from matplotlib import pyplot as plt

i_path = 'input/*'

for i in glob.glob(i_path):
    filename = str(i).split('\\')[-1]
    print(filename)
    im = io.imread(i)
    mng = plt.get_current_fig_manager()
    mng.window.state('zoomed')
    plt.imshow(im)
    x = plt.ginput(1)
    print(x)
    plt.close()

    plt.imshow(im[int(x[0][1])-100:int(x[0][1])+100, int(x[0][0])-100:int(x[0][0])+100])
    plt.waitforbuttonpress(timeout=5)
    plt.close()


'''
    plt.imshow(im)
    plt.annotate('yay!', x[0])
    plt.waitforbuttonpress(timeout=5)

    plt.show()
    plt.close()
'''