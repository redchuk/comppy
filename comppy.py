import glob
from skimage import io
from matplotlib import pyplot as plt

i_path = 'input/plate2_B01_s3_w13F8D900F-FF8D-440D-921D-51C21118670B.tif'


for i in glob.glob(i_path):

    filename = str(i).split('\\')[-1]
    print (filename)
    stack = io.imread(i)
    plt.imshow(stack)
    x = plt.ginput(2)
    print(x)
    plt.close()

    plt.imshow(stack)
    plt.annotate('yay!', x[0])
    plt.waitforbuttonpress(timeout=5)

    plt.show()
    plt.close()
    break