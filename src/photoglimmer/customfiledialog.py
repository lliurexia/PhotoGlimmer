
# ###############################################################################
# originally sourced from  https://stackoverflow.com/a/47599536/5132823
# by https://stackoverflow.com/users/6622587/eyllanesc
# File license CC BY-SA 3.0
# ###############################################################################
import sys
from PySide2.QtCore import Qt, QTimer
from PySide2.QtGui import QPixmap
from PySide2.QtWidgets import QApplication, QFileDialog, QVBoxLayout, QLabel, QDialog, QPushButton, QLineEdit
import  qdarktheme
from photoglimmer.locales import i18n


class  QFileDialogPreview(QFileDialog):


    def  __init__(self, *args, **kwargs):
        QFileDialog.__init__(self, *args, **kwargs)
        self.setOption(QFileDialog.DontUseNativeDialog, True)
        self.setOption(QFileDialog.HideNameFilterDetails, True)      
        self.setWindowTitle(i18n.get('dialogs.open_image_dialog', "PhotoGlimmer: Open an Image"))        
        layoutV = QVBoxLayout()
        layoutV.setAlignment(Qt.AlignVCenter )
        layoutV.setMargin(10)
        self.setBaseSize(self.width() + 350, self.height())
        self.setSizeGripEnabled(True)
        image_files = i18n.get('dialogs.image_files', 'Image files')
        self.setNameFilter(f'{image_files} (*.png *.jpg *.bmp *.webp *.JPG *.jpeg *.JPEG )')
        self.mpPreview = QLabel(i18n.get('dialogs.preview', "Preview"), self)
        self.mpPreview.setFixedSize(250, 250)
        self.mpPreview.setAlignment(Qt.AlignCenter)
        self.mpPreview.setObjectName("labelPreview")
        self.mpPreview.setStyleSheet('''border: 2px solid gray;
                                        border-radius: 10px;
                                        padding: 8px 8px;                                        
                                        background: 666666;''')
        layoutV.addStretch()
        layoutV.addWidget(self.mpPreview)
        layoutV.addStretch()
        lt=self.layout()        
        lt.addLayout(  layoutV ,1,4) 
        self.currentChanged.connect(self.onChange)
        self.fileSelected.connect(self.onFileSelected)
        self.filesSelected.connect(self.onFilesSelected)
        self._fileSelected = None
        self._filesSelected = None 
        
        # Translate additional dialog texts
        self.translateDialogTexts()
        
        # Connect to multiple signals to ensure translations are maintained
        self.currentChanged.connect(self.updateButtonTranslations)
        self.accepted.connect(self.updateButtonTranslations)
        self.rejected.connect(self.updateButtonTranslations)
        
        # Set up a timer to periodically update button translations
        # This ensures they stay translated regardless of Qt's internal state changes
        self.translationTimer = QTimer(self)
        self.translationTimer.timeout.connect(self.updateButtonTranslations)
        self.translationTimer.start(500)  # Update every 500ms


    def  onChange(self, path):
        pixmap = QPixmap(path)
        if(pixmap.isNull()):
            self.mpPreview.setText(i18n.get('dialogs.preview', "Preview"))
        else:
            self.mpPreview.setPixmap(pixmap.scaled(self.mpPreview.width(), self.mpPreview.height(), Qt.KeepAspectRatio, Qt.SmoothTransformation))


    def  onFileSelected(self, file):
        self._fileSelected = file        


    def  onFilesSelected(self, files):
        self._filesSelected = files


    def  getFileSelected(self):
        return self._fileSelected


    def  getFilesSelected(self):
        return self._filesSelected
        
    def translateDialogTexts(self):
        # Translate the labels and buttons in the dialog
        # Find widgets by their type and default text
        
        # Translate labels
        for child in self.findChildren(QLabel):
            text = child.text().strip()
            
            # Check for different variations of the text
            if text == 'Look in:' or text == 'Look in':
                child.setText(i18n.get('dialogs.look_in', 'Look in:'))
            elif text == 'File name:' or text == 'File name' or text == 'Filename:':
                child.setText(i18n.get('dialogs.file_name', 'File name:'))
            elif text == 'Files of type:' or text == 'Files of type' or text == 'File type:':
                child.setText(i18n.get('dialogs.files_of_type', 'Files of type:'))
        
        # Translate all buttons using the common method
        self.updateButtonTranslations()
        
        # Also try to find the file name line edit
        for lineEdit in self.findChildren(QLineEdit):
            if lineEdit.objectName() == 'fileNameEdit':
                # Set placeholder text
                lineEdit.setPlaceholderText(i18n.get('dialogs.file_name', 'File name'))
    
    def updateButtonTranslations(self, path=None):
        # This method is called both during initialization and when the current path changes
        # The path parameter is used when connected to the currentChanged signal
        
        # Get the translated button texts
        open_text = i18n.get('dialogs.open_button', 'Open')
        cancel_text = i18n.get('dialogs.cancel_button', 'Cancel')
        
        # First, try to find the standard dialog buttons
        buttons = self.findChildren(QPushButton)
        open_button = None
        cancel_button = None
        
        # Find buttons by object name (most reliable method)
        for button in buttons:
            obj_name = button.objectName()
            if 'open' in obj_name.lower():
                open_button = button
            elif 'cancel' in obj_name.lower():
                cancel_button = button
        
        # If not found by object name, try by text
        if not open_button:
            for button in buttons:
                if button.text().lower() in ['open', '&open']:
                    open_button = button
                    break
        
        if not cancel_button:
            for button in buttons:
                if button.text().lower() in ['cancel', '&cancel']:
                    cancel_button = button
                    break
        
        # Apply translations if buttons were found
        if open_button:
            open_button.setText(open_text)
        
        if cancel_button:
            cancel_button.setText(cancel_text)
        
        # As a last resort, try to translate all buttons that might match
        for button in buttons:
            text = button.text().strip().lower()
            if text in ['open', '&open']:
                button.setText(open_text)
            elif text in ['cancel', '&cancel']:
                button.setText(cancel_text)

    
    @staticmethod


    def  getOpenFileName( parent, dir:str):
        fdlg = QFileDialogPreview(parent)
        if (parent != None):
            nWidth=int(parent.width()*0.8)
            nHeight=int(parent.height()*0.8)
            parentPos = parent.mapToGlobal(parent.pos())  
            fdlg.setGeometry(parentPos.x() + parent.width()/2 - nWidth/2,
                    parentPos.y() + parent.height()/2 - nHeight/2,
                    nWidth, nHeight);
            fdlg.setDirectory(dir)
        dlgresult= fdlg.exec_()
        selectedimg = ''
        if dlgresult == QDialog.Accepted :
            selectedimg =fdlg.getFileSelected()
        # Return the selected image
        return (selectedimg,dlgresult == QDialog.Accepted)


class QFileSaveDialog(QFileDialog):
    """A custom file save dialog with localized text"""
    
    def __init__(self, parent=None, caption="", directory="", filter=""):
        super(QFileSaveDialog, self).__init__(parent, caption, directory, filter)
        self.setOption(QFileDialog.DontUseNativeDialog, True)
        self.setAcceptMode(QFileDialog.AcceptSave)
        
        # Force the dialog to be created immediately so we can access its widgets
        self.show()
        self.hide()
        
        # Translate dialog texts
        self.translateDialogTexts()
        
        # Connect to multiple signals to ensure translations are maintained
        self.currentChanged.connect(self.updateButtonTranslations)
        self.accepted.connect(self.updateButtonTranslations)
        self.rejected.connect(self.updateButtonTranslations)
        self.directoryEntered.connect(self.updateButtonTranslations)
        self.filterSelected.connect(self.updateButtonTranslations)
        
        # Set up a timer to periodically update button translations
        self.translationTimer = QTimer(self)
        self.translationTimer.timeout.connect(self.updateButtonTranslations)
        self.translationTimer.start(200)  # Update more frequently (every 200ms)
    
    def translateDialogTexts(self):
        # Translate the labels and buttons in the dialog
        
        # Translate labels
        for child in self.findChildren(QLabel):
            text = child.text().strip()
            
            # Check for different variations of the text
            if text == 'Look in:' or text == 'Look in':
                child.setText(i18n.get('dialogs.look_in', 'Look in:'))
            elif text == 'File name:' or text == 'File name' or text == 'Filename:' or 'file' in text.lower() and 'name' in text.lower():
                child.setText(i18n.get('dialogs.file_name', 'File name:'))
            elif text == 'Files of type:' or text == 'Files of type' or text == 'File type:' or 'type' in text.lower():
                child.setText(i18n.get('dialogs.files_of_type', 'Files of type:'))
        
        # Translate all buttons using the common method
        self.updateButtonTranslations()
        
        # Also try to find the file name line edit
        for lineEdit in self.findChildren(QLineEdit):
            if 'name' in lineEdit.objectName().lower() or lineEdit.objectName() == 'fileNameEdit':
                # Set placeholder text
                lineEdit.setPlaceholderText(i18n.get('dialogs.file_name', 'File name'))

    
    def updateButtonTranslations(self, path=None):
        # Get the translated button texts
        save_text = i18n.get('dialogs.save_button', 'Save')
        cancel_text = i18n.get('dialogs.cancel_button', 'Cancel')
        
        # First, try to find the standard dialog buttons
        buttons = self.findChildren(QPushButton)
        save_button = None
        cancel_button = None
        
        # Find buttons by object name (most reliable method)
        for button in buttons:
            obj_name = button.objectName()
            if obj_name and ('save' in obj_name.lower() or 'accept' in obj_name.lower() or 'ok' in obj_name.lower()):
                save_button = button
            elif obj_name and ('cancel' in obj_name.lower() or 'reject' in obj_name.lower()):
                cancel_button = button
        
        # If not found by object name, try by text
        if not save_button:
            for button in buttons:
                text = button.text().lower()
                if text in ['save', '&save']:
                    save_button = button
                    break
        
        if not cancel_button:
            for button in buttons:
                text = button.text().lower()
                if text in ['cancel', '&cancel']:
                    cancel_button = button
                    break
        
        # Apply translations if buttons were found
        if save_button:
            save_button.setText(save_text)
        
        if cancel_button:
            cancel_button.setText(cancel_text)
        
        # As a last resort, try to translate all buttons that might match
        for button in buttons:
            text = button.text().strip().lower()
            if text in ['save', '&save']:
                button.setText(save_text)
            elif text in ['cancel', '&cancel']:
                button.setText(cancel_text)
        
        # Special handling for QDialogButtonBox buttons
        buttonBox = None
        for widget in self.children():
            if widget.inherits('QDialogButtonBox'):
                buttonBox = widget
                break
        
        if buttonBox:
            for button in buttonBox.buttons():
                role = buttonBox.buttonRole(button)
                if role == 0:  # AcceptRole
                    button.setText(save_text)
                elif role == 1:  # RejectRole
                    button.setText(cancel_text)
    
    @staticmethod
    def getSaveFileName(parent=None, caption="", directory="", filter=""):
        dialog = QFileSaveDialog(parent, caption, directory, filter)
        result = dialog.exec_()
        
        if result == QDialog.Accepted:
            selected_file = dialog.selectedFiles()[0]
            return (selected_file, dialog.selectedNameFilter())
        else:
            return ("", "")
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = QFileDialogPreview()
    window.show()
    sys.exit(app.exec_())