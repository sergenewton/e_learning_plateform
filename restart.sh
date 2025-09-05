#!/bin/bash
# Script pour redémarrer l'application e-learning
# Usage: ./restart.sh

echo "Arrêt du serveur en cours..."
pkill -f "python manage.py runserver"

echo "Nettoyage des fichiers __pycache__..."
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -name "*.pyc" -delete

echo "Collecte des fichiers statiques..."
python manage.py collectstatic --noinput

echo "Application des migrations..."
python manage.py migrate

echo "Redémarrage du serveur..."
python manage.py runserver &

echo "L'application e-learning a été redémarrée avec succès!"
echo "Accédez à http://127.0.0.1:8000 pour y accéder."
