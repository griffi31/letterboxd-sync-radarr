import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- CONFIG ---
LETTERBOXD_USERNAME = "griffi31"
RADARR_URL = "http://192.168.6.225:7878"  # Correct IP address for Radarr
RADARR_API_KEY = "3465bf63846142239eda93b573b55d3c"
QUALITY_PROFILE_ID = 7
ROOT_FOLDER_PATH = "/movies"

# --- FUNCTIONS ---

def fetch_watchlist(username):
    print("Fetching Letterboxd Watchlist using Selenium...")

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    service = Service("/usr/bin/chromedriver")  # Make sure the chromedriver path is correct
    driver = webdriver.Chrome(service=service, options=chrome_options)

    watchlist_url = f"https://letterboxd.com/{username}/watchlist/"
    driver.get(watchlist_url)
    
    # Wait for the poster elements to be fully loaded
    wait = WebDriverWait(driver, 20)  # Increase wait time for full page load
    posters = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "li.poster-container")))

    print(f"Found {len(posters)} poster elements.")  # Log the number of poster elements

    movies = []

    for poster in posters:
        try:
            # Try to extract the title from the data-original-title attribute of the 'a.frame' tag
            title_element = poster.find_element(By.CSS_SELECTOR, "a.frame")
            movie_title = title_element.get_attribute("data-original-title") if title_element else None

            # Log and check if the title was found
            print(f"Found movie title: {movie_title}")  
            
            if movie_title:
                movies.append(movie_title)
        except Exception as e:
            print(f"Error reading poster: {e}")
            continue

    driver.quit()

    print(f"Found {len(movies)} movies.")
    return movies

def movie_in_radarr(movie_title):
    params = {"term": movie_title}
    headers = {"X-Api-Key": RADARR_API_KEY}
    response = requests.get(f"{RADARR_URL}/api/v3/movie/lookup", params=params, headers=headers)
    if response.status_code != 200:
        print(f"Failed to search Radarr for {movie_title}")
        return None

    results = response.json()
    if results:
        return results[0]
    else:
        return None

def add_movie_to_radarr(movie_info):
    payload = {
        "title": movie_info['title'],
        "qualityProfileId": QUALITY_PROFILE_ID,
        "titleSlug": movie_info['titleSlug'],
        "images": movie_info['images'],
        "tmdbId": movie_info['tmdbId'],
        "year": movie_info['year'],
        "rootFolderPath": ROOT_FOLDER_PATH,
        "monitored": True,
        "addOptions": {"searchForMovie": True}
    }
    headers = {"X-Api-Key": RADARR_API_KEY, "Content-Type": "application/json"}
    response = requests.post(f"{RADARR_URL}/api/v3/movie", json=payload, headers=headers)

    if response.status_code == 201:
        print(f"✅ Added {movie_info['title']} to Radarr!")
    elif response.status_code == 400 and 'already in your library' in response.text:
        print(f"✅ {movie_info['title']} is already in Radarr.")
    else:
        print(f"❌ Failed to add {movie_info['title']} to Radarr: {response.text}")

# --- MAIN ---
if __name__ == "__main__":
    # Fetch the watchlist from Letterboxd
    watchlist = fetch_watchlist(LETTERBOXD_USERNAME)

    for title in watchlist:
        print(f"Processing {title}...")
        movie = movie_in_radarr(title)
        if movie:
            add_movie_to_radarr(movie)
        else:
            print(f"❌ Could not find {title} in Radarr lookup.")
        time.sleep(1)  # Polite delay

    print("🎉 Done syncing Letterboxd watchlist!")
