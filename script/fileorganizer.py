import os
import shutil

# Use current directory as the source folder
source_folder = os.getcwd()

# Map existing file extensions to broader categories
category_map = {
    "Software": ["exe", "msi", "apk", "bat", "ppk", "py", "php", "mq5", "cab"],
    "Zip": ["zip", "7z", "rar", "tar", "gz", "iso", "crdownload", "parts"],
    "Media": ["mp3", "wav", "mp4", "mkv", "avi", "jpeg", "jpg", "png", "svg"],
    "Documents": ["pdf", "docx", "txt", "xlsx", "xls", "pptx", "odt", "ods", "htm", "html", "ini", "log", "epub", "csv"],
    "Others": []  # Anything else
}

# Safely move files without overwriting
def safe_move(file_path, dest_folder):
    filename = os.path.basename(file_path)
    dest_path = os.path.join(dest_folder, filename)
    counter = 1
    while os.path.exists(dest_path):
        name, ext = os.path.splitext(filename)
        dest_path = os.path.join(dest_folder, f"{name}({counter}){ext}")
        counter += 1
    shutil.move(file_path, dest_path)

# Loop through all items in the current directory
for item in os.listdir(source_folder):
    item_path = os.path.join(source_folder, item)
    
    # Only organize files, skip directories
    if os.path.isfile(item_path):
        ext = os.path.splitext(item)[1][1:].lower()  # Get extension without dot
        category_found = False
        
        # Find matching category
        for category, extensions in category_map.items():
            if ext in extensions:
                dest_category = os.path.join(source_folder, category)
                category_found = True
                break
        
        # Default category if not found
        if not category_found:
            dest_category = os.path.join(source_folder, "Others")
        
        # Create category folder if missing
        if not os.path.exists(dest_category):
            os.makedirs(dest_category)
        
        # Move the file
        safe_move(item_path, dest_category)

print("Current folder has been reorganized into Software, Zip, Media, Documents, Others!")