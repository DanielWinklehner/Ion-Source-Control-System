# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'designer/ProcedureDialog.ui'
#
# Created by: PyQt5 UI code generator 5.5.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_ProcedureDialog(object):
    def setupUi(self, ProcedureDialog):
        ProcedureDialog.setObjectName("ProcedureDialog")
        ProcedureDialog.resize(1106, 876)
        font = QtGui.QFont()
        font.setFamily("Ubuntu")
        font.setPointSize(12)
        ProcedureDialog.setFont(font)
        self.verticalLayout = QtWidgets.QVBoxLayout(ProcedureDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_7 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_7.addItem(spacerItem)
        self.label = QtWidgets.QLabel(ProcedureDialog)
        self.label.setObjectName("label")
        self.horizontalLayout_7.addWidget(self.label)
        self.txtProcedureName = QtWidgets.QLineEdit(ProcedureDialog)
        self.txtProcedureName.setAlignment(QtCore.Qt.AlignCenter)
        self.txtProcedureName.setObjectName("txtProcedureName")
        self.horizontalLayout_7.addWidget(self.txtProcedureName)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_7.addItem(spacerItem1)
        self.verticalLayout.addLayout(self.horizontalLayout_7)
        self.tabWidget = QtWidgets.QTabWidget(ProcedureDialog)
        self.tabWidget.setObjectName("tabWidget")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.tab)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.groupBox_2 = QtWidgets.QGroupBox(self.tab)
        self.groupBox_2.setObjectName("groupBox_2")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.groupBox_2)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.rbValue = QtWidgets.QRadioButton(self.groupBox_2)
        self.rbValue.setChecked(True)
        self.rbValue.setObjectName("rbValue")
        self.gridLayout_3.addWidget(self.rbValue, 0, 0, 1, 1)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem2)
        self.cbRuleDevice = QtWidgets.QComboBox(self.groupBox_2)
        self.cbRuleDevice.setCurrentText("")
        self.cbRuleDevice.setObjectName("cbRuleDevice")
        self.horizontalLayout_3.addWidget(self.cbRuleDevice)
        self.label_3 = QtWidgets.QLabel(self.groupBox_2)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout_3.addWidget(self.label_3)
        self.cbRuleChannel = QtWidgets.QComboBox(self.groupBox_2)
        self.cbRuleChannel.setCurrentText("")
        self.cbRuleChannel.setObjectName("cbRuleChannel")
        self.horizontalLayout_3.addWidget(self.cbRuleChannel)
        self.label_4 = QtWidgets.QLabel(self.groupBox_2)
        self.label_4.setObjectName("label_4")
        self.horizontalLayout_3.addWidget(self.label_4)
        self.cbRuleCompare = QtWidgets.QComboBox(self.groupBox_2)
        self.cbRuleCompare.setCurrentText("")
        self.cbRuleCompare.setObjectName("cbRuleCompare")
        self.horizontalLayout_3.addWidget(self.cbRuleCompare)
        self.cbRuleBool = QtWidgets.QComboBox(self.groupBox_2)
        self.cbRuleBool.setObjectName("cbRuleBool")
        self.horizontalLayout_3.addWidget(self.cbRuleBool)
        self.txtRuleVal = QtWidgets.QLineEdit(self.groupBox_2)
        self.txtRuleVal.setAlignment(QtCore.Qt.AlignCenter)
        self.txtRuleVal.setObjectName("txtRuleVal")
        self.horizontalLayout_3.addWidget(self.txtRuleVal)
        self.lblRuleUnit = QtWidgets.QLabel(self.groupBox_2)
        self.lblRuleUnit.setObjectName("lblRuleUnit")
        self.horizontalLayout_3.addWidget(self.lblRuleUnit)
        spacerItem3 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem3)
        self.gridLayout_3.addLayout(self.horizontalLayout_3, 0, 1, 1, 1)
        self.rbEvent = QtWidgets.QRadioButton(self.groupBox_2)
        self.rbEvent.setObjectName("rbEvent")
        self.gridLayout_3.addWidget(self.rbEvent, 1, 0, 1, 1)
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        spacerItem4 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_5.addItem(spacerItem4)
        self.cbEvent = QtWidgets.QComboBox(self.groupBox_2)
        self.cbEvent.setEnabled(False)
        self.cbEvent.setObjectName("cbEvent")
        self.horizontalLayout_5.addWidget(self.cbEvent)
        spacerItem5 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_5.addItem(spacerItem5)
        self.gridLayout_3.addLayout(self.horizontalLayout_5, 1, 1, 1, 1)
        self.rbManual = QtWidgets.QRadioButton(self.groupBox_2)
        self.rbManual.setObjectName("rbManual")
        self.gridLayout_3.addWidget(self.rbManual, 2, 0, 1, 1)
        self.verticalLayout_2.addWidget(self.groupBox_2)
        self.groupBox_3 = QtWidgets.QGroupBox(self.tab)
        self.groupBox_3.setMaximumSize(QtCore.QSize(16777215, 475))
        self.groupBox_3.setObjectName("groupBox_3")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.groupBox_3)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.horizontalLayout_8 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_8.setObjectName("horizontalLayout_8")
        self.label_2 = QtWidgets.QLabel(self.groupBox_3)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_8.addWidget(self.label_2)
        self.cbActionDevice = QtWidgets.QComboBox(self.groupBox_3)
        self.cbActionDevice.setCurrentText("")
        self.cbActionDevice.setObjectName("cbActionDevice")
        self.horizontalLayout_8.addWidget(self.cbActionDevice)
        self.label_5 = QtWidgets.QLabel(self.groupBox_3)
        self.label_5.setObjectName("label_5")
        self.horizontalLayout_8.addWidget(self.label_5)
        self.cbActionChannel = QtWidgets.QComboBox(self.groupBox_3)
        self.cbActionChannel.setCurrentText("")
        self.cbActionChannel.setObjectName("cbActionChannel")
        self.horizontalLayout_8.addWidget(self.cbActionChannel)
        self.label_6 = QtWidgets.QLabel(self.groupBox_3)
        self.label_6.setObjectName("label_6")
        self.horizontalLayout_8.addWidget(self.label_6)
        self.cbActionBool = QtWidgets.QComboBox(self.groupBox_3)
        self.cbActionBool.setObjectName("cbActionBool")
        self.horizontalLayout_8.addWidget(self.cbActionBool)
        self.txtActionVal = QtWidgets.QLineEdit(self.groupBox_3)
        self.txtActionVal.setAlignment(QtCore.Qt.AlignCenter)
        self.txtActionVal.setObjectName("txtActionVal")
        self.horizontalLayout_8.addWidget(self.txtActionVal)
        self.lblActionUnit = QtWidgets.QLabel(self.groupBox_3)
        self.lblActionUnit.setObjectName("lblActionUnit")
        self.horizontalLayout_8.addWidget(self.lblActionUnit)
        spacerItem6 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_8.addItem(spacerItem6)
        self.label_7 = QtWidgets.QLabel(self.groupBox_3)
        self.label_7.setObjectName("label_7")
        self.horizontalLayout_8.addWidget(self.label_7)
        self.lineEdit = QtWidgets.QLineEdit(self.groupBox_3)
        self.lineEdit.setMaxLength(10)
        self.lineEdit.setAlignment(QtCore.Qt.AlignCenter)
        self.lineEdit.setObjectName("lineEdit")
        self.horizontalLayout_8.addWidget(self.lineEdit)
        self.label_8 = QtWidgets.QLabel(self.groupBox_3)
        self.label_8.setObjectName("label_8")
        self.horizontalLayout_8.addWidget(self.label_8)
        spacerItem7 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_8.addItem(spacerItem7)
        self.btnAddAction = QtWidgets.QPushButton(self.groupBox_3)
        self.btnAddAction.setObjectName("btnAddAction")
        self.horizontalLayout_8.addWidget(self.btnAddAction)
        self.verticalLayout_3.addLayout(self.horizontalLayout_8)
        self.scAction = QtWidgets.QScrollArea(self.groupBox_3)
        self.scAction.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.scAction.setWidgetResizable(True)
        self.scAction.setObjectName("scAction")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 1032, 242))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.gridLayout = QtWidgets.QGridLayout(self.scrollAreaWidgetContents)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.fmActions = QtWidgets.QFrame(self.scrollAreaWidgetContents)
        self.fmActions.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.fmActions.setFrameShadow(QtWidgets.QFrame.Raised)
        self.fmActions.setObjectName("fmActions")
        self.gridLayout.addWidget(self.fmActions, 0, 0, 1, 1)
        self.scAction.setWidget(self.scrollAreaWidgetContents)
        self.verticalLayout_3.addWidget(self.scAction)
        self.verticalLayout_2.addWidget(self.groupBox_3)
        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.horizontalLayout_11 = QtWidgets.QHBoxLayout(self.tab_2)
        self.horizontalLayout_11.setObjectName("horizontalLayout_11")
        spacerItem8 = QtWidgets.QSpacerItem(281, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_11.addItem(spacerItem8)
        self.verticalLayout_5 = QtWidgets.QVBoxLayout()
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        spacerItem9 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_5.addItem(spacerItem9)
        self.verticalLayout_4 = QtWidgets.QVBoxLayout()
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.gridLayout_5 = QtWidgets.QGridLayout()
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.label_17 = QtWidgets.QLabel(self.tab_2)
        self.label_17.setObjectName("label_17")
        self.gridLayout_5.addWidget(self.label_17, 1, 0, 1, 1)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.cbPidDeviceRead = QtWidgets.QComboBox(self.tab_2)
        self.cbPidDeviceRead.setMinimumSize(QtCore.QSize(0, 0))
        self.cbPidDeviceRead.setCurrentText("")
        self.cbPidDeviceRead.setObjectName("cbPidDeviceRead")
        self.horizontalLayout_4.addWidget(self.cbPidDeviceRead)
        self.label_9 = QtWidgets.QLabel(self.tab_2)
        self.label_9.setObjectName("label_9")
        self.horizontalLayout_4.addWidget(self.label_9)
        self.cbPidChannelRead = QtWidgets.QComboBox(self.tab_2)
        self.cbPidChannelRead.setMinimumSize(QtCore.QSize(0, 0))
        self.cbPidChannelRead.setObjectName("cbPidChannelRead")
        self.cbPidChannelRead.addItem("")
        self.horizontalLayout_4.addWidget(self.cbPidChannelRead)
        self.gridLayout_5.addLayout(self.horizontalLayout_4, 0, 1, 1, 1)
        self.label_16 = QtWidgets.QLabel(self.tab_2)
        self.label_16.setObjectName("label_16")
        self.gridLayout_5.addWidget(self.label_16, 0, 0, 1, 1)
        self.horizontalLayout_10 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_10.setObjectName("horizontalLayout_10")
        self.cbPidDeviceWrite = QtWidgets.QComboBox(self.tab_2)
        self.cbPidDeviceWrite.setMinimumSize(QtCore.QSize(0, 0))
        self.cbPidDeviceWrite.setCurrentText("")
        self.cbPidDeviceWrite.setObjectName("cbPidDeviceWrite")
        self.horizontalLayout_10.addWidget(self.cbPidDeviceWrite)
        self.label_15 = QtWidgets.QLabel(self.tab_2)
        self.label_15.setObjectName("label_15")
        self.horizontalLayout_10.addWidget(self.label_15)
        self.cbPidChannelWrite = QtWidgets.QComboBox(self.tab_2)
        self.cbPidChannelWrite.setMinimumSize(QtCore.QSize(0, 0))
        self.cbPidChannelWrite.setObjectName("cbPidChannelWrite")
        self.cbPidChannelWrite.addItem("")
        self.horizontalLayout_10.addWidget(self.cbPidChannelWrite)
        self.gridLayout_5.addLayout(self.horizontalLayout_10, 1, 1, 1, 1)
        self.label_10 = QtWidgets.QLabel(self.tab_2)
        self.label_10.setObjectName("label_10")
        self.gridLayout_5.addWidget(self.label_10, 2, 0, 1, 1)
        self.txtTarget = QtWidgets.QLineEdit(self.tab_2)
        self.txtTarget.setAlignment(QtCore.Qt.AlignCenter)
        self.txtTarget.setObjectName("txtTarget")
        self.gridLayout_5.addWidget(self.txtTarget, 2, 1, 1, 1)
        self.verticalLayout_4.addLayout(self.gridLayout_5)
        self.groupBox_5 = QtWidgets.QGroupBox(self.tab_2)
        self.groupBox_5.setObjectName("groupBox_5")
        self.gridLayout_4 = QtWidgets.QGridLayout(self.groupBox_5)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.label_11 = QtWidgets.QLabel(self.groupBox_5)
        self.label_11.setObjectName("label_11")
        self.gridLayout_4.addWidget(self.label_11, 0, 0, 1, 1)
        self.txtdt = QtWidgets.QLineEdit(self.groupBox_5)
        self.txtdt.setAlignment(QtCore.Qt.AlignCenter)
        self.txtdt.setObjectName("txtdt")
        self.gridLayout_4.addWidget(self.txtdt, 0, 1, 1, 1)
        self.label_12 = QtWidgets.QLabel(self.groupBox_5)
        self.label_12.setObjectName("label_12")
        self.gridLayout_4.addWidget(self.label_12, 1, 0, 1, 1)
        self.txtP = QtWidgets.QLineEdit(self.groupBox_5)
        self.txtP.setAlignment(QtCore.Qt.AlignCenter)
        self.txtP.setObjectName("txtP")
        self.gridLayout_4.addWidget(self.txtP, 1, 1, 1, 1)
        self.label_13 = QtWidgets.QLabel(self.groupBox_5)
        self.label_13.setObjectName("label_13")
        self.gridLayout_4.addWidget(self.label_13, 2, 0, 1, 1)
        self.txtI = QtWidgets.QLineEdit(self.groupBox_5)
        self.txtI.setAlignment(QtCore.Qt.AlignCenter)
        self.txtI.setObjectName("txtI")
        self.gridLayout_4.addWidget(self.txtI, 2, 1, 1, 1)
        self.label_14 = QtWidgets.QLabel(self.groupBox_5)
        self.label_14.setObjectName("label_14")
        self.gridLayout_4.addWidget(self.label_14, 3, 0, 1, 1)
        self.txtD = QtWidgets.QLineEdit(self.groupBox_5)
        self.txtD.setAlignment(QtCore.Qt.AlignCenter)
        self.txtD.setObjectName("txtD")
        self.gridLayout_4.addWidget(self.txtD, 3, 1, 1, 1)
        self.verticalLayout_4.addWidget(self.groupBox_5)
        self.verticalLayout_5.addLayout(self.verticalLayout_4)
        self.groupBox = QtWidgets.QGroupBox(self.tab_2)
        self.groupBox.setObjectName("groupBox")
        self.gridLayout_6 = QtWidgets.QGridLayout(self.groupBox)
        self.gridLayout_6.setObjectName("gridLayout_6")
        self.txtAverage = QtWidgets.QLineEdit(self.groupBox)
        self.txtAverage.setEnabled(True)
        self.txtAverage.setAlignment(QtCore.Qt.AlignCenter)
        self.txtAverage.setObjectName("txtAverage")
        self.gridLayout_6.addWidget(self.txtAverage, 0, 1, 1, 1)
        self.label_18 = QtWidgets.QLabel(self.groupBox)
        self.label_18.setObjectName("label_18")
        self.gridLayout_6.addWidget(self.label_18, 0, 2, 1, 1)
        self.txtWarmup = QtWidgets.QLineEdit(self.groupBox)
        self.txtWarmup.setEnabled(True)
        self.txtWarmup.setAlignment(QtCore.Qt.AlignCenter)
        self.txtWarmup.setObjectName("txtWarmup")
        self.gridLayout_6.addWidget(self.txtWarmup, 1, 1, 1, 1)
        self.label_19 = QtWidgets.QLabel(self.groupBox)
        self.label_19.setObjectName("label_19")
        self.gridLayout_6.addWidget(self.label_19, 1, 2, 1, 1)
        self.txtOffset = QtWidgets.QLineEdit(self.groupBox)
        self.txtOffset.setEnabled(True)
        self.txtOffset.setAlignment(QtCore.Qt.AlignCenter)
        self.txtOffset.setObjectName("txtOffset")
        self.gridLayout_6.addWidget(self.txtOffset, 2, 1, 1, 1)
        self.lblUnit = QtWidgets.QLabel(self.groupBox)
        self.lblUnit.setObjectName("lblUnit")
        self.gridLayout_6.addWidget(self.lblUnit, 2, 2, 1, 1)
        self.label_20 = QtWidgets.QLabel(self.groupBox)
        self.label_20.setObjectName("label_20")
        self.gridLayout_6.addWidget(self.label_20, 0, 0, 1, 1)
        self.label_21 = QtWidgets.QLabel(self.groupBox)
        self.label_21.setObjectName("label_21")
        self.gridLayout_6.addWidget(self.label_21, 1, 0, 1, 1)
        self.label_22 = QtWidgets.QLabel(self.groupBox)
        self.label_22.setObjectName("label_22")
        self.gridLayout_6.addWidget(self.label_22, 2, 0, 1, 1)
        self.verticalLayout_5.addWidget(self.groupBox)
        spacerItem10 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_5.addItem(spacerItem10)
        self.horizontalLayout_11.addLayout(self.verticalLayout_5)
        spacerItem11 = QtWidgets.QSpacerItem(281, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_11.addItem(spacerItem11)
        self.tabWidget.addTab(self.tab_2, "")
        self.tab_3 = QtWidgets.QWidget()
        self.tab_3.setObjectName("tab_3")
        self.horizontalLayout_17 = QtWidgets.QHBoxLayout(self.tab_3)
        self.horizontalLayout_17.setObjectName("horizontalLayout_17")
        spacerItem12 = QtWidgets.QSpacerItem(268, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_17.addItem(spacerItem12)
        self.verticalLayout_7 = QtWidgets.QVBoxLayout()
        self.verticalLayout_7.setObjectName("verticalLayout_7")
        spacerItem13 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_7.addItem(spacerItem13)
        self.groupBox_6 = QtWidgets.QGroupBox(self.tab_3)
        self.groupBox_6.setObjectName("groupBox_6")
        self.gridLayout_7 = QtWidgets.QGridLayout(self.groupBox_6)
        self.gridLayout_7.setObjectName("gridLayout_7")
        self.label_31 = QtWidgets.QLabel(self.groupBox_6)
        self.label_31.setObjectName("label_31")
        self.gridLayout_7.addWidget(self.label_31, 0, 0, 1, 1)
        self.horizontalLayout_14 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_14.setObjectName("horizontalLayout_14")
        self.cbTimerDeviceStart = QtWidgets.QComboBox(self.groupBox_6)
        self.cbTimerDeviceStart.setObjectName("cbTimerDeviceStart")
        self.horizontalLayout_14.addWidget(self.cbTimerDeviceStart)
        self.label_30 = QtWidgets.QLabel(self.groupBox_6)
        self.label_30.setAlignment(QtCore.Qt.AlignCenter)
        self.label_30.setObjectName("label_30")
        self.horizontalLayout_14.addWidget(self.label_30)
        self.cbTimerChannelStart = QtWidgets.QComboBox(self.groupBox_6)
        self.cbTimerChannelStart.setMinimumSize(QtCore.QSize(0, 0))
        self.cbTimerChannelStart.setObjectName("cbTimerChannelStart")
        self.cbTimerChannelStart.addItem("")
        self.horizontalLayout_14.addWidget(self.cbTimerChannelStart)
        self.gridLayout_7.addLayout(self.horizontalLayout_14, 0, 1, 1, 1)
        self.label_23 = QtWidgets.QLabel(self.groupBox_6)
        self.label_23.setObjectName("label_23")
        self.gridLayout_7.addWidget(self.label_23, 1, 0, 1, 1)
        self.horizontalLayout_12 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_12.setObjectName("horizontalLayout_12")
        self.cbTimerStartComp = QtWidgets.QComboBox(self.groupBox_6)
        self.cbTimerStartComp.setObjectName("cbTimerStartComp")
        self.cbTimerStartComp.addItem("")
        self.cbTimerStartComp.addItem("")
        self.horizontalLayout_12.addWidget(self.cbTimerStartComp)
        self.txtTimerStart = QtWidgets.QLineEdit(self.groupBox_6)
        self.txtTimerStart.setAlignment(QtCore.Qt.AlignCenter)
        self.txtTimerStart.setObjectName("txtTimerStart")
        self.horizontalLayout_12.addWidget(self.txtTimerStart)
        self.lblTimerStartUnit = QtWidgets.QLabel(self.groupBox_6)
        self.lblTimerStartUnit.setObjectName("lblTimerStartUnit")
        self.horizontalLayout_12.addWidget(self.lblTimerStartUnit)
        self.gridLayout_7.addLayout(self.horizontalLayout_12, 1, 1, 1, 1)
        self.verticalLayout_7.addWidget(self.groupBox_6)
        self.groupBox_7 = QtWidgets.QGroupBox(self.tab_3)
        self.groupBox_7.setObjectName("groupBox_7")
        self.gridLayout_8 = QtWidgets.QGridLayout(self.groupBox_7)
        self.gridLayout_8.setObjectName("gridLayout_8")
        self.label_33 = QtWidgets.QLabel(self.groupBox_7)
        self.label_33.setObjectName("label_33")
        self.gridLayout_8.addWidget(self.label_33, 0, 0, 1, 1)
        self.horizontalLayout_15 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_15.setObjectName("horizontalLayout_15")
        self.cbTimerDeviceStop = QtWidgets.QComboBox(self.groupBox_7)
        self.cbTimerDeviceStop.setObjectName("cbTimerDeviceStop")
        self.horizontalLayout_15.addWidget(self.cbTimerDeviceStop)
        self.label_35 = QtWidgets.QLabel(self.groupBox_7)
        self.label_35.setAlignment(QtCore.Qt.AlignCenter)
        self.label_35.setObjectName("label_35")
        self.horizontalLayout_15.addWidget(self.label_35)
        self.cbTimerChannelStop = QtWidgets.QComboBox(self.groupBox_7)
        self.cbTimerChannelStop.setMinimumSize(QtCore.QSize(0, 0))
        self.cbTimerChannelStop.setObjectName("cbTimerChannelStop")
        self.cbTimerChannelStop.addItem("")
        self.horizontalLayout_15.addWidget(self.cbTimerChannelStop)
        self.gridLayout_8.addLayout(self.horizontalLayout_15, 0, 1, 1, 1)
        self.label_24 = QtWidgets.QLabel(self.groupBox_7)
        self.label_24.setObjectName("label_24")
        self.gridLayout_8.addWidget(self.label_24, 1, 0, 1, 1)
        self.horizontalLayout_16 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_16.setObjectName("horizontalLayout_16")
        self.cbTimerStopComp = QtWidgets.QComboBox(self.groupBox_7)
        self.cbTimerStopComp.setObjectName("cbTimerStopComp")
        self.cbTimerStopComp.addItem("")
        self.cbTimerStopComp.addItem("")
        self.horizontalLayout_16.addWidget(self.cbTimerStopComp)
        self.txtTimerStop = QtWidgets.QLineEdit(self.groupBox_7)
        self.txtTimerStop.setAlignment(QtCore.Qt.AlignCenter)
        self.txtTimerStop.setObjectName("txtTimerStop")
        self.horizontalLayout_16.addWidget(self.txtTimerStop)
        self.lblTimerStopUnit = QtWidgets.QLabel(self.groupBox_7)
        self.lblTimerStopUnit.setObjectName("lblTimerStopUnit")
        self.horizontalLayout_16.addWidget(self.lblTimerStopUnit)
        self.gridLayout_8.addLayout(self.horizontalLayout_16, 1, 1, 1, 1)
        self.verticalLayout_7.addWidget(self.groupBox_7)
        self.groupBox_4 = QtWidgets.QGroupBox(self.tab_3)
        self.groupBox_4.setObjectName("groupBox_4")
        self.verticalLayout_6 = QtWidgets.QVBoxLayout(self.groupBox_4)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.horizontalLayout_13 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_13.setObjectName("horizontalLayout_13")
        self.label_34 = QtWidgets.QLabel(self.groupBox_4)
        self.label_34.setObjectName("label_34")
        self.horizontalLayout_13.addWidget(self.label_34)
        self.txtTimerMinTime = QtWidgets.QLineEdit(self.groupBox_4)
        self.txtTimerMinTime.setEnabled(True)
        self.txtTimerMinTime.setAlignment(QtCore.Qt.AlignCenter)
        self.txtTimerMinTime.setObjectName("txtTimerMinTime")
        self.horizontalLayout_13.addWidget(self.txtTimerMinTime)
        self.label_32 = QtWidgets.QLabel(self.groupBox_4)
        self.label_32.setObjectName("label_32")
        self.horizontalLayout_13.addWidget(self.label_32)
        self.verticalLayout_6.addLayout(self.horizontalLayout_13)
        self.chkTimerContinuous = QtWidgets.QCheckBox(self.groupBox_4)
        self.chkTimerContinuous.setObjectName("chkTimerContinuous")
        self.verticalLayout_6.addWidget(self.chkTimerContinuous)
        self.verticalLayout_7.addWidget(self.groupBox_4)
        spacerItem14 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_7.addItem(spacerItem14)
        self.horizontalLayout_17.addLayout(self.verticalLayout_7)
        spacerItem15 = QtWidgets.QSpacerItem(268, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_17.addItem(spacerItem15)
        self.tabWidget.addTab(self.tab_3, "")
        self.verticalLayout.addWidget(self.tabWidget)
        self.horizontalLayout_9 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_9.setObjectName("horizontalLayout_9")
        self.gbOptions = QtWidgets.QGroupBox(ProcedureDialog)
        self.gbOptions.setObjectName("gbOptions")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.gbOptions)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.chkCritical = QtWidgets.QCheckBox(self.gbOptions)
        self.chkCritical.setObjectName("chkCritical")
        self.horizontalLayout.addWidget(self.chkCritical)
        self.horizontalLayout_9.addWidget(self.gbOptions)
        self.gbNotify = QtWidgets.QGroupBox(ProcedureDialog)
        self.gbNotify.setObjectName("gbNotify")
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout(self.gbNotify)
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.chkEmail = QtWidgets.QCheckBox(self.gbNotify)
        self.chkEmail.setObjectName("chkEmail")
        self.horizontalLayout_6.addWidget(self.chkEmail)
        self.chkText = QtWidgets.QCheckBox(self.gbNotify)
        self.chkText.setObjectName("chkText")
        self.horizontalLayout_6.addWidget(self.chkText)
        self.horizontalLayout_9.addWidget(self.gbNotify)
        self.verticalLayout.addLayout(self.horizontalLayout_9)
        self.gbContact = QtWidgets.QGroupBox(ProcedureDialog)
        self.gbContact.setObjectName("gbContact")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.gbContact)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.txtText = QtWidgets.QLineEdit(self.gbContact)
        self.txtText.setObjectName("txtText")
        self.gridLayout_2.addWidget(self.txtText, 1, 2, 1, 1)
        spacerItem16 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_2.addItem(spacerItem16, 0, 3, 1, 1)
        self.lblText = QtWidgets.QLabel(self.gbContact)
        self.lblText.setObjectName("lblText")
        self.gridLayout_2.addWidget(self.lblText, 1, 1, 1, 1)
        self.lblEmail = QtWidgets.QLabel(self.gbContact)
        self.lblEmail.setObjectName("lblEmail")
        self.gridLayout_2.addWidget(self.lblEmail, 0, 1, 1, 1)
        self.txtEmail = QtWidgets.QLineEdit(self.gbContact)
        self.txtEmail.setObjectName("txtEmail")
        self.gridLayout_2.addWidget(self.txtEmail, 0, 2, 1, 1)
        spacerItem17 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_2.addItem(spacerItem17, 0, 0, 1, 1)
        spacerItem18 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_2.addItem(spacerItem18, 1, 3, 1, 1)
        spacerItem19 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_2.addItem(spacerItem19, 1, 0, 1, 1)
        self.verticalLayout.addWidget(self.gbContact)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacerItem20 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem20)
        self.btnDone = QtWidgets.QPushButton(ProcedureDialog)
        self.btnDone.setObjectName("btnDone")
        self.horizontalLayout_2.addWidget(self.btnDone)
        spacerItem21 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem21)
        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.retranslateUi(ProcedureDialog)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(ProcedureDialog)

    def retranslateUi(self, ProcedureDialog):
        _translate = QtCore.QCoreApplication.translate
        ProcedureDialog.setWindowTitle(_translate("ProcedureDialog", "Add/Edit Procedure"))
        self.label.setText(_translate("ProcedureDialog", "Name"))
        self.txtProcedureName.setText(_translate("ProcedureDialog", "My Procedure"))
        self.groupBox_2.setTitle(_translate("ProcedureDialog", "Rule"))
        self.rbValue.setText(_translate("ProcedureDialog", "Value"))
        self.label_3.setText(_translate("ProcedureDialog", "."))
        self.label_4.setText(_translate("ProcedureDialog", "is"))
        self.lblRuleUnit.setText(_translate("ProcedureDialog", "TextLabel"))
        self.rbEvent.setText(_translate("ProcedureDialog", "Event"))
        self.rbManual.setText(_translate("ProcedureDialog", "Manual"))
        self.groupBox_3.setTitle(_translate("ProcedureDialog", "Action"))
        self.label_2.setText(_translate("ProcedureDialog", "Set"))
        self.label_5.setText(_translate("ProcedureDialog", "."))
        self.label_6.setText(_translate("ProcedureDialog", "to"))
        self.lblActionUnit.setText(_translate("ProcedureDialog", "TextLabel"))
        self.label_7.setText(_translate("ProcedureDialog", "Delay:"))
        self.lineEdit.setText(_translate("ProcedureDialog", "0.0"))
        self.label_8.setText(_translate("ProcedureDialog", "s"))
        self.btnAddAction.setText(_translate("ProcedureDialog", "Add"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("ProcedureDialog", "Basic"))
        self.label_17.setText(_translate("ProcedureDialog", "Write Channel:"))
        self.label_9.setText(_translate("ProcedureDialog", "."))
        self.cbPidChannelRead.setCurrentText(_translate("ProcedureDialog", "- Choose a device -"))
        self.cbPidChannelRead.setItemText(0, _translate("ProcedureDialog", "- Choose a device -"))
        self.label_16.setText(_translate("ProcedureDialog", "Read Channel:"))
        self.label_15.setText(_translate("ProcedureDialog", "."))
        self.cbPidChannelWrite.setCurrentText(_translate("ProcedureDialog", "- Choose a device -"))
        self.cbPidChannelWrite.setItemText(0, _translate("ProcedureDialog", "- Choose a device -"))
        self.label_10.setText(_translate("ProcedureDialog", "Target Value:"))
        self.txtTarget.setText(_translate("ProcedureDialog", "0.0"))
        self.groupBox_5.setTitle(_translate("ProcedureDialog", "PID"))
        self.label_11.setText(_translate("ProcedureDialog", "Time Step:"))
        self.txtdt.setText(_translate("ProcedureDialog", "0.0"))
        self.label_12.setText(_translate("ProcedureDialog", "P"))
        self.txtP.setText(_translate("ProcedureDialog", "0.0"))
        self.label_13.setText(_translate("ProcedureDialog", "I"))
        self.txtI.setText(_translate("ProcedureDialog", "0.0"))
        self.label_14.setText(_translate("ProcedureDialog", "D"))
        self.txtD.setText(_translate("ProcedureDialog", "0.0"))
        self.groupBox.setTitle(_translate("ProcedureDialog", "More Options"))
        self.txtAverage.setText(_translate("ProcedureDialog", "1"))
        self.label_18.setText(_translate("ProcedureDialog", "samples"))
        self.txtWarmup.setText(_translate("ProcedureDialog", "0"))
        self.label_19.setText(_translate("ProcedureDialog", "samples"))
        self.txtOffset.setText(_translate("ProcedureDialog", "0.0"))
        self.lblUnit.setText(_translate("ProcedureDialog", "Unit"))
        self.label_20.setText(_translate("ProcedureDialog", "Average"))
        self.label_21.setText(_translate("ProcedureDialog", "Warmup"))
        self.label_22.setText(_translate("ProcedureDialog", "Offset"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("ProcedureDialog", "PID"))
        self.groupBox_6.setTitle(_translate("ProcedureDialog", "Start Condition"))
        self.label_31.setText(_translate("ProcedureDialog", "Channel:"))
        self.label_30.setText(_translate("ProcedureDialog", "."))
        self.cbTimerChannelStart.setCurrentText(_translate("ProcedureDialog", "- Choose a device -"))
        self.cbTimerChannelStart.setItemText(0, _translate("ProcedureDialog", "- Choose a device -"))
        self.label_23.setText(_translate("ProcedureDialog", "Start when:"))
        self.cbTimerStartComp.setItemText(0, _translate("ProcedureDialog", ">"))
        self.cbTimerStartComp.setItemText(1, _translate("ProcedureDialog", "<"))
        self.txtTimerStart.setText(_translate("ProcedureDialog", "0.0"))
        self.lblTimerStartUnit.setText(_translate("ProcedureDialog", "Unit"))
        self.groupBox_7.setTitle(_translate("ProcedureDialog", "Stop Condition"))
        self.label_33.setText(_translate("ProcedureDialog", "Channel:"))
        self.label_35.setText(_translate("ProcedureDialog", "."))
        self.cbTimerChannelStop.setCurrentText(_translate("ProcedureDialog", "- Choose a device -"))
        self.cbTimerChannelStop.setItemText(0, _translate("ProcedureDialog", "- Choose a device -"))
        self.label_24.setText(_translate("ProcedureDialog", "Stop when:"))
        self.cbTimerStopComp.setItemText(0, _translate("ProcedureDialog", ">"))
        self.cbTimerStopComp.setItemText(1, _translate("ProcedureDialog", "<"))
        self.txtTimerStop.setText(_translate("ProcedureDialog", "0.0"))
        self.lblTimerStopUnit.setText(_translate("ProcedureDialog", "Unit"))
        self.groupBox_4.setTitle(_translate("ProcedureDialog", "Options"))
        self.label_34.setText(_translate("ProcedureDialog", "Minimum Time:"))
        self.txtTimerMinTime.setText(_translate("ProcedureDialog", "0"))
        self.label_32.setText(_translate("ProcedureDialog", "s"))
        self.chkTimerContinuous.setText(_translate("ProcedureDialog", "Continuous"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_3), _translate("ProcedureDialog", "Timer"))
        self.gbOptions.setTitle(_translate("ProcedureDialog", "Options"))
        self.chkCritical.setText(_translate("ProcedureDialog", "Critical"))
        self.gbNotify.setTitle(_translate("ProcedureDialog", "Notify"))
        self.chkEmail.setText(_translate("ProcedureDialog", "Email"))
        self.chkText.setText(_translate("ProcedureDialog", "Text"))
        self.gbContact.setTitle(_translate("ProcedureDialog", "Contact Information"))
        self.lblText.setText(_translate("ProcedureDialog", "Mobile"))
        self.lblEmail.setText(_translate("ProcedureDialog", "Email"))
        self.btnDone.setText(_translate("ProcedureDialog", "Done"))

