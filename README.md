# Kimai Parser
This project is a tool for generating CSV files based on a time tracking CSV file.

### Installation
This project requires Python 3.7 or higher. Clone the repository and install the required packages:

### Usage
```
usage: index.py [-h] [--output OUTPUT_DIR] filepath project [project ...]

positional arguments:
  filepath              path to the time tracking CSV file
  project               one or more project names to include in the output CSV files

optional arguments:
  -h, --help            show this help message and exit
  --output OUTPUT_DIR
                        path to the directory where the output CSV files will be saved (default: current directory)
```

### Example usage:
```
python index.py time_tracking.csv ProjectA ProjectB --output output_files
```
This will generate monthly CSV files for "ProjectA" and "ProjectB" in the "output_files" directory.