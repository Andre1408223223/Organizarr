SONARR_URL = 'http://100.100.22.66:8989'
SONARR_API_KEY = '96486d37113846e5bacb90fc761ad96b' 
ROOT_FOLDER = "/home/andre/Shared/Entertainment_drive/Downloads/TV-Shows"
import requests
from fuzzywuzzy import fuzz

def logger(message):
   print(message)

class Metadata:
    def get_sonnar_id_from_title(self, title, threshold=80):
        url = f"{SONARR_URL}/api/v3/series"
        headers = {
            "X-Api-Key": SONARR_API_KEY
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        series_list = response.json()
        best_match = None
        highest_score = 0
        for show in series_list:
            score = fuzz.token_set_ratio(show["title"].lower(), title.lower())
            if score > highest_score and score >= threshold:
                highest_score = score
                best_match = show
        if best_match:
            return best_match["id"]
        
        return None

    def add_to_sonarr(self, series_title, QUALITY_PROFILE_ID=4):
        headers = {
            'X-Api-Key': SONARR_API_KEY,
            'Content-Type': 'application/json'
        }
        search_url = f'{SONARR_URL}/api/v3/series/lookup?term={series_title}'
        response = requests.get(search_url, headers=headers)
    
        if response.status_code != 200 or not response.json():
            logger(f"Series '{series_title}' not found.")
            return
    
        candidates = response.json()
        
        # Find best fuzzy match in candidates
        best_match = None
        highest_score = 0
        for candidate in candidates:
            score = fuzz.token_set_ratio(candidate['title'].lower(), series_title.lower())
            if score > highest_score:
                highest_score = score
                best_match = candidate
        
        if not best_match or highest_score < 70:  # threshold for matching
            logger(f"No good fuzzy match found for '{series_title}'. Best score: {highest_score}")
            return
    
        series_data = best_match
        payload = {
            'tvdbId': series_data['tvdbId'],
            'title': series_data['title'],
            'qualityProfileId': int(QUALITY_PROFILE_ID),
            'titleSlug': series_data['titleSlug'],
            'images': series_data['images'],
            'seasons': [{'seasonNumber': s['seasonNumber'], 'monitored': False} for s in series_data['seasons']],
            'monitored': False,
            'rootFolderPath': ROOT_FOLDER,
            'addOptions': {
                'searchForMissingEpisodes': False,
                'monitor': 'none'
            }
        }
        add_url = f'{SONARR_URL}/api/v3/series'
        add_response = requests.post(add_url, json=payload, headers=headers)
        if add_response.status_code != 201:
            logger(f"Failed to add series: {add_response.status_code} - {add_response.text}")

    def remove_from_sonarr(self, series_title):
        headers = {
            "X-Api-Key": SONARR_API_KEY
        }

        id = self.get_sonnar_id_from_title(series_title)
        if not id:
            logger(f"Series '{series_title}' not found in Sonarr.")
            return
        
        url = f"{SONARR_URL}/api/v3/series/{id}?deleteFiles=false"
        response = requests.delete(url, headers=headers)
        if response.status_code != 200:
            logger(f"Failed to remove '{series_title}': {response.status_code} - {response.text}")

    def get_metadata(self, title, season=None, episode=None):
        series_id = self.get_sonnar_id_from_title(title)

        if not series_id:
            self.add_to_sonarr(title)

        


if __name__ == "__main__":
    m = Metadata()
    print(m.get_metadata("Solo leveling", season=1, episode=1))