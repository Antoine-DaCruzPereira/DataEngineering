import subprocess
import time
import sys
import os

def run_command(command):
    """Exécute une commande shell et l'affiche joliment"""
    print(f"🔹 Exécution : {command}")
    try:
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError:
        print(f"❌ Erreur lors de l'exécution de : {command}")
        sys.exit(1)

def main():
    print("\n" + "="*40)
    print("🚀 LANCEMENT AUTOMATISÉ DU PROJET SCRAPPY")
    print("="*40 + "\n")

    print("🧹 Étape 1 : Nettoyage des anciens conteneurs...")
    subprocess.call("docker-compose down --remove-orphans", shell=True)

    print("\n🏗️  Étape 2 : Construction et Démarrage des services...")
    try:
        subprocess.run("docker-compose up --build", shell=True)
    except KeyboardInterrupt:
        print("\n\n🛑 Arrêt demandé par l'utilisateur.")
        print("💤 Extinction propre des services...")
        subprocess.run("docker-compose down", shell=True)
        print("✅ Tout est éteint. À bientôt !")

if __name__ == "__main__":
    try:
        subprocess.run("docker info", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except:
        print("❌ ERREUR : Docker n'est pas lancé sur ton Mac !")
        print("👉 Lance l'application Docker Desktop et réessaie.")
        sys.exit(1)
        
    main()