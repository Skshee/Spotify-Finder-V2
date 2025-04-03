import tkinter as tk
from API import SpotifyAPI
from UI import SpotifyUI

def main():
    # Initialize the API controller
    api_controller = SpotifyAPI()
    
    # Initialize the UI
    root = tk.Tk()
    app = SpotifyUI(root, api_controller)
    
    # Start the application
    root.mainloop()

if __name__ == "__main__":
    main()