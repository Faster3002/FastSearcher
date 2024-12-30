import os
import sys
import urllib.request
import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText

import io
import requests
from PIL import Image, ImageTk

import threading
import getpass  # Pour récupérer le nom d'utilisateur local
import zipfile
import shutil

GITHUB_REPO = "Faster3002/FastSearcher"  # Remplacez par votre "NomUtilisateur/NomDepot"
RELEASE_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
LOCAL_VERSION_FILE = "version.txt"  # Fichier local pour stocker la version
UPDATE_DIR = "update_tmp"  # Dossier temporaire pour les mises à jour

def get_local_version():
    """Récupère la version locale depuis le fichier version.txt."""
    if os.path.exists(LOCAL_VERSION_FILE):
        with open(LOCAL_VERSION_FILE, "r") as f:
            return f.read().strip()
    return None

def fetch_latest_version():
    """Récupère la version la plus récente depuis GitHub."""
    GITHUB_TOKEN = "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"  # Remplacez par votre token
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}

    try:
        response = requests.get(RELEASE_API_URL, headers=headers, timeout=10)
        response.raise_for_status()
        release_data = response.json()

        latest_version = release_data.get("tag_name")
        assets_url = release_data.get("assets_url")
        asset_url = None

        # Appel direct à l'API des assets
        if assets_url:
            print("Récupération des assets depuis :", assets_url)
            assets_response = requests.get(assets_url, headers=headers, timeout=10)
            assets_response.raise_for_status()
            assets = assets_response.json()

            if assets:
                for asset in assets:
                    print(f"Asset trouvé : {asset['name']} (URL : {asset['browser_download_url']})")
                    if "Source" not in asset["name"] and asset["name"].endswith(".zip"):
                        asset_url = asset["browser_download_url"]
                        break
            else:
                print("Aucun asset trouvé.")
        else:
            print("Pas d'URL d'assets dans la release.")

        return latest_version, asset_url
    except requests.RequestException as e:
        print(f"Erreur lors de la récupération des données GitHub : {e}")
        return None, None

def download_and_apply_update(asset_url):
    """Télécharge et applique les mises à jour."""
    try:
        print("Téléchargement de la mise à jour...")
        response = requests.get(asset_url, stream=True, timeout=10)
        response.raise_for_status()

        # Enregistrer le fichier ZIP
        zip_path = os.path.join(UPDATE_DIR, "update.zip")
        os.makedirs(UPDATE_DIR, exist_ok=True)
        with open(zip_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        # Extraire le contenu
        print("Extraction des fichiers...")
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(UPDATE_DIR)

        # Remplacer les fichiers locaux
        for root, _, files in os.walk(UPDATE_DIR):
            for file in files:
                src_path = os.path.join(root, file)
                rel_path = os.path.relpath(src_path, UPDATE_DIR)
                dest_path = os.path.join(".", rel_path)

                # Déplace les fichiers extraits
                os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                shutil.move(src_path, dest_path)

        # Nettoyage
        shutil.rmtree(UPDATE_DIR)
        print("Mise à jour appliquée avec succès.")

    except Exception as e:
        print(f"Erreur lors de la mise à jour : {e}")
        shutil.rmtree(UPDATE_DIR, ignore_errors=True)

def check_for_updates():
    """Vérifie les mises à jour et les applique si nécessaire."""
    print("Vérification des mises à jour...")
    local_version = get_local_version()
    latest_version, asset_url = fetch_latest_version()

    if not latest_version or not asset_url:
        print("Impossible de vérifier les mises à jour.")
        return

    print(f"Version locale : {local_version}")
    print(f"Dernière version disponible : {latest_version}")

    if local_version != latest_version:
        print("Une mise à jour est disponible. Téléchargement...")
        download_and_apply_update(asset_url)

        # Mettre à jour le fichier version.txt
        with open(LOCAL_VERSION_FILE, "w") as f:
            f.write(latest_version)

        print("Mise à jour terminée. Redémarrez le programme.")
        sys.exit(0)
    else:
        print("Votre programme est déjà à jour.")

# ---------- Votre code principal commence ici ----------

def close_console():
    """
    Masque la console sur Windows.
    Sur d'autres OS, cette fonction ne fait rien.
    """
    import platform
    if platform.system() == "Windows":
        import ctypes
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)


import io
import requests
from PIL import Image, ImageTk

import threading
import getpass  # Pour récupérer le nom d'utilisateur local


def close_console():
    """
    Masque la console sur Windows.
    Sur d'autres OS, cette fonction ne fait rien.
    """
    import platform
    if platform.system() == "Windows":
        import ctypes
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)


# ---------- Script original ----------
banner_text = r"""
  █████▒▄▄▄        ██████ ▄▄▄█████▓▓█████  ██▀███  
▓██   ▒▒████▄    ▒██    ▒ ▓  ██▒ ▓▒▓█   ▀ ▓██ ▒ ██▒
▒████ ░▒██  ▀█▄  ░ ▓██▄   ▒ ▓██░ ▒░▒███   ▓██ ░▄█ ▒
░▓█▒  ░░██▄▄▄▄██   ▒   ██▒░ ▓██▓ ░ ▒▓█  ▄ ▒██▀▀█▄  
░▒█░    ▓█   ▓██▒▒██████▒▒  ▒██▒ ░ ░▒████▒░██▓ ▒██▒
 ▒ ░    ▒▒   ▓▒█░▒ ▒▓▒ ▒ ░  ▒ ░░   ░░ ▒░ ░░ ▒▓ ░▒▓░
 ░       ▒   ▒▒ ░░ ░▒  ░ ░    ░     ░ ░  ░  ░▒ ░ ▒░
 ░ ░     ░   ▒   ░  ░  ░    ░         ░     ░░   ░ 
             ░  ░      ░              ░  ░   ░     
                                                   
"""

menu = "Entre une informations a search."

def check_whitelist():
    """
    Récupère l'IP publique (internet) via https://api.ipify.org
    et vérifie si elle est dans la liste blanche.
    Retourne True si accès autorisé, sinon False.
    """
    whitelisted_ips = [
        "37.66.44.176",
        "89.156.247.99",
    ]

    try:
        with urllib.request.urlopen("https://api.ipify.org") as response:
            public_ip = response.read().decode('utf-8').strip()
        
        public_ip_short = public_ip.split('.')[-1]
        
        print(f"Votre IP Hash publique est : {public_ip_short}")
        
        if public_ip in whitelisted_ips:
            print("IP whitelisted. Accès autorisé.\n")
            return True
        else:
            print("IP NON WHITELISTED. Accès refusé.\n")
            return False

    except Exception as e:
        print(f"Impossible de déterminer l'IP publique ({e}). Accès refusé.\n")
        return False


def lookup(identifiant):
    """
    Recherche l'identifiant dans tous les fichiers .txt et .sql
    du dossier 'db'. Retourne une liste de tuples (chemin_fichier, numero_ligne, contenu).
    
    Nouvelle logique :
      1) On scanne le fichier pour extraire tous les blocs délimités par [ et ].
         - Pour chaque bloc, on regarde s'il contient l'identifiant. Si oui, on ajoute
           la totalité du bloc comme un seul "résultat".
      2) Pour les lignes hors bloc, on vérifie si elles contiennent l'identifiant
         et on les ajoute si c'est le cas.
    """
    dossier = "db"
    resultats = []

    for racine, sous_dossiers, fichiers in os.walk(dossier):
        for fichier in fichiers:
            if fichier.lower().endswith((".txt", ".sql")):
                chemin_fichier = os.path.join(racine, fichier)
                try:
                    with open(chemin_fichier, "r", encoding="utf-8", errors="ignore") as f:
                        lignes = f.readlines()

                    # --- Étape 1 : Détection et récupération des blocs [ ... ] ---
                    in_block = False
                    block_start_line = 0
                    block_lines = []

                    # Pour gérer la capture de blocs multiples dans le même fichier,
                    # on aura besoin de stocker temporairement les "blocs" capturés,
                    # puis vérifier si l'identifiant s'y trouve.
                    captured_blocks = []  # Liste de tuples (start_line, block_str)

                    for i, ligne_courante in enumerate(lignes):
                        # Cherche un '[' éventuel
                        if not in_block:
                            # On détecte l'ouverture d'un bloc
                            if "[" in ligne_courante:
                                # On démarre la capture
                                in_block = True
                                block_start_line = i
                                block_lines = [ligne_courante]
                                # Si la ligne contient déjà ']', on ferme tout de suite
                                if "]" in ligne_courante:
                                    in_block = False
                                    block_str = "\n".join(block_lines)
                                    captured_blocks.append((block_start_line, block_str))
                            else:
                                # On n'est pas dans un bloc, on check si identifiant
                                # apparaît dans la ligne hors bloc
                                if identifiant in ligne_courante:
                                    # Ajoute la ligne seule au résultat
                                    resultats.append((
                                        chemin_fichier,
                                        i + 1,
                                        ligne_courante.rstrip()
                                    ))
                        else:
                            # On est déjà dans un bloc
                            block_lines.append(ligne_courante)
                            # On vérifie si cette ligne contient la fermeture ']'
                            if "]" in ligne_courante:
                                in_block = False
                                block_str = "\n".join(block_lines)
                                captured_blocks.append((block_start_line, block_str))
                    
                    # À la fin, s'il restait un bloc ouvert (pas de ']' trouvé),
                    # on le capture quand même (cas rare si mal formé)
                    if in_block and block_lines:
                        block_str = "\n".join(block_lines)
                        captured_blocks.append((block_start_line, block_str))

                    # --- Étape 2 : On regarde dans chaque bloc si identifiant est présent ---
                    for (start_line, block_str) in captured_blocks:
                        if identifiant in block_str:
                            resultats.append((
                                chemin_fichier,
                                start_line + 1,  # numéro humain (commence à 1)
                                block_str
                            ))

                except Exception as e:
                    # On stocke la ligne d’erreur dans le résultat
                    resultats.append((chemin_fichier, 0, f"Erreur de lecture : {e}"))
    return resultats


# ---------- Widget animation "demi-cercle" ----------
class RotatingArc(tk.Canvas):
    """
    Canvas qui dessine un demi-cercle et le fait tourner pour simuler un 'spinner'.
    """
    def __init__(self, parent, size=60, arc_color="#FF4C4C", arc_width=4, *args, **kwargs):
        super().__init__(parent, width=size, height=size, bg="#2C2C2C", highlightthickness=0, *args, **kwargs)
        self.size = size
        self.arc_color = arc_color
        self.arc_width = arc_width

        self.angle = 0
        self.arc_extent = 180  # Pour un demi-cercle
        self.animating = False

    def start(self, speed=50):
        """Démarre l'animation."""
        self.animating = True
        self._animate(speed)

    def stop(self):
        """Arrête l'animation."""
        self.animating = False

    def _animate(self, speed):
        if not self.animating:
            return
        # Efface l'arc précédent
        self.delete("arc")
        # Dessine un arc en rotation
        self.create_arc(
            0, 0, self.size, self.size,
            start=self.angle,
            extent=self.arc_extent,
            style="arc",
            outline=self.arc_color,
            width=self.arc_width,
            tags="arc"
        )
        self.angle = (self.angle + 10) % 360
        self.after(speed, lambda: self._animate(speed))


# ---------- Nouveau : Interface graphique ----------
class DarkGUI(tk.Tk):
    """
    Classe principale de l'interface graphique.
    Hérite de Tk et gère l'affichage d'un thème sombre et moderne.
    """
    def __init__(self):
        super().__init__()

        # Téléchargement et application de l'icône (PNG)
        icon_url = "https://image.noelshack.com/fichiers/2024/52/6/1735425331-1296902.png"
        try:
            response = requests.get(icon_url, timeout=5)
            response.raise_for_status()
            image_data = response.content

            # Conversion en ImageTk via PIL
            image = Image.open(io.BytesIO(image_data))
            icon_tk = ImageTk.PhotoImage(image)
            self.iconphoto(False, icon_tk)
        except Exception as e:
            print(f"Impossible de charger l'icône : {e}")

        # Configuration de la fenêtre
        self.title("FastScript - Search db")
        self.geometry("800x600")
        self.configure(bg="#2C2C2C")  # Fond sombre

        # Configuration du style ttk pour un look "dark"
        style = ttk.Style(self)
        style.theme_use("clam")
        
        # Personnalisation des couleurs du thème
        style.configure("TLabel",
                        background="#2C2C2C",
                        foreground="#FFFFFF",
                        font=("Segoe UI", 10))
        
        # Personnalisation pour les boutons
        style.configure("TButton",
                        background="#4A4A4A",
                        foreground="#FFFFFF",
                        font=("Segoe UI", 10, "bold"),
                        padding=5,
                        borderwidth=0)
        style.map("TButton",
                  background=[("active", "#666666")])

        style.configure("TEntry",
                        fieldbackground="#3B3B3B",
                        foreground="#FFFFFF",
                        padding=5)
        
        style.configure("TFrame",
                        background="#2C2C2C")
        
        # Création du contenu de la fenêtre
        self.create_widgets()

    def create_widgets(self):
        """ Crée et dispose les widgets dans la fenêtre. """

        # --- Barre du haut (User + Accès autorisé) ---
        top_frame = ttk.Frame(self)
        top_frame.pack(fill="x", pady=(10,0), padx=20)

        # Récupération du user local (login Windows)
        username = getpass.getuser()

        # Label pour afficher user + accès autorisé
        user_label = ttk.Label(
            top_frame,
            text=f"{username} - Accès autorisé",
            foreground="green",
            font=("Segoe UI", 12, "bold")
        )
        user_label.pack(side="left", anchor="w")

        # Cadre principal
        main_frame = ttk.Frame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Bannière (Label avec le texte ASCII)
        self.banner_label = ttk.Label(
            main_frame,
            text=banner_text,
            anchor="center",
            font=("Consolas", 12, "bold")
        )
        self.banner_label.pack(pady=(0, 10))
        
        # Petit message supplémentaire
        self.menu_label = ttk.Label(
            main_frame,
            text=menu,
            anchor="center",
            font=("Segoe UI", 10)
        )
        self.menu_label.pack(pady=(0, 20))

        # Zone de saisie de l'identifiant
        self.identifiant_var = tk.StringVar()
        self.entry_identifiant = ttk.Entry(
            main_frame,
            textvariable=self.identifiant_var,
            width=50
        )
        self.entry_identifiant.pack(pady=(0, 10))

        # Cadre pour les boutons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack()

        # Bouton de recherche
        self.search_button = ttk.Button(
            button_frame,
            text="Rechercher",
            command=self.on_search
        )
        self.search_button.pack(side="left", padx=5)

        # Bouton pour clear les résultats
        self.clear_button = ttk.Button(
            button_frame,
            text="Clear",
            command=self.on_clear
        )
        self.clear_button.pack(side="left", padx=5)

        # Bouton quitter
        self.quit_button = ttk.Button(
            button_frame,
            text="Quitter",
            command=self.quit
        )
        self.quit_button.pack(side="left", padx=5)

        # --- Demi-cercle qui tourne (remplace la progress_bar) ---
        self.spinner = RotatingArc(main_frame, size=50, arc_color="#FF4C4C", arc_width=4)
        self.spinner.pack(pady=10)

        # Zone de texte défilante pour afficher les résultats
        self.results_text = ScrolledText(
            main_frame,
            width=90,
            height=15,
            bg="#3B3B3B",
            fg="#FFFFFF",
            insertbackground="#FFFFFF",  # Couleur du curseur
            font=("Consolas", 10)
        )
        self.results_text.pack(fill="both", expand=True, pady=(10, 0))

        # Tags pour styliser le texte dans la zone de résultats
        self.results_text.tag_config("bold", font=("Consolas", 10, "bold"))
        self.results_text.tag_config("red", foreground="#FF4C4C")

        # Par défaut, on arrête le spinner
        self.spinner.stop()

    def on_search(self):
        """ Appelée lorsqu'on clique sur le bouton Rechercher. 
            Lance la recherche dans un thread pour conserver une interface réactive.
        """
        identifiant = self.identifiant_var.get().strip()
        if not identifiant:
            self.results_text.insert(tk.END, "Veuillez saisir un identifiant.\n")
            return

        # On démarre le spinner
        self.spinner.start(speed=50)

        # On désactive le bouton de recherche pour éviter double-clic
        self.search_button.config(state="disabled")

        # Lance la recherche dans un thread à part
        def worker():
            try:
                resultats = lookup(identifiant)
            except Exception as e:
                resultats = [("", 0, f"Une erreur s'est produite : {e}")]
            self.after(0, lambda: self.on_search_complete(resultats))

        threading.Thread(target=worker, daemon=True).start()

    def on_search_complete(self, resultats):
        """ Appelée quand la recherche (thread) se termine. """
        # Stoppe le spinner
        self.spinner.stop()

        # On réactive le bouton de recherche
        self.search_button.config(state="normal")

        # Ajoute les résultats à la zone de texte
        if resultats:
            for chemin, ligne, contenu in resultats:
                if chemin:
                    self.results_text.insert(tk.END, f"Fichier : {chemin} (Ligne {ligne})\n", "bold")
                    self.results_text.insert(tk.END, f"{contenu}\n\n", "red")
                else:
                    # Cas d'erreur (chemin vide)
                    self.results_text.insert(tk.END, f"{contenu}\n", "red")
        else:
            self.results_text.insert(tk.END, "Aucun résultat.\n")

    def on_clear(self):
        """ Efface le contenu de la zone de résultats. """
        self.results_text.delete("1.0", tk.END)


def main():
    """
    Point d'entrée du script :
    1. Vérifie l'IP whitelistee
    2. Masque la console si IP OK (Windows)
    3. Lance la GUI
    """
    check_for_updates()

    if not check_whitelist():
        input("Appuyez sur Entrée pour fermer la console.")
        sys.exit(1)

    close_console()  # Masque la console Windows

    # Lancement de l'interface graphique
    app = DarkGUI()
    app.mainloop()


if __name__ == "__main__":
    main()
