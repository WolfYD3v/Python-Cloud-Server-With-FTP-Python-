#!/bin/bash
# ... (votre code d'installation avec uv) ...

# 1. Vérifiez que le venv existe
if [ -f .venv/bin/python ]; then
    echo "Lancement du script avec le Python de l'environnement virtuel..."
    # 2. Exécutez le script en appelant directement l'interpréteur du venv
    .venv/bin/python main.py
else
    echo "Erreur: L'environnement virtuel (.venv) est introuvable."
fi
