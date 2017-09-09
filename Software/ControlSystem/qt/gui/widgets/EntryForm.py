#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Thomas Wester <twester@mit.edu>
# Device/channel entry form

from PyQt5.QtWidgets import QGridLayout, QHBoxLayout, QVBoxLayout, \
                            QLineEdit, QLabel, QPushButton, QComboBox, \
                            QFrame, QWidget
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from PyQt5.QtGui import QFont

class EntryForm(QWidget):

    _save_changes_signal = pyqtSignal(dict)

    def __init__(self, title, subtitle, properties, parent=None):
        super().__init__()
        self._title = title
        self._subtitle = subtitle
        self._properties = properties
        self._parent = parent

        self._property_list = sorted([(name, x) for name, x in self._properties.items()], 
                                     key=lambda y: y[1]['display_order'])

        # create the entry form widget
        self._widget_layout = QGridLayout()

        for i, prop in enumerate(self._property_list):
            lbl = QLabel(prop[1]['display_name'])

            self._widget_layout.addWidget(lbl, i, 0)

            if prop[1]['entry_type'] == 'text':
                txt = QLineEdit(str(prop[1]['value']))
                self._widget_layout.addWidget(txt, i, 1)

            elif prop[1]['entry_type'] == 'combo':
                cb = QComboBox()
                cb.addItems(prop[1]['defaults'])
                cb.setCurrentIndex(prop[1]['defaults'].index(prop[1]['value']))
                self._widget_layout.addWidget(cb, i, 1)

        self._widget = QFrame()
        self._layout = QVBoxLayout()
        self._widget.setLayout(self._layout)

        lblTitle = QLabel(self._title)
        font = QFont()
        font.setPointSize(14)
        lblTitle.setFont(font)

        lblSubtitle = QLabel(self._subtitle)
        btnSave = QPushButton('Save Changes')
        btnSave.clicked.connect(lambda: self.on_save_changes_click())

        hbox = QHBoxLayout()
        hbox.addStretch()
        hbox.addWidget(btnSave)
        hbox.addStretch()

        self._layout.addWidget(lblTitle)
        self._layout.addWidget(lblSubtitle)
        self._layout.addLayout(self._widget_layout)
        self._layout.addLayout(hbox)
        self._layout.addStretch()

        if self._parent is not None:
            btnDelete = QPushButton('Delete')
            btnDelete.clicked.connect(self.on_delete_click)
            hbox = QHBoxLayout()
            hbox.addStretch()
            hbox.addWidget(btnDelete)
            hbox.addStretch()
            self._layout.addLayout(hbox)

    @pyqtSlot()
    def on_save_changes_click(self):
        newvals = {}
        for i, prop in enumerate(self._property_list):
            widget = self._widget_layout.itemAt(2 * i + 1).widget()
            if prop[1]['entry_type'] == 'text':
                val = widget.text().strip()
            elif prop[1]['entry_type'] == 'combo':
                val = widget.currentText()

            newvals[prop[0]] = val

        self._save_changes_signal.emit(newvals)

    def on_delete_click(self):
        print('test')

    @property
    def widget(self):
        return self._widget

    @property
    def save_signal(self):
        return self._save_changes_signal