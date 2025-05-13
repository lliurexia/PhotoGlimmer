#!/bin/bash

# Asegurar que se usa la versión correcta de NumPy
export PYTHONPATH="$(python3 -m site --user-site):$PYTHONPATH"

# Habilitar salida de depuración
export PYTHONUNBUFFERED=1

# Ejecutar PhotoGlimmer con salida a la consola
python3 -m photoglimmer 2>&1 | tee photoglimmer_debug.log
