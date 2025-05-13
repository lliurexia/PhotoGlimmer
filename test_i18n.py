#!/usr/bin/env python3

# Script para probar el mu00f3dulo de internacionalizaciu00f3n
import sys
import os

# Au00f1adir el directorio src al path para poder importar photoglimmer
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Importar el mu00f3dulo de internacionalizaciu00f3n
import photoglimmer.locales.i18n as i18n

# Inicializar el sistema de traducciu00f3n
print("Inicializando sistema de traducciu00f3n...")
i18n.init()

# Obtener los idiomas disponibles
print(f"Idiomas disponibles: {i18n.get_languages()}")

# Obtener el idioma actual
print(f"Idioma actual: {i18n.get_current_language()}")

# Probar algunas traducciones
print(f"Traducciu00f3n de 'app.title': {i18n.get('app.title')}")
print(f"Traducciu00f3n de 'buttons.save': {i18n.get('buttons.save')}")
print(f"Traducciu00f3n de 'checkboxes.pp': {i18n.get('checkboxes.pp')}")

# Cambiar el idioma a espau00f1ol
print("\nCambiando idioma a espau00f1ol...")
result = i18n.set_language('es')
print(f"Resultado: {result}")
print(f"Idioma actual despuu00e9s del cambio: {i18n.get_current_language()}")

# Probar algunas traducciones en espau00f1ol
print(f"Traducciu00f3n de 'app.title': {i18n.get('app.title')}")
print(f"Traducciu00f3n de 'buttons.save': {i18n.get('buttons.save')}")
print(f"Traducciu00f3n de 'checkboxes.pp': {i18n.get('checkboxes.pp')}")

# Cambiar el idioma a catalu00e1n
print("\nCambiando idioma a catalu00e1n...")
result = i18n.set_language('ca')
print(f"Resultado: {result}")
print(f"Idioma actual despuu00e9s del cambio: {i18n.get_current_language()}")

# Probar algunas traducciones en catalu00e1n
print(f"Traducciu00f3n de 'app.title': {i18n.get('app.title')}")
print(f"Traducciu00f3n de 'buttons.save': {i18n.get('buttons.save')}")
print(f"Traducciu00f3n de 'checkboxes.pp': {i18n.get('checkboxes.pp')}")
