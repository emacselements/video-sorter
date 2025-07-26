#!/usr/bin/env python3
# pip install python-vlc
import os
import sys
import tkinter as tk
from tkinter import filedialog
import vlc
import time

class VideoSorter:
    def __init__(self, root):
        self.root = root
        self.root.title("Video File Sorter")
        self.root.geometry("800x600")
        
        # Set up VLC instance and player (with reduced verbosity)
        self.instance = vlc.Instance('--quiet', '--no-xlib')
        self.player = self.instance.media_player_new()
        self.is_fullscreen = False
        self.is_muted = False
        self.previous_volume = 70  # Default volume
        self.is_repeat = False  # Repeat mode flag
        self.is_auto_play = False  # Auto play mode flag
        self.is_random = False  # Random mode flag
        
        # Create a frame for embedding the video
        self.video_frame = tk.Frame(root, bg="black")
        self.video_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create a timer to update the time display
        self.update_timer_id = None
        
        # Control panel at the bottom
        self.control_panel = tk.Frame(root, height=80)  # Increased height for 3 rows
        self.control_panel.pack(fill=tk.X, side=tk.BOTTOM)
        
        # Create buttons - first row (playback controls)
        button_frame1 = tk.Frame(self.control_panel)
        button_frame1.pack(fill=tk.X, side=tk.TOP, padx=5, pady=2)
        
        self.play_pause_button = tk.Button(button_frame1, text="Play/Pause", command=self.toggle_play)
        self.play_pause_button.pack(side=tk.LEFT, padx=5, pady=2)
        
        self.replay_button = tk.Button(button_frame1, text="Replay", command=self.replay_video)
        self.replay_button.pack(side=tk.LEFT, padx=5, pady=2)
        
        self.skip_back_button = tk.Button(button_frame1, text="<< 15s", command=self.skip_backward)
        self.skip_back_button.pack(side=tk.LEFT, padx=5, pady=2)
        
        self.skip_forward_button = tk.Button(button_frame1, text="15s >>", command=self.skip_forward)
        self.skip_forward_button.pack(side=tk.LEFT, padx=5, pady=2)
        
        self.skip_forward_long_button = tk.Button(button_frame1, text="45s >>", command=self.skip_forward_long)
        self.skip_forward_long_button.pack(side=tk.LEFT, padx=5, pady=2)
        
        # Second row (navigation and mode buttons)
        button_frame2 = tk.Frame(self.control_panel)
        button_frame2.pack(fill=tk.X, side=tk.TOP, padx=5, pady=2)
        
        self.prev_button = tk.Button(button_frame2, text="Previous", command=self.prev_video)
        self.prev_button.pack(side=tk.LEFT, padx=5, pady=2)
        
        self.next_button = tk.Button(button_frame2, text="Next", command=self.next_video)
        self.next_button.pack(side=tk.LEFT, padx=5, pady=2)
        
        self.repeat_button = tk.Button(button_frame2, text="Repeat: Off", command=self.toggle_repeat)
        self.repeat_button.pack(side=tk.LEFT, padx=5, pady=2)
        
        self.auto_play_button = tk.Button(button_frame2, text="Auto: Off", command=self.toggle_auto_play)
        self.auto_play_button.pack(side=tk.LEFT, padx=5, pady=2)
        
        self.random_button = tk.Button(button_frame2, text="Random: Off", command=self.toggle_random)
        self.random_button.pack(side=tk.LEFT, padx=5, pady=2)
        
        # Third row (file operations and system buttons)
        button_frame3 = tk.Frame(self.control_panel)
        button_frame3.pack(fill=tk.X, side=tk.TOP, padx=5, pady=2)
        
        self.delete_button = tk.Button(button_frame3, text="Delete", command=self.delete_video)
        self.delete_button.pack(side=tk.LEFT, padx=5, pady=2)
        
        self.fullscreen_button = tk.Button(button_frame3, text="Fullscreen", command=self.toggle_fullscreen)
        self.fullscreen_button.pack(side=tk.LEFT, padx=5, pady=2)
        
        # Add folder selection button
        self.select_folder_button = tk.Button(button_frame3, text="Select Folder", command=self.select_folder)
        self.select_folder_button.pack(side=tk.LEFT, padx=5, pady=2)
        
        # Add exit button
        self.exit_button = tk.Button(button_frame3, text="Exit", command=self.on_close, bg="#ffcccc")
        self.exit_button.pack(side=tk.LEFT, padx=5, pady=2)
        
        # Fourth row with volume controls
        volume_frame = tk.Frame(self.control_panel)
        volume_frame.pack(fill=tk.X, side=tk.TOP, padx=5, pady=2)
        
        self.mute_button = tk.Button(volume_frame, text="Mute", command=self.toggle_mute, width=5)
        self.mute_button.pack(side=tk.LEFT, padx=5, pady=2)
        
        volume_label = tk.Label(volume_frame, text="Volume:")
        volume_label.pack(side=tk.LEFT, padx=5, pady=2)
        
        self.volume_scale = tk.Scale(volume_frame, from_=0, to=100, orient=tk.HORIZONTAL, 
                                     command=self.set_volume, length=200)
        self.volume_scale.set(70)  # Default volume level
        self.volume_scale.pack(side=tk.LEFT, padx=5, pady=2)
        
        # Add timer label in volume frame
        self.time_label = tk.Label(volume_frame, text="00:00 / 00:00", 
                                  fg="black", bg="#dddddd", padx=5, pady=2,
                                  font=("Arial", 10), relief=tk.GROOVE)
        self.time_label.pack(side=tk.LEFT, padx=10, pady=2)
        
        # Status label
        self.status_label = tk.Label(volume_frame, text="No folder selected")
        self.status_label.pack(side=tk.RIGHT, padx=10, pady=2)
        
        # Video list and current position
        self.video_files = []
        self.current_index = -1
        
        # Load folder history
        self.history_file = os.path.expanduser("~/.video_sorter_history")
        self.folder_history = self.load_folder_history()
        
        # Bind the window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Set up key bindings
        self.root.bind("<space>", lambda e: self.toggle_play())
        self.root.bind("r", lambda e: self.replay_video())
        self.root.bind("l", lambda e: self.toggle_repeat())  # 'l' for loop
        self.root.bind("a", lambda e: self.toggle_auto_play())  # 'a' for auto
        self.root.bind("s", lambda e: self.toggle_random())  # 's' for shuffle
        self.root.bind("<Delete>", lambda e: self.delete_video())
        self.root.bind("<Right>", lambda e: self.skip_forward())
        self.root.bind("<Left>", lambda e: self.skip_backward())
        self.root.bind("<Up>", lambda e: self.next_video())
        self.root.bind("<Down>", lambda e: self.prev_video())
        self.root.bind("<F11>", lambda e: self.toggle_fullscreen())
        self.root.bind("<Escape>", lambda e: self.exit_fullscreen())
        self.root.bind("m", lambda e: self.toggle_mute())
    
    def load_folder_history(self):
        """Load folder history from file"""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r') as f:
                    return [line.strip() for line in f.readlines() if line.strip()]
        except:
            pass
        return []
    
    def save_folder_history(self):
        """Save folder history to file"""
        try:
            with open(self.history_file, 'w') as f:
                for folder in self.folder_history:
                    f.write(folder + '\n')
        except:
            pass
    
    def add_to_history(self, folder_path):
        """Add folder to history, moving it to top if it exists"""
        if folder_path in self.folder_history:
            self.folder_history.remove(folder_path)
        self.folder_history.insert(0, folder_path)
        # Keep only last 10 folders
        self.folder_history = self.folder_history[:10]
        self.save_folder_history()
    
    def select_folder(self):
        # Create a popup menu for folder selection
        import tkinter.messagebox as messagebox
        
        if self.folder_history:
            # Create a simple dialog with history
            choice_window = tk.Toplevel(self.root)
            choice_window.title("Select Folder")
            choice_window.geometry("500x300")
            choice_window.transient(self.root)
            choice_window.grab_set()
            
            tk.Label(choice_window, text="Recent folders:", font=("Arial", 12, "bold")).pack(pady=5)
            
            # Create listbox for history
            listbox_frame = tk.Frame(choice_window)
            listbox_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
            
            scrollbar = tk.Scrollbar(listbox_frame)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            self.history_listbox = tk.Listbox(listbox_frame, yscrollcommand=scrollbar.set)
            self.history_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.config(command=self.history_listbox.yview)
            
            # Populate listbox with history
            for folder in self.folder_history:
                if os.path.exists(folder):  # Only show existing folders
                    self.history_listbox.insert(tk.END, folder)
            
            # Button frame
            button_frame = tk.Frame(choice_window)
            button_frame.pack(fill=tk.X, padx=10, pady=5)
            
            def use_selected():
                selection = self.history_listbox.curselection()
                if selection:
                    folder_path = self.history_listbox.get(selection[0])
                    choice_window.destroy()
                    self.add_to_history(folder_path)
                    self.load_videos_from_folder(folder_path)
            
            def browse_new():
                choice_window.destroy()
                self.browse_for_folder()
            
            tk.Button(button_frame, text="Use Selected", command=use_selected).pack(side=tk.LEFT, padx=5)
            tk.Button(button_frame, text="Browse New Folder", command=browse_new).pack(side=tk.LEFT, padx=5)
            tk.Button(button_frame, text="Cancel", command=choice_window.destroy).pack(side=tk.RIGHT, padx=5)
            
            # Double-click to select
            self.history_listbox.bind("<Double-Button-1>", lambda e: use_selected())
            
        else:
            # No history, go straight to browser
            self.browse_for_folder()
    
    def browse_for_folder(self):
        # Set initial directory to last used folder if available
        initial_dir = self.folder_history[0] if self.folder_history else None
        if initial_dir and not os.path.exists(initial_dir):
            initial_dir = os.path.dirname(initial_dir) if initial_dir else None
        
        folder_path = filedialog.askdirectory(
            title="Select Folder Containing Videos",
            initialdir=initial_dir,
            mustexist=True
        )
        
        if folder_path:
            self.add_to_history(folder_path)
            self.load_videos_from_folder(folder_path)
    
    def load_videos_from_folder(self, folder_path):
        # Common video file extensions
        video_extensions = ('.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v')
        
        # Get all video files (skip dot files)
        self.video_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) 
                           if os.path.isfile(os.path.join(folder_path, f)) and 
                           not f.startswith('.') and
                           f.lower().endswith(video_extensions)]
        
        if not self.video_files:
            self.status_label.config(text="No video files found in folder")
            return
        
        self.current_index = 0
        self.status_label.config(text=f"Found {len(self.video_files)} videos")
        self.play_current_video()
    
    def play_current_video(self):
        if not self.video_files or self.current_index < 0 or self.current_index >= len(self.video_files):
            return
        
        # Get the current video file
        video_path = self.video_files[self.current_index]
        
        # Update the window title with the filename
        filename = os.path.basename(video_path)
        self.root.title(f"Video File Sorter - {filename}")
        
        # Stop any current playback and mute before loading new video to prevent audio artifacts
        self.player.audio_set_mute(True)
        self.player.stop()
        
        # Create a new media with options
        media = self.instance.media_new(str(video_path))
        
        # Set media to player
        self.player.set_media(media)
        
        # On Linux, you need to give the ID of the window to embed the video
        if sys.platform.startswith('linux'):
            self.player.set_xwindow(self.video_frame.winfo_id())
        elif sys.platform == "win32":
            self.player.set_hwnd(self.video_frame.winfo_id())
        elif sys.platform == "darwin":
            self.player.set_nsobject(self.video_frame.winfo_id())
        
        # Set volume to match the scale
        self.player.audio_set_volume(self.volume_scale.get())
        
        # Start playing
        self.player.play()
        
        # Setup a timer to restore audio and start timer updates as soon as the player is ready
        def check_and_restore():
            # Once media is parsed and playing, restore audio
            state = self.player.get_state()
            if state in (vlc.State.Playing, vlc.State.Paused):
                # Restore audio state after a short delay
                self.root.after(50, self.restore_audio)
                # Start updating the timer
                self.start_time_updates()
            else:
                # Check again in 100ms
                self.root.after(100, check_and_restore)
                
        # Start the check timer
        self.root.after(100, check_and_restore)
        
        # Update status
        self.status_label.config(text=f"Playing {self.current_index+1}/{len(self.video_files)}")
    
    def replay_video(self):
        """Restart the current video from the beginning"""
        if not self.video_files or self.current_index < 0 or self.current_index >= len(self.video_files):
            return
        
        # Stop the player
        self.player.stop()
        
        # Small delay to ensure stop is processed
        self.root.after(100, self._restart_video)
    
    def _restart_video(self):
        """Helper method to restart video after stop"""
        # Start playing again
        self.player.play()
        
        # Wait for player to be ready, then seek to beginning (0 seconds)
        def check_and_seek():
            state = self.player.get_state()
            if state in (vlc.State.Playing, vlc.State.Paused):
                self.player.set_time(0)  # Start from beginning
                self.start_time_updates()
            else:
                self.root.after(100, check_and_seek)
        
        self.root.after(100, check_and_seek)
    
    def format_time(self, ms):
        """Format milliseconds to MM:SS format"""
        seconds = ms // 1000
        minutes = seconds // 60
        seconds %= 60
        return f"{minutes:02d}:{seconds:02d}"
    
    def update_time_display(self):
        """Update the time display"""
        if self.player.is_playing() or self.player.get_state() == vlc.State.Paused:
            current = self.player.get_time()
            duration = self.player.get_length()
            
            if current >= 0 and duration > 0:
                self.time_label.config(text=f"{self.format_time(current)} / {self.format_time(duration)}")
            
            # Schedule next update
            self.update_timer_id = self.root.after(500, self.update_time_display)
        elif self.player.get_state() == vlc.State.Ended:
            # Video ended, check what to do next
            if self.is_repeat:
                # Repeat current video
                self.replay_video()
            elif self.is_auto_play:
                # Move to next video automatically
                if self.is_random:
                    self.random_video()
                else:
                    self.next_video()
            else:
                # Just keep checking for state changes
                self.update_timer_id = self.root.after(500, self.update_time_display)
        else:
            # Check again in case state changes
            self.update_timer_id = self.root.after(500, self.update_time_display)
    
    def start_time_updates(self):
        """Start updating the time display"""
        # Cancel any existing timer
        if self.update_timer_id:
            self.root.after_cancel(self.update_timer_id)
        
        # Start updating
        self.update_time_display()
    
    def restore_audio(self):
        # Restore audio to previous state
        if not self.is_muted:
            self.player.audio_set_mute(False)
    
    def skip_forward(self):
        if self.player.is_playing() or self.player.get_state() == vlc.State.Paused:
            current_time = self.player.get_time()
            self.player.set_time(current_time + 15000)  # Skip forward 15 seconds
    
    def skip_forward_long(self):
        if self.player.is_playing() or self.player.get_state() == vlc.State.Paused:
            current_time = self.player.get_time()
            self.player.set_time(current_time + 45000)  # Skip forward 45 seconds
    
    def skip_backward(self):
        if self.player.is_playing() or self.player.get_state() == vlc.State.Paused:
            current_time = self.player.get_time()
            # Make sure we don't go below 0
            new_time = max(0, current_time - 15000)  # Skip backward 15 seconds
            self.player.set_time(new_time)
    

    
    def toggle_fullscreen(self):
        if not self.is_fullscreen:
            self.original_geometry = self.root.geometry()
            self.root.attributes('-fullscreen', True)
            # Keep control panel visible in fullscreen mode
            self.is_fullscreen = True
        else:
            self.exit_fullscreen()
    
    def exit_fullscreen(self):
        if self.is_fullscreen:
            self.root.attributes('-fullscreen', False)
            self.root.geometry(self.original_geometry)
            self.is_fullscreen = False
    
    def toggle_play(self):
        state = self.player.get_state()
        if state == vlc.State.Ended:
            # Video has ended, restart from beginning
            self.player.stop()
            self.root.after(100, lambda: self.player.play())
        elif self.player.is_playing():
            self.player.pause()
        else:
            self.player.play()
    
    def toggle_repeat(self):
        """Toggle repeat mode on/off"""
        self.is_repeat = not self.is_repeat
        self.repeat_button.config(text=f"Repeat: {'On' if self.is_repeat else 'Off'}")
    
    def toggle_auto_play(self):
        """Toggle auto play mode on/off"""
        self.is_auto_play = not self.is_auto_play
        self.auto_play_button.config(text=f"Auto: {'On' if self.is_auto_play else 'Off'}")
    
    def toggle_random(self):
        """Toggle random mode on/off"""
        self.is_random = not self.is_random
        self.random_button.config(text=f"Random: {'On' if self.is_random else 'Off'}")
    
    def random_video(self):
        """Jump to a random video"""
        if not self.video_files or len(self.video_files) <= 1:
            return
        
        import random
        
        # Get a random index that's different from current
        available_indices = [i for i in range(len(self.video_files)) if i != self.current_index]
        if available_indices:
            self.current_index = random.choice(available_indices)
            self.play_current_video()
    
    def toggle_mute(self):
        self.is_muted = not self.is_muted
        self.player.audio_set_mute(self.is_muted)
        self.mute_button.config(text="Unmute" if self.is_muted else "Mute")
    
    def set_volume(self, value):
        volume = int(value)
        self.player.audio_set_volume(volume)
        self.previous_volume = volume
    
    def next_video(self):
        if not self.video_files:
            return
        
        if self.is_random:
            self.random_video()
        else:
            self.current_index = (self.current_index + 1) % len(self.video_files)
            self.play_current_video()
    
    def prev_video(self):
        if not self.video_files:
            return
        
        if self.is_random:
            self.random_video()
        else:
            self.current_index = (self.current_index - 1) % len(self.video_files)
            self.play_current_video()
    
    def delete_video(self):
        if not self.video_files or self.current_index < 0 or self.current_index >= len(self.video_files):
            return
        
        # Get the current video file
        video_path = self.video_files[self.current_index]
        
        # Stop playback
        self.player.stop()
        
        try:
            # Delete the file
            os.remove(video_path)
            self.status_label.config(text=f"Deleted {os.path.basename(video_path)}")
            
            # Remove from our list
            del self.video_files[self.current_index]
            
            # Move to next video or update UI
            if self.video_files:
                if self.current_index >= len(self.video_files):
                    self.current_index = len(self.video_files) - 1
                self.play_current_video()
            else:
                self.status_label.config(text="No videos left")
                self.root.title("Video File Sorter")
        except Exception as e:
            self.status_label.config(text=f"Error: {str(e)}")
    
    def on_close(self):
        # Cancel any timers
        if self.update_timer_id:
            self.root.after_cancel(self.update_timer_id)
            
        # Clean up resources
        self.player.stop()
        self.root.destroy()

# Main function to start the application
def main():
    root = tk.Tk()
    app = VideoSorter(root)
    root.mainloop()

if __name__ == "__main__":
    main()
