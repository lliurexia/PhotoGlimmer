# Methods for language management in PhotoGlimmer

from PySide2.QtWidgets import QMenu, QAction, QLabel, QPushButton
from PySide2 import QtWidgets
from PySide2.QtCore import Qt
import photoglimmer.locales.i18n as i18n

# Global variable for the application name
appname = "PhotoGlimmer"

def setup_language_menu(self):
    """Sets up the language menu"""
    # Find the tools menu
    tools_menu = self.findChild(QMenu, "menuTools")
    if not tools_menu:
        return
    
    # Create a new menu for languages
    self.language_menu = QMenu(i18n.get('menu.language', 'Language'), self)
    tools_menu.addSeparator()
    tools_menu.addMenu(self.language_menu)
    
    # Add actions for each available language
    languages = i18n.get_languages()
    language_names = {
        'en': 'English',
        'es': 'Spanish',
        'ca': 'Catalan'
    }
    
    for lang in languages:
        action = QAction(language_names.get(lang, lang), self)
        action.setData(lang)
        action.triggered.connect(self.change_language)
        self.language_menu.addAction(action)

def change_language(self):
    """Changes the application language"""
    action = self.sender()
    if action:
        lang_code = action.data()
        result = i18n.set_language(lang_code)
        if result:
            # Update UI texts immediately
            self.updateTexts()

def update_texts(self):
    """Updates all UI texts with the current language"""
    try:
        # Update window title
        from . import photoglimmer_ui
        title_text = f"{photoglimmer_ui.appname}: {i18n.get('app.title')}"
        self.setWindowTitle(title_text)
        
        # Direct update of specific UI elements
        # Buttons
        self.buttonBrowse.setToolTip(i18n.get('tooltips.browse'))
        self.buttonSave.setText(i18n.get('buttons.save'))
        self.buttonReset.setText(i18n.get('buttons.reset'))
        
        # Checkboxes
        self.checkBoxDenoise.setText(i18n.get('checkboxes.denoise'))
        self.checkBoxDenoise.setToolTip(i18n.get('tooltips.denoise'))
        self.checkBoxPP.setText(i18n.get('checkboxes.pp'))
        self.checkBoxPP.setToolTip(i18n.get('tooltips.pp'))
        
        # Slider tooltips
        self.slideThresh.setToolTip(i18n.get('tooltips.threshold'))
        self.slideSaturat.setToolTip(i18n.get('tooltips.saturation'))
        self.slideBrightness.setToolTip(i18n.get('tooltips.brightness'))
        self.slideBlurEdge.setToolTip(i18n.get('tooltips.blur_edge'))
        self.slideBelndwt1.setToolTip(i18n.get('tooltips.blend_weight'))
        self.slideBgBlur.setToolTip(i18n.get('tooltips.bg_blur'))
        self.sliderSegMode.setToolTip(i18n.get('tooltips.segmenter'))
        
        # Update BG and FG tooltips if the labels exist
        if hasattr(self, 'labelBG'):
            self.labelBG.setToolTip(i18n.get('tooltips.bg', 'Background - applies effects to background'))
        if hasattr(self, 'labelFG'):
            self.labelFG.setToolTip(i18n.get('tooltips.fg', 'Foreground - applies effects to foreground'))
            
        # Update main image tooltip
        if hasattr(self, 'labelImg'):
            self.labelImg.setToolTip(i18n.get('tooltips.main_image', 'You have not opened any image file. Use File Open button on top left.'))
        
        # Handle slider labels using a more robust approach
        frame_sliders = self.findChild(QtWidgets.QFrame, 'frameSliders')
        if frame_sliders:
            # Map slider positions to translation keys
            # We'll use the label's geometry to identify which label is which
            slider_labels = frame_sliders.findChildren(QtWidgets.QLabel)
            
            # Just in case it's the first run, set property on each label for identification
            # This is a one-time setup that will help with language switching
            if not hasattr(self, '_slider_labels_tagged'):
                # Standard slider labels and their translation keys
                slider_keys = [
                    'labels.brightness',
                    'labels.saturation', 
                    'labels.blend_weight',
                    'labels.threshold',
                    'labels.blur_edge',
                    'labels.bg_blur'
                ]
                
                # English text to identify first-time labels
                english_texts = {
                    'Brightness': 'labels.brightness',
                    'Saturation': 'labels.saturation',
                    'Preserve': 'labels.blend_weight',
                    'Threshold': 'labels.threshold',
                    'Edge Blur': 'labels.blur_edge',
                    'Bg Blur': 'labels.bg_blur'
                }
                
                # Initially tag labels by their English text
                for label in slider_labels:
                    current_text = label.text()
                    if current_text in english_texts:
                        # Store the translation key as a property of the label
                        label.setProperty('translation_key', english_texts[current_text])
                
                # Mark that we've tagged the labels
                self._slider_labels_tagged = True
            
            # Now translate all labels based on their stored translation key
            for label in slider_labels:
                translation_key = label.property('translation_key')
                if translation_key:
                    translated_text = i18n.get(translation_key)
                    label.setText(translated_text)
        
        # Define mapping of object names to translation keys for other UI elements
        ui_element_mapping = {
            # Labels
            "labelBrightness": {"type": QtWidgets.QLabel, "key": "labels.brightness"},
            "labelSaturation": {"type": QtWidgets.QLabel, "key": "labels.saturation"},
            "labelBlendWeight": {"type": QtWidgets.QLabel, "key": "labels.blend_weight"},
            "labelThreshold": {"type": QtWidgets.QLabel, "key": "labels.threshold"},
            "labelBlurEdge": {"type": QtWidgets.QLabel, "key": "labels.blur_edge"},
            "labelBgBlur": {"type": QtWidgets.QLabel, "key": "labels.bg_blur"},
            
            # Any additional UI elements can be added here following the same pattern
            # e.g., "elementName": {"type": ElementType, "key": "translation.key"}
        }
        
        # Update all elements using the mapping
        for obj_name, info in ui_element_mapping.items():
            element = self.window.findChild(info["type"], obj_name)
            if element:
                translated_text = i18n.get(info["key"])
                element.setText(translated_text)
        
        # Update menu texts
        self.updateMenuTexts()
    except Exception as e:
        print(f"Error updating texts: {e}")



def update_menu_texts(self):
    """Updates menu texts with the current language"""
    # Update menu titles
    menuFile = self.findChild(QMenu, "menuFile")
    menuHelp = self.findChild(QMenu, "menuHelp")
    menuTools = self.findChild(QMenu, "menuTools")
    
    if menuFile:
        menuFile.setTitle(i18n.get('menu.file'))
    if menuHelp:
        menuHelp.setTitle(i18n.get('menu.help'))
    if menuTools:
        menuTools.setTitle(i18n.get('menu.tools'))
    
    # Update menu action texts
    if hasattr(self, 'menuOpen') and self.menuOpen:
        self.menuOpen.setText(i18n.get('menu.open'))
        self.menuOpen.setToolTip(i18n.get('dialogs.open_image'))
    if hasattr(self, 'menuSave') and self.menuSave:
        self.menuSave.setText(i18n.get('menu.save'))
    if hasattr(self, 'menuQuit') and self.menuQuit:
        self.menuQuit.setText(i18n.get('menu.quit'))
    if hasattr(self, 'menuAbout') and self.menuAbout:
        self.menuAbout.setText(i18n.get('menu.about'))
    if hasattr(self, 'menuParFolder') and self.menuParFolder:
        self.menuParFolder.setText(i18n.get('menu.locate_on_disk'))
        self.menuParFolder.setToolTip(i18n.get('dialogs.open_containing_folder'))
    if hasattr(self, 'menuTranspExp') and self.menuTranspExp:
        self.menuTranspExp.setText(i18n.get('menu.fg_to_clipboard'))
        self.menuTranspExp.setToolTip(i18n.get('dialogs.save_transparent_png'))
