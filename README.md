# E-Learning Platform

Une plateforme d'e-learning complète construite avec Django pour offrir des cours en ligne, des quiz et des certificats.

## Fonctionnalités

- Système d'authentification complet (inscription, connexion, profils)
- Gestion des cours avec modules et contenus multimédia
- Suivi de progression des étudiants
- Système de quiz et d'évaluations
- Génération de certificats PDF
- Interface d'administration pour les instructeurs

## Configuration

### Prérequis

- Python 3.10+
- Django 5.0+
- Autres dépendances (voir requirements.txt)

### Installation

1. Cloner le dépôt :
```bash
git clone <repository-url>
cd e_learning_plateform
```

2. Créer un environnement virtuel et l'activer :
```bash
python -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate
```

3. Installer les dépendances :
```bash
pip install -r requirements.txt
```

4. Configurer la base de données :
```bash
python manage.py migrate
```

5. Créer un superutilisateur :
```bash
python manage.py createsuperuser
```

6. Lancer le serveur de développement :
```bash
python manage.py runserver
```

## Structure du projet

- `accounts` : Gestion des utilisateurs et profils
- `courses` : Gestion des cours, modules et contenus
- `quizzes` : Système de quiz et évaluations
- `certificates` : Génération et vérification de certificats
- `media` : Fichiers téléchargés (images, vidéos, documents)
- `static` : Fichiers statiques (CSS, JS, images)
- `templates` : Modèles HTML

## Résolution des problèmes courants

### Problèmes de certificats

Si vous rencontrez des problèmes lors de la génération de certificats :
- Vérifiez que la bibliothèque ReportLab est correctement installée
- Assurez-vous que le paramètre `BASE_URL` est défini dans settings.py
- Vérifiez que les dossiers media sont accessibles en écriture

### Navigation entre modules

Si vous rencontrez des problèmes avec la navigation entre modules :
- Vérifiez que les modules ont un ordre défini
- Assurez-vous que les templates utilisent correctement les méthodes `get_next_module` et `get_previous_module`

## Déploiement en production

Pour un déploiement en production :
1. Configurez les paramètres de production dans settings.py :
   - Désactivez DEBUG
   - Configurez une base de données plus robuste (PostgreSQL recommandé)
   - Configurez correctement les clés secrètes
   - Configurez le stockage des fichiers statiques et média

2. Utilisez un serveur WSGI comme Gunicorn :
```bash
pip install gunicorn
gunicorn elearning_platform.wsgi:application
```

3. Configurez un serveur web comme Nginx pour servir les fichiers statiques et média


