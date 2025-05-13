#!/bin/bash

# Asegurar que se usa la versión correcta de NumPy
export PYTHONPATH="$(python3 -m site --user-site):$PYTHONPATH"

# Ejecutar PhotoGlimmer directamente desde el código fuente
cd src
PYTHONPATH=".:$PYTHONPATH" python3 -c 'import photoglimmer.photoglimmer_ui as app; app.main()'
