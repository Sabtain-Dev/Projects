#!/usr/bin/env python3
# linux_file_explorer.py
# Linux-only interactive CLI File Explorer (safe, path-based)

import os
import shutil
import subprocess
import sys
import zipfile
from datetime import datetime
from pathlib import Path
import stat

APP_NAME = "Linux File Explorer (CLI)"

def human_size(n):
    # simple human readable size
    for unit in ['B','KB','MB','GB','TB']:
        if abs(n) < 1024.0:
            return f"{n:.1f}{unit}"
        n /= 1024.0
    return f"{n:.1f}PB"

def format_mode(mode):
    return stat.filemode(mode)

def safe_input(prompt="> "):
    try:
        return input(prompt)
    except (EOFError, KeyboardInterrupt):
        print()
        return ""

def list_dir(path: Path, show_all=False):
    try:
        if not path.exists():
            print(f"Path does not exist: {path}")
            return
        entries = sorted(path.iterdir(), key=lambda p: p.name.lower())
        for p in entries:
            if not show_all and p.name.startswith('.'):
                continue
            st = p.stat()
            m = format_mode(st.st_mode)
            size = human_size(st.st_size) if p.is_file() else "-"
            mtime = datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
            print(f"{m}  {size:>8}  {mtime}  {p.name}")
    except PermissionError:
        print("Permission denied.")
    except Exception as e:
        print(f"Error listing directory: {e}")

def show_stat(path: Path):
    try:
        st = path.stat()
        print(f"Path: {path}")
        print(f"Type: {'directory' if path.is_dir() else 'file' if path.is_file() else 'other'}")
        print(f"Size: {st.st_size} bytes ({human_size(st.st_size)})")
        print(f"Permissions: {format_mode(st.st_mode)} (octal: {oct(st.st_mode & 0o777)})")
        print(f"Owner UID:GID: {st.st_uid}:{st.st_gid}")
        print(f"Last modified: {datetime.fromtimestamp(st.st_mtime)}")
        print(f"Last accessed: {datetime.fromtimestamp(st.st_atime)}")
        print(f"Created (ctime): {datetime.fromtimestamp(st.st_ctime)}")
    except FileNotFoundError:
        print("Path not found.")
    except PermissionError:
        print("Permission denied.")
    except Exception as e:
        print(f"Error reading file properties: {e}")

def make_dir(path: Path, parents=False, mode=0o775):
    try:
        path.mkdir(parents=parents, mode=mode, exist_ok=False)
        print(f"Directory created: {path}")
    except FileExistsError:
        print("Directory already exists.")
    except PermissionError:
        print("Permission denied.")
    except Exception as e:
        print(f"Error creating directory: {e}")

def create_file(path: Path):
    try:
        if path.exists():
            print("File already exists.")
            return
        path.parent.mkdir(parents=True, exist_ok=True)
        path.touch()
        print(f"File created: {path}")
    except PermissionError:
        print("Permission denied.")
    except Exception as e:
        print(f"Error creating file: {e}")

def remove_file(path: Path, force=False):
    try:
        if not path.exists():
            print("Path not found.")
            return
        if path.is_dir():
            print("Path is a directory; use rmdir to remove directories.")
            return
        if not force:
            ans = safe_input(f"Delete file {path}? (y/N): ").lower()
            if ans != 'y':
                print("Aborted.")
                return
        path.unlink()
        print(f"File deleted: {path}")
    except PermissionError:
        print("Permission denied.")
    except Exception as e:
        print(f"Error deleting file: {e}")

def remove_dir(path: Path, recursive=False):
    try:
        if not path.exists():
            print("Path not found.")
            return
        if not path.is_dir():
            print("Path is not a directory.")
            return
        if recursive:
            ans = safe_input(f"Recursively delete directory {path}? This is irreversible (y/N): ").lower()
            if ans != 'y':
                print("Aborted.")
                return
            shutil.rmtree(path)
            print(f"Directory recursively deleted: {path}")
        else:
            path.rmdir()
            print(f"Directory deleted: {path}")
    except OSError as e:
        print(f"Error removing directory: {e}")
    except PermissionError:
        print("Permission denied.")

def copy_item(src: Path, dst: Path):
    try:
        if not src.exists():
            print("Source not found.")
            return
        dst_parent = dst if dst.is_dir() else dst.parent
        dst_parent.mkdir(parents=True, exist_ok=True)
        if src.is_dir():
            # copytree requires dst not existing — create inside dst
            target = dst / src.name if dst.is_dir() else dst
            if target.exists():
                print(f"Destination exists: {target}")
                return
            shutil.copytree(src, target)
            print(f"Directory copied: {src} -> {target}")
        else:
            target = dst / src.name if dst.is_dir() else dst
            shutil.copy2(src, target)
            print(f"File copied: {src} -> {target}")
    except PermissionError:
        print("Permission denied.")
    except Exception as e:
        print(f"Error copying: {e}")

def move_item(src: Path, dst: Path):
    try:
        if not src.exists():
            print("Source not found.")
            return
        dst_parent = dst if dst.is_dir() else dst.parent
        dst_parent.mkdir(parents=True, exist_ok=True)
        target = dst / src.name if dst.is_dir() else dst
        shutil.move(str(src), str(target))
        print(f"Moved: {src} -> {target}")
    except PermissionError:
        print("Permission denied.")
    except Exception as e:
        print(f"Error moving: {e}")

def parse_mode(mode_str: str):
    """
    Accepts:
      - octal digits like 755 or 0755
      - rwxr-xr-x style (9 chars)
    Returns integer mode (e.g., 0o755).
    """
    mode_str = mode_str.strip()
    if mode_str.isdigit():
        # octal digits
        try:
            return int(mode_str, 8)
        except ValueError:
            raise ValueError("Invalid octal mode.")
    if len(mode_str) == 9 and all(c in 'rwx-' for c in mode_str):
        mapping = {'r':4,'w':2,'x':1,'-':0}
        val = 0
        for i in range(3):  # user, group, other
            trip = mode_str[i*3:(i+1)*3]
            v = mapping[trip[0]] + mapping[trip[1]] + mapping[trip[2]]
            val = (val << 3) | v
        return val
    raise ValueError("Mode must be octal digits like 775 or rwxr-xr-x format.")

def change_permissions(path: Path, mode_str: str):
    try:
        mode = parse_mode(mode_str)
        os.chmod(path, mode)
        print(f"Permissions of {path} set to {oct(mode)} / {format_mode(path.stat().st_mode)}")
    except FileNotFoundError:
        print("Path not found.")
    except PermissionError:
        print("Permission denied.")
    except ValueError as e:
        print(f"Invalid mode: {e}")
    except Exception as e:
        print(f"Error changing permissions: {e}")

def compress_files(file_paths, archive_name):
    """
    Creates a zip archive. file_paths is list of Path objects.
    """
    try:
        if not archive_name.endswith('.zip'):
            archive_name += '.zip'
        with zipfile.ZipFile(archive_name, 'w', zipfile.ZIP_DEFLATED) as zf:
            for p in file_paths:
                if not p.exists():
                    print(f"Skipping (not found): {p}")
                    continue
                if p.is_file():
                    zf.write(p, arcname=p.name)
                else:
                    # write directory recursively
                    for f in p.rglob('*'):
                        zf.write(f, arcname=str(f.relative_to(p.parent)))
        print(f"Created archive: {archive_name}")
    except Exception as e:
        print(f"Error compressing: {e}")

def extract_archive(archive_path: Path, destination: Path):
    try:
        if not archive_path.exists():
            print("Archive not found.")
            return
        shutil.unpack_archive(str(archive_path), str(destination))
        print(f"Extracted {archive_path} -> {destination}")
    except shutil.ReadError:
        print("Unsupported archive format or corrupted archive.")
    except Exception as e:
        print(f"Error extracting archive: {e}")

def open_with_default(path: Path):
    try:
        if not path.exists():
            print("Path not found.")
            return
        cmd = shutil.which("xdg-open")
        if cmd is None:
            print("xdg-open not available on this system.")
            return
        subprocess.Popen([cmd, str(path)])
        print(f"Opened: {path}")
    except Exception as e:
        print(f"Error opening file: {e}")

def open_chrome():
    possible = ["google-chrome", "chrome", "chromium", "chromium-browser"]
    for name in possible:
        exe = shutil.which(name)
        if exe:
            try:
                subprocess.Popen([exe])
                print(f"Launched {name}.")
                return
            except Exception as e:
                print(f"Error launching {name}: {e}")
                return
    print("No known Chrome/Chromium binary found in PATH.")

def safe_search(start: Path, name: str, max_depth=5):
    """
    Search for files/directories named `name` starting at `start`.
    max_depth prevents runaway searches; default 5 levels.
    """
    results = []
    try:
        start = start.resolve()
    except Exception:
        pass
    # breadth-first with depth
    from collections import deque
    q = deque([(start, 0)])
    while q:
        cur, depth = q.popleft()
        if depth > max_depth:
            continue
        try:
            for child in cur.iterdir():
                if child.name == name:
                    results.append(child)
                if child.is_dir() and depth < max_depth:
                    q.append((child, depth + 1))
        except PermissionError:
            continue
        except FileNotFoundError:
            continue
    return results

def batch_copy(files, destination):
    for f in files:
        copy_item(Path(f), Path(destination))

def batch_move(files, destination):
    for f in files:
        move_item(Path(f), Path(destination))

def batch_delete(files):
    for f in files:
        p = Path(f)
        if p.is_dir():
            remove_dir(p, recursive=True)
        else:
            remove_file(p, force=True)

def prompt_help():
    print("""
Commands (examples):
  ls [path]               - list directory (ls or ls /home/user)
  pwd                     - print current working directory
  cd <path>               - change working directory
  stat <path>             - show file/directory properties
  mkdir <path>            - create directory
  touch <path>            - create empty file
  rm <path>               - delete file (asks confirmation)
  rmdir <path> [--rm]     - delete dir, use --rm for recursive
  cp <src> <dst>          - copy file or directory to destination
  mv <src> <dst>          - move/rename
  search <root> <name>    - search name under root (limited depth)
  chmod <mode> <path>     - change permissions (775 or rwxr-xr-x)
  compress <archive> <paths...> - create zip archive
  extract <archive> <dest> - extract archive
  open <path>             - open with default GUI app (xdg-open)
  open-chrome             - open Chrome/Chromium
  batch copy|move|delete  - then follow prompts for space-separated paths
  help                    - show this help
  exit | quit             - exit the program
""")

def main():
    cwd = Path.cwd()
    print(f"{APP_NAME}\nType 'help' for commands.\n")
    while True:
        try:
            cmdline = safe_input(f"{cwd}> ").strip()
            if not cmdline:
                continue
            parts = cmdline.split()
            cmd = parts[0].lower()
            args = parts[1:]

            if cmd in ('exit','quit'):
                print("Goodbye.")
                break
            elif cmd == 'help':
                prompt_help()
            elif cmd == 'pwd':
                print(cwd)
            elif cmd == 'ls':
                p = Path(args[0]) if args else cwd
                list_dir(p)
            elif cmd == 'ls-all':
                p = Path(args[0]) if args else cwd
                list_dir(p, show_all=True)
            elif cmd == 'cd':
                if not args:
                    print("Usage: cd <path>")
                    continue
                target = Path(args[0]).expanduser()
                if not target.exists():
                    print("Path does not exist.")
                    continue
                if not target.is_dir():
                    print("Path is not a directory.")
                    continue
                cwd = target.resolve()
            elif cmd == 'stat':
                if not args:
                    print("Usage: stat <path>")
                    continue
                show_stat(Path(args[0]))
            elif cmd == 'mkdir':
                if not args:
                    print("Usage: mkdir <path>")
                    continue
                make_dir(Path(args[0]), parents=True)
            elif cmd == 'touch':
                if not args:
                    print("Usage: touch <path>")
                    continue
                create_file(Path(args[0]))
            elif cmd == 'rm':
                if not args:
                    print("Usage: rm <path>")
                    continue
                remove_file(Path(args[0]))
            elif cmd == 'rmdir':
                if not args:
                    print("Usage: rmdir <path> [--rm]")
                    continue
                recursive = '--rm' in args
                path_str = args[0]
                remove_dir(Path(path_str), recursive=recursive)
            elif cmd == 'cp':
                if len(args) < 2:
                    print("Usage: cp <src> <dst>")
                    continue
                copy_item(Path(args[0]), Path(args[1]))
            elif cmd == 'mv':
                if len(args) < 2:
                    print("Usage: mv <src> <dst>")
                    continue
                move_item(Path(args[0]), Path(args[1]))
            elif cmd == 'search':
                if len(args) < 2:
                    print("Usage: search <root> <name>")
                    continue
                root = Path(args[0])
                name = args[1]
                depth = int(args[2]) if len(args) > 2 and args[2].isdigit() else 5
                results = safe_search(root, name, max_depth=depth)
                if results:
                    print("Found:")
                    for r in results:
                        print(r)
                else:
                    print("No results.")
            elif cmd == 'chmod':
                if len(args) < 2:
                    print("Usage: chmod <mode> <path>")
                    continue
                change_permissions(Path(args[1]), args[0])
            elif cmd == 'compress':
                if len(args) < 2:
                    print("Usage: compress <archive_name.zip> <paths...>")
                    continue
                archive = args[0]
                files = [Path(p) for p in args[1:]]
                compress_files(files, archive if archive.endswith('.zip') else archive)
            elif cmd == 'extract':
                if len(args) < 2:
                    print("Usage: extract <archive.zip> <destination>")
                    continue
                extract_archive(Path(args[0]), Path(args[1]))
            elif cmd == 'open':
                if not args:
                    print("Usage: open <path>")
                    continue
                open_with_default(Path(args[0]))
            elif cmd == 'open-chrome':
                open_chrome()
            elif cmd == 'batch':
                if not args:
                    print("Usage: batch copy|move|delete")
                    continue
                sub = args[0]
                if sub == 'copy':
                    srcs = safe_input("Enter space-separated source paths: ").split()
                    dst = safe_input("Enter destination directory: ").strip()
                    batch_copy(srcs, dst)
                elif sub == 'move':
                    srcs = safe_input("Enter space-separated source paths: ").split()
                    dst = safe_input("Enter destination directory: ").strip()
                    batch_move(srcs, dst)
                elif sub == 'delete':
                    srcs = safe_input("Enter space-separated paths to delete: ").split()
                    ans = safe_input("Are you sure? This will delete all provided paths (y/N): ").lower()
                    if ans == 'y':
                        batch_delete(srcs)
                    else:
                        print("Aborted.")
                else:
                    print("Unknown batch command. Use copy|move|delete.")
            else:
                print("Unknown command. Type 'help' for a list of commands.")
        except KeyboardInterrupt:
            print("\n(To exit, type 'exit' or 'quit')")
        except Exception as e:
            print(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()
