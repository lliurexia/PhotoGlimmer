# ###############################################################################
# Localization module for PhotoGlimmer
# ###############################################################################

import os
import json
import locale
from pathlib import Path

class I18n:
    """Class for managing PhotoGlimmer internationalization"""
    
    def __init__(self, lang=None):
        """Initializes the translation system
        
        Args:
            lang (str, optional): Language code to use. If None, it is automatically detected.
        """
        self.translations = {}
        self.current_lang = None
        
        # Directory where translation files are located
        self.locales_dir = Path(os.path.dirname(os.path.abspath(__file__)))
        
        # Load all available languages
        self._load_available_languages()
        
        # Set the language
        if lang and lang in self.available_languages:
            self.set_language(lang)
        else:
            self._detect_and_set_language()
    
    def _load_available_languages(self):
        """Loads the list of available languages based on JSON files in the locales directory"""
        self.available_languages = []
        for file in self.locales_dir.glob("*.json"):
            lang_code = file.stem
            self.available_languages.append(lang_code)
            
            # Cargar las traducciones
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    self.translations[lang_code] = json.load(f)
            except Exception as e:
                pass
    

    
    def _detect_and_set_language(self):
        """Detects the system language and sets the closest available language"""
        try:
            system_lang, _ = locale.getdefaultlocale()
            if system_lang:
                lang_code = system_lang.split('_')[0].lower()
                
                # Check if the language is available
                if lang_code in self.available_languages:
                    self.set_language(lang_code)
                    return
        except Exception:
            pass
        
        # If it could not be detected or is not available, use English by default
        if 'en' in self.available_languages:
            self.set_language('en')
        else:
            # Use the first available language
            if self.available_languages:
                self.set_language(self.available_languages[0])
    
    def set_language(self, lang_code):
        """Sets the current language
        
        Args:
            lang_code (str): Language code to set
        
        Returns:
            bool: True if the language was set successfully, False otherwise
        """
        if lang_code in self.available_languages:
            self.current_lang = lang_code
            return True
        return False
    
    def get_languages(self):
        """Gets the list of available languages
        
        Returns:
            list: List of available language codes
        """
        return self.available_languages
    
    def get_current_language(self):
        """Obtiene el idioma actual
        
        Returns:
            str: Código del idioma actual
        """
        return self.current_lang
    
    def get(self, key, default=None):
        """Obtiene una traducción basada en una clave anidada
        
        Args:
            key (str): Clave de traducción en formato 'categoria.subcategoria.texto'
            default (str, optional): Valor por defecto si no se encuentra la traducción
        
        Returns:
            str: Texto traducido o el valor por defecto
        """
        if not self.current_lang or not key:
            return default if default is not None else key
        
        # Dividir la clave en partes
        parts = key.split('.')
        
        # Navegar por el diccionario de traducciones
        current = self.translations.get(self.current_lang, {})
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return default if default is not None else key
        
        return current if current else (default if default is not None else key)

# Instancia global para usar en toda la aplicación
_i18n = None

def init(lang=None):
    """Inicializa el sistema de traducción
    
    Args:
        lang (str, optional): Código de idioma a usar. Si es None, se detecta automáticamente.
    """
    global _i18n
    _i18n = I18n(lang)
    return _i18n

def get(key, default=None):
    """Obtiene una traducción basada en una clave anidada
    
    Args:
        key (str): Clave de traducción en formato 'categoria.subcategoria.texto'
        default (str, optional): Valor por defecto si no se encuentra la traducción
    
    Returns:
        str: Texto traducido o el valor por defecto
    """
    global _i18n
    if _i18n is None:
        init()
    return _i18n.get(key, default)

def set_language(lang_code):
    """Establece el idioma actual
    
    Args:
        lang_code (str): Código del idioma a establecer
    
    Returns:
        bool: True si el idioma se estableció correctamente, False en caso contrario
    """
    global _i18n
    if _i18n is None:
        init(lang_code)
        return True
    return _i18n.set_language(lang_code)

def get_languages():
    """Obtiene la lista de idiomas disponibles
    
    Returns:
        list: Lista de códigos de idioma disponibles
    """
    global _i18n
    if _i18n is None:
        init()
    return _i18n.get_languages()

def get_current_language():
    """Obtiene el idioma actual
    
    Returns:
        str: Código del idioma actual
    """
    global _i18n
    if _i18n is None:
        init()
    return _i18n.get_current_language()
