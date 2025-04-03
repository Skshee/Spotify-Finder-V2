import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import io
import requests
from threading import Thread

class SpotifyUI:
    def __init__(self, root, api_controller):
        self.root = root
        self.api_controller = api_controller  # This connects to main.py functionality
        
        # Configure main window
        self.root.title("Spotify Artist Lookup")
        self.root.geometry("900x900")  # Increased height to accommodate 750px image
        self.root.configure(bg="#191414")  # Spotify black
        
        self.create_widgets()
    
    def update_status(self, message):
        self.status_label.config(text=message)
        self.root.update_idletasks()

    def search_artist(self):
        # Clear previous data
        self.tracks_listbox.delete(0, tk.END)
        self.artist_name_label.config(text="")
        self.artist_info_label.config(text="")
        self.artist_image_label.config(image="")
        
        artist_name = self.search_entry.get().strip()
        if not artist_name:
            self.update_status("Please enter an artist name")
            return
        
        self.update_status(f"Searching for {artist_name}...")
        self.root.update()
        
        # Use the API controller to search for artist
        artist = self.api_controller.search_artist_by_name(artist_name)
        if not artist:
            self.update_status("Artist not found")
            return
        
        # Update artist info
        self.artist_name_label.config(text=artist["name"])
        
        followers = artist.get("followers", {}).get("total", 0)
        popularity = artist.get("popularity", 0)
        genres = ", ".join(artist.get("genres", [])[:3])
        
        info_text = f"Followers: {followers:,}\n"
        info_text += f"Popularity: {popularity}/100\n"
        if genres:
            info_text += f"Genres: {genres}"
        
        self.artist_info_label.config(text=info_text)
        
        # Load artist image
        if artist.get("images") and len(artist["images"]) > 0:
            image_url = artist["images"][0]["url"]
            Thread(target=self.load_artist_image, args=(image_url,)).start()
        
        # Get top tracks
        artist_id = artist["id"]
        tracks = self.api_controller.get_songs_by_artist(artist_id)
        
        # Update tracks listbox
        for i, track in enumerate(tracks):
            track_name = track["name"]
            
            # Get featured artists if any
            featured_artists = []
            for artist in track.get("artists", [])[1:]:  # Skip the main artist
                featured_artists.append(artist["name"])
            
            featured_str = ""
            if featured_artists:
                featured_str = f" (with {', '.join(featured_artists)})"
            
            duration_ms = track.get("duration_ms", 0)
            minutes = duration_ms // 60000
            seconds = (duration_ms // 1000) % 60
            duration = f"{minutes}:{seconds:02d}"
            
            track_text = f"{i+1}. {track_name}{featured_str} - {duration}"
            self.tracks_listbox.insert(tk.END, track_text)
        
        self.update_status(f"Found {artist['name']} with {len(tracks)} top tracks")

    def load_artist_image(self, image_url):
        try:
            response = requests.get(image_url)
            img_data = response.content
            img = Image.open(io.BytesIO(img_data))
            
            # Print original size for debugging
            print(f"Original image size: {img.size}")
            
            # Resize to 750x750
            img = img.resize((500, 500), Image.LANCZOS)
            
            # Verify new size
            print(f"Resized image size: {img.size}")
            
            # Convert to PhotoImage
            photo = ImageTk.PhotoImage(img)
            
            # Configure the label to display the image
            self.artist_image_label.config(image=photo)
            self.artist_image_label.image = photo  # Keep reference to avoid garbage collection
            
            # Update the label size explicitly
            self.artist_image_label.config(width=500, height=500)
            
            # Ensure the label has enough space in the layout
            self.artist_image_label.pack(expand=True, fill="both")
            
        except Exception as e:
            print(f"Error loading image: {e}")
            self.update_status("Error loading artist image")

    def create_widgets(self):
        # Header
        header_frame = tk.Frame(self.root, bg="#1DB954")  # Spotify green
        header_frame.pack(fill=tk.X, pady=0)
        
        header_label = tk.Label(header_frame, text="Spotify Artist Lookup", 
                               font=("Helvetica", 24, "bold"), bg="#1DB954", fg="white")
        header_label.pack(pady=15)
        
        # Search frame
        search_frame = tk.Frame(self.root, bg="#191414")
        search_frame.pack(fill=tk.X, pady=20, padx=30)
        
        search_label = tk.Label(search_frame, text="Artist Name:", 
                              font=("Helvetica", 14), bg="#191414", fg="white")
        search_label.pack(side=tk.LEFT, padx=5)
        
        self.search_entry = tk.Entry(search_frame, font=("Helvetica", 14), width=40)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        self.search_entry.bind("<Return>", lambda event: self.search_artist())
        
        search_button = tk.Button(search_frame, text="Search", command=self.search_artist,
                                bg="#1DB954", fg="white", font=("Helvetica", 12, "bold"),
                                padx=10, pady=3)
        search_button.pack(side=tk.LEFT, padx=5)
        
        # Main content frame
        content_frame = tk.Frame(self.root, bg="#191414")
        content_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=10)
        
        # Artist info frame (left side)
        self.artist_frame = tk.Frame(content_frame, bg="#191414")
        self.artist_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 30))
        
        # Artist image placeholder
        self.artist_image_label = tk.Label(self.artist_frame, bg="#333333")
        self.artist_image_label.pack(pady=(0, 15))
        
        # Artist name label
        self.artist_name_label = tk.Label(self.artist_frame, text="", 
                                       font=("Helvetica", 18, "bold"), bg="#191414", fg="white",
                                       wraplength=300)
        self.artist_name_label.pack(pady=5)
        
        # Artist followers and popularity
        self.artist_info_label = tk.Label(self.artist_frame, text="", 
                                       font=("Helvetica", 12), bg="#191414", fg="#b3b3b3",
                                       wraplength=300, justify=tk.LEFT)
        self.artist_info_label.pack(pady=5)
        
        # Songs frame (right side)
        songs_frame = tk.Frame(content_frame, bg="#191414")
        songs_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        songs_label = tk.Label(songs_frame, text="Top Tracks", 
                             font=("Helvetica", 18, "bold"), bg="#191414", fg="white")
        songs_label.pack(anchor=tk.W, pady=(0, 15))
        
        # Tracks listbox with scrollbar
        tracks_frame = tk.Frame(songs_frame, bg="#191414")
        tracks_frame.pack(fill=tk.BOTH, expand=True)
        
        self.tracks_listbox = tk.Listbox(tracks_frame, bg="#333333", fg="white", 
                                      font=("Helvetica", 12), selectbackground="#1DB954",
                                      highlightthickness=0, bd=0)
        self.tracks_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(tracks_frame, orient=tk.VERTICAL, command=self.tracks_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tracks_listbox.config(yscrollcommand=scrollbar.set)
        
        # Status bar
        self.status_label = tk.Label(self.root, text="Ready", bd=1, relief=tk.SUNKEN, anchor=tk.W,
                                  bg="#333333", fg="#b3b3b3", font=("Helvetica", 10))
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)