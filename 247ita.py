import random
import json
import os
import requests
from bs4 import BeautifulSoup
import time
from dotenv import load_dotenv
load_dotenv()

PROXY = os.getenv("DDPROXY", "")
MFPDD= os.getenv("DDMFPDD", "")
MFPDD2= os.getenv("DDMFPDD2", "")
MFPDDNOPSW = os.getenv("DDMFPDDNOPSW", "")
# Costanti
M3U8_OUTPUT_FILE = "247ita.m3u8"
REFERER = "forcedtoplay.xyz"
ORIGIN = "forcedtoplay.xyz"
HEADER = f"&h_user-agent=Mozilla%2F5.0+%28Windows+NT+10.0%3B+Win64%3B+x64%29+AppleWebKit%2F537.36+%28KHTML%2C+like+Gecko%29+Chrome%2F133.0.0.0+Safari%2F537.36&h_referer=https%3A%2F%2F{REFERER}%2F&h_origin=https%3A%2F%2F{ORIGIN}"
# File e URL statici
daddyLiveChannelsFileName = '247channels.html'
daddyLiveChannelsURL = 'https://daddylive.dad/24-7-channels.php'

# Headers per le richieste
headers = {
    "Accept": "*/*",
    "Accept-Language": "it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7,es;q=0.6,ru;q=0.5",
    "Priority": "u=1, i",
    "sec-ch-ua": '"Not(A:Brand";v="99", "Google Chrome";v="133", "Chromium";v="133"',
    "Sec-Ch-UA-Mobile": "?0",
    "Sec-Ch-UA-Platform": "Windows",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-Storage-Access": "active",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
}

# Mappa dei loghi per alcuni canali specifici
STATIC_LOGOS = {
    "sky uno": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/italy/sky-uno-it.png",
    "rai 1": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/italy/rai-1-it.png",
    "rai 2": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/italy/rai-2-it.png",
    "rai 3": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/italy/rai-3-it.png",
    "eurosport 1": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/spain/eurosport-1-es.png",
    "eurosport 2": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/spain/eurosport-2-es.png",
    "italia 1": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/italy/italia1-it.png",
    "la7": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/italy/la7-it.png",
    "la7d": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/italy/la7d-it.png",
    "rai sport": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/italy/rai-sport-it.png",
    "rai premium": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/italy/rai-premium-it.png",
    "sky sports golf": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/italy/sky-sport-golf-it.png",
    "sky sport motogp": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/italy/sky-sport-motogp-it.png",
    "sky sport tennis": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/italy/sky-sport-tennis-it.png",
    "sky sport f1": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/italy/sky-sport-f1-it.png",
    "sky sport football": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/italy/sky-sport-football-it.png",
    "sky sport uno": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/italy/sky-sport-uno-it.png",
    "sky sport arena": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/italy/sky-sport-arena-it.png",
    "sky cinema collection": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/italy/sky-cinema-collection-it.png",
    "sky cinema uno": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/italy/sky-cinema-uno-it.png",
    "sky cinema action": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/italy/sky-cinema-action-it.png",
    "sky cinema comedy": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/italy/sky-cinema-comedy-it.png",
    "sky cinema uno +24": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/italy/sky-cinema-uno-plus24-it.png",
    "sky cinema romance": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/italy/sky-cinema-romance-it.png",
    "sky cinema family": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/italy/sky-cinema-family-it.png",
    "sky cinema due +24": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/italy/sky-cinema-due-plus24-it.png",
    "sky cinema drama": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/italy/sky-cinema-drama-it.png",
    "sky cinema suspense": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/italy/sky-cinema-suspense-it.png",
    "sky sport 24": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/italy/sky-sport-24-it.png",
    "sky sport calcio": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/italy/sky-sport-calcio-it.png",
    "sky sport": "https://play-lh.googleusercontent.com/u7UNH06SU4KsMM4ZGWr7wghkJYN75PNCEMxnIYULpA__VPg8zfEOYMIAhUaIdmZnqw=w480-h960-rw",
    "sky calcio 1": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/germany/sky-select-1-alt-de.png",
    "sky calcio 2": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/germany/sky-select-2-alt-de.png",
    "sky calcio 3": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/germany/sky-select-3-alt-de.png",
    "sky calcio 4": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/germany/sky-select-4-alt-de.png",
    "sky calcio 5": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/germany/sky-select-5-alt-de.png",
    "sky calcio 6": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/germany/sky-select-6-alt-de.png",
    "sky calcio 7": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/germany/sky-select-7-alt-de.png",
    "sky serie": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/italy/sky-serie-it.png",
    "20 mediaset": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/italy/20-it.png",
    "dazn 1": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a2/DAZN_1_Logo.svg/774px-DAZN_1_Logo.svg.png"
}

# Mappa degli ID TVG per alcuni canali specifici
STATIC_TVG_IDS = {
    "sky uno": "skyuno.it",
    "rai 1": "rai1.it",
    "rai 2": "rai2.it",
    "rai 3": "rai3.it",
    "eurosport 1": "eurosport1.it",
    "eurosport 2": "eurosport2.it",
    "italia 1": "italia1.it",
    "la7": "la7.it",
    "la7d": "la7d.it",
    "rai sport": "raisport.it",
    "rai premium": "raipremium.it",
    "sky sports golf": "skysportgolf.it",
    "sky sport motogp": "skysportmotogp.it",
    "sky sport tennis": "skysporttennis.it",
    "sky sport f1": "skysportf1.it",
    "sky sport football": "skysportmax.it",
    "sky sport uno": "skysportuno.it",
    "sky sport arena": "skysportarena.it",
    "sky cinema collection": "skycinemacollectionhd.it",
    "sky cinema uno": "skycinemauno.it",
    "sky cinema action": "skycinemaaction.it",
    "sky cinema comedy": "skycinemacomedy.it",
    "sky cinema uno +24": "skycinemauno+24.it",
    "sky cinema romance": "skycinemaromance.it",
    "sky cinema family": "skycinemafamily.it",
    "sky cinema due +24": "skycinemadue+24.it",
    "sky cinema drama": "skycinemadrama.it",
    "sky cinema suspense": "skycinemasuspense.it",
    "sky sport 24": "skysport24.it",
    "sky sport calcio": "skysportcalcio.it",
    "sky calcio 1": "skysport251.it",
    "sky calcio 2": "skysport252.it",
    "sky calcio 3": "skysport253.it",
    "sky calcio 4": "skysport254.it",
    "sky calcio 5": "skysport255.it",
    "sky calcio 6": "skysport256.it",
    "sky calcio 7": "skysport257.it",
    "sky serie": "skyserie.it",
    "20 mediaset": "20mediasethd.it",
}

# Mappa delle categorie per alcuni canali specifici
STATIC_CATEGORIES = {
    "sky uno": "Sky",
    "rai 1": "Rai Tv",
    "rai 2": "Rai Tv",
    "rai 3": "Rai Tv",
    "eurosport 1": "Sport",
    "eurosport 2": "Sport",
    "italia 1": "Mediaset",
    "la7": "Tv Italia",
    "la7d": "Tv Italia",
    "rai sport": "Sport",
    "rai premium": "Rai Tv",
    "sky sports golf": "Sport",
    "sky sport motogp": "Sport",
    "sky sport tennis": "Sport",
    "sky sport f1": "Sport",
    "sky sport football": "Sport",
    "sky sport uno": "Sport",
    "sky sport arena": "Sport",
    "sky cinema collection": "Sky",
    "sky cinema uno": "Sky",
    "sky cinema action": "Sky",
    "sky cinema comedy": "Sky",
    "sky cinema uno +24": "Sky",
    "sky cinema romance": "Sky",
    "sky cinema family": "Sky",
    "sky cinema due +24": "Sky",
    "sky cinema drama": "Sky",
    "sky cinema suspense": "Sky",
    "sky sport 24": "Sport",
    "sky sport calcio": "Sport",
    "sky calcio 1": "Sport",
    "sky calcio 2": "Sport",
    "sky calcio 3": "Sport",
    "sky calcio 4": "Sport",
    "sky calcio 5": "Sport",
    "sky calcio 6": "Sport",
    "sky calcio 7": "Sport",
    "sky serie": "Sky",
    "20 mediaset": "Mediaset",
}

def get_stream_link(dlhd_id, max_retries=3):
    print(f"Getting stream link for channel ID: {dlhd_id}...")
    
    # Restituisci direttamente l'URL senza fare richieste HTTP
    return f"https://daddylive.dad/embed/stream-{dlhd_id}.php"

def fetch_with_debug(filename, url):
    try:
        print(f'Downloading {url}...')
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        with open(filename, 'wb') as file:
            file.write(response.content)

        print(f'File {filename} downloaded successfully.')
    except requests.exceptions.RequestException as e:
        print(f'Error downloading {url}: {e}')

def search_category(channel_name):
    return STATIC_CATEGORIES.get(channel_name.lower().strip(), "Undefined")

def search_streams(file_path, keyword):
    matches = []
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            soup = BeautifulSoup(file.read(), 'html.parser')
            links = soup.find_all('a', href=True)

        for link in links:
            if keyword.lower() in link.text.lower():
                href = link['href']
                stream_number = href.split('-')[-1].replace('.php', '')
                stream_name = link.text.strip()
                match = (stream_number, stream_name)

                if match not in matches:
                    matches.append(match)
    except FileNotFoundError:
        print(f'The file {file_path} does not exist.')
    return matches

def search_logo(channel_name):
    channel_name_lower = channel_name.lower().strip()
    for key, url in STATIC_LOGOS.items():
        if key in channel_name_lower:
            return url
    return "https://raw.githubusercontent.com/cribbiox/eventi/refs/heads/main/ddlive.png"

def search_tvg_id(channel_name):
    channel_name_lower = channel_name.lower().strip()
    for key, tvg_id in STATIC_TVG_IDS.items():
        if key in channel_name_lower:
            return tvg_id
    return "unknown"

def generate_m3u8_247(matches):
    if not matches:
        print("No matches found for 24/7 channels. Skipping M3U8 generation.")
        return 0

    processed_247_channels = 0

    # Inizializza il file M3U8
    with open(M3U8_OUTPUT_FILE, 'w', encoding='utf-8') as file:
        file.write('#EXTM3U\n')

    # Aggiungi i canali 24/7
    with open(M3U8_OUTPUT_FILE, 'a', encoding='utf-8') as file:
        for channel in matches:
            channel_id = channel[0]
            channel_name = channel[1].replace("Italy", "").replace("8", "").replace("(251)", "").replace("(252)", "").replace("(253)", "").replace("(254)", "").replace("(255)", "").replace("(256)", "").replace("(257)", "").replace("HD+", "")
            tvicon_path = search_logo(channel_name)
            tvg_id = search_tvg_id(channel_name)
            category = search_category(channel_name)
            print(f"Processing 24/7 channel: {channel_name} - Channel Count (24/7): {processed_247_channels + 1}")

            stream_url_dynamic = get_stream_link(channel_id)

            if stream_url_dynamic:
                file.write(f"#EXTINF:-1 tvg-id=\"{tvg_id}\" tvg-name=\"{channel_name}\" tvg-logo=\"{tvicon_path}\" group-title=\"{category}\", {channel_name} (D)\n")
                file.write(f"{PROXY}{MFPDD}{stream_url_dynamic}{MFPDDNOPSW}{MFPDD2}\n\n")
                processed_247_channels += 1
            else:
                print(f"Failed to get stream URL for 24/7 channel ID: {channel_id}. Skipping M3U8 entry for this channel.")

    return processed_247_channels

def add_dazn1_channel():
    print("Aggiunta manuale del canale DAZN 1")
    channel_id = "877"
    channel_name = "DAZN 1"
    tvicon_path = STATIC_LOGOS.get("dazn 1", "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a2/DAZN_1_Logo.svg/774px-DAZN_1_Logo.svg.png")
    tvg_id = "dazn1.it"
    category = "Sport"

    stream_url_dynamic = get_stream_link(channel_id)
    if stream_url_dynamic:
        with open(M3U8_OUTPUT_FILE, 'a', encoding='utf-8') as file:
            file.write(f"#EXTINF:-1 tvg-id=\"{tvg_id}\" tvg-name=\"{channel_name}\" tvg-logo=\"{tvicon_path}\" group-title=\"{category}\", {channel_name} (D)\n")
            file.write(f"{PROXY}{MFPDD}{stream_url_dynamic}{MFPDDNOPSW}{MFPDD2}\n\n")

            return 1
    else:
        print(f"Failed to get stream URL for DAZN 1 channel ID: {channel_id}")
        return 0

# Rimuovi il file esistente per garantirne la rigenerazione
if os.path.exists(M3U8_OUTPUT_FILE):
    os.remove(M3U8_OUTPUT_FILE)

# Fetch e generazione M3U8 per i canali 24/7
fetch_with_debug(daddyLiveChannelsFileName, daddyLiveChannelsURL)
matches_247 = search_streams(daddyLiveChannelsFileName, "Italy")
total_247_channels = generate_m3u8_247(matches_247)

# Aggiungi il canale DAZN 1
dazn_added = add_dazn1_channel()

print(f"Script completato. Canali 24/7 aggiunti: {total_247_channels}, DAZN 1 aggiunto: {dazn_added}")
