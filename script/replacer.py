//read files and rename them


import os

# --- CONFIGURATION ---
directory = os.getcwd()  # current directory
old_word = "OLDWORD"     # word to replace
new_word = "NEWWORD"     # replacement word

# --- PROCESS FILES ---
for filename in os.listdir(directory):
    filepath = os.path.join(directory, filename)
    
    # Only process files (ignore directories)
    if os.path.isfile(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if old_word in content:
                new_content = content.replace(old_word, new_word)
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                print(f"[Updated] {filename}")
        except UnicodeDecodeError:
            # Skip binary files
            print(f"[Skipped binary] {filename}")
        except Exception as e:
            print(f"[Error] {filename}: {e}")