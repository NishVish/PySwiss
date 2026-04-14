import os
from moviepy import VideoFileClip # New import style for MoviePy 2.0+

def fix_video_for_web(input_path, output_path):
    try:
        print(f"--- Starting Conversion: {input_path} ---")
        
        # Load the video
        with VideoFileClip(input_path) as video:
            # Write using H.264 (libx264)
            # We use 'libx264' because it is the browser standard
            video.write_videofile(
                output_path, 
                codec="libx264", 
                audio_codec="aac"
            )
        
        print(f"--- Success! Web-ready video saved to: {output_path} ---")
        
    except Exception as e:
        print(f"An error occurred: {e}")

# --- PATHS ---
video_input = r'C:/xampp/htdocs/iitm/lara/public/session/default/output.mp4'
video_output = r'C:/xampp/htdocs/iitm/lara/public/session/default/video_fixed.mp4'

if __name__ == "__main__":
    if os.path.exists(video_input):
        fix_video_for_web(video_input, video_output)
    else:
        print(f"Error: Could not find the file at {video_input}")