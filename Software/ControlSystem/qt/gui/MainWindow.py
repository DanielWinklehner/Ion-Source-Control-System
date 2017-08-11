#!/usr/bin/env python

from PyQt5.QtWidgets import QApplication, QMainWindow

from .ui_MainWindow import Ui_MainWindow

class MainWindow(QMainWindow):

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        ## connect menu bar handlers
        self.ui.btnQuit.clicked.connect(self.close)

        ## remove the temporary rate label
        self.ui.label_2.deleteLater()

        ## set status message
        self.ui.statusBar.showMessage('test')


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    mainwindow = MainWindow()
    mainwindow.show()

    sys.exit(app.exec_())
