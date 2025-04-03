import os
import base64
import json
from requests import post, get
from dotenv import load_dotenv

class SpotifyAPI:
    def __init__(self):
        # Load environment variables
        load_dotenv()
        self.client_id = os.getenv("CLIENT_ID")
        self.client_secret = os.getenv("CLIENT_SECRET")
        
        # Initialize token
        self.token = self.get_token()
    
    def get_token(self):
        """Get Spotify API access token"""
        auth_string = self.client_id + ":" + self.client_secret
        auth_bytes = auth_string.encode("utf-8")
        auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

        url = "https://accounts.spotify.com/api/token"
        headers = {
            "Authorization": "Basic " + auth_base64,
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = {"grant_type": "client_credentials"}
        result = post(url, headers=headers, data=data)
        json_result = json.loads(result.content)
        return json_result["access_token"]
    
    def get_auth_header(self):
        """Get authorization header for API requests"""
        return {"Authorization": "Bearer " + self.token}
    
    def search_artist_by_name(self, artist_name):
        """Search for an artist by name"""
        url = "https://api.spotify.com/v1/search"
        headers = self.get_auth_header()
        query = f"?q={artist_name}&type=artist&limit=1"

        query_url = url + query
        result = get(query_url, headers=headers)
        json_result = json.loads(result.content)

        if "artists" not in json_result or "items" not in json_result["artists"]:
            print("No Artist Found")
            return None

        return json_result["artists"]["items"][0]
    
    def get_songs_by_artist(self, artist_id):
        """Get top tracks for an artist"""
        url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks?market=IN"
        headers = self.get_auth_header()
        result = get(url, headers=headers)
        json_result = json.loads(result.content)

        if "tracks" not in json_result:
            print("Error fetching songs")
            return []

        return json_result["tracks"]
        

    