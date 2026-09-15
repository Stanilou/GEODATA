import serial
import csv
import os
import re


# ============================================================
# CONFIGURATION
# ============================================================

PORT = "COM6"
BAUDRATE = 115200

FICHIER_CSV = "donnees_gps.csv"


# ============================================================
# CONNEXION ARDUINO
# ============================================================

print("----------------------------------------")
print("       ENREGISTREUR GPS")
print("----------------------------------------")
print()

print("Connexion à l'Arduino...")
print("Port :", PORT)
print("Vitesse :", BAUDRATE)

try:

    arduino = serial.Serial(
        PORT,
        BAUDRATE,
        timeout=2
    )

except serial.SerialException as erreur:

    print()
    print("ERREUR : impossible de se connecter à l'Arduino.")
    print()
    print("Vérifie que :")
    print("- l'Arduino est branchée")
    print("- le bon port COM est utilisé")
    print("- le Moniteur série Arduino est fermé")
    print()
    print("Détail :", erreur)

    input("Appuie sur Entrée pour quitter...")
    exit()


# ============================================================
# NETTOYAGE DU BUFFER
# ============================================================

arduino.reset_input_buffer()


# ============================================================
# OUVERTURE DU FICHIER CSV
# ============================================================

fichier_existe = os.path.exists(FICHIER_CSV)

fichier = open(
    FICHIER_CSV,
    "a",
    newline="",
    encoding="utf-8"
)

writer = csv.writer(
    fichier,
    delimiter=";"
)


# ============================================================
# EN-TÊTE CSV
# ============================================================

if not fichier_existe or os.path.getsize(FICHIER_CSV) == 0:

    writer.writerow([
        "satellites",
        "latitude",
        "longitude",
        "date",
        "heure"
    ])

    fichier.flush()


# ============================================================
# DÉBUT
# ============================================================

print()
print("----------------------------------------")
print("Enregistrement démarré")
print("----------------------------------------")
print()

print("Fichier :", FICHIER_CSV)
print()
print("En attente des données GPS...")
print()
print("Appuie sur CTRL+C pour arrêter.")
print()


nombre_points = 0


# ============================================================
# BOUCLE PRINCIPALE
# ============================================================

try:

    while True:

        # ----------------------------------------------------
        # Lecture d'une ligne
        # ----------------------------------------------------

        ligne = arduino.readline()

        if not ligne:
            continue


        # ----------------------------------------------------
        # Conversion en texte
        # ----------------------------------------------------

        ligne = ligne.decode(
            "utf-8",
            errors="ignore"
        ).strip()


        # ----------------------------------------------------
        # Ignorer les lignes vides
        # ----------------------------------------------------

        if not ligne:
            continue


        # ----------------------------------------------------
        # Affichage
        # ----------------------------------------------------

        print("Arduino :", ligne)


        # ====================================================
        # ANALYSE DE LA LIGNE GPS
        # ====================================================
        #
        # Format reçu :
        #
        # 3    47.834018    1.942690    09/15/2026 09:26:45
        #
        # ====================================================

        # Découpage en utilisant un ou plusieurs espaces
        morceaux = re.split(r"\s+", ligne)


        # ----------------------------------------------------
        # Vérification
        # ----------------------------------------------------

        if len(morceaux) != 5:

            print("Données incorrectes :", morceaux)
            continue


        # ----------------------------------------------------
        # Récupération
        # ----------------------------------------------------

        satellites = morceaux[0]

        latitude = morceaux[1]

        longitude = morceaux[2]

        date = morceaux[3]

        heure = morceaux[4]


        # ----------------------------------------------------
        # Vérification des nombres
        # ----------------------------------------------------

        try:

            satellites_int = int(satellites)

            latitude_float = float(latitude)

            longitude_float = float(longitude)

        except ValueError:

            print("Erreur : données GPS invalides.")
            continue


        # ----------------------------------------------------
        # Vérification de la position
        # ----------------------------------------------------

        if latitude_float == 0 or longitude_float == 0:

            print("Position GPS invalide.")
            continue


        # ====================================================
        # ÉCRITURE DANS LE CSV
        # ====================================================

        writer.writerow([
            satellites_int,
            f"{latitude_float:.6f}",
            f"{longitude_float:.6f}",
            date,
            heure
        ])


        # Écriture immédiate sur le disque
        fichier.flush()


        # ----------------------------------------------------
        # Compteur
        # ----------------------------------------------------

        nombre_points += 1


        # ----------------------------------------------------
        # Affichage
        # ----------------------------------------------------

        print(
            f"POINT {nombre_points} enregistré"
        )

        print(
            f"  Satellites : {satellites_int}"
        )

        print(
            f"  Latitude   : {latitude_float:.6f}"
        )

        print(
            f"  Longitude  : {longitude_float:.6f}"
        )

        print(
            f"  Date       : {date}"
        )

        print(
            f"  Heure      : {heure}"
        )

        print()


# ============================================================
# ARRÊT AVEC CTRL+C
# ============================================================

except KeyboardInterrupt:

    print()
    print("----------------------------------------")
    print("Arrêt de l'enregistrement")
    print("----------------------------------------")
    print()

    print(
        "Nombre de points enregistrés :",
        nombre_points
    )


# ============================================================
# FERMETURE
# ============================================================

finally:

    fichier.close()

    arduino.close()

    print()
    print("Fichier sauvegardé :", FICHIER_CSV)
    print("Connexion Arduino fermée.")
    print()
