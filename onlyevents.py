import random
import uuid
import fetcher
import json
import os
import datetime
import pytz
import requests
from bs4 import BeautifulSoup
import time
from dotenv import load_dotenv
load_dotenv()

PROXY = os.getenv("DDPROXY", "")
MFPDD= os.getenv("DDMFPDD", "")
MFPDD2= os.getenv("DDMFPDD2", "")

# Costanti
NUM_CHANNELS = 10000
DADDY_JSON_FILE = "daddyliveSchedule.json"
M3U8_OUTPUT_FILE = "onlyevents.m3u8"
LOGO = "https://raw.githubusercontent.com/cribbiox/eventi/refs/heads/main/ddsport.png"
#REFERER = "forcedtoplay.xyz"
#ORIGIN = "forcedtoplay.xyz"
#HEADER = f"&h_user-agent=Mozilla%2F5.0+%28Windows+NT+10.0%3B+Win64%3B+x64%29+AppleWebKit%2F537.36+%28KHTML%2C+like+Gecko%29+Chrome%2F133.0.0.0+Safari%2F537.36&h_referer=https%3A%2F%2F{REFERER}%2F&h_origin=https%3A%2F%2F{ORIGIN}"

mStartTime = 0
mStopTime = 0

# Headers and related constants from the first code block (assuming these are needed for requests)
Referer = "https://ilovetoplay.xyz/"
Origin = "https://ilovetoplay.xyz"
key_url = "https%3A%2F%2Fkey2.keylocking.ru%2F"

headers = { # **Define base headers *without* Referer and Origin**
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
# Simulated client and credentials - Replace with your actual client and credentials if needed
client = requests # Using requests as a synchronous client

def get_stream_link(dlhd_id, event_name="", channel_name="", max_retries=3):
    print(f"Getting stream link for channel ID: {dlhd_id} - {event_name} on {channel_name}...")
    
    # Restituisci direttamente l'URL senza fare richieste HTTP
    return f"https://daddylive.dad/embed/stream-{dlhd_id}.php"

# Rimuove i file esistenti per garantirne la rigenerazione
for file in [M3U8_OUTPUT_FILE]: # daddyLiveChannelsFileName kept for file removal consistency, but not used  tolto (, DADDY_JSON_FILE)
    if os.path.exists(file):
        os.remove(file)

# Funzioni prima parte dello script
def generate_unique_ids(count, seed=42):
    random.seed(seed)
    return [str(uuid.UUID(int=random.getrandbits(128))) for _ in range(count)]

def loadJSON(filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        return json.load(file)


def addChannelsByLeagueSport():
    global channelCount
    processed_schedule_channels = 0  # Counter for schedule channels

    # Define categories to exclude - these must match exact category names in JSON
    excluded_categories = [
        "TV Shows", "Cricket", "Aussie rules", "Snooker", "Baseball",
        "Biathlon", "Cross Country", "Horse Racing", "Ice Hockey",
        "Waterpolo", "Golf", "Darts", "Cycling",
        "TV Shows</span>", "Cricket</span>", "Aussie rules</span>", "Snooker</span>", "Baseball</span>",
        "Biathlon</span>", "Cross Country</span>", "Horse Racing</span>", "Ice Hockey</span>",
        "Waterpolo</span>", "Golf</span>", "Darts</span>", "Cycling</span>", "Handball</span>", "Squash</span>"
    ]

    # Debug counters
    total_events = 0
    skipped_events = 0
    category_stats = {}  # To track how many events per category

    # First pass to gather category statistics
    for day, day_data in dadjson.items():
        try:
            for sport_key, sport_events in day_data.items():
                # Clean the sport key by removing HTML tags
                clean_sport_key = sport_key.replace("</span>", "").replace("<span>", "").strip()

               #sport_key = sport_key.replace("</span>", "").replace("<span>", "").strip()
                if clean_sport_key not in category_stats:
                    category_stats[clean_sport_key] = 0
                category_stats[clean_sport_key] += len(sport_events)
        except (KeyError, TypeError):
            pass  # Skip problematic days

    # Print category statistics
    print("\n=== Available Categories ===")
    for category, count in sorted(category_stats.items()):
        excluded = "EXCLUDED" if category in excluded_categories else ""
        print(f"{category}: {count} events {excluded}")
    print("===========================\n")

    # Second pass to process events
    for day, day_data in dadjson.items():
        try:
            for sport_key, sport_events in day_data.items():
                # Clean the sport key by removing HTML tags
                #sport_key = sport_key.replace("</span>", "").replace("<span>", "").strip()
                clean_sport_key = sport_key.replace("</span>", "").replace("<span>", "").strip()

                total_events += len(sport_events)

                # Skip only exact category matches
                if clean_sport_key in excluded_categories:
                    skipped_events += len(sport_events)
                    continue

                for game in sport_events:
                    for channel in game.get("channels", []):
                        try:
                            # Clean and format day
                            # Clean and format day
                            clean_day = day.replace(" - Schedule Time UK GMT", "")
                            # Rimuovi completamente i suffissi ordinali (st, nd, rd, th)
                            clean_day = clean_day.replace("st ", " ").replace("nd ", " ").replace("rd ", " ").replace("th ", " ")
                            # Rimuovi anche i suffissi attaccati al numero (1st, 2nd, 3rd, etc.)
                            import re
                            clean_day = re.sub(r'(\d+)(st|nd|rd|th)', r'\1', clean_day)
                            
                            print(f"Original day: '{day}'")
                            print(f"Clean day after processing: '{clean_day}'")
                            
                            day_parts = clean_day.split()
                            print(f"Day parts: {day_parts}")  # Debug per vedere i componenti della data

                            # Handle various date formats with better validation
                            day_num = None
                            month_name = None
                            year = None
                            
                            if len(day_parts) >= 4:  # Standard format: Weekday Month Day Year
                                weekday = day_parts[0]
                                # Verifica se il secondo elemento contiene lettere (è il mese) o numeri (è il giorno)
                                if any(c.isalpha() for c in day_parts[1]):
                                    # Formato: Weekday Month Day Year
                                    month_name = day_parts[1]
                                    day_num = day_parts[2]
                                elif any(c.isalpha() for c in day_parts[2]):
                                    # Formato: Weekday Day Month Year
                                    day_num = day_parts[1]
                                    month_name = day_parts[2]
                                else:
                                    # Se non riusciamo a determinare, assumiamo il formato più comune
                                    day_num = day_parts[1]
                                    month_name = day_parts[2]
                                year = day_parts[3]
                                print(f"Parsed date components: weekday={weekday}, day={day_num}, month={month_name}, year={year}")
                            elif len(day_parts) == 3:
                                # Format could be: "Weekday Day Year" (missing month) or "Day Month Year"
                                if day_parts[0].lower() in ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]:
                                    # It's "Weekday Day Year" format (missing month)
                                    day_num = day_parts[1]
                                    # Get current month for Rome timezone
                                    rome_tz = pytz.timezone('Europe/Rome')
                                    current_month = datetime.datetime.now(rome_tz).strftime('%B')
                                    month_name = current_month
                                    year = day_parts[2]
                                else:
                                    # Assume Day Month Year
                                    day_num = day_parts[0]
                                    month_name = day_parts[1]
                                    year = day_parts[2]
                            else:
                                # Use current date from Rome timezone
                                rome_tz = pytz.timezone('Europe/Rome')
                                now = datetime.datetime.now(rome_tz)
                                day_num = now.strftime('%d')
                                month_name = now.strftime('%B')
                                year = now.strftime('%Y')
                                print(f"Using current Rome date for: {clean_day}")

                            # Validate day_num - ensure it's a number and extract only digits
                            if day_num:
                                # Extract only digits from day_num
                                day_num_digits = re.sub(r'[^0-9]', '', str(day_num))
                                if day_num_digits:
                                    day_num = day_num_digits
                                else:
                                    # If no digits found, use current day
                                    rome_tz = pytz.timezone('Europe/Rome')
                                    day_num = datetime.datetime.now(rome_tz).strftime('%d')
                                    print(f"Warning: Invalid day number '{day_num}', using current day: {day_num}")
                            else:
                                # If day_num is None, use current day
                                rome_tz = pytz.timezone('Europe/Rome')
                                day_num = datetime.datetime.now(rome_tz).strftime('%d')
                                print(f"Warning: Missing day number, using current day: {day_num}")

                            # Get time from game data
                            time_str = game.get("time", "00:00")

                            # Converti l'orario da UK a CET (aggiungi 1 ora invece di 2)
                            time_parts = time_str.split(":")
                            if len(time_parts) == 2:
                                hour = int(time_parts[0])
                                minute = time_parts[1]
                                # Aggiungi una ora all'orario UK
                                hour_cet = (hour + 1) % 24
                                # Assicura che l'ora abbia due cifre
                                hour_cet_str = f"{hour_cet:02d}"
                                # Nuovo time_str con orario CET
                                time_str_cet = f"{hour_cet_str}:{minute}"
                            else:
                                # Se il formato dell'orario non è corretto, mantieni l'originale
                                time_str_cet = time_str

                            # Convert month name to number
                            month_map = {
                                "January": "01", "February": "02", "March": "03", "April": "04",
                                "May": "05", "June": "06", "July": "07", "August": "08",
                                "September": "09", "October": "10", "November": "11", "December": "12"
                            }
                            month_num = month_map.get(month_name, "01")  # Default to January if not found

                            # Ensure day has leading zero if needed
                            if len(str(day_num)) == 1:
                                day_num = f"0{day_num}"

                            # Create formatted date time
                            year_short = str(year)[-2:]  # Extract last two digits of year
                            formatted_date_time = f"{day_num}/{month_num}/{year_short} - {time_str_cet}"

                            # Also create proper datetime objects for EPG
                            # Make sure we're using clean numbers for the date components
                            try:
                                # Ensure all date components are valid
                                if not day_num or day_num == "":
                                    rome_tz = pytz.timezone('Europe/Rome')
                                    day_num = datetime.datetime.now(rome_tz).strftime('%d')
                                    print(f"Using current day as fallback: {day_num}")
                                
                                if not month_num or month_num == "":
                                    month_num = "01"  # Default to January
                                    print(f"Using January as fallback month")
                                
                                if not year or year == "":
                                    rome_tz = pytz.timezone('Europe/Rome')
                                    year = datetime.datetime.now(rome_tz).strftime('%Y')
                                    print(f"Using current year as fallback: {year}")
                                
                                if not time_str or time_str == "":
                                    time_str = "00:00"
                                    print(f"Using 00:00 as fallback time")
                                
                                # Ensure day_num has proper format (1-31)
                                try:
                                    day_int = int(day_num)
                                    if day_int < 1 or day_int > 31:
                                        day_num = "01"  # Default to first day of month
                                        print(f"Day number out of range, using 01 as fallback")
                                except ValueError:
                                    day_num = "01"  # Default to first day of month
                                    print(f"Invalid day number format, using 01 as fallback")
                                
                                # Ensure day has leading zero if needed
                                if len(str(day_num)) == 1:
                                    day_num = f"0{day_num}"
                                
                                date_str = f"{year}-{month_num}-{day_num} {time_str}:00"
                                print(f"Attempting to parse date: '{date_str}'")
                                start_date_utc = datetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
                                
                                # Convert to Amsterdam timezone
                                amsterdam_timezone = pytz.timezone("Europe/Amsterdam")
                                start_date_amsterdam = start_date_utc.replace(tzinfo=pytz.UTC).astimezone(amsterdam_timezone)
                                
                                # Format for EPG
                                mStartTime = start_date_amsterdam.strftime("%Y%m%d%H%M%S")
                                mStopTime = (start_date_amsterdam + datetime.timedelta(days=2)).strftime("%Y%m%d%H%M%S")
                            except ValueError as e:
                                # Definisci date_str qui se non è già definita
                                error_msg = str(e)
                                if 'date_str' not in locals():
                                    date_str = f"Error with: {year}-{month_num}-{day_num} {time_str}:00"
                                
                                print(f"Date parsing error: {error_msg} for date string '{date_str}'")
                                # Use current time as fallback
                                amsterdam_timezone = pytz.timezone("Europe/Amsterdam")
                                now = datetime.datetime.now(amsterdam_timezone)
                                mStartTime = now.strftime("%Y%m%d%H%M%S")
                                mStopTime = (now + datetime.timedelta(days=2)).strftime("%Y%m%d%H%M%S")

                            # Remove the problematic else statement that has no matching if
                            # else:
                            #    print(f"Invalid date format after cleaning: {clean_day}")
                            #    continue

                        except Exception as e:
                            print(f"Error processing date '{day}': {e}")
                            print(f"Game time: {game.get('time', 'No time found')}")
                            continue

                        # Get next unique ID
                        UniqueID = unique_ids.pop(0)

                        try:
                            # Build channel name with new date format
                          # channelName = game["event"] + " " + formatted_date_time + "  " + channel["channel_name"]
                            channelName = formatted_date_time + "  " + channel["channel_name"]

                            # Extract event part and channel part for TVG ID
                           #if ":" in game["event"]:
                           #    event_part = game["event"].split(":")[0].strip()
                           #else:
                           #    event_part = game["event"].strip()
                            event_name = game["event"].split(":")[0].strip() if ":" in game["event"] else game["event"].strip()
                            event_details = game["event"]  # Keep the full event details for tvg-name

                           #channel_part = channel["channel_name"].strip()
                           #custom_tvg_id = f"{event_part} - {channel_part}"

                        except (TypeError, KeyError) as e:
                            print(f"Error processing event: {e}")
                            continue

                        # Process channel information
                        channelID = f"{channel['channel_id']}"
                        tvgName = channelName
                        tvLabel = tvgName
                        channelCount += 1
                        print(f"Processing channel {channelCount}: {clean_sport_key} - {channelName}")

                        # Get stream URL
                        stream_url_dynamic = get_stream_link(channelID, game["event"], channel["channel_name"])

                        if stream_url_dynamic:
                            # Write to M3U8 file
                            with open(M3U8_OUTPUT_FILE, 'a', encoding='utf-8') as file:
                                if channelCount == 1:
                                    file.write('#EXTM3U\n')

                            with open(M3U8_OUTPUT_FILE, 'a', encoding='utf-8') as file:
                                # Estrai l'orario dal formatted_date_time
                                time_only = time_str_cet if time_str_cet else "00:00"

                                # Crea il nuovo formato per tvg-name con l'orario all'inizio e la data alla fine
                                tvg_name = f"{time_only} {event_details} - {day_num}/{month_num}/{year_short}"

                                file.write(f'#EXTINF:-1 tvg-id="{event_name} - {event_details.split(":", 1)[1].strip() if ":" in event_details else event_details}" tvg-name="{tvg_name}" tvg-logo="{LOGO}" group-title="{clean_sport_key}", {channel["channel_name"]}\n')
                                file.write(f"{PROXY}{MFPDD}{stream_url_dynamic}{MFPDD2}\n\n")


                            processed_schedule_channels += 1
                        else:
                            print(f"Failed to get stream URL for channel ID: {channelID}")


        except KeyError as e:
            print(f"KeyError: {e} - Key may not exist in JSON structure")

    # Print summary
    print(f"\n=== Processing Summary ===")
    print(f"Total events found: {total_events}")
    print(f"Events skipped due to category filters: {skipped_events}")
    print(f"Channels successfully processed: {processed_schedule_channels}")
    print(f"===========================\n")

    return processed_schedule_channels

STATIC_LOGOS = {
    "sky uno": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/italy/sky-uno-it.png",
    "dazn 1": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a2/DAZN_1_Logo.svg/774px-DAZN_1_Logo.svg.png"
}

STATIC_TVG_IDS = {
    "sky uno": "sky uno",
    "20 mediaset": "Mediaset 20",
}

STATIC_CATEGORIES = {
    "sky uno": "Sky",
    "20 mediaset": "Mediaset",
}

def fetch_with_debug(filename, url):
    try:
        #print(f'Downloading {url}...') # Debug removed
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        with open(filename, 'wb') as file:
            file.write(response.content)

        #print(f'File {filename} downloaded successfully.') # Debug removed
    except requests.exceptions.RequestException as e:
        #print(f'Error downloading {url}: {e}') # Debug removed
        pass # No debug print, just skip


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
        #print(f'The file {file_path} does not exist.') # Debug removed
        pass # No debug print, just skip
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

def generate_m3u8_247(matches): # Rinominata per evitare conflitti, ma non sarà usata
    if not matches:
        #print("No matches found for 24/7 channels. Skipping M3U8 generation.") # Debug removed
        return 0 # Return 0 as no 24/7 channels processed

    processed_247_channels = 0 # Counter for 24/7 channels, but will remain 0
    with open(M3U8_OUTPUT_FILE, 'a', encoding='utf-8') as file: # Appende al file esistente
        pass # 24/7 generation is skipped, so the loop and content writing are removed

    #print("M3U8 file updated with 24/7 channels.") # Debug removed, and incorrect message
    return processed_247_channels # Return count of processed 24/7 channels (always 0 now)


# Inizio del codice principale

# Inizializza contatore e genera ID univoci
channelCount = 0
unique_ids = generate_unique_ids(NUM_CHANNELS)
total_schedule_channels = 0 # Counter for total schedule channels attempted
total_247_channels = 0 # Counter for total 24/7 channels attempted - will remain 0

# Scarica il file JSON con la programmazione
# fetcher.fetchHTML(DADDY_JSON_FILE, "https://daddylive.dad/schedule/schedule-generated.json")

# Carica i dati dal JSON
dadjson = loadJSON(DADDY_JSON_FILE)

# Aggiunge i canali reali
total_schedule_channels = addChannelsByLeagueSport()

# Verifica se sono stati creati canali validi
if channelCount == 0:
    print("Nessun canale valido trovato dalla programmazione.") # Modificata la frase
    pass


# Fetch e generazione M3U8 per i canali 24/7 - RIMOSSO COMPLETAMENTE
# fetch_with_debug(daddyLiveChannelsFileName, daddyLiveChannelsURL)
# matches_247 = search_streams(daddyLiveChannelsFileName, "Italy") # Cerca tutti i canali
# total_247_channels = generate_m3u8_247(matches_247)

print(f"Script completato. Canali eventi aggiunti: {total_schedule_channels}") # Messaggio finale modificato, solo canali eventi
