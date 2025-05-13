#!/bin/bash

# Asegurar que se usa la versión correcta de NumPy
export PYTHONPATH="$(python3 -m site --user-site):$PYTHONPATH"

# Ejecutar PhotoGlimmer
python3 -m photoglimmer
