# Cursor-Restore - Cursor History Rescue Mission

## 😱 The Problem: When Cursor Goes Rogue

Picture this: You're happily coding away, making beautiful progress on your project, when suddenly... **POOF!** 💥 

Cursor decides to have a digital tantrum and **deletes your entire directory**. All your precious code, documentation, and that brilliant algorithm you spent 3 hours perfecting at 2 AM? Gone. Vanished. Disappeared into the digital void like your motivation after a failed deployment on Friday afternoon.

You stare at your empty folder in disbelief. Your heart sinks faster than a poorly written sorting algorithm. The five stages of grief hit you like a stack overflow:

1. **Denial**: "This can't be happening. It's just a display bug, right? RIGHT?!"
2. **Anger**: *Aggressively smashes Ctrl+Z hoping for a miracle*
3. **Bargaining**: "I promise I'll commit more frequently if you just bring my files back!"
4. **Depression**: *Contemplates switching careers to farming*
5. **Acceptance**: "Well, I guess I'll just rewrite everything from memory... 😭"

## 🦸‍♂️ The Hero: Cursor Restore Script

But wait! Before you update your LinkedIn to "Former Developer, Current Digital Archaeologist," there's HOPE! 

Turns out, Cursor has been secretly hoarding your files like a digital packrat in its hidden backup lair (`%APPDATA%\Cursor\User\History`). It's been making sneaky copies of everything you've touched, storing them with cryptic names like a spy agency's filing system.

Our hero script swoops in to:
- 🕵️ **Decode the Mystery**: Translates Cursor's URL-encoded hieroglyphics back to normal paths
- 🔍 **Hunt Down Your Files**: Searches through hundreds of backup folders faster than you can say "git blame"
- ⏰ **Time Travel**: Finds the latest version of each file (because who wants yesterday's bugs?)
- 🏗️ **Rebuild Your Empire**: Reconstructs your entire directory structure like nothing ever happened

It's like having a time machine, but for code instead of preventing you from buying cryptocurrency in 2010.

## 🎯 The Solution: Digital Phoenix Rising

### Basic Usage

```bash
# Restore files from the last 7 days (default)
python cursor_restore.py --restore-path "C:/Users/YourName/Projects/MyProject/"

# Restore to a specific folder
python cursor_restore.py --restore-path "C:/Users/YourName/Projects/MyProject/" --output-dir "my_restored_files"

# Use custom time range
python cursor_restore.py --restore-path "C:/Users/YourName/Projects/MyProject/" --start-time "2024-01-01 00:00:00" --end-time "2024-12-31 23:59:59"

# Search back 30 days instead of 7
python cursor_restore.py --restore-path "C:/Users/YourName/Projects/MyProject/" --days-back 30

# Use custom Cursor history directory (if not using default)
python cursor_restore.py --history-dir "C:/path/to/cursor/history" --restore-path "C:/Users/YourName/Projects/MyProject/"

# Restore all files from the past year
python cursor_restore.py --restore-path "C:/Users/YourName/Projects/MyProject/" --days-back 365 --output-dir "recovered_project"
```

### Parameters

- `--history-dir, -d`: Directory containing Cursor history (default: %APPDATA%\Cursor\User\History)
- `--restore-path, -r`: **Required** - Original directory path to restore
- `--output-dir, -o`: Output directory for restored files (default: restoredFolder)  
- `--start-time, -s`: Start timestamp in format "YYYY-MM-DD HH:MM:SS"
- `--end-time, -e`: End timestamp in format "YYYY-MM-DD HH:MM:SS"
- `--days-back, -b`: Number of days back to search (default: 7, ignored if --start-time provided)

### How It Works

1. Scans all folders in the Cursor history directory
2. Reads each `entries.json` file to find files from your target directory
3. Filters by timestamp range
4. For each file, finds the latest version within the time range
5. Restores files to the output directory maintaining the original folder structure

### Path Handling

The script robustly handles various path formats and differences:

- **URL Encoding**: Automatically decodes URL-encoded paths (e.g., `file:///c%3A/Users/` → `C:/Users/`)
- **Path Separators**: Works with both forward slashes (`/`) and backslashes (`\`)
- **Case Sensitivity**: Handles Windows case-insensitive path matching
- **Protocol Prefixes**: Strips `file://` prefixes from resource URLs
- **Trailing Slashes**: Normalizes paths with or without trailing slashes

This means you can specify your restore path in any of these formats:
- `C:/Users/YourName/Projects/MyProject/`
- `C:\Users\YourName\Projects\MyProject`
- `c:/users/yourname/projects/myproject`

### Example Output

```
Cursor History Restore Script
==================================================
History directory: C:\Users\YourName\AppData\Roaming\Cursor\User\History
Restore path: C:/Users/YourName/Projects/MyProject/
Output directory: restoredFolder
Time range: 2024-07-31 22:42:22 to 2025-07-31 22:42:22

Scanning history directory: C:\Users\YourName\AppData\Roaming\Cursor\User\History
Looking for files from: C:/Users/YourName/Projects/MyProject/
Time range: 2024-07-31 22:42:22 to 2025-07-31 22:42:22
Found: src/main.py (from 2024-07-31 20:57:26.596000)
Found: src/utils.py (from 2024-07-30 01:46:41.681000)
Found: docs/readme.md (from 2024-07-31 01:10:04.441000)
Found: config/settings.json (from 2024-07-31 20:57:25.985000)
Found: tests/test_main.py (from 2024-07-31 20:57:26.489000)
...
Found: requirements.txt (from 2024-07-31 20:18:13.957000)

Processed 451 folders, found 25 matching files

Restoring files to: restoredFolder
Restored: src/main.py
Restored: src/utils.py
Restored: docs/readme.md
...
Restored: requirements.txt

Successfully restored 25 files

Restore complete!
```

---

## 🎉 Happy Ending

Your files are back! Your code lives again! And now you have a new superpower: the ability to rescue your work from the digital abyss whenever Cursor decides to throw another tantrum.

*May your commits be frequent and your backups be automatic.* 🙏

**P.S.** - This script is like insurance for your sanity. You hope you'll never need it, but when you do, you'll be eternally grateful it exists.
