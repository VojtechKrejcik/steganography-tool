import sys
import os
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import QFileDialog, QMainWindow
from PyQt6 import uic
from src.hider import *

class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sh = SteganoHider()
        uic.loadUi("my.ui", self)
        self.setWindowTitle("Steganosaurus - the steganography tool")
        self.msgPushButton.clicked.connect(self.msgInputDialog)
        self.imagePushButton.clicked.connect(self.imageInputDialog)
        self.outputPushButton.clicked.connect(self.outputInputDialog)
        self.msgLineEdit.textChanged.connect(self.validate)
        self.imageLineEdit.textChanged.connect(self.validate)
        self.encryptCheckBox.stateChanged.connect(self.checkboxChanged)
        self.hidePushButton.clicked.connect(self.hide)
        # Reveal tab
        self.revealImagePushButton.clicked.connect(self.revealImageDialog)
        self.revealOutputPushButton.clicked.connect(self.revealOutputDialog)
        self.revealPushButton.clicked.connect(self.reveal)

    def msgInputDialog(self):
        text, ok = QFileDialog.getOpenFileName(self, 'Open file', '', 'All files (*)')
        self.msgLineEdit.setText(text)

    def imageInputDialog(self):
        text, ok = QFileDialog.getOpenFileName(self, 'Open file', '', 'Image (*.png)')
        self.imageLineEdit.setText(text)

    def outputInputDialog(self):
        text = QFileDialog.getExistingDirectory(self, 'Choose directory')
        self.imageLineEdit.setText(text)

    def validate(self):
        msg = self.msgLineEdit.text()
        img = self.imageLineEdit.text()
        valid = False
        if not os.path.isfile(msg):
            validationMessage = "Missing message to hide"
        elif not os.path.isfile(img) or img.split(".")[-1] != "png":
            validationMessage = "Target file is missing or it is not .png file"
        else:
            valid, validationMessage = self.sh.validate(msg, img)
        
        self.hidePushButton.setEnabled(valid)
        self.validationLabel.setText(validationMessage)
                # call validate
    def checkboxChanged(self):
        self.passphraseLineEdit.setEnabled(self.encryptCheckBox.isChecked())
            
    def hide(self):
        print("HIDE")
        passphrase = self.passphraseLineEdit.text()
        if len(passphrase) < 6:
            passphrase += '0' * (6-len(passphrase))

        self.sh.hide_message(self.outputLineEdit.text(), self.encryptCheckBox.isChecked(), self.passphraseLineEdit.text())

   #####################################################################################
   # Reveal tab                                                                     ####
   #####################################################################################
    def revealImageDialog(self):
        text, ok = QFileDialog.getOpenFileName(self, 'Open file', '', 'Image (*.png)')
        self.revealImageLineEdit.setText(text)

    def revealOutputDialog(self):
        text = QFileDialog.getExistingDirectory(self, 'Choose directory')
        self.revealOutputLineEdit.setText(text)
    
    def reveal(self):
        passphrase = self.revealPassphraseLineEdit.text()
        if len(passphrase) < 6:
            passphrase += '0' * (6-len(passphrase))
        self.sh.extract_message(self.revealImageLineEdit.text(), self.revealOutputLineEdit.text(), True, passphrase)

app = QtWidgets.QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()
