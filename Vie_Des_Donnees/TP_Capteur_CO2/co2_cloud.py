"""
Lit les lignes "CO2;température;humidité" envoyées par l'Arduino
(port série) et les pousse vers le dashboard GEODATA.
Installation : pip install requests pyserial
"""
import time
import requests
import serial
import serial.tools.list_ports

# ── À MODIFIER ──────────────────────────────────────────────
API_URL  = "http://students.geodata-osuc-dashboards.org/api/push"
API_KEY  = "m1-grp4-2024"   # clé de VOTRE groupe (grp1 à grp4)
PORT     = "COM5"             # ex. "COM3" ou "/dev/ttyACM0" ; None = détection auto
BAUDRATE = 115200           # identique à Serial.begin() côté Arduino
# ────────────────────────────────────────────────────────────

def trouver_port():
    """Retourne le premier port qui ressemble à un Arduino."""
    for p in serial.tools.list_ports.comports():
        desc = (p.description or "") + (p.manufacturer or "")
        if "Arduino" in desc or "CH340" in desc or "USB" in desc.upper():
            return p.device
    raise RuntimeError("Aucun port Arduino trouvé : renseignez PORT à la main.")

def envoyer(donnees: dict):
    """Envoie un dictionnaire de mesures vers le dashboard."""
    try:
        r = requests.post(API_URL, json=donnees,
                          headers={"x-api-key": API_KEY}, timeout=5)
        if r.status_code == 200:
            print(f"✓ Envoyé : {donnees}")
        else:
            print(f"✗ Erreur {r.status_code} : {r.text}")
    except Exception as e:
        print(f"✗ Connexion échouée : {e}")

def parser(ligne: str):
    """'612;22.41;45.20' -> dict ; None si la ligne est invalide."""
    parties = ligne.split(";")
    if len(parties) != 3:
        return None
    try:
        co2, temp, hum = int(parties[0]), float(parties[1]), float(parties[2])
    except ValueError:
        return None
    return {
        "co2_ppm": co2,
        "temperature_C": round(temp, 2),
        "humidite_pct": round(hum, 2),
    }

if __name__ == "__main__":
    port = PORT or trouver_port()
    print(f"Ouverture de {port} à {BAUDRATE} bauds...")
    ser = serial.Serial(port, BAUDRATE, timeout=15)
    time.sleep(2)  # l'Arduino redémarre à l'ouverture du port
    print("Lecture série + envoi en cours... (Ctrl+C pour arrêter)")
    try:
        while True:
            ligne = ser.readline().decode("utf-8", errors="ignore").strip()
            if not ligne:
                continue
            mesures = parser(ligne)
            if mesures is None:
                print(f"Ligne ignorée : {ligne}")
                continue
            envoyer(mesures)
    except KeyboardInterrupt:
        print("\nArrêt.")
    finally:
        ser.close()
