import os
import re
import shutil
import argparse
import sys
import time

def count_part_id_elements(file_path):
    """Count the number of <score-part> elements in a file."""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            # Find all occurrences of <score-part id="..."> in the file
            matches = re.findall(r'<score-part id="[^"]+">', content)
            return len(matches)
    except Exception as e:
        sys.stdout.write(f"Error processing {file_path}: {e}\n")
        sys.stdout.flush()
        return 0

def categorize_xml_in_folder(folder_path, copy_mode=True, verbose=True):
    """Categorize XML files in a specific folder."""
    folder_path = os.path.abspath(folder_path)
    folder_name = os.path.basename(folder_path)
    
    if verbose:
        sys.stdout.write(f"\nProcessing folder: {folder_path}\n")
        sys.stdout.write("=" * 50 + "\n")
        sys.stdout.flush()
    
    # Get all XML files in the current folder (non-recursive)
    xml_files = []
    for file in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file)
        if file.endswith('.xml') and os.path.isfile(file_path):
            xml_files.append(file)
    
    if not xml_files:
        if verbose:
            sys.stdout.write(f"No XML files found in {folder_name}. Skipping.\n")
            sys.stdout.flush()
        return 0
    
    # Define destination directory paths (but don't create them yet)
    dest_dirs = {
        "single": os.path.join(folder_path, "1_part"),
        "dual_quad": os.path.join(folder_path, "2_4_parts"),
        "mixed": os.path.join(folder_path, "3_5-8_parts"),
        "large": os.path.join(folder_path, "9+_parts")
    }
    
    # First scan to count files per category
    category_counts = {"single": 0, "dual_quad": 0, "mixed": 0, "large": 0, "skipped": 0}
    file_categories = {}  # Store category for each file
    
    if verbose:
        sys.stdout.write(f"Scanning {len(xml_files)} XML files in {folder_name}...\n")
        sys.stdout.flush()
    
    # Show progress for large folders
    total_files = len(xml_files)
    for i, file in enumerate(xml_files):
        if verbose and total_files > 10 and (i % 5 == 0 or i == total_files - 1):
            progress = (i + 1) / total_files * 100
            sys.stdout.write(f"Progress: {progress:.1f}% ({i+1}/{total_files})\r")
            sys.stdout.flush()
            
        file_path = os.path.join(folder_path, file)
        count = count_part_id_elements(file_path)
        
        # Determine category based on new rules
        if count == 1:
            category = "single"
        elif count == 2 or count == 4:
            category = "dual_quad"
        elif count in [3, 5, 6, 7, 8]:
            category = "mixed"
        elif count >= 9:
            category = "large"
        else:
            if verbose:
                sys.stdout.write(f"Skipping '{file}': No <score-part> elements found\n")
                sys.stdout.flush()
            category_counts["skipped"] += 1
            continue
        
        category_counts[category] += 1
        file_categories[file] = category
    
    # Create only needed directories
    created_dirs = set()
    for category, count in category_counts.items():
        if category != "skipped" and count > 0:
            os.makedirs(dest_dirs[category], exist_ok=True)
            created_dirs.add(category)
            if verbose:
                sys.stdout.write(f"Created directory: {os.path.basename(dest_dirs[category])}\n")
                sys.stdout.flush()
    
    # Now process files and move/copy them
    if verbose:
        sys.stdout.write(f"\nMoving files to appropriate folders...\n")
        sys.stdout.flush()
    
    # Process each file
    for file, category in file_categories.items():
        file_path = os.path.join(folder_path, file)
        dest_dir = dest_dirs[category]
        dest_path = os.path.join(dest_dir, file)
        
        # Move or copy the file
        try:
            if copy_mode:
                shutil.copy2(file_path, dest_path)
                action = "Copied"
            else:
                shutil.move(file_path, dest_path)
                action = "Moved"
            if verbose:
                sys.stdout.write(f"{action} '{file}' to '{os.path.basename(dest_dir)}'\n")
                sys.stdout.flush()
        except Exception as e:
            if verbose:
                sys.stdout.write(f"Error processing {file}: {e}\n")
                sys.stdout.flush()
    
    # Print summary for this folder
    if verbose:
        sys.stdout.write(f"\nSummary for {folder_name}:\n")
        sys.stdout.write(f"- Files with 1 part: {category_counts['single']}\n")
        sys.stdout.write(f"- Files with 2 or 4 parts: {category_counts['dual_quad']}\n")
        sys.stdout.write(f"- Files with 3, 5-8 parts: {category_counts['mixed']}\n")
        sys.stdout.write(f"- Files with 9+ parts: {category_counts['large']}\n")
        sys.stdout.write(f"- Files with no parts: {category_counts['skipped']}\n")
        sys.stdout.write(f"Total files processed: {sum(category_counts.values())}\n")
        sys.stdout.flush()
    
    return sum(category_counts.values()) - category_counts["skipped"]

def categorize_files_recursive(source_dir='.', copy_mode=True, recursive=True, max_depth=None, current_depth=0, verbose=True):
    """Categorize files based on the number of <score-part> elements in all subfolders."""
    start_time = time.time()
    
    # Convert to absolute path
    source_dir = os.path.abspath(source_dir)
    if verbose:
        sys.stdout.write(f"Starting to process: {source_dir}\n")
        sys.stdout.write("-" * 60 + "\n")
        sys.stdout.flush()
    
    # Process root directory
    processed_count = categorize_xml_in_folder(source_dir, copy_mode, verbose)
    total_processed = processed_count
    
    # If recursive and we haven't reached max depth, process all subdirectories
    if recursive and (max_depth is None or current_depth < max_depth):
        # Get all subdirectories (non-recursive)
        subdirs_to_process = []
        for item in os.listdir(source_dir):
            item_path = os.path.join(source_dir, item)
            # Skip our categorized folders and hidden folders
            if os.path.isdir(item_path) and not item.startswith(".") and not item in ["1_part", "2_4_parts", "3_5-8_parts", "9+_parts"]:
                subdirs_to_process.append(item_path)
                
        if subdirs_to_process and verbose:
            sys.stdout.write(f"\nFound {len(subdirs_to_process)} subdirectories to process recursively.\n")
            sys.stdout.flush()
            
        # Process each subdirectory recursively    
        for i, subdir in enumerate(subdirs_to_process):
            if verbose:
                sys.stdout.write(f"\n[{i+1}/{len(subdirs_to_process)}] Recursively processing subdirectory: {os.path.basename(subdir)}\n")
                sys.stdout.write("=" * 60 + "\n")
                sys.stdout.flush()
                
            # Recursively process this subdirectory
            subdir_processed = categorize_files_recursive(subdir, copy_mode, recursive, max_depth, current_depth + 1, verbose)
            total_processed += subdir_processed
            
            if verbose:
                sys.stdout.write(f"Completed processing subdirectory: {os.path.basename(subdir)}, processed {subdir_processed} files\n")
                sys.stdout.flush()
        
        if verbose and len(subdirs_to_process) > 0:
            sys.stdout.write("\n" + "=" * 60 + "\n")
            sys.stdout.write(f"Returning to parent directory: {os.path.basename(source_dir)}\n")
            sys.stdout.flush()
            
    elapsed_time = time.time() - start_time
    if verbose and recursive and source_dir == os.path.abspath('.') and current_depth == 0:
        sys.stdout.write(f"\nGrand Total: Processed {total_processed} XML files across all folders.\n")
        sys.stdout.write(f"Total time: {elapsed_time:.2f} seconds\n")
        sys.stdout.flush()
    
    return total_processed

def process_specific_subdirectory(base_dir, subdir_name, copy_mode=True, recursive=True, verbose=True):
    """Process a specific subdirectory under the base directory."""
    # Handle Windows paths correctly
    base_dir = os.path.abspath(base_dir)
    
    # Find the subdirectory
    target_dir = os.path.join(base_dir, subdir_name)
    
    if not os.path.isdir(target_dir):
        sys.stdout.write(f"Error: Subdirectory '{subdir_name}' not found in '{base_dir}'.\n")
        sys.stdout.flush()
        return 0
    
    if verbose:
        sys.stdout.write(f"Processing specific subdirectory: {target_dir}\n")
        sys.stdout.write("=" * 60 + "\n")
        sys.stdout.flush()
    
    # Process the subdirectory
    return categorize_files_recursive(target_dir, copy_mode, recursive, verbose=verbose)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Categorize MusicXML files based on the number of <score-part> elements.")
    parser.add_argument("-d", "--directory", default=".", 
                        help="Source directory to process (default: current directory)")
    parser.add_argument("-m", "--move", action="store_true", 
                        help="Move files instead of copying them")
    parser.add_argument("-nr", "--no-recursive", action="store_true", 
                        help="Do not process subdirectories recursively (default is recursive)")
    parser.add_argument("-s", "--subdirectory", 
                        help="Process only a specific subdirectory under the main directory")
    parser.add_argument("-l1", "--level-one", action="store_true",
                        help="Process only immediate subdirectories (depth=1)")
    parser.add_argument("-q", "--quiet", action="store_true",
                        help="Reduce output verbosity")
    
    args = parser.parse_args()
    
    if not args.quiet:
        sys.stdout.write("Categorizing MusicXML files based on <score-part> elements...\n")
        sys.stdout.flush()
    
    # Handle Windows paths correctly
    directory = os.path.abspath(args.directory)
    
    if args.subdirectory:
        # Process only a specific subdirectory
        process_specific_subdirectory(directory, args.subdirectory, not args.move, not args.no_recursive, not args.quiet)
    elif args.level_one:
        # Process only immediate subdirectories (depth=1)
        categorize_files_recursive(directory, not args.move, not args.no_recursive, max_depth=1, verbose=not args.quiet)
    else:
        # Normal processing
        categorize_files_recursive(directory, not args.move, not args.no_recursive, verbose=not args.quiet)
    
    if not args.quiet:
        sys.stdout.write("\nCategorization complete!\n")
        sys.stdout.flush() 