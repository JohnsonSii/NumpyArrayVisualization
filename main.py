import sys
from PyQt5.QtCore import Qt, QPoint, QSize, QPointF
from PyQt5.QtGui import QPixmap, QPainter, QImage
from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel, QSizePolicy, QMessageBox
from PIL import Image
import numpy as np
import pickle
from matplotlib import pyplot as plt

from framework import Ui_MainWindow
from component import VisualizationFrameworkLabel
from tools import judgeInputType, dataReshape, dataTranspose


class VFLabel(VisualizationFrameworkLabel):
    def __init__(self, parent):
        super().__init__(parent)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super().dragEnterEvent(event)

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                NumpyShowWindow.FILE_PATH = url.toLocalFile()
                npShowWin.pushButton_binary.setText("二值化 (Binary)")
                if judgeInputType(NumpyShowWindow.FILE_PATH) == 'img':
                    self.setPixmap(QPixmap(NumpyShowWindow.FILE_PATH))
                    img = Image.open(NumpyShowWindow.FILE_PATH)
                    img.save('tmp.png')
                    npShowWin.lineEdit_shape.setText(f"W: {img.size[0]}, H: {img.size[1]}")
                    npShowWin.cache_data = img
                else:
                    with open(NumpyShowWindow.FILE_PATH, 'rb') as rf:
                        data = pickle.load(rf)
                        if type(data) == np.ndarray:
                            if len(data.shape) == 2:
                                data = np.expand_dims(data, axis=-1)
                                data = np.expand_dims(data, axis=0)
                            if len(data.shape) == 3:
                                data = np.expand_dims(data, axis=-1)
                            npShowWin.lineEdit_shape.setText(f"{data.shape}")
                            npShowWin.cache_data = data
                            npShowWin.data_shape = data.shape
                            npShowWin.data_transpose = tuple(range(len(data.shape)))
                            npShowWin.lineEdit_reshape.setText(f"{npShowWin.data_shape}")
                            npShowWin.lineEdit_transpose.setText(f"{npShowWin.data_transpose}")
                            npShowWin.page = 0
                            npShowWin.horizontalSlider.setRange(0, data.shape[-1] - 1)
                            if data.shape[-1] == 1 or data.shape[-1] == 3:
                                npShowWin.paintHandle()
                            else:
                                npShowWin.paintSingleChannelHandle()
        else:
            super().dropEvent(event)


class NumpyShowWindow(QMainWindow, Ui_MainWindow):
    FILE_PATH = ""

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.label_img = VFLabel(self.frame_main)
        self.label_img.setText("")
        self.label_img.setObjectName("label_img")
        self.gridLayout.addWidget(self.label_img, 0, 0, 1, 1)
        self.pushButton_binary.clicked.connect(self.binaryImage)
        self.pushButton_reshape.clicked.connect(self.dataReshapeHandle)
        self.pushButton_transpose.clicked.connect(self.dataTransposeHandle)
        self.pushButton_paint.clicked.connect(self.paintHandle)
        self.pushButton_next.clicked.connect(self.nextPageHandle)
        self.pushButton_last.clicked.connect(self.lastPageHandle)
        self.pushButton_page.clicked.connect(self.jumpPageHandle)
        self.pushButton_channel.clicked.connect(self.paintSingleChannelHandle)
        self.horizontalSlider.valueChanged.connect(self.onSliderValueChanged)
        self.lineEdit_channel.setText("0")

        self.cache_data = None
        self.data_shape = None
        self.data_transpose = None
        self.page = 0
        self.current_channel = 0

    def onSliderValueChanged(self, value):
        self.lineEdit_channel.setText(str(value))

    def binaryImage(self):
        if judgeInputType(NumpyShowWindow.FILE_PATH) == 'img':
            if self.pushButton_binary.text() == "二值化 (Binary)":
                self.cache_data = Image.open('tmp.png')
                self.cache_data.convert('1').save('tmp.png')
                self.label_img.setPixmap(QPixmap('tmp.png'))
                self.pushButton_binary.setText("恢复 (Recover)")
            else:
                self.cache_data.save('tmp.png')
                self.label_img.setPixmap(QPixmap('tmp.png'))
                self.pushButton_binary.setText("二值化 (Binary)")

    def dataReshapeHandle(self):
        if self.cache_data is not None:
            shape = eval(self.lineEdit_reshape.text())
            res = dataReshape(self.cache_data, shape)
            if res is not None:
                self.cache_data = res
                self.data_shape = shape
                self.lineEdit_shape.setText(f"{shape}")
                self.horizontalSlider.setRange(0, self.cache_data.shape[-1] - 1)
                self.page = 0
                self.lineEdit_page.setText("0")
            else:
                QMessageBox.information(self, "错误 (Error)", "非法形状输入 (Illegal shape input)")
                self.lineEdit_reshape.setText(f"{self.data_shape}")
                self.lineEdit_transpose.setText(f"{self.data_transpose}")

    def dataTransposeHandle(self):
        if self.cache_data is not None:
            shape = eval(self.lineEdit_transpose.text())
            res = dataTranspose(self.cache_data, shape)
            if res is not None:
                self.cache_data = res
                self.data_shape = res.shape
                self.lineEdit_shape.setText(f"{res.shape}")
                self.lineEdit_reshape.setText(f"{res.shape}")
                self.lineEdit_transpose.setText(f"{self.data_transpose}")
                self.horizontalSlider.setRange(0, self.cache_data.shape[-1] - 1)
                self.page = 0
                self.lineEdit_page.setText("0")
            else:
                QMessageBox.information(self, "错误 (Error)", "非法形状输入 (Illegal shape input)")
                self.lineEdit_reshape.setText(f"{self.data_shape}")
                self.lineEdit_transpose.setText(f"{self.data_transpose}")

    def paintHandle(self):
        if self.cache_data is not None:
            if self.cache_data.shape[-1] == 1 or self.cache_data.shape[-1] == 3:
                fig, ax = plt.subplots()
                ax.imshow(self.cache_data[self.page], cmap=self.comboBox.currentText())
                ax.axis('off')
                fig.savefig('tmp.png', bbox_inches='tight', pad_inches=0)
                plt.close()
                self.lineEdit_page.setText(f"{self.page}")
                self.label_img.setPixmap(QPixmap('tmp.png'))
            else:
                QMessageBox.information(self, "错误 (Error)",
                                        "多通道图像请选择绘制单通道 (For multi-channel images, please choose to draw one channel)")

    def paintSingleChannelHandle(self):
        if self.cache_data is not None:
            try:
                if self.lineEdit_channel.text() != "":
                    current_channel = int(eval(self.lineEdit_channel.text()))

                    fig, ax = plt.subplots()
                    img = self.cache_data[self.page].transpose((2, 0, 1))[current_channel]
                    ax.imshow(img, cmap=self.comboBox.currentText())
                    ax.axis('off')
                    fig.savefig('tmp.png', bbox_inches='tight', pad_inches=0)
                    plt.close()
                    self.lineEdit_page.setText(f"{self.page}")
                    self.label_img.setPixmap(QPixmap('tmp.png'))
                    self.current_channel = current_channel
            except:
                QMessageBox.information(self, "错误 (Error)", "非法通道输入 (Illegal channel input)")
                self.lineEdit_channel.setText(f"{self.current_channel}")

    def nextPageHandle(self):
        if self.cache_data is not None:
            page = self.page + 1
            if page >= 0 and page < self.cache_data.shape[0]:
                self.page = page
                if self.cache_data.shape[-1] == 1 or self.cache_data.shape[-1] == 3:
                    self.paintHandle()
                else:
                    self.paintSingleChannelHandle()

    def lastPageHandle(self):
        if self.cache_data is not None:
            page = self.page - 1
            if page >= 0 and page < self.cache_data.shape[0]:
                self.page = page
                if self.cache_data.shape[-1] == 1 or self.cache_data.shape[-1] == 3:
                    self.paintHandle()
                else:
                    self.paintSingleChannelHandle()

    def jumpPageHandle(self):
        if self.cache_data is not None:
            try:
                page = int(self.lineEdit_page.text())
                if page >= 0 and page < self.cache_data.shape[0]:
                    self.page = page
                    if self.cache_data.shape[-1] == 1 or self.cache_data.shape[-1] == 3:
                        self.paintHandle()
                    else:
                        self.paintSingleChannelHandle()
                else:
                    self.lineEdit_page.setText(f"{self.page}")
            except:
                QMessageBox.information(self, "错误 (Error)", "非法页码输入 (Illegal page input)")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    npShowWin = NumpyShowWindow()
    npShowWin.show()
    sys.exit(app.exec_())
