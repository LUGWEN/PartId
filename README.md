# MusicXML File Categorizer

This script categorizes MusicXML files based on the number of `<score-part>` elements they contain, organizing them into appropriate subdirectories.

## Categories

Files are sorted into three categories:

- **1_part**: Files with exactly 1 part
- **2-6_parts**: Files with 2 to 6 parts
- **multi_parts**: Files with more than 6 parts

## Usage

```
python categorize_files.py [options]
```

Or with uv:

```
uv run categorize_files.py [options]
```

### Options

- `-d, --directory DIR`: Source directory to process (default: current directory)
- `-m, --move`: Move files instead of copying them (default is copy)
- `-nr, --no-recursive`: Do not process subdirectories recursively (default is recursive)
- `-s, --subdirectory SUBDIR`: Process only a specific subdirectory under the main directory
- `-l1, --level-one`: Process only immediate subdirectories (depth=1)
- `-q, --quiet`: Reduce output verbosity

## Examples

### Process all files in the current directory and all subdirectories (recursive)

```
uv run categorize_files.py
```

### Process files in a specific directory

```
uv run categorize_files.py -d "D:\GITHUB\PartId\Beethoven"
```

### Process only immediate subdirectories (first level)

```
uv run categorize_files.py -l1
```

### Process a specific subdirectory

```
uv run categorize_files.py -s "Beethoven"
```

### Move files instead of copying them

```
uv run categorize_files.py -m
```

## Directory Structure Example

Before:
```
D:\GITHUB\PartId\
├── Beethoven\
│   ├── Sonata No. 11 Bb major, Opus 22\
│   │   ├── file1.xml
│   │   └── file2.xml
│   └── Symphony No. 5\
│       ├── file3.xml
│       └── file4.xml
```

After:
```
D:\GITHUB\PartId\
├── Beethoven\
│   ├── Sonata No. 11 Bb major, Opus 22\
│   │   ├── 1_part\
│   │   │   └── file1.xml
│   │   └── 2-6_parts\
│   │       └── file2.xml
│   └── Symphony No. 5\
│       ├── multi_parts\
│       │   └── file3.xml
│       └── 2-6_parts\
│           └── file4.xml
``` 