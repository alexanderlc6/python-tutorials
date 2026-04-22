import re
import xml.dom.minidom

import numpy as np
from matplotlib import pyplot as plt
import PIL.Image
import pdb

dom = xml.dom.minidom.parse('annotations.xml')
root = dom.documentElement
# pdb.set_trace()

img_list = root.getElementsByTagName('image')

for img_i in img_list:
    # Get image info(name,size)
    img_name = img_i.getAttribute('name')
    img_size = (int(img_i.getAttribute('width')), int(img_i.getAttribute('height')))

    # Get label info
    mask_list = img_i.getElementsByTagName('task')
    polyline_list = img_i.getElementsByTagName('polyline')
    mask_info, polyline_info = [], []

    # Get mask label details
    for mask_i in mask_list:
        rle_convert_temp = [int(mask_i.getAttribute('left')), int(mask_i.getAttribute('top')), int(mask_i.getAttribute('width')), int(mask_i.getAttribute('height'))]
        mask_temp = [int(num) for num in re.findall(r'\d+', mask_i.getAttribute('rle'))]

        # Change rle data format to matrix format: [x1,y1,x2,y2]
        assert sum(mask_temp) == rle_convert_temp[2] * rle_convert_temp[3]

        M = np.zeros(rle_convert_temp[2], rle_convert_temp[3])
        N = len(mask_temp)
        n = 0
        val = 1
        for pos in range(N):
            val = not val
            for c in range(mask_temp[pos]):
                M[n] = val
                n += 1
        GEMFIELD = M.reshape(([rle_convert_temp[2], rle_convert_temp[3]]), order='F')
        count = 0
        ans = []
        for i in range(GEMFIELD.shape[0]):
            for j in range(GEMFIELD.shape[1]):
                if GEMFIELD[i][j] != 0:
                    count += 1
                    ans.append(j + rle_convert_temp[1])
                    ans.append(i + rle_convert_temp[0])
        mask_info.append(ans)

    # Get centerline label details, format: [x1,y1,x2,y2,x3,y3]
    for polyline_i in polyline_list:
        pattern = r'[-+]?[0-9]*\.?[0-9]?[0-9]'
        polyline_info.append([float(num) for num in re.findall(pattern, polyline_i.getAttribute('points'))])

    img_path = '/Users/alexlc/Products/src/AI/python-tutorials/resources/label_imgs/' + img_name
    img_temp = PIL.Image.open(img_path)
    plt.imshow(img_temp)

    for ii in range(len(polyline_info)):
        ans = polyline_info[ii]
        x, y = [], []
        for jj in range(int(len(ans) / 2)):
            x.append(ans[2 * jj + 1])
            y.append(ans[2 * jj])
            plt.plot(y, x, c='blue')
    for ii in range(len(mask_info)):
        ans2 = mask_info[ii]
        im2 = np.zeros(np.shape(img_temp)[:2], int)
        for jj in range(int(len(ans2) / 2)):
            im2[ans2[jj * 2], ans2[ii * 2 + 1]] = 1
        plt.imshow(im2, alpha=0.3)

    plt.show()
    # pdb.set_trace()