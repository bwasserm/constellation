import numpy as np
from matplotlib import pyplot as plt
from PIL import Image
from resizeimage import resizeimage

#Ballon grid parameters
ballonSize = 70
randRatio = .1 #how far should the balloons drift from dead center, 0 is no drift
dimX = 10
dimY = 10
gridSize = dimX*dimY

#Resize the imported image to fit the 
fd_img = open('C:/Users/jwest/Desktop/Packman.bmp')
img = Image.open(fd_img).convert('RGBA')
img = resizeimage.resize_contain(img, [dimX, dimY])
pix = np.array(img)

#reshape the array
pix = pix.reshape(-1, pix.shape[2])
pix = pix/255.0

#set up balloon location stuff
gridLocX = np.zeros(gridSize)
gridLocY = np.zeros(gridSize)
count = 0
for x in range(dimX):
    for y in range(dimY):
        gridLocX[count] = x + np.random.randn()*randRatio-(randRatio/2)
        gridLocY[count] = y + np.random.randn()*randRatio-(randRatio/2)
        count += 1
 
 #plot the ballon Grid
colors = np.random.rand(gridSize)
plt.scatter(gridLocY,gridLocX,s=ballonSize, c=pix, alpha=1)
plt.gca().set_facecolor('black')
plt.axes().set_aspect('equal', 'datalim')
plt.show()

