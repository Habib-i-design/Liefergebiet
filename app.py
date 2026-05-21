import streamlit as st
import requests
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="Liefergebiet Generator", page_icon="🗺️")
st.title("🗺️ Liefergebiet Generator")

modus = st.radio("Modus", ["Einzelne Adresse", "Mehrere Adressen"])

if modus == "Einzelne Adresse":
    adressen = [st.text_input("Adresse", placeholder="z.B. Hauptstraße 1, Berlin")]
else:
    anzahl = st.number_input("Anzahl der Adressen", min_value=2, max_value=20, value=2)
    adressen = []
    for i in range(int(anzahl)):
        a = st.text_input(f"Adresse {i+1}", placeholder=f"z.B. Hauptstraße {i+1}, Berlin", key=f"addr_{i}")
        adressen.append(a)

groesse = st.radio("Stadtgröße", ["DeZentral (12 min / 3 Zonen)", "Zentral (9 min / 3 Zonen)"])
asana_speichern = st.checkbox("📋 Aufgabe & KML in Asana speichern")

ZONEN = {
    "gross": [
        {"minuten": 4,  "name": "P1", "mbw": "15€", "dfee": "0,99€", "zeit": "10-20 Min"},
        {"minuten": 8,  "name": "P2", "mbw": "20€", "dfee": "1,49€", "zeit": "15-30 Min"},
        {"minuten": 12, "name": "P3", "mbw": "25€", "dfee": "1,99€", "zeit": "20-40 Min"},
    ],
    "klein": [
        {"minuten": 3, "name": "P1", "mbw": "10€", "dfee": "0,99€", "zeit": "10-20 Min"},
        {"minuten": 6, "name": "P2", "mbw": "15€", "dfee": "1,49€", "zeit": "15-30 Min"},
        {"minuten": 9, "name": "P3", "mbw": "20€", "dfee": "1,99€", "zeit": "20-40 Min"},
    ]
}

ASANA_TOKEN = "2/1211823102810426/1214963519294552:bdae30234e781ec6b63ed6637ef86057"
ASANA_PROJEKT_ID = "1208785883888744"

def geocode(address):
    res = requests.get(
        "https://nominatim.openstreetmap.org/search",
        params={"q": address, "format": "json", "limit": 1},
        headers={"User-Agent": "LiefergebietTool/1.0"}
    )
    data = res.json()
    if not data:
        raise Exception(f"Adresse nicht gefunden: {address}")
    return float(data[0]["lon"]), float(data[0]["lat"]), data[0]["display_name"]

def get_isochrones(lon, lat, range_min, intervals):
    range_sec = range_min * 60
    interval_sec = (range_min / intervals) * 60
    res = requests.post(
        "https://api.openrouteservice.org/v2/isochrones/driving-car",
        headers={
            "Authorization": "eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6IjA3ZDNlOTA2Mjk3ZTQ4ZTliMGQ0YzczMmQxYTUzMGI0IiwiaCI6Im11cm11cjY0In0=",
            "Content-Type": "application/json"
        },
        json={
            "locations": [[lon, lat]],
            "range": [range_sec],
            "interval": interval_sec,
            "range_type": "time",
            "smoothing": 0.25,
            "attributes": ["total_pop"]
        }
    )
    res.raise_for_status()
    return res.json()

def geojson_to_kml(geojson, address, zonen):
    features = geojson.get("features", [])
    features_sorted = sorted(features, key=lambda f: f["properties"]["value"])
    placemarks = ""
    for i, f in enumerate(features_sorted):
        zone = zonen[i] if i < len(zonen) else {"name": f"{i+1}", "mbw": "-", "dfee": "-", "zeit": "-", "minuten": "-"}
        pop = f["properties"].get("total_pop", 0)
        pop_str = f"{int(pop):,}".replace(",", ".")
        coords = " ".join(
            f"{c[0]},{c[1]},0"
            for c in f["geometry"]["coordinates"][0]
        )
        beschreibung = (
            f"Zone: {zone['name']} | "
            f"MBW: {zone['mbw']} | "
            f"Delivery Fee: {zone['dfee']} | "
            f"Lieferzeit: {zone['zeit']} | "
            f"Einwohner: {pop_str}"
        )
        placemarks += f"""
  <Placemark>
    <name>{zone['name']} | MBW: {zone['mbw']} | Delivery Fee: {zone['dfee']} | Lieferzeit: {zone['zeit']}</name>
    <description>{beschreibung}</description>
    <Style>
      <LineStyle><color>ff0066ff</color><width>2</width></LineStyle>
      <PolyStyle><color>330066ff</color></PolyStyle>
    </Style>
    <Polygon><outerBoundaryIs><LinearRing>
      <coordinates>{coords}</coordinates>
    </LinearRing></outerBoundaryIs></Polygon>
  </Placemark>"""
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
<Document>
  <name>Liefergebiet – {address}</name>
{placemarks}
</Document>
</kml>"""

def save_to_asana(address, kml, zonen):
    headers = {
        "Authorization": f"Bearer {ASANA_TOKEN}",
        "Content-Type": "application/json"
    }
    task_res = requests.post(
        "https://app.asana.com/api/1.0/tasks",
        headers=headers,
        json={
            "data": {
                "name": f"Liefergebiet – {address}",
                "projects": [ASANA_PROJEKT_ID],
                "notes": "\n".join([
                    f"{z['name']} ({z['minuten']} Min) | MBW: {z['mbw']} | Fee: {z['dfee']} | Zeit: {z['zeit']} | Einwohner: {z.get('pop', 0):,}".replace(",", ".")
                    for z in zonen
                ]),
                "custom_fields": {
                    "1209741946679941": "1209741951038590"
                }
            }
        }
    )
    task = task_res.json()["data"]
    task_id = task["gid"]

    requests.post(
        f"https://app.asana.com/api/1.0/tasks/{task_id}/attachments",
        headers={"Authorization": f"Bearer {ASANA_TOKEN}"},
        files={"file": (f"{address}.kml", kml, "application/vnd.google-earth.kml+xml")}
    )
    return task_id

def verarbeite_adresse(address, ist_gross):
    range_min = 12 if ist_gross else 9
    intervals = 3
    zonen = ZONEN["gross"] if ist_gross else ZONEN["klein"]

    lon, lat, display = geocode(address)
    geojson = get_isochrones(lon, lat, range_min, intervals)
    features_sorted = sorted(geojson.get("features", []), key=lambda f: f["properties"]["value"])

    zonen_mit_pop = []
    for i, z in enumerate(zonen):
        pop = 0
        if i < len(features_sorted):
            pop = int(features_sorted[i]["properties"].get("total_pop", 0))
        zonen_mit_pop.append({**z, "pop": pop})

    kml = geojson_to_kml(geojson, address, zonen)
    filename = address.replace(" ", "_")[:40] + ".kml"

    return {
        "display": display,
        "kml": kml,
        "filename": filename,
        "zonen": zonen_mit_pop,
        "geojson": geojson,
        "lat": lat,
        "lon": lon,
        "address": address,
        "task_id": None
    }

# Session state
if "results" not in st.session_state:
    st.session_state.results = []

adressen_gefuellt = [a for a in adressen if a.strip()]

if st.button("KML generieren") and adressen_gefuellt:
    st.session_state.results = []
    ist_gross = "DeZentral" in groesse

    for address in adressen_gefuellt:
        with st.spinner(f"Verarbeite: {address}..."):
            try:
                result = verarbeite_adresse(address, ist_gross)
                if asana_speichern:
                    task_id = save_to_asana(address, result["kml"], result["zonen"])
                    result["task_id"] = task_id
                st.session_state.results.append(result)
            except Exception as e:
                st.error(f"Fehler bei '{address}': {e}")

# Ergebnisse anzeigen
for r in st.session_state.results:
    st.divider()
    st.subheader(f"📍 {r['address']}")
    st.success(f"Gefunden: {r['display']}")

    if r.get("task_id"):
        st.info(f"✅ In Asana gespeichert: https://app.asana.com/0/{ASANA_PROJEKT_ID}/{r['task_id']}")

    st.download_button(
        label=f"⬇️ KML herunterladen",
        data=r["kml"],
        file_name=r["filename"],
        mime="application/vnd.google-earth.kml+xml",
        key=f"dl_{r['address']}"
    )

    st.write("**Zonen Übersicht:**")
    for z in r["zonen"]:
        pop_str = f"{z['pop']:,}".replace(",", ".")
        st.write(f"**{z['name']} ({z['minuten']} Min)** – MBW: {z['mbw']} | Fee: {z['dfee']} | Zeit: {z['zeit']} | 👥 {pop_str} Einwohner")

    m = folium.Map(location=[r["lat"], r["lon"]], zoom_start=12)
    farben = ["red", "orange", "beige"]
    features_sorted = sorted(r["geojson"].get("features", []), key=lambda f: f["properties"]["value"])
    for i, f in enumerate(features_sorted):
        zone = r["zonen"][i] if i < len(r["zonen"]) else {}
        pop_str = f"{zone.get('pop', 0):,}".replace(",", ".")
        folium.GeoJson(
            f,
            style_function=lambda x, c=farben[i % len(farben)]: {
                "fillColor": c, "color": "red", "weight": 2, "fillOpacity": 0.3
            },
            tooltip=f"{zone.get('name','')} | MBW: {zone.get('mbw','')} | Fee: {zone.get('dfee','')} | {zone.get('zeit','')} | 👥 {pop_str}"
        ).add_to(m)
    folium.Marker([r["lat"], r["lon"]], tooltip=r["address"]).add_to(m)
    st_folium(m, width=700, height=450, key=f"map_{r['address']}")
