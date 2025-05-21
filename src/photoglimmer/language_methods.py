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
        'ca': 'Catalan (Valencian)'
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
    """Updates all UI texts with the current language - simplified version"""
    try:
        # Update window title
        from . import photoglimmer_ui
        title_text = f"{photoglimmer_ui.appname}: {i18n.get('app.title')}"
        self.setWindowTitle(title_text)
        
        # Common UI elements - using direct approach with hasattr checks for safety
        # Buttons
        if hasattr(self, 'buttonBrowse'):
            self.buttonBrowse.setToolTip(i18n.get('tooltips.browse'))
        if hasattr(self, 'buttonSave'):
            self.buttonSave.setText(i18n.get('buttons.save'))
            self.buttonSave.setToolTip(i18n.get('tooltips.save_button', 'Save edited file. It might take more time than previews.'))
        if hasattr(self, 'buttonReset'):
            self.buttonReset.setText(i18n.get('buttons.reset'))
        
        # Checkboxes
        if hasattr(self, 'checkBoxDenoise'):
            self.checkBoxDenoise.setText(i18n.get('checkboxes.denoise'))
            self.checkBoxDenoise.setToolTip(i18n.get('tooltips.denoise'))
        if hasattr(self, 'checkBoxPP'):
            self.checkBoxPP.setText(i18n.get('checkboxes.pp'))
            self.checkBoxPP.setToolTip(i18n.get('tooltips.pp'))
        
        # Slider tooltips
        if hasattr(self, 'slideThresh'):
            self.slideThresh.setToolTip(i18n.get('tooltips.threshold'))
        if hasattr(self, 'slideSaturat'):
            self.slideSaturat.setToolTip(i18n.get('tooltips.saturation'))
        if hasattr(self, 'slideBrightness'):
            self.slideBrightness.setToolTip(i18n.get('tooltips.brightness'))
        if hasattr(self, 'slideBlurEdge'):
            self.slideBlurEdge.setToolTip(i18n.get('tooltips.blur_edge'))
        if hasattr(self, 'slideBelndwt1'):
            self.slideBelndwt1.setToolTip(i18n.get('tooltips.blend_weight'))
        if hasattr(self, 'slideBgBlur'):
            self.slideBgBlur.setToolTip(i18n.get('tooltips.bg_blur'))
        if hasattr(self, 'sliderSegMode'):
            self.sliderSegMode.setToolTip(i18n.get('tooltips.segmenter'))
        
        # Special labels
        if hasattr(self, 'labelBG'):
            self.labelBG.setToolTip(i18n.get('tooltips.bg', 'Background - applies effects to background'))
        if hasattr(self, 'labelFG'):
            self.labelFG.setToolTip(i18n.get('tooltips.fg', 'Foreground - applies effects to foreground'))
        if hasattr(self, 'labelImg'):
            self.labelImg.setToolTip(i18n.get('tooltips.main_image', 'You have not opened any image file. Use File Open button on top left.'))
        
        # Handle slider labels using the property-based approach (this works well and should be preserved)
        frame_sliders = self.findChild(QtWidgets.QFrame, 'frameSliders')
        if frame_sliders:
            slider_labels = frame_sliders.findChildren(QtWidgets.QLabel)
            
            # First run: set properties on labels for identification
            if not hasattr(self, '_slider_labels_tagged'):
                # English text to translation key mapping
                english_texts = {
                    'Brightness': 'labels.brightness',
                    'Saturation': 'labels.saturation',
                    'Preserve': 'labels.blend_weight',
                    'Threshold': 'labels.threshold',
                    'Edge Blur': 'labels.blur_edge',
                    'Bg Blur': 'labels.bg_blur'
                }
                
                # Tag labels by their English text
                for label in slider_labels:
                    current_text = label.text()
                    if current_text in english_texts:
                        label.setProperty('translation_key', english_texts[current_text])
                
                self._slider_labels_tagged = True
            
            # Apply translations based on stored keys
            for label in slider_labels:
                translation_key = label.property('translation_key')
                if translation_key:
                    translated_text = i18n.get(translation_key)
                    label.setText(translated_text)
        
        # Update menu texts
        self.updateMenuTexts()
    except Exception as e:
        print(f"Error updating texts: {e}")

def update_menu_texts(self):
    """Updates menu texts with the current language - simplified version"""
    # Menu title mapping
    menu_mapping = {
        "menuFile": "menu.file",
        "menuHelp": "menu.help",
        "menuTools": "menu.tools"
    }
    
    # Update menu titles
    for menu_name, translation_key in menu_mapping.items():
        menu = self.findChild(QMenu, menu_name)
        if menu:
            menu.setTitle(i18n.get(translation_key))
    
    # Menu action mapping
    action_mapping = {
        'menuOpen': {'text': 'menu.open', 'tooltip': 'dialogs.open_image'},
        'menuSave': {'text': 'menu.save'},
        'menuQuit': {'text': 'menu.quit'},
        'menuAbout': {'text': 'menu.about'},
        'menuParFolder': {'text': 'menu.locate_on_disk', 'tooltip': 'dialogs.open_containing_folder'},
        'menuTranspExp': {'text': 'menu.fg_to_clipboard', 'tooltip': 'dialogs.save_transparent_png'}
    }
    
    # Update menu actions
    for action_name, keys in action_mapping.items():
        if hasattr(self, action_name) and getattr(self, action_name):
            action = getattr(self, action_name)
            if 'text' in keys:
                action.setText(i18n.get(keys['text']))
            if 'tooltip' in keys:
                action.setToolTip(i18n.get(keys['tooltip']))
