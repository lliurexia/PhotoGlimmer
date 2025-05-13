# Mu00e9todos para la gestiu00f3n de idiomas en PhotoGlimmer

from PySide2.QtWidgets import QMenu, QAction, QLabel, QPushButton
from PySide2 import QtWidgets
from PySide2.QtCore import Qt
import photoglimmer.locales.i18n as i18n

# Variable global para el nombre de la aplicaciu00f3n
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
        # Definir las claves de traducciu00f3n para las etiquetas principales
        label_keys = [
            "labels.brightness",
            "labels.saturation",
            "labels.blend_weight",
            "labels.threshold",
            "labels.blur_edge",
            "labels.bg_blur",
            "checkboxes.pp",
            "checkboxes.denoise"
        ]
        
        # Definir mapeo de nombres de objetos a claves de traducciu00f3n
        label_object_mapping = {
            "labelBrightness": "labels.brightness",
            "labelSaturation": "labels.saturation",
            "labelBlendWeight": "labels.blend_weight",
            "labelThreshold": "labels.threshold",
            "labelBlurEdge": "labels.blur_edge",
            "labelBgBlur": "labels.bg_blur"
        }
        
        # Buscar todas las etiquetas con nombres específicos y actualizarlas
        for obj_name, translation_key in label_object_mapping.items():
            label = self.window.findChild(QtWidgets.QLabel, obj_name)
            if label:
                translated_text = i18n.get(translation_key)
                print(f"Traduciendo etiqueta '{obj_name}' a '{translated_text}'")
                label.setText(translated_text)
        
        # Buscar etiquetas por texto
        # Primero, obtener todas las etiquetas de la interfaz
        all_labels = self.window.findChildren(QtWidgets.QLabel)
        print(f"Encontradas {len(all_labels)} etiquetas en la interfaz")
        
        # Crear un mapeo de textos posibles a claves de traducciu00f3n
        # Esto incluye textos en todos los idiomas disponibles
        text_to_key = {}
        for key in label_keys:
            # Obtener la traducciu00f3n en cada idioma disponible
            for lang in i18n.get_languages():
                # Guardar temporalmente el idioma actual
                current_lang = i18n.get_current_language()
                # Cambiar al idioma para obtener la traducciu00f3n
                i18n.set_language(lang)
                # Obtener la traducciu00f3n en este idioma
                translated_text = i18n.get(key)
                if translated_text:
                    text_to_key[translated_text] = key
                # Restaurar el idioma original
                i18n.set_language(current_lang)
        
        # Actualizar cada etiqueta si su texto actual estu00e1 en el mapeo
        for label in all_labels:
            current_text = label.text()
            if current_text in text_to_key:
                translation_key = text_to_key[current_text]
                translated_text = i18n.get(translation_key)
                print(f"Traduciendo etiqueta '{current_text}' a '{translated_text}'")
                label.setText(translated_text)
        
        # Update all buttons in the interface
        all_buttons = self.window.findChildren(QtWidgets.QPushButton)
        
        # Update menu texts
        self.updateMenuTexts()
    except Exception as e:
        print(f"Error updating texts: {e}")

def update_menu_texts(self):
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
