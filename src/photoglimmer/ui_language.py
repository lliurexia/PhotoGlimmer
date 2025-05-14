# Methods for language management in PhotoGlimmer

from PySide2.QtWidgets import QMenu, QAction
import i18n

def setupLanguageMenu(self):
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
        action.triggered.connect(self.changeLanguage)
        self.language_menu.addAction(action)


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
        from photoglimmer_ui import appname
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
        from PySide2 import QtWidgets
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
