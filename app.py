import streamlit as st
import requests
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="Liefergebiet Generator", page_icon="🗺️")
st.title("🗺️ Liefergebiet Generator")

LOCATION_OPTIONS = {
   "– Keine Auswahl –": None,
   "Betrifft alle Stores": "1208524500818885",
   "B01 - Berlin Mitte": "1211465516299839",
   "B02 - Berlin Prenzlauer Berg": "1211465472127607",
   "B04 - Berlin Reinickendorf": "1208850202094800",
   "B06 - Berlin Alt Moabit": "1209283167132120",
   "B07 - Berlin Turmstraße": "1209304695980264",
   "B08 - Berlin Friedrichshain": "1209712163677460",
   "B10 - Berlin Spittelmarkt": "1209712163677462",
   "B13 - Berlin Tempelhof": "1210729068685298",
   "B14 - Berlin Wilmersdorf": "1210844711065784",
   "B15 - Berlin Wedding": "1211042984172141",
   "B16 - Berlin Wittenau": "1211042984172142",
   "B17 - Berlin Wittenbergplatz": "1211042984172143",
   "B18 - Berlin Wuhlheide": "1211245857139588",
   "B19 - Berlin Nollendorfplatz": "1211326810108095",
   "B20 - Berlin Steglitz": "1211326810108096",
   "B21 - Berlin Moabit": "1211326810108097",
   "B22 - Berlin Neukölln": "1211371947423970",
   "B23 - Berlin Lichtenberg": "1211371947423969",
   "B24 - Berlin Charlottenburg": "1211507862320674",
   "B25 - Berlin Mehringdamm": "1211895882157582",
   "B26 - Berlin Ostkreuz": "1211895882157583",
   "B27 - Berlin Hallesches Ufer": "1211934379554994",
   "B28 - Spandau Mitte": "1211934379554995",
   "B29 - Berlin Tempelhofer Damm": "1211934379554998",
   "B30 - Berlin Kochstrasse": "1211946652644831",
   "B31 - Berlin Körnerkiez": "1211962300158529",
   "B32 - Berlin Wutzkyallee": "1212011991668346",
   "B33 - Berlin Oranienstraße": "1212152967719172",
   "B34 - Berlin Fennpfuhl": "1212304936865790",
   "B35 - Berlin Innsbrucker Platz": "1212509136297833",
   "B36 - Berlin Schlesische Straße": "1212906246162810",
   "B37 - Berlin Cuvrystraße": "1212924032200679",
   "B38 - Berlin Müllerstraße": "1212924032200689",
   "B39 - Berlin Seestraße": "1212985787922706",
   "B40 - Berlin Leopoldplatz": "1212985787922707",
   "B41 - Berlin Ahrensfelderplatz": "1212985787922708",
   "B42 - Berlin Barnimplatz": "1212985787922709",
   "B43 - Berlin Reinickendorferstraße": "1212985787922713",
   "B44 - Berlin Wilhelmstadt": "1212991469847470",
   "B45 - Berlin Wilhelmsruher Damm": "1212991469847471",
   "B46 - Berlin Alt-Tempelhof": "1213881463517979",
   "B47 - Berlin Neu-Hohenschönhausen": "1213906809101651",
   "AB01 - Aschaffenburg Stockstadt": "1211465516299840",
   "BAD01 - Baden-Baden Oos": "1212735759585614",
   "BB01 - Böblingen": "1214630390124676",
   "BB02 - Ehningen": "1214630390124677",
   "BN01 - Bonn Beuel": "1211465472127609",
   "BS01 - Braunschweig Innenstadt": "1213450342587412",
   "C01 - Chemnitz Mitte": "1211507820405942",
   "C02 - Chemnitz Lutherviertel": "1213709552385596",
   "C03 - Chemnitz Kassberg": "1213881463517975",
   "C04 - Chemnitz Hauptbahnhof": "1213881463517977",
   "C05 - Chemnitz Schlosschemitz": "1213966131605771",
   "C06 - Chemnitz Südring": "1214221005326296",
   "C07 - Chemnitz Rathausplatz": "1214221005326297",
   "D01 - Düssel. Friedrichstadt": "1208205453015311",
   "D02 - Düsseldorf Oberbilk": "1208566010189936",
   "D03 - Düsseldorf Hauptbahnhof": "1211635894019844",
   "D04 - Düsseldorf Derendorf": "1213395642489203",
   "DD01 - Dresden Altstadt": "1210820914993393",
   "DO01 - Dortmund Lanstrop": "1214216753720851",
   "DU01 - Duisburg Mitte": "1211054316967101",
   "DU02 - Duisburg Großenbaum": "1212001443770794",
   "EF01 - Erfurt Mitte": "1210674811880527",
   "ES01 - Filderstadt (Esslingen)": "1211782990487232",
   "ES02 - Esslingen Altbach": "1214082816866000",
   "F01 - Frankfurt Westend": "1211465471605876",
   "F03 - Frankfurt Europaviertel": "1211465471605875",
   "F04 - Frankfurt Bornheim": "1209486700878593",
   "GE01 - Gelsenkirchen Mitte": "1208638072989115",
   "GI01 - Gießen Schiffenberger Tal": "1213216634032209",
   "GP01 - Göppingen": "1211782990487233",
   "HB01 - Bremerhaven Leherheide": "1214564784857053",
   "HD01 - Hockenheim Mitte": "1211465471605874",
   "HD02 - Wiesloch Altwiesloch": "1214848126944042",
   "HH01 - Hamburg St. Pauli": "1209016494469303",
   "HH02 - Hamburg Hasselbrook": "1209247035134279",
   "HH03 - Hamburg Langenhorn": "1209247035134280",
   "HH04 - Hamburg Hammerbrook": "1209247035134281",
   "HH05 - Hamburg Borgfelde": "1209283306522028",
   "HH06 - Hamburg Eppendorf": "1209487028987910",
   "HH07 - Hamburg Farmsen": "1209874019382261",
   "HH09 - Hamburg Eimsbüttel": "1209875545398072",
   "HH11 - Hamburg Eilbek": "1209986251827526",
   "HH12 - Hamburg Winterhude": "1210711333159249",
   "HH13 - Hamburg Rotherbaum": "1210729068685297",
   "HH14 - Hamburg Bergedorf": "1210857155469944",
   "HH15 - Hamburg Sasel": "1211042984172139",
   "HH16 - Hamburg Wandsbek": "1211302081259161",
   "HH17 - Hamburg Bahrenfeld": "1211962300158520",
   "HH18 - Hamburg Harburg": "1212001443430696",
   "HH19 - Hamburg Tonndorf": "1212304936865791",
   "HH20 - Hamburg Altona Nord": "1212974274969859",
   "HH21 - Hamburg Heimfeld": "1213212436537788",
   "HL01 - Lübeck": "1211046192012136",
   "HL02 - Lübeck St. Lorenz Nord": "1213806521462793",
   "HN01 - Heilbronn": "1211088926489667",
   "HN02 - Heilbronn Süd": "1212509136297873",
   "K01 - Köln Altstadt": "1211465516299842",
   "K02 - Köln Deutz": "1208205453015317",
   "K03 - Köln Ehrenfeld": "1208205453015318",
   "K04 - Köln Zollstock": "1208341274879674",
   "K06 - Köln Lövenich": "1211465471605877",
   "K07 - Köln Mülheim": "1208999950748439",
   "K08 - Köln Nippes": "1209089379072211",
   "K09 - Köln Mediapark": "1211211007360989",
   "KO01 - Koblenz Goldgrube": "1213536801867799",
   "KR01 - Krefeld Mitte": "1208548778909295",
   "KR02 - Krefeld Nord": "1211694161647987",
   "LB01 - Remseck (Ludwigsburg)": "1211574938964666",
   "LB02 - Vaihingen an der Enz": "1214597768904668",
   "LG01 - Lüneburg": "1211042984172140",
   "MA01 - Mannheim Vogelstang": "1211465463638158",
   "MA02 - Mannheim Neckarau": "1208999950748440",
   "MA03 - Mannheim Mitte": "1210707848202404",
   "MA04 - Mannheim Fahrlach": "1211453006427324",
   "MG01 - Mönchengladbach": "1209396812901284",
   "MG02 - Mönchengladbach Süd": "1212924032200687",
   "M01 - München Maxvorstadt": "1211465516299841",
   "N01 - Nürnberg Süd": "1208638072989116",
   "N02 - Nürnberg West": "1214250222400706",
   "NF01 - Bredstedt (Nordfriesenland)": "1211703719485015",
   "OF01 - Offenbach West": "1211245798325794",
   "OH01 - Stockelsdorf Süd (Ostholstein)": "1212991469847477",
   "P01 - Potsdam Babelsberg": "1214002253799524",
   "P02 - Potsdam Babelsberg Süd": "1209712163677463",
   "PF01 - Pforzheim Oststadt": "1212735759585616",
   "PF02 - Pforzheim Hauptbahnhof": "1213966131605773",
   "PI01 - Moorrege (Pinneberg)": "1211089479199565",
   "RT01 - Reutlingen Süd": "1210729068685299",
   "S01 - Stuttgart Bad Cannstatt": "1211596501906448",
   "S02 - Stuttgart Süd": "1211596501906449",
   "S03 - Stuttgart Hedelfingen": "1211782990487234",
   "S04 - Stuttgart Ost": "1211895882157669",
   "S05 - Stuttgart Neckar": "1212509136297859",
   "S06 - Stuttgart Heslach": "1212735759585617",
   "SE01 - Henstedt-Ulzburg": "1212316126710066",
   "SP01 - Speyer Stadtmitte": "1211465463638159",
   "TR01 - Trier Konz": "1213794627287615",
   "TÜ01 - Tübingen Universität": "1210531081188245",
   "UL01 - Ulm West": "1213450342587410",
   "WN01 - Weinstadt (Waiblingen)": "1211783113710758",
   "WN02 - Schorndorf (Waiblingen)": "1211783113710759",
   "WN03 - Korb": "1213640143095435",
   "WN04 - Burgstetten Bahnhofsplatz": "1213759901015190",
   "WN05 - Leutenbach": "1213881463517976",
   "WOB01 - Wolfsburg Nordstadt": "1211703719485016",
}

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
ASANA_LOCATION_FIELD_ID = "1208205453015310"
TINA_USER_ID = "1213450625875853"

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

def geojson_to_kml(geojson, store_name, zonen):
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
 <name>Liefergebiet: {store_name}</name>
{placemarks}
</Document>
</kml>"""

def save_to_asana(store_name, kml, zonen, location_gid):
   headers = {
       "Authorization": f"Bearer {ASANA_TOKEN}",
       "Content-Type": "application/json"
   }
   custom_fields = {
       "1209741946679941": "1209741951038590"
   }
   if location_gid:
       custom_fields[ASANA_LOCATION_FIELD_ID] = [location_gid]

   task_res = requests.post(
       "https://app.asana.com/api/1.0/tasks",
       headers=headers,
       json={
           "data": {
               "name": f"Liefergebiet: {store_name}",
               "assignee": TINA_USER_ID,
               "projects": [ASANA_PROJEKT_ID],
               "notes": "\n".join([
                   f"{z['name']} ({z['minuten']} Min) | MBW: {z['mbw']} | Fee: {z['dfee']} | Zeit: {z['zeit']} | Einwohner: {z.get('pop', 0):,}".replace(",", ".")
                   for z in zonen
               ]),
               "custom_fields": custom_fields
           }
       }
   )
   task = task_res.json()["data"]
   task_id = task["gid"]

   requests.post(
       f"https://app.asana.com/api/1.0/tasks/{task_id}/attachments",
       headers={"Authorization": f"Bearer {ASANA_TOKEN}"},
       files={"file": (f"{store_name}.kml", kml, "application/vnd.google-earth.kml+xml")}
   )
   return task_id

def verarbeite_adresse(address, store_name, ist_gross):
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

   kml = geojson_to_kml(geojson, store_name, zonen_mit_pop)
   filename = store_name.replace(" ", "_")[:40] + ".kml"

   return {
       "display": display,
       "kml": kml,
       "filename": filename,
       "zonen": zonen_mit_pop,
       "geojson": geojson,
       "lat": lat,
       "lon": lon,
       "store_name": store_name,
       "task_id": None
   }


modus = st.radio("Modus", ["Einzelne Adresse", "Mehrere Adressen"])
groesse = st.radio("Stadtgröße", ["DeZentral (12 min / 3 Zonen)", "Zentral (9 min / 3 Zonen)"])


eintraege = []
if modus == "Einzelne Adresse":
   col1, col2, col3 = st.columns([2, 2, 2])
   with col1:
       a = st.text_input("Adresse", placeholder="z.B. Hauptstraße 1, Berlin")
   with col2:
       sn = st.text_input("Store Name", placeholder="z.B. HD02 - Wiesloch Altwiesloch")
   with col3:
       loc = st.selectbox("Location (Asana)", list(LOCATION_OPTIONS.keys()))
   eintraege = [{"address": a, "store_name": sn, "location": loc}]
else:
   anzahl = st.number_input("Anzahl der Adressen", min_value=2, max_value=20, value=2)
   for i in range(int(anzahl)):
       st.markdown(f"**Store {i+1}**")
       col1, col2, col3 = st.columns([2, 2, 2])
       with col1:
           a = st.text_input("Adresse", placeholder="z.B. Hauptstraße 1, Berlin", key=f"addr_{i}")
       with col2:
           sn = st.text_input("Store Name", placeholder="z.B. HD02 - Wiesloch", key=f"sn_{i}")
       with col3:
           loc = st.selectbox("Location (Asana)", list(LOCATION_OPTIONS.keys()), key=f"loc_{i}")
       eintraege.append({"address": a, "store_name": sn, "location": loc})


if "results" not in st.session_state:
   st.session_state.results = []

gefuellt = [e for e in eintraege if e["address"].strip() and e["store_name"].strip()]


if st.button("KML generieren") and gefuellt:
   st.session_state.results = []
   ist_gross = "DeZentral" in groesse

   for e in gefuellt:
       with st.spinner(f"Verarbeite: {e['store_name']}..."):
           try:
               result = verarbeite_adresse(e["address"], e["store_name"], ist_gross)
               if asana_speichern:
                   location_gid = LOCATION_OPTIONS.get(e["location"])
                   task_id = save_to_asana(e["store_name"], result["kml"], result["zonen"], location_gid)
                   result["task_id"] = task_id
               st.session_state.results.append(result)
           except Exception as ex:
               st.error(f"Fehler bei '{e['store_name']}': {ex}")


# Ergebnisse anzeigen
for r in st.session_state.results:
   st.divider()
   st.subheader(f"📍 {r['store_name']}")
   st.success(f"Gefunden: {r['display']}")

   if r.get("task_id"):
       st.info(f"✅ In Asana gespeichert: https://app.asana.com/0/{ASANA_PROJEKT_ID}/{r['task_id']}")

   st.download_button(
       label="⬇️ KML herunterladen",
       data=r["kml"],
       file_name=r["filename"],
       mime="application/vnd.google-earth.kml+xml",
       key=f"dl_{r['store_name']}"
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
   folium.Marker([r["lat"], r["lon"]], tooltip=r["store_name"]).add_to(m)
   st_folium(m, width=700, height=450, key=f"map_{r['store_name']}")
asana_speichern = st.checkbox("📋 Aufgabe & KML in Asana speichern")
