import os
import re
import shutil
import argparse
import sys

def count_part_id_elements(file_path):
    """Count the number of <score-part> elements in a file."""
    sys.stdout.write(f"Analyzing file: {file_path}\n")
    sys.stdout.flush()
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            # Find all occurrences of <score-part id="..."> in the file
            matches = re.findall(r'<score-part id="[^"]+">', content)
            sys.stdout.write(f"  Found {len(matches)} <score-part> elements\n")
            sys.stdout.flush()
            return len(matches)
    except Exception as e:
        sys.stdout.write(f"Error processing {file_path}: {e}\n")
        sys.stdout.flush()
        return 0

def categorize_files(source_dir='.', copy_mode=True):
    """Categorize files based on the number of <score-part> elements."""
    # Convert to absolute path
    source_dir = os.path.abspath(source_dir)
    sys.stdout.write(f"Processing files in: {source_dir}\n")
    sys.stdout.flush()
    
    # Get all XML files in the source directory
    files = []
    for file in os.listdir(source_dir):
        if file.endswith('.xml') and os.path.isfile(os.path.join(source_dir, file)):
            files.append(file)
            sys.stdout.write(f"Found XML file: {file}\n")
            sys.stdout.flush()
    
    if not files:
        sys.stdout.write("No XML files found in the directory!\n")
        sys.stdout.flush()
        return
    
    # Create destination directories
    dest_dirs = {
        "single": os.path.join(source_dir, "1_single_part"),
        "double": os.path.join(source_dir, "2_double_parts"),
        "multiple": os.path.join(source_dir, "3_multiple_parts")
    }
    
    for dir_name, dir_path in dest_dirs.items():
        os.makedirs(dir_path, exist_ok=True)
        sys.stdout.write(f"Created directory: {dir_path}\n")
        sys.stdout.flush()
    
    # Count stats
    stats = {"single": 0, "double": 0, "multiple": 0, "skipped": 0}
    
    # Process each file
    sys.stdout.write(f"Processing {len(files)} XML files...\n")
    sys.stdout.flush()
    
    for file in files:
        file_path = os.path.join(source_dir, file)
        count = count_part_id_elements(file_path)
        
        # Determine destination directory
        if count == 1:
            dest_dir = dest_dirs["single"]
            category = "single"
        elif count == 2:
            dest_dir = dest_dirs["double"]
            category = "double"
        elif count >= 3:
            dest_dir = dest_dirs["multiple"]
            category = "multiple"
        else:
            # Skip files with no <score-part> elements
            sys.stdout.write(f"Skipping '{file}': No <score-part> elements found\n")
            sys.stdout.flush()
            stats["skipped"] += 1
            continue
        
        # Create destination path
        dest_path = os.path.join(dest_dir, file)
        
        # Move or copy the file
        try:
            if copy_mode:
                shutil.copy2(file_path, dest_path)
                action = "Copied"
            else:
                shutil.move(file_path, dest_path)
                action = "Moved"
            sys.stdout.write(f"{action} '{file}' to '{os.path.basename(dest_dir)}' (part count: {count})\n")
            sys.stdout.flush()
            stats[category] += 1
        except Exception as e:
            sys.stdout.write(f"Error processing {file}: {e}\n")
            sys.stdout.flush()
    
    # Print summary
    sys.stdout.write("\nSummary:\n")
    sys.stdout.write(f"- Files with 1 part: {stats['single']}\n")
    sys.stdout.write(f"- Files with 2 parts: {stats['double']}\n")
    sys.stdout.write(f"- Files with 3+ parts: {stats['multiple']}\n")
    sys.stdout.write(f"- Files with no parts: {stats['skipped']}\n")
    sys.stdout.write(f"Total files processed: {sum(stats.values())}\n")
    sys.stdout.flush()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Categorize MusicXML files based on the number of <score-part> elements.")
    parser.add_argument("-d", "--directory", default=".", 
                        help="Source directory to process (default: current directory)")
    parser.add_argument("-m", "--move", action="store_true", 
                        help="Move files instead of copying them")
    
    args = parser.parse_args()
    
    sys.stdout.write("Categorizing MusicXML files based on <score-part> elements...\n")
    sys.stdout.flush()
    categorize_files(args.directory, not args.move)
    sys.stdout.write("Categorization complete!\n")
    sys.stdout.flush() 