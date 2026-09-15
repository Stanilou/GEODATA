import folium
import pandas as pd

# Lire le fichier GPS
df = pd.read_csv("donnees_gps.csv", sep=";")

# Convertir les coordonnées en nombres
df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")

# Supprimer les lignes invalides
df = df.dropna(subset=["latitude", "longitude"])

print(f"{len(df)} points GPS récupérés")

# Centre de la carte
centre = [
    df.iloc[0]["latitude"],
    df.iloc[0]["longitude"]
]

# Créer la carte
carte = folium.Map(
    location=centre,
    zoom_start=15,
    tiles=None
)

# Fond de carte Esri
folium.TileLayer(
    tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}",
    attr="Esri",
    name="Esri World Street Map"
).add_to(carte)

# Tracer le trajet
coordonnees = df[["latitude", "longitude"]].values.tolist()

folium.PolyLine(
    coordonnees,
    weight=4,
    opacity=0.8
).add_to(carte)

# Ajouter les points GPS sous forme de petits cercles
for i, point in df.iterrows():

    folium.CircleMarker(
        location=[
            point["latitude"],
            point["longitude"]
        ],
        radius=3,
        fill=True,
        fill_opacity=0.7,
        popup=f"""
        Point GPS : {i}<br>
        Satellites : {point['satellites']}<br>
        Latitude : {point['latitude']}<br>
        Longitude : {point['longitude']}<br>
        Date : {point['date']}<br>
        Heure : {point['heure']}
        """
    ).add_to(carte)

# Marqueur de départ
folium.Marker(
    coordonnees[0],
    popup="Départ",
    tooltip="Départ"
).add_to(carte)

# Marqueur d'arrivée
folium.Marker(
    coordonnees[-1],
    popup="Arrivée",
    tooltip="Arrivée"
).add_to(carte)

# Contrôle des couches
folium.LayerControl().add_to(carte)

# Sauvegarder
carte.save("carte_gps.html")

print("Carte créée : carte_gps.html")