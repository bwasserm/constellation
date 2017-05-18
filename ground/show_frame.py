from pathlib import Path
import sys
import time

from PIL import Image
from PIL.ImageQt import ImageQt
from PyQt5 import QtGui
from PyQt5.QtWidgets import QApplication, QWidget, QLabel
from PyQt5.QtGui import QIcon, QPixmap

from ground_base import Frame, GroundBase

class App(QWidget):

    def __init__(self):
        super().__init__()

    def handle_frame(self, frame):
        print("we got one", type(frame), frame.width, frame.height, frame.image.size, frame.image.getpixel((0,0)))
        #im = frame.image
        #qim = ImageQt(im)
        #pix = QtGui.QPixmap.fromImage(qim)
        #label = QLabel(self)
        #label.setPixmap(pix)
        #self.show()

def main():
    app = QApplication(sys.argv)
    gui = App()

    #file_path = "SMPTE_Color_Bars.svg.png"
    #im = Image.open(file_path)
    #qim = ImageQt(im)
    #pix = QtGui.QPixmap.fromImage(qim)
    #label = QLabel(gui)
    #label.setPixmap(pix)


    ground = GroundBase()
    ground.parse_args()
    ground.register_frame_received(gui.handle_frame)
    ground.wait_for_frames()

    #sys.exit(app.exec_())

if __name__ == '__main__':
    main()