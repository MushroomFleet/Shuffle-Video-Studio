import os
import re
import sys

def rename_files(directory=".", prefix_word=None):
    if not prefix_word:
        print("Error: No prefix word provided")
        return
        
    # Get all files in the directory
    files = os.listdir(directory)
    
    # Regular expression pattern to match files like "<prefix>_00001.mp4"
    pattern = re.compile(f'{prefix_word}_(\d{{5}})\.mp4')
    
    files_renamed = 0
    for filename in files:
        match = pattern.match(filename)
        if match:
            # Extract the number and remove leading zero
            number = match.group(1)
            new_number = str(int(number))  # Remove leading zeros
            new_number = new_number.zfill(4)  # Pad with zeros to make it 4 digits
            
            # Create new filename
            new_filename = f"clip_{new_number}.mp4"
            
            # Full paths for old and new files
            old_file = os.path.join(directory, filename)
            new_file = os.path.join(directory, new_filename)
            
            # Rename the file
            try:
                os.rename(old_file, new_file)
                print(f"Renamed: {filename} → {new_filename}")
                files_renamed += 1
            except Exception as e:
                print(f"Error renaming {filename}: {e}")
    
    if files_renamed == 0:
        print(f"\nNo files found starting with '{prefix_word}_'")
    else:
        print(f"\nRenamed {files_renamed} files successfully")

if __name__ == "__main__":
    # Get prefix word from command line argument if provided
    prefix_word = sys.argv[1] if len(sys.argv) > 1 else None
    rename_files(".", prefix_word)
