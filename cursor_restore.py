#!/usr/bin/env python3
"""
Cursor History Restore Script

This script restores files from Cursor's backup history by finding the latest
versions of files within a specified directory and time range.
"""

import os
import json
import argparse
import shutil
import time
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import unquote
from typing import Dict, List, Tuple, Optional

def parse_timestamp(timestamp_ms: int) -> datetime:
    """Convert millisecond timestamp to datetime object."""
    return datetime.fromtimestamp(timestamp_ms / 1000)

def url_decode_path(url_path: str) -> str:
    """Decode URL-encoded file path."""
    if url_path.startswith('file:///'):
        url_path = url_path[8:]  # Remove 'file:///'
    return unquote(url_path)

def normalize_path(path: str) -> str:
    """Normalize path separators and make it comparable."""
    # Handle URL-encoded paths first
    if path.startswith('file:///'):
        path = url_decode_path(path)
    
    # Normalize separators and resolve path
    normalized = os.path.normpath(path).replace('\\', '/')
    
    # Ensure consistent case on Windows (paths are case-insensitive)
    if os.name == 'nt':
        normalized = normalized.lower()
    
    # Remove trailing slashes for consistency
    if normalized.endswith('/') and len(normalized) > 1:
        normalized = normalized.rstrip('/')
    
    return normalized

def is_path_in_directory(file_path: str, target_dir: str) -> bool:
    """Check if the file path is within the target directory."""
    file_path_norm = normalize_path(file_path)
    target_dir_norm = normalize_path(target_dir)
    
    # Ensure target directory ends with / for proper prefix matching
    if not target_dir_norm.endswith('/'):
        target_dir_norm += '/'
    
    return file_path_norm.startswith(target_dir_norm) or file_path_norm == target_dir_norm.rstrip('/')

def get_relative_path(file_path: str, target_dir: str) -> str:
    """Get the relative path of a file within the target directory."""
    file_path_norm = normalize_path(file_path)
    target_dir_norm = normalize_path(target_dir)
    
    # Ensure target directory ends with / for proper prefix matching
    if not target_dir_norm.endswith('/'):
        target_dir_norm += '/'
    
    if not (file_path_norm.startswith(target_dir_norm) or file_path_norm == target_dir_norm.rstrip('/')):
        raise ValueError(f"File {file_path} is not within directory {target_dir}")
    
    # Remove the target directory prefix
    if file_path_norm == target_dir_norm.rstrip('/'):
        # This is the root directory itself
        return ""
    
    relative = file_path_norm[len(target_dir_norm):]
    return relative

def find_latest_files(history_dir: str, target_restore_dir: str, 
                     start_time: datetime, end_time: datetime) -> Dict[str, Tuple[str, datetime]]:
    """
    Find the latest version of each file within the specified directory and time range.
    
    Returns:
        Dict mapping relative file paths to (backup_file_path, timestamp) tuples
    """
    latest_files = {}
    
    history_path = Path(history_dir)
    if not history_path.exists():
        raise FileNotFoundError(f"History directory not found: {history_dir}")
    
    print(f"Scanning history directory: {history_dir}")
    print(f"Looking for files from: {target_restore_dir}")
    print(f"Time range: {start_time} to {end_time}")
    
    folder_count = 0
    matching_files = 0
    
    # Iterate through all folders in the history directory
    for folder in history_path.iterdir():
        if not folder.is_dir():
            continue
            
        folder_count += 1
        entries_file = folder / "entries.json"
        
        if not entries_file.exists():
            continue
            
        try:
            with open(entries_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            resource_url = data.get('resource', '')
            if not resource_url:
                continue
                
            # Decode the file path
            original_file_path = url_decode_path(resource_url)
            

            # Check if this file is within our target directory
            if not is_path_in_directory(original_file_path, target_restore_dir):
                continue
                
            # Get relative path within the target directory
            try:
                relative_path = get_relative_path(original_file_path, target_restore_dir)
            except ValueError:
                continue
            
            # Find the latest entry within our time range
            latest_entry = None
            latest_timestamp = None
            
            for entry in data.get('entries', []):
                timestamp_ms = entry.get('timestamp')
                if not timestamp_ms:
                    continue
                    
                entry_time = parse_timestamp(timestamp_ms)
                
                # Check if within time range
                if not (start_time <= entry_time <= end_time):
                    continue
                    
                if latest_timestamp is None or entry_time > latest_timestamp:
                    latest_entry = entry
                    latest_timestamp = entry_time
            
            if latest_entry:
                backup_file_path = folder / latest_entry['id']
                if backup_file_path.exists():
                    latest_files[relative_path] = (str(backup_file_path), latest_timestamp)
                    matching_files += 1
                    print(f"Found: {relative_path} (from {latest_timestamp})")
        
        except (json.JSONDecodeError, KeyError, OSError) as e:
            print(f"Warning: Error processing {folder}: {e}")
            continue
    
    print(f"\nProcessed {folder_count} folders, found {matching_files} matching files")
    return latest_files

def restore_files(latest_files: Dict[str, Tuple[str, datetime]], output_dir: str):
    """Restore the files to the output directory."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    print(f"\nRestoring files to: {output_dir}")
    
    restored_count = 0
    
    for relative_path, (backup_file_path, timestamp) in latest_files.items():
        # Create the full output path
        output_file_path = output_path / relative_path
        
        # Create parent directories if needed
        output_file_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            # Copy the file
            shutil.copy2(backup_file_path, output_file_path)
            print(f"Restored: {relative_path}")
            restored_count += 1
        except OSError as e:
            print(f"Error restoring {relative_path}: {e}")
    
    print(f"\nSuccessfully restored {restored_count} files")

def main():
    parser = argparse.ArgumentParser(description='Restore files from Cursor history backups')
    
    # Default to %APPDATA%\Cursor\User\History on Windows
    default_history_dir = os.path.expandvars(r'%APPDATA%\Cursor\User\History')
    
    parser.add_argument('--history-dir', '-d', 
                       default=default_history_dir,
                       help=f'Directory containing Cursor history (default: {default_history_dir})')
    
    parser.add_argument('--restore-path', '-r',
                       required=True,
                       help='Original directory path to restore (e.g., C:/Users/YourName/Projects/MyProject/)')
    
    parser.add_argument('--output-dir', '-o',
                       default='restoredFolder',
                       help='Output directory for restored files (default: restoredFolder)')
    
    parser.add_argument('--start-time', '-s',
                       help='Start timestamp (YYYY-MM-DD HH:MM:SS) - default: 1 week ago')
    
    parser.add_argument('--end-time', '-e',
                       help='End timestamp (YYYY-MM-DD HH:MM:SS) - default: now')
    
    parser.add_argument('--days-back', '-b',
                       type=int, default=7,
                       help='Number of days back to search (default: 7, ignored if --start-time provided)')
    
    args = parser.parse_args()
    
    # Parse timestamps
    if args.end_time:
        end_time = datetime.strptime(args.end_time, '%Y-%m-%d %H:%M:%S')
    else:
        end_time = datetime.now()
    
    if args.start_time:
        start_time = datetime.strptime(args.start_time, '%Y-%m-%d %H:%M:%S')
    else:
        start_time = end_time - timedelta(days=args.days_back)
    
    print("Cursor History Restore Script")
    print("=" * 50)
    print(f"History directory: {args.history_dir}")
    print(f"Restore path: {args.restore_path}")
    print(f"Output directory: {args.output_dir}")
    print(f"Time range: {start_time} to {end_time}")
    print()
    
    try:
        # Find the latest files
        latest_files = find_latest_files(
            args.history_dir, 
            args.restore_path, 
            start_time, 
            end_time
        )
        
        if not latest_files:
            print("No files found matching the criteria.")
            return
        
        # Restore the files
        restore_files(latest_files, args.output_dir)
        
        print("\nRestore complete!")
        
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0

if __name__ == '__main__':
    exit(main())