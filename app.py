import streamlit as st
import requests

st.set_page_config(page_title="Liefergebiet Generator", page_icon="🗺️")
st.title("🗺️ Liefergebiet Generator")
st.write("Gib eine Adresse ein und lade das Liefergebiet als KML herunter.")

address = st.text_input("Adresse", placeholder="z.B. Hauptstraße 1, Berlin")
groesse = st.radio("Stadtgröße", ["Großstadt (12 min / 4 Zonen)", "Kleinstadt (9 min / 3 Zonen)"])

def geocode(address):
    res = requests.get(
        "https://nominatim.openstreetmap.org/search",
        params={"q": address, "format": "json", "limit": 1},
        headers={"User-Agent": "LiefergebietTool/1.0"}
    )
    data = res.json()
    if not data:
        raise Exception("Adresse nicht gefunden.")
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
            "smoothing": 0.25
        }
    )
    res.raise_for_status()
    return res.json()

def geojson_to_kml(geojson, address):
    features = geojson.get("features", [])
    placemarks = ""
    for f in features:
        minutes = round(f["properties"]["value"] / 60)
        coords = " ".join(
            f"{c[0]},{c[1]},0"
            for c in f["geometry"]["coordinates"][0]
        )
        placemarks += f"""
  <Placemark>
    <name>{minutes} Minuten</name>
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

if st.button("KML generieren") and address:
    with st.spinner("Generiere Liefergebiet..."):
        try:
            range_min = 12 if "Großstadt" in groesse else 9
            intervals = 4 if "Großstadt" in groesse else 3

            lon, lat, display = geocode(address)
            st.success(f"Adresse gefunden: {display}")

            geojson = get_isochrones(lon, lat, range_min, intervals)
            kml = geojson_to_kml(geojson, address)

            filename = address.replace(" ", "_")[:40] + ".kml"
            st.download_button(
                label="⬇️ KML herunterladen",
                data=kml,
                file_name=filename,
                mime="application/vnd.google-earth.kml+xml"
            )
        except Exception as e:
            st.error(f"Fehler: {e}")
