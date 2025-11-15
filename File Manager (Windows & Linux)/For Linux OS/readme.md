# Linux File Explorer (CLI)

A **Linux-only interactive Command-Line File Explorer** built with Python.  
It provides common file system operations like listing, creating, deleting, copying, moving files/directories, searching, changing permissions, compressing/extracting files, and opening files with default applications — all in a safe, path-based interactive shell.

---

## Features

- Navigate directories: `ls`, `pwd`, `cd`
- Create and remove files/directories: `touch`, `mkdir`, `rm`, `rmdir`
- Copy and move files/directories: `cp`, `mv`
- File properties: `stat`
- Change permissions: `chmod` (octal or rwxr-xr-x style)
- Compress and extract files: `compress`, `extract` (ZIP archives)
- Open files with default GUI applications: `open`
- Open Chrome/Chromium: `open-chrome`
- Safe search with depth limit: `search`
- Batch operations: `batch copy|move|delete`
- Built entirely with Python standard library

---

## Requirements

- Linux OS
- Python 3.8 or higher

---

## Installation

1. Clone or download this repository.
2. Make the script executable (optional):
   ```bash
   chmod +x linux_file_explorer.py

### 3. Run the script:
- python3 linux_file_explorer.py

### 4. Usage
- Type commands interactively. Example:
1. /home/user> ls
2. /home/user> cd Documents
3. /home/user/Documents> mkdir TestDir
4. /home/user/Documents> touch file.txt
5. /home/user/Documents> cp file.txt ../Backup/
6. /home/user/Documents> chmod 775 file.txt
7. /home/user/Documents> compress archive.zip file.txt TestDir
8. /home/user/Documents> extract archive.zip ./Extracted
9. /home/user/Documents> open file.txt
10. /home/user/Documents> search /home user_manual.pdf
Type help to see all available commands.

### 5. Notes
 - rmdir --rm will recursively delete directories after confirmation.
 - chmod accepts either octal (e.g., 775) or 9-character permission string (e.g., rwxr-xr-x).
 - search has a default maximum depth of 5 to prevent excessive recursion.
 - The project is Linux-only. Some commands (open, open-chrome) rely on xdg-open and Chrome/Chromium being installed.

### 7. License
- This project is open-source and free to use.

---

