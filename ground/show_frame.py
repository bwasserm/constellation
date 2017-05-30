from pathlib import Path
from queue import Queue
import sys
import time

from PIL import Image
from PIL.ImageQt import ImageQt
from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import QApplication, QWidget, QLabel
from PyQt5.QtGui import QIcon, QPixmap

from ground_base import Frame, GroundBase


class GroundThread(QtCore.QThread):

    new_frame_signal = QtCore.pyqtBoundSignal()

    def __init__(self, target, queue):
        QtCore.QThread.__init__(self)
        self.func = target
        self.queue = queue
        print("created waiting thread")

    def handle_frame(self, frame):
        print("we got one", type(frame), frame.width, frame.height, frame.image.size, frame.image.getpixel((0,0)))
        self.queue.put(frame)
        self.new_frame_signal.emit()

    def run(self):
        print("waiting thread running")
        self.func()

class App(QWidget):

    def __init__(self):
        super().__init__()
        ground = GroundBase()
        ground.parse_args()
        
        self.image_queue = Queue()
        self.receive_thread = GroundThread(target=ground.wait_for_frames,
                                           queue=self.image_queue)
        print('a')
        ground.register_frame_received(self.receive_thread.handle_frame)
        print('c')
        self.receive_thread.new_frame_signal.connect(self.show_frame)
        print('d')
        self.receive_thread.start()
        print('b')

        self.setWindowTitle("Constellation Viewer")
        self.setGeometry(10, 10, 100, 100)
        self.label = QLabel(self)
        self.label.setText("No Image Yet")

        print("created app")
        self.show()

    @QtCore.pyqtSlot()
    def show_frame(self):
        if not self.image_queue.empty():
            frame = self.image_queue.pop()
            print(frame)
            im = frame.image
            qim = ImageQt(im)
            pix = QtGui.QPixmap.fromImage(qim)
            self.label.setPixmap(pix)
            self.resize(pix.width(), pix.height())
            self.show()
        

def main():
    app = QApplication(sys.argv)
    gui = App()

    #file_path = "color_bars.jpg"
    #im = Image.open(file_path)
    #qim = ImageQt(im)
    #pix = QtGui.QPixmap.fromImage(qim)
    #label = QLabel(gui)
    #label.setPixmap(pix)

    #ground.wait_for_frames()

    sys.exit(app.exec_())

if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.argv.extend(["--dest_addr=10002", "--listen_port=10003"])
    main()