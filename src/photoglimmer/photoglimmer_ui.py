
# ###############################################################################
# Copyright : Rahul Singh
# URL       : https://github.com/codecliff/PhotoGlimmer
# License   : LGPL
# email     : codecliff@users.noreply.github.com
# Disclaimer: No warranties, stated or implied.
#  Description:
# Entry point for the applicaiton.
# Handles all UI related activities and some ui stylization, even though
# the UI is almost entirely defined in a .ui file created using QT Designer
# ###############################################################################
#imports
import os, sys, shutil, time, tempfile
# QT
from PySide2 import QtWidgets,  QtCore
from PySide2.QtUiTools import QUiLoader
from PySide2.QtGui import QPixmap, QIcon, QMovie, QKeySequence
from PySide2.QtCore import QThreadPool, QFile
from PySide2.QtWidgets import QStyle, QMessageBox, QAction, QGridLayout, QLabel, QMenu
# Only if using qdarktheme style
import  qdarktheme
# This application
import photoglimmer.photoglimmer_backend as photoglimmer_backend
from photoglimmer.threadwork import *
import photoglimmer.customfiledialog as customfiledialog
import photoglimmer.uihelper_transparency 
import photoglimmer.locales.i18n as i18n
from photoglimmer.language_methods import setup_language_menu, change_language, update_texts, update_menu_texts
import cv2
#/**   START Patch FOR cv2+qt plugin **/
# https://forum.qt.io/post/654289
ci_build_and_not_headless = False
try:
    from cv2.version import ci_build, headless
    ci_and_not_headless = ci_build and not headless
except Exception as err:
    print(f"Error loading patch for cv2+qt : {err}")
if sys.platform.startswith("linux") and ci_and_not_headless:
    os.environ.pop("QT_QPA_PLATFORM_PLUGIN_PATH")
if sys.platform.startswith("linux") and ci_and_not_headless:
    os.environ.pop("QT_QPA_FONTDIR")
QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)
appname = "PhotoGlimmer"
iconpath = "resources/appicon.png"
progbarpath = "resources/spinner3_8.gif"
tempdir = None
tempImage_original = "tmp_original.jpg"
preferSystemFileDlg= False 

# Initialize the localization system
i18n.init()


class  Ui(QtWidgets.QMainWindow):
    # Add language management methods
    setupLanguageMenu = setup_language_menu
    change_language = change_language  # Use the same name as in language_methods.py
    updateTexts = update_texts
    updateMenuTexts = update_menu_texts
    tempimage = photoglimmer_backend.fname_resultimg


    def  __init__(self):
        super(Ui, self).__init__()
        
        # Initialize the translation system
        i18n.init()
        
        self.loader = QUiLoader()
        uifile= QFile(self.getAbsolutePathForFile("./photoglimmer_qt.ui"))
        self.window= self.loader.load(uifile)
        self.setCentralWidget(self.window) 
        uifile.close()
        self.setAcceptDrops(True)
        self.setUpMyUI()
        self.displaySliderValues()
        self.is_state_dirty = False
        self.is_segmentation_needed= True
        self.is_tweaking_needed= True
        self.createTempDir()
        photoglimmer_backend.initializeImageObjects() 
        self.thread_pool = QThreadPool()
        
        # Configure language menu
        self.setupLanguageMenu()
        
        # Apply translations to the interface
        self.updateTexts()
        
        self.showMaximized()
        self.disableSliders()
        self.setStatus(i18n.get('app.open_image'))
        if len(sys.argv) > 1:
            arg_img = sys.argv[-1]
            if (os.path.exists(arg_img) and  self.isImageURL(arg_img )) :
                photoglimmer_backend.originalImgPath = arg_img
                self.setupBrowsedImage()


    def  setUpMyUI(self):
        self.statusBar = self.findChild(QtWidgets.QStatusBar, "statusbar")
        self.buttonBrowse = self.findChild(QtWidgets.QPushButton,
                                           "button2Browse")
        self.buttonBrowse.clicked.connect(self.goBrowse)
        self.buttonReset = self.findChild(QtWidgets.QPushButton,
                                            "buttonReset")
        self.buttonReset.clicked.connect(self.goReset)
        self.buttonSave = self.findChild(QtWidgets.QPushButton, 
                                         "button2Save")
        self.buttonSave.clicked.connect(self.goSave)
        self.labelImg = self.findChild(QtWidgets.QLabel, 'label_mainimage')
        self.labelMask = self.findChild(QtWidgets.QLabel, 'label_maskimage')
        self.checkBoxDenoise= self.findChild(QtWidgets.QCheckBox, 'check_blur')
        self.checkBoxPP= self.findChild(QtWidgets.QCheckBox, 'check_pp')
        
        # Get labels for BG and FG
        self.labelBG = self.findChild(QtWidgets.QLabel, 'label_fore')
        self.labelFG = self.findChild(QtWidgets.QLabel, 'label_back')
        
        self.sliderSegMode = self.findChild(QtWidgets.QAbstractSlider,
                                            'sliderModeToggle')
        self.slideThresh = self.findChild(QtWidgets.QAbstractSlider,
                                          'slider_thresh')
        self.slideSaturat = self.findChild(QtWidgets.QAbstractSlider,
                                           'slider_saturation')
        self.slideBelndwt1 = self.findChild(QtWidgets.QAbstractSlider,
                                            'slider_blendwt1')
        self.slideBrightness = self.findChild(QtWidgets.QAbstractSlider,
                                              'slider_bright')
        self.slideBlurEdge = self.findChild(QtWidgets.QAbstractSlider,
                                        'slider_bluredge')
        self.slideBgBlur = self.findChild(QtWidgets.QAbstractSlider,
                                        'slider_bgblur')
        self.slideBgBlur.setEnabled(False) 
        self.lcdThresh = self.findChild(QtWidgets.QLCDNumber, 'lcd_thresh')
        self.lcdSaturat = self.findChild(QtWidgets.QLCDNumber, 'lcd_satur')
        self.lcdBrightness = self.findChild(QtWidgets.QLCDNumber, 'lcd_bright')
        self.lcdBlur = self.findChild(QtWidgets.QLCDNumber, 'lcd_blur')
        self.lcdBlendwt1 = self.findChild(QtWidgets.QLCDNumber, 'lcd_blendwt1')
        self.lcdBgBlur = self.findChild(QtWidgets.QLCDNumber, 'lcd_bgblur')
        self.checkBoxPP.setChecked(False)
        self.controlBox = self.findChild(QtWidgets.QFrame, 'frameSliders')
        icon_save = self.style().standardIcon(QStyle.SP_DriveFDIcon)
        self.buttonSave.setIcon(icon_save)
        icon_open = self.style().standardIcon(QStyle.SP_DirIcon)
        icon_reset=  self.style().standardIcon(QStyle.SP_MediaSkipBackward)
        self.buttonBrowse.setIcon(icon_open)
        self.buttonReset.setIcon(icon_reset)
        self.appicon = QIcon(self.getAbsolutePathForFile(iconpath))
        self.setWindowIcon(self.appicon)
        self.labelImg.installEventFilter(self)
        self.sliderSegMode.sliderReleased.connect(self.handleSegModeSliderRelease)
        self.slideSaturat.sliderReleased.connect(self.handleTweakSlidersRelease)
        self.slideBrightness.sliderReleased.connect(self.handleTweakSlidersRelease)
        self.slideBgBlur.sliderReleased.connect(self.handleTweakSlidersRelease)
        self.slideThresh.sliderReleased.connect(self.handleSegmentationSlidersRelease)
        self.slideBlurEdge.sliderReleased.connect(self.handleSegmentationSlidersRelease)
        self.slideBelndwt1.sliderReleased.connect(self.handleSliderRelesedEvent)
        for slider in self.findChildren(QtWidgets.QSlider):
            slider.valueChanged.connect(self.updateLCDValues)
        self.checkBoxPP.stateChanged.connect(self.handleCheckBoxeEvents)
        self.checkBoxDenoise.stateChanged.connect(self.handleCheckBoxeEvents)
        self.saveUiDefaults()
        self.setUpMenubar()


    def  getImagesDirectory(self):
        from  PySide2.QtCore import QStandardPaths
        pth=QStandardPaths.PicturesLocation
        sysimgfolder= str(QStandardPaths.writableLocation(pth) )
        if os.path.exists(sysimgfolder):
            return sysimgfolder
        return None


    def  setAppStyleSheets(self):
        self.sliderSegMode.setStyleSheet('''
                                         QSlider::handle:horizontal {
                                             color:white; background: white;
                                             border: 2px solid #5c5c5c;
                                             border-radius: 10px;}                                         
                                         ''')
        self.buttonBrowse.setStyleSheet("border-color:white ")
        self.buttonSave.setStyleSheet("border-color:gray; color:gray")


    def  setUpMenubar(self):
        self.menuOpen = self.findChild(QAction, "action_open")
        self.menuSave = self.findChild(QAction, "action_save")
        self.menuQuit = self.findChild(QAction, "action_quit")
        self.menuAbout = self.findChild(QAction, "action_about")
        self.menuParFolder = self.findChild(QAction, "action_ParentFolder")
        self.menuTranspExp= self.findChild(QAction, "actionExportTransparency")
        self.menuOpen.triggered.connect(self.goBrowse)
        self.menuOpen.setShortcut(QKeySequence("Ctrl+O"))
        self.menuSave.triggered.connect(self.goSave)
        self.menuSave.setShortcut(QKeySequence("Ctrl+S"))
        self.menuQuit.triggered.connect(self.close) 
        self.menuQuit.setShortcut(QKeySequence("Ctrl+Q"))
        self.menuParFolder.triggered.connect(self.openSystemExplorer)
        self.menuAbout.triggered.connect(self.openHelpURL) 
        self.menuTranspExp.triggered.connect(self.exportTransparency)
        
        # Actualizar textos de menú
        self.updateMenuTexts()


    def  dragEnterEvent(self, event):
        isImage= self.isImageURL(event.mimeData().urls()[0].toLocalFile())
        if(isImage):
            event.acceptProposedAction()
        else:
            event.ignore()


    def  dropEvent(self, event):
        isImage= self.isImageURL(event.mimeData().urls()[0].toLocalFile())
        if(isImage):
            fname= event.mimeData().urls()[0].toLocalFile()
            self.openNewImage(fname)
        else:
            event.ignore()


    def  isImageURL(self,  url:str ):
        from  mimetypes import MimeTypes
        t,enc= MimeTypes().guess_type(url, strict=True) 
        if t is None:
            return False
        if t.startswith("image/"):
            return True
        return False


    def  setStatus(self, msg):
        self.statusBar.showMessage(msg)


    def  showMessage(self, title="", text=None ,
                    message=None):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setText(text if text else i18n.get('messages.message_about'))
        msg.setInformativeText(message if message else i18n.get('messages.some_message_shown'))
        title=f"{appname}: {title} "
        msg.setWindowTitle(title)
        msg.exec_()


    def  showConfirmationBox(self, titl=None, questn=None):
        # Create a custom message box to use localized button texts
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setWindowTitle(titl if titl else i18n.get('dialogs.confirm'))
        msg_box.setText(questn if questn else i18n.get('dialogs.really'))
        
        # Add localized Yes and No buttons
        yes_button = msg_box.addButton(i18n.get('buttons.yes'), QMessageBox.YesRole)
        no_button = msg_box.addButton(i18n.get('buttons.no'), QMessageBox.NoRole)
        msg_box.setDefaultButton(no_button)
        
        # Show the dialog and get the result
        msg_box.exec_()
        
        # Check which button was clicked
        result = msg_box.clickedButton() == yes_button
        return result


    def  saveUiDefaults(self):
        slds= self.findChildren(QtWidgets.QSlider)
        chks= self.findChildren(QtWidgets.QCheckBox)
        self.slider_defaults=[]
        self.checkbx_defaults=[]
        for s in slds:
            self.slider_defaults.append(s.value())
        for c in chks:
            self.checkbx_defaults.append(c.checkState())    


    def  resetUiToDefaults(self):
        sliders= self.findChildren(QtWidgets.QSlider)
        checkbxs= self.findChildren(QtWidgets.QCheckBox)
        for x in list(zip(sliders, self.slider_defaults)):
            x[0].setValue(x[1])
        for c in list(zip(checkbxs, self.checkbx_defaults)):
            c[0].setCheckState(c[1])


    def  saveSliderValues(self):
        slds= self.findChildren(QtWidgets.QSlider)
        sldvals=[]
        for s in slds:
            sldvals.append(s.value())
        return sldvals


    def  setSliderValues(self, sldvals):
        sliders= self.findChildren(QtWidgets.QSlider)
        for x in list(zip(sliders, sldvals)):
            if (x[0] is not self.sliderSegMode):
                x[0].setValue(x[1])
        self.displaySliderValues()


    def  eventFilter(self, obj, event):
        if event.type(
        ) == QtCore.QEvent.MouseButtonPress and self.is_state_dirty and self.isUIEnabled:
            self.showImage(photoglimmer_backend.scaledImgpath)
            return True
        elif event.type(
        ) == QtCore.QEvent.MouseButtonRelease and self.is_state_dirty and self.isUIEnabled:
            self.showImage(self.tempimage)
            return True
        return False


    def  raiseSegmentationFlag(self, value:bool):
        self.is_segmentation_needed= value


    def  raiseTweakFlag(self, value:bool):
        self.is_tweaking_needed= value


    def  disableSliders(self):
        self.isUIEnabled=False 
        self.controlBox.setEnabled(False)
        self.sliderSegMode.setEnabled(False)
        self.buttonSave.setEnabled(False)
        self.buttonReset.setEnabled(False)
        self.menuSave.setEnabled(False)
        self.buttonSave.setStyleSheet("border-color:gray; color:gray")


    def  enableSliders(self):
        self.isUIEnabled=True
        self.controlBox.setEnabled(True)
        self.sliderSegMode.setEnabled(True)
        self.buttonSave.setEnabled(True)
        self.buttonReset.setEnabled(True)
        self.menuSave.setEnabled(True)
        self.buttonSave.setStyleSheet("border-color:white; color:white")


    def  updateLCDValues(self,val):
        sld = self.sender()
        if sld is self.slideBrightness :
            self.lcdBrightness.display(val)
        elif sld is self.slideSaturat :
            self.lcdSaturat.display(val)
        elif sld is self.slideThresh :
            self.lcdThresh.display(val)
        elif sld is self.slideBelndwt1 :
            self.lcdBlendwt1.display(val)
        elif sld is self.slideBlurEdge :
            self.lcdBlur.display(val)
        elif sld is self.slideBgBlur :
            self.lcdBgBlur.display(val)    


    def  displaySliderValues(self):
        self.lcdThresh.display(self.slideThresh.value())
        self.lcdBlendwt1.display(self.slideBelndwt1.value())
        self.lcdBlur.display(self.slideBlurEdge.value())
        self.lcdBrightness.display(self.slideBrightness.value())
        self.lcdSaturat.display(self.slideSaturat.value())
        self.lcdBgBlur.display(self.slideBgBlur.value())


    def  handleSegModeSliderRelease(self) :
        new_seg_mode = ('BG', 'FORE')[int(
            self.sliderSegMode.value())]
        photoglimmer_backend.switchImgLayer(new_seg_mode)
        self.restoreUIValuesToLayer( photoglimmer_backend.currImg)
        self.slideBgBlur.setEnabled(new_seg_mode == 'BG')


    def  handleSegmentationSlidersRelease(self):
        self.raiseSegmentationFlag(True)
        self.handleSliderRelesedEvent()


    def  handleTweakSlidersRelease(self):
        self.raiseTweakFlag(True)
        self.handleSliderRelesedEvent()


    def  handleCheckBoxeEvents(self):
        self.setBackendVariables()
        self.processImage()


    def  handleSliderRelesedEvent(self):
        self.setBackendVariables()
        self.processImage()


    def  setImageAdjustMode(self):
        photoglimmer_backend.imageAdjustMode = "HSV"


    def  showImage(self, fname):
        self.pixmap = QPixmap(fname)
        myScaledPixmap = self.pixmap
        self.labelImg.setPixmap(myScaledPixmap)
        self.setStatus(i18n.get('app.save_prompt'))
        if (fname is not self.tempimage):
            self.labelImg.setProperty("toolTip",
                                      photoglimmer_backend.originalImgPath)


    def  showMask(self, fname):
        self.pixmap = QPixmap(fname)
        self.myScaledMask = self.pixmap.scaledToHeight(
            self.labelMask.height() - 20,  
            QtCore.Qt.SmoothTransformation)  
        self.labelMask.setPixmap(self.myScaledMask)


    def  startBusySpinner(self):
        self.progressmovie = QMovie(self.getAbsolutePathForFile(progbarpath))
        self.spinnerLabel=QLabel(self.labelImg)
        self.spinnerLabel.setMovie(self.progressmovie)
        self.spinnerLabel.setFixedSize(200,  200)
        mid= ( (self.labelImg.width()-self.spinnerLabel.width())//2,
            (self.labelImg.height()-self.spinnerLabel.height())//2 )
        self.spinnerLabel.move(mid[0], mid[1])
        self.labelImg.setEnabled(False)
        self.progressmovie.start()
        self.spinnerLabel.show()


    def  stopBusySpinner(self):
        if (self.progressmovie is not None):
            self.progressmovie.stop()
        if (self.spinnerLabel is not None):
            self.spinnerLabel.hide()
        self.labelImg.setEnabled(True)


    def  goBrowse(self):
        from os.path import expanduser
        homedir = self.getImagesDirectory()
        if (homedir is None):
            homedir = expanduser("~")
        if (photoglimmer_backend.originalImgPath and
            photoglimmer_backend.originalImgPath.strip() and
            os.path.exists(photoglimmer_backend.originalImgPath)):
            homedir= os. path. dirname(photoglimmer_backend.originalImgPath)
        fname=[""]
        if preferSystemFileDlg :
            fname = QtWidgets.QFileDialog.getOpenFileName(
            self,
            caption=f"{appname}: {i18n.get('dialogs.open_image', 'Open image file')}",
            dir= homedir,
            filter=(i18n.get('dialogs.image_files', 'Image Files') + " (*.png *.jpg *.bmp *.webp *.JPG *.jpeg *.JPEG )"))
        else:
            fname = customfiledialog.QFileDialogPreview.getOpenFileName(parent=self,dir= homedir )
        if (fname[0] == ''):
            return
        if not self.isImageURL(  fname[0] ):
            self.showMessage(title=i18n.get('dialogs.error', 'Error!'), 
                          text=i18n.get('dialogs.invalid_file', 'Invalid file'),
                          message=f"{i18n.get('dialogs.not_an_image', 'Not an image?')}: {fname[0]}  ")
            return
        try:
            self.openNewImage(fname[0])
        except Exception as e:
            self.showMessage(i18n.get('dialogs.error', 'Error'), 
                          i18n.get('dialogs.not_an_image', 'Not an image?'), 
                          type(e).__name__)


    def  openNewImage(self, imgpath):
        photoglimmer_backend.initializeImageObjects()
        photoglimmer_backend.originalImgPath = imgpath
        self.setupBrowsedImage() 
        self.resetUiToDefaults() 
        self.setBackendVariables() 


    def  setupBrowsedImage(self):
        self.emptyTempDir()
        self.createWorkingImage()
        self.is_state_dirty = False
        self.is_segmentation_needed=True
        self.is_tweaking_needed=True
        self.labelMask.clear()        
        self.showImage(photoglimmer_backend.resultImgPath)
        self.enableSliders()
        self.setStatus(i18n.get('app.save_prompt'))


    def  goReset(self):
        photoglimmer_backend.resetBackend()
        self.openNewImage(photoglimmer_backend.originalImgPath)


    def  goSave(self):
        if (not self.is_state_dirty):
            self.showMessage(message=i18n.get('messages.nothing_edited', 'Nothing Edited Yet!'),
                              text=i18n.get('messages.unedited', 'Unedited'),
                              title=i18n.get('messages.nothing_to_save', 'Nothing To Save!'))
            return
        self.disableSliders()
        self.setStatus(i18n.get('status.processing'))
        self.startBusySpinner()
        photoglimmer_backend.backupScaledImages()
        worker = Worker(self._goSave_bgstuff)
        worker.signals.finished.connect(self._showSaveDialog)
        self.thread_pool.start(worker)


    def  _goSave_bgstuff(self, progress_callback=None):
        result_image = photoglimmer_backend.processImageFinal(
            isOriginalImage=True, isSegmentationNeeded= False,
            isTweakingNeeded=True )
        self.tempimage = self.createTempFile(fname=tempImage_original,
                                             img=result_image, jpegqual=97)
        return


    def  _showSaveDialog(self):
        fname=None
        newfile= self.appendToFilePath( photoglimmer_backend.originalImgPath)
        # Use our custom save dialog instead of the standard one
        from photoglimmer.customfiledialog import QFileSaveDialog
        fileName, _ = QFileSaveDialog.getSaveFileName(
            self,
            caption=f"{appname}: {i18n.get('dialogs.save_image', 'Save File')}",
            directory=newfile,  
            filter=(i18n.get('dialogs.image_files', 'Image Files') + " (*.jpg, *.png)"))
        if fileName:
            _, ext = os.path.splitext(self.tempimage)
            print( f"going to save {self.tempimage} , extension {ext}")
            fname = f"{fileName}"
            if not fname.endswith(ext) :
                fname = f"{fileName}.{ext}"
                if(os.path.exists(fname)): 
                    fname=f"{fileName}_{appname}_{time.time()}.{ext}"
            with open(fname, 'w') as f:
                try:
                    shutil.copy(self.tempimage, fname)
                except Exception as e:
                    print(f"An error occurred: {e}")
                    self.showMessage(  title=i18n.get('dialogs.error', 'Error!'),
                                      text=i18n.get('messages.error_saving', 'Error saving file'),
                                      message=e)
        else:
            pass   
        self.stopBusySpinner()
        if(fname is not None):
            photoglimmer_backend.transferAlteredExif( photoglimmer_backend.originalImgPath,
                                                            fname )
            self.showMessage( text=i18n.get('messages.file_saved', 'File Saved'),  message=i18n.get('messages.saved_file', 'Saved {}').format(fname) )
        self.enableSliders()
        photoglimmer_backend.RestoreScaledImages() 
        self.tempimage=photoglimmer_backend.resultImgPath 
        self.showImage(self.tempimage)                 
        return


    def  closeEvent(self, event):
        res= self.showConfirmationBox(titl=i18n.get('dialogs.quit', 'Quit?'),
                                      questn=i18n.get('dialogs.confirm_quit', 'Are you sure you want to quit?'))
        if not res:
            event.ignore()
        else:
            event.accept()


    def  appendToFilePath(self,fpath):
        name, ext = os.path.splitext(fpath)
        file_name = f"{name}_{appname}{ext}"
        return file_name
    basedir=os.path.dirname(__file__)


    def  getAbsolutePathForFile(self, fname:str):
        f= os.path.abspath(__file__)
        d= os.path.dirname(f)
        abspth=os.path.join(self.basedir, fname)
        return abspth


    def  openSystemExplorer(self):
        if photoglimmer_backend.originalImgPath :
            dirpath = os.path.abspath(os.path.dirname(
                photoglimmer_backend.originalImgPath))
            self.openBrowser(dirpath)


    def  openHelpURL(self):
        helpurl= "https://github.com/lliurexia/PhotoGlimmer"
        self.openBrowser(helpurl)


    def  openBrowser(self, dirpath):
        import subprocess, platform
        osname= platform.system()
        if (osname in ['Windows', 'windows', 'win32']):
            os.startfile(dirpath)
            return
        opener = "open" if osname in ["darwin", "Darwin"] else "xdg-open"
        subprocess.call([opener, dirpath])


    def  getScreenSize( self ):
        from PySide2.QtWidgets import QApplication, QDesktopWidget
        desktop = QDesktopWidget()
        screen_width = desktop.screenGeometry().width()
        screen_height = desktop.screenGeometry().height()
        print(f"Screen Width: {screen_width}")
        print(f"Screen Height: {screen_height}")


    def  createWorkingImage(self):
        h = min(self.labelImg.height(),1200)
        w = min(self.labelImg.width(),1200)
        img_bgr = photoglimmer_backend.cv2.imread(
            photoglimmer_backend.originalImgPath)
        if img_bgr is None:
            raise TypeError("Not an Image! ")
        scaledimg_bgr = img_bgr
        if (img_bgr.shape[0] > w or img_bgr.shape[1] > h):
            scaledimg_bgr = photoglimmer_backend.resizeImageToFit(img_bgr, w, h)
        photoglimmer_backend.setupWorkingImages(scaledimg_bgr)


    def  setTempDir(self, tempd):
        global tempdir
        tempdir = tempd


    def  createTempDir(self):
        import  qdarktheme
        import tempfile
        import photoglimmer.locales.i18n as i18n
        import os
        import shutil
        
        global tempdir, tempImage_original
        
        try:
            # Check if temp directory exists and is accessible
            if tempdir and hasattr(tempdir, 'name') and os.path.exists(tempdir.name):
                # Temp directory exists, just return it
                return tempdir.name
                
            # Create a new temporary directory
            tempd = tempfile.TemporaryDirectory(prefix=f"{appname}_")
            tempdir = tempd
            photoglimmer_backend.tempdirpath = tempd.name
            print(f"Created temporary directory: {tempdir.name}")
            
            # Change permissions of the temporary directory to make it readable by all users
            try:
                os.chmod(tempd.name, 0o755)  # rwxr-xr-x: read and execute permissions for all users
            except Exception as e:
                print(f"Error changing temporary directory permissions: {e}")
                
            return tempdir.name
            
        except Exception as e:
            print(f"Error creating temporary directory: {e}")
            
            # Fallback: create a directory in user's home folder if system temp fails
            fallback_dir = os.path.join(os.path.expanduser("~"), ".photoglimmer_temp")
            try:
                os.makedirs(fallback_dir, exist_ok=True)
                print(f"Using fallback directory: {fallback_dir}")
                photoglimmer_backend.tempdirpath = fallback_dir
                return fallback_dir
            except Exception as e2:
                print(f"Critical error - even fallback directory failed: {e2}")
                return None


    def  createTempFile(self, fname, img, jpegqual=100):
        global tempdir
        
        try:
            # Make sure we have a valid temporary directory
            temp_path = None
            
            # Check if tempdir exists and is valid
            if tempdir and hasattr(tempdir, 'name') and os.path.exists(tempdir.name):
                temp_path = tempdir.name
            else:
                # Re-create temp directory if it doesn't exist or is invalid
                temp_path = self.createTempDir()
                
            if not temp_path:
                # Critical error: couldn't create temp directory
                self.showMessage(
                    i18n.get('dialogs.error', 'Error'),
                    i18n.get('messages.error_temp_dir', 'Error creating temporary directory')
                )
                return None
                
            # Create the temporary file path
            f = os.path.join(temp_path, fname)
            
            # Add extension if needed
            if (img.shape[-1]==4):
                f += ".png"
                
            # Write the image to the temporary file
            photoglimmer_backend.cv2.imwrite(
                img=img, 
                filename=f, 
                params=[cv2.IMWRITE_JPEG_QUALITY, jpegqual]
            )
            
            return f
            
        except Exception as e:
            print(f"Error creating temporary file {fname}: {e}")
            self.showMessage(
                i18n.get('dialogs.error', 'Error'),
                i18n.get('messages.error_temp_file', 'Error creating temporary file')
            )
            return None


    def  emptyTempDir(self):
        global tempdir
        
        try:
            # Check if tempdir is valid
            if not tempdir or not hasattr(tempdir, 'name') or not os.path.exists(tempdir.name):
                print("Temporary directory doesn't exist or is invalid.")
                return False
                
            # Remove all files from the temporary directory
            deleted_count = 0
            for fl in os.listdir(tempdir.name):
                try:
                    file_path = os.path.join(tempdir.name, fl)
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                        deleted_count += 1
                except Exception as file_err:
                    print(f"Error removing temporary file {fl}: {file_err}")
                    
            print(f"Emptied temporary directory: {deleted_count} files removed")
            return True
            
        except Exception as err:
            print(f"Error emptying temporary directory: {err}")
            return False


    def  setBackendVariables(self):
        seg_threshold = float(
            self.slideThresh.value()) / 100
        blendweight_img1 = float(
            self.slideBelndwt1.value()) / 100
        brightness = int(self.slideBrightness.value())
        saturation = int(self.slideSaturat.value())
        blur_edge = int(self.slideBlurEdge.value())
        seg_mode = ('BG', 'FORE')[int(
            self.sliderSegMode.value())]
        denoise_it= bool(self.checkBoxDenoise.isChecked())
        postprocess_it= bool(self.checkBoxPP.isChecked())        
        photoglimmer_backend.blurfactor_bg= int( self.slideBgBlur.value() )        
        photoglimmer_backend.setCurrValues(
            seg_threshold,
            blendweight_img1,
            blur_edge ,
            postprocess_it ,
            brightness ,
            saturation ,
            denoise_it,
            )
        self.setImageAdjustMode()


    def  restoreUIValuesToLayer( self, imgpar ):
        self.slideThresh.setValue( int(100*imgpar.seg_threshold ))
        self.slideBelndwt1.setValue( int(100*imgpar.blendweight_img1 ))
        self.slideBrightness.setValue(imgpar.brightness)
        self.slideSaturat.setValue(imgpar.saturation)
        self.slideBlurEdge.setValue(imgpar.blur_edge)
        self.checkBoxDenoise.setChecked(imgpar.denoise_it)
        self.checkBoxPP.setChecked(imgpar.postprocess_it)
        self.displaySliderValues()


    def  exportTransparency( self):
        self.old_status= self.statusBar.currentMessage()
        self.setStatus(i18n.get('status.processing'))
        worker2 = Worker(self._transparencyToClipboard)
        worker2.signals.finished.connect(self._displayTransparencyCompleted)
        self.thread_pool.start(worker2)        


    def  _transparencyToClipboard(self, progress_callback=None):
        helper_transp= photoglimmer.uihelper_transparency.UIHelper(self)       
        helper_transp.transparency_to_clipboard(  
                                           originalImgPath= photoglimmer_backend.originalImgPath,
                                           tempdirpath=photoglimmer_backend.tempdirpath)


    def  _displayTransparencyCompleted(self, progress_callback=None):
        self.showMessage( i18n.get('messages.fg_copied', 'Foreground Copied To Clipboard'), 
                            i18n.get('messages.paste_to_editor', 'Paste it to your favourite image Editor'))
        self.setStatus(self.old_status)
        self.old_status=""


    def  processImage(self):
        self.disableSliders()
        if (photoglimmer_backend.scaledImgpath == None
                or not os.path.exists(photoglimmer_backend.scaledImgpath)):
            self.showMessage(i18n.get('dialogs.error', 'Error!'),
                          i18n.get('messages.unedited', 'Empty'), 
                          i18n.get('messages.no_image_opened', 'You haven\'t Opened any Image!'))
            return
        worker2 = Worker(self._processImage_bgstuff)
        worker2.signals.finished.connect(self._endImageProcessing)
        self.thread_pool.start(worker2)


    def  _processImage_bgstuff(self, progress_callback=None):
        result_image = photoglimmer_backend.processImageFinal(
            isOriginalImage=False,
            isSegmentationNeeded=self.is_segmentation_needed,
            isTweakingNeeded= self.is_tweaking_needed)
        self.tempimage = self.createTempFile(fname=photoglimmer_backend.fname_resultimg,
                                             img=result_image)


    def  _endImageProcessing(self):
        self.showImage(self.tempimage)
        self.showMask(
            os.path.join(photoglimmer_backend.tempdirpath,
                         photoglimmer_backend.fname_maskImgBlurred))
        self.enableSliders()
        self.is_state_dirty = True
        self.raiseSegmentationFlag(False)
        self.raiseTweakFlag(False)


def  main():
    global app,tempdir
    if len(sys.argv)>1 and str.strip(sys.argv[1]) in ["-v","--version" ]:
        print(f"PhotoGlimmer Version 0.4.0")
        sys.exit(0)
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")
    # Handle different versions of qdarktheme
    try:
        # Try newer API first
        qdarktheme.setup_theme("dark")
    except AttributeError:
        # Fall back to older API if available
        try:
            qdarktheme.load_stylesheet("dark")
        except AttributeError:
            # If all else fails, just apply the style directly to the application
            try:
                app.setStyleSheet(qdarktheme.load_stylesheet())
            except:
                print("Warning: Could not apply dark theme. Continuing with default theme.")
    window = Ui()
    window.setAppStyleSheets() 
    app.exec_()
    # Check if tempdir exists before attempting to clean it
    if tempdir is not None:
        tempdir.cleanup()
    sys.exit(0)


# Methods for language management


def changeLanguage(self):
    """Changes the application language"""
    action = self.sender()
    if action:
        lang_code = action.data()
        result = i18n.set_language(lang_code)
        if result:
            # Update UI texts immediately
            self.updateTexts()


def updateTexts(self):
    """Updates all UI texts with the current language"""
    try:
        # Get current language
        current_lang = i18n.get_current_language()
        
        # Update window title
        title_text = f"{appname}: {i18n.get('app.title')}"
        self.setWindowTitle(title_text)
        
        # Update button texts
        save_text = i18n.get('buttons.save')
        reset_text = i18n.get('buttons.reset')
        self.buttonBrowse.setToolTip(i18n.get('tooltips.browse'))
        self.buttonSave.setText(save_text)
        self.buttonReset.setText(reset_text)
        
        # Update checkbox texts
        pp_text = i18n.get('checkboxes.pp')
        denoise_text = i18n.get('checkboxes.denoise')
        self.checkBoxPP.setText(pp_text)
        self.checkBoxPP.setToolTip(i18n.get('tooltips.pp'))
        self.checkBoxDenoise.setText(denoise_text)
        self.checkBoxDenoise.setToolTip(i18n.get('tooltips.denoise'))
        
        # Update slider tooltips
        self.slideThresh.setToolTip(i18n.get('tooltips.threshold'))
        self.slideSaturat.setToolTip(i18n.get('tooltips.saturation'))
        self.slideBrightness.setToolTip(i18n.get('tooltips.brightness'))
        self.slideBlurEdge.setToolTip(i18n.get('tooltips.blur_edge'))
        self.slideBelndwt1.setToolTip(i18n.get('tooltips.blend_weight'))
        self.slideBgBlur.setToolTip(i18n.get('tooltips.bg_blur'))
        self.sliderSegMode.setToolTip(i18n.get('tooltips.threshold'))
        
        # Update all labels in the interface
        # Mapping of English texts to translation keys
        label_text_mapping = {
            "Brightness": "labels.brightness",
            "Saturation": "labels.saturation",
            "Preserve": "labels.blend_weight",
            "Threshold": "labels.threshold",
            "Edge Blur": "labels.blur_edge",
            "Bg Blur": "labels.bg_blur",
            "PP": "checkboxes.pp",
            "Denoise": "checkboxes.denoise"
        }
        
        # Find all labels in the interface
        all_labels = self.window.findChildren(QtWidgets.QLabel)
        
        # Update each label if its current text is in the mapping
        for label in all_labels:
            current_text = label.text()
            if current_text in label_text_mapping:
                translation_key = label_text_mapping[current_text]
                translated_text = i18n.get(translation_key)
                label.setText(translated_text)
        
        # Update all buttons in the interface
        all_buttons = self.window.findChildren(QtWidgets.QPushButton)
        
        # Update menu texts
        self.updateMenuTexts()
    except Exception as e:
        print(f"Error updating texts: {e}")
    


def updateMenuTexts(self):
    """Updates the menu texts"""
    # Update menu texts
    menuFile = self.findChild(QMenu, "menuFile")
    menuHelp = self.findChild(QMenu, "menuHelp")
    menuTools = self.findChild(QMenu, "menuTools")
    
    if menuFile:
        menuFile.setTitle(i18n.get('menu.file'))
    if menuHelp:
        menuHelp.setTitle(i18n.get('menu.help'))
    if menuTools:
        menuTools.setTitle(i18n.get('menu.tools'))
    
    # Actualizar textos de las acciones de menú
    if self.menuOpen:
        self.menuOpen.setText(i18n.get('menu.open'))
        self.menuOpen.setToolTip(i18n.get('dialogs.open_image'))
    if self.menuSave:
        self.menuSave.setText(i18n.get('menu.save'))
    if self.menuQuit:
        self.menuQuit.setText(i18n.get('menu.quit'))
    if self.menuAbout:
        self.menuAbout.setText(i18n.get('menu.about'))
    if self.menuParFolder:
        self.menuParFolder.setText(i18n.get('menu.locate_on_disk'))
        self.menuParFolder.setToolTip(i18n.get('dialogs.open_containing_folder'))
    if self.menuTranspExp:
        self.menuTranspExp.setText(i18n.get('menu.fg_to_clipboard'))
        self.menuTranspExp.setToolTip(i18n.get('dialogs.save_transparent_png'))


# Add new methods to the Ui class


if __name__ == '__main__':
    main()