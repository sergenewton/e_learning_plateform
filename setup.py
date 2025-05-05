#!/usr/bin/env python
"""
Script d'initialisation pour la plateforme e-learning
Ce script permet d'automatiser l'installation et la configuration initiale du projet.
"""
import os
import sys
import subprocess
import django
from getpass import getpass

# Vérifier que nous sommes dans un environnement virtuel
if not hasattr(sys, 'real_prefix') and not sys.base_prefix != sys.prefix:
    print("Ce script doit être exécuté dans un environnement virtuel.")
    print("Activez votre environnement virtuel et réessayez.")
    sys.exit(1)

def run_command(command):
    """Exécute une commande shell et affiche le résultat"""
    print(f"Exécution de : {command}")
    process = subprocess.Popen(command, shell=True)
    process.wait()
    
    if process.returncode != 0:
        print(f"Erreur lors de l'exécution de la commande : {command}")
        sys.exit(1)

def create_superuser():
    """Crée un superutilisateur pour l'administration Django"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'elearning_platform.settings')
    django.setup()
    
    from accounts.models import User
    
    if User.objects.filter(is_superuser=True).exists():
        print("Un superutilisateur existe déjà.")
        return
    
    print("\nCréation d'un superutilisateur pour l'administration")
    username = input("Nom d'utilisateur : ")
    email = input("Adresse e-mail : ")
    password = getpass("Mot de passe : ")
    password_confirm = getpass("Confirmer le mot de passe : ")
    
    if password != password_confirm:
        print("Les mots de passe ne correspondent pas.")
        return create_superuser()
    
    try:
        User.objects.create_superuser(username, email, password)
        print("Superutilisateur créé avec succès !")
    except Exception as e:
        print(f"Erreur lors de la création du superutilisateur : {e}")

def create_sample_data():
    """Crée des données d'exemple pour la démonstration"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'elearning_platform.settings')
    django.setup()
    
    from courses.models import Category, Course
    from accounts.models import User
    from django.utils.text import slugify
    
    # Créer des catégories
    categories = [
        "Développement Web",
        "Science des Données",
        "Intelligence Artificielle",
        "Marketing Digital",
        "Design Graphique"
    ]
    
    for category_name in categories:
        Category.objects.get_or_create(
            name=category_name,
            slug=slugify(category_name),
            description=f"Cours dans le domaine de {category_name}"
        )
    
    print("Catégories de base créées avec succès !")

def main():
    """Fonction principale du script"""
    print("=== Initialisation de la plateforme e-learning ===\n")
    
    # Installation des dépendances
    print("1. Installation des dépendances")
    run_command("pip install -r requirements.txt")
    
    # Création des migrations
    print("\n2. Création des migrations")
    run_command("python manage.py makemigrations accounts")
    run_command("python manage.py makemigrations courses")
    run_command("python manage.py makemigrations quizzes")
    run_command("python manage.py makemigrations certificates")
    
    # Application des migrations
    print("\n3. Application des migrations")
    run_command("python manage.py migrate")
    
    # Collecte des fichiers statiques
    print("\n4. Collecte des fichiers statiques")
    run_command("python manage.py collectstatic --noinput")
    
    # Création d'un superutilisateur
    print("\n5. Création d'un superutilisateur")
    create_superuser()
    
    # Création des données d'exemple
    print("\n6. Création de données d'exemple")
    create_sample_data()
    
    print("\n=== Initialisation terminée ===")
    print("\nVous pouvez maintenant lancer le serveur de développement avec :")
    print("python manage.py runserver")

if __name__ == "__main__":
    main()