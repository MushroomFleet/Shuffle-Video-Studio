# Video File Renaming Utility

This utility helps rename video files from a pattern of `[prefix]_00000.mp4` to `clip_0000.mp4`. It consists of two scripts that work together to make the renaming process simple and user-friendly.

## Features

- Converts 5-digit numbering (00000) to 4-digit numbering (0000)
- Changes any prefix word to "clip"
- Preserves the .mp4 extension
- Interactive command prompt interface
- Error checking for Python installation
- File operation status reporting

## Requirements

- Python 3.x installed and available in system PATH
- Windows operating system (for the batch file)

## Files Included

1. `rename_files.py` - The Python script that performs the actual file renaming
2. `rename_files.bat` - A Windows batch file that provides a user-friendly interface

## Installation

1. Download both `rename_files.py` and `rename_files.bat`
2. Place both files in the same directory as your video files
3. No additional installation is required

## Usage

### Method 1: Using the Batch File (Recommended)

1. Double-click `rename_files.bat`
2. When prompted, enter the prefix word of your current files (e.g., "donut" for files named like "donut_00001.mp4")
3. Press any key to confirm and start the renaming process
4. Wait for the process to complete

### Method 2: Using Python Directly

```bash
python rename_files.py [prefix_word]
```

For example:
```bash
python rename_files.py donut
```

## Examples

### Before:
```
donut_00001.mp4
donut_00002.mp4
donut_00003.mp4
```

### After:
```
clip_0001.mp4
clip_0002.mp4
clip_0003.mp4
```

## Error Handling

The scripts include error handling for:
- Missing Python installation
- Invalid or missing prefix word
- File access/permission issues
- No matching files found

## Limitations

- Only works with .mp4 files
- Expects exactly 5 digits in the source filename
- Files must follow the exact pattern: `[prefix]_00000.mp4`
- Cannot process files in subfolders

## Caution

- Always backup your files before running any renaming operations
- Test with a small number of files first
- Make sure your files follow the expected naming pattern exactly

## Troubleshooting

1. **"Python is not installed or not in PATH!"**
   - Install Python from python.org
   - Make sure to check "Add Python to PATH" during installation

2. **"No files found starting with '[prefix]'"**
   - Verify that you entered the correct prefix
   - Check that your files follow the exact pattern: `[prefix]_00000.mp4`

3. **Permission errors**
   - Run the batch file as administrator
   - Check file and folder permissions

## Support

If you encounter any issues or need modifications, please:
1. Verify your file naming pattern matches the expected format
2. Check that Python is properly installed
3. Ensure you have write permissions in the folder

