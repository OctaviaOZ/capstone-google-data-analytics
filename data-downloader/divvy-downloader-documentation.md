# Divvy Tripdata Downloader

This document explains how to use the `divvy_downloader.py` script to download Divvy bike trip data from the public S3 bucket.

## Overview

The Divvy Tripdata Downloader is a Python script that efficiently downloads bike-sharing trip data from the Divvy public S3 bucket. It provides a flexible command-line interface for filtering and controlling downloads with features for concurrent processing, progress tracking, and resumable downloads.

## Features

- **Data Discovery**: Automatically parses the S3 bucket's XML index to find all available data files
- **Flexible Filtering**: Filter files by year, quarter, or custom regex patterns
- **Resume Support**: Skip already downloaded files with size verification
- **Progress Tracking**: Visual progress bars for individual files and overall download
- **Configurable**: Extensive command-line options for customization

## Requirements

- Python 3.9 or newer
- Required Python packages:
  - `requests`: For HTTP communication
  - `beautifulsoup4`: For XML parsing
  - `tqdm`: For progress bars

Install the dependencies using pip:

```bash
pip install requests beautifulsoup4 tqdm
```

## Basic Usage

At its simplest, you can run the script with no arguments to download all available Divvy tripdata files:

```bash
python divvy_downloader.py
```

This will:
1. Connect to the Divvy S3 bucket
2. List all available files
3. Download all files to a `data` directory

## Command-Line Options

The script provides numerous command-line arguments to customize its behavior:

| Argument | Description | Default |
|----------|-------------|---------|
| `--url` | Base URL of the Divvy data S3 bucket | `https://divvy-tripdata.s3.amazonaws.com/` |
| `--output-dir` | Directory to save downloaded files | `data` |
| `--pattern` | Regex pattern to filter files by name | None |
| `--year` | Filter files by year (e.g., 2023) | None |
| `--quarter` | Filter files by quarter (1-4), must be used with --year | None |
| `--list-only` | Only list available files without downloading | False |

## Examples

### List All Available Files Without Downloading

```bash
python .\data-downloader\divvy_downloader.py --list-only
```

### Download Files from a Specific Year

```bash
python .\data-downloader\divvy_downloader.py --year 2023
```

### Download Files from a Specific Quarter

```bash
python .\data-downloader\divvy_downloader.py --year 2024 --quarter 3
```

### Use a Custom Pattern to Filter Files

```bash
python .\data-downloader\divvy_downloader.py --pattern "202301.*\.zip"
```

### Download to a Custom Directory

```bash
python .\data-downloader\divvy_downloader.py --output-dir "data"
```

### Combine Multiple Options

```bash
python .\data-downloader\divvy_downloader.py --year 2023 --output-dir "data"
```

## Script Structure

The script is organized around a `DivvyDataDownloader` class with these key methods:

1. `get_available_files()`: Fetches and parses the index page to extract file information
2. `filter_files_by_pattern()`, `filter_files_by_year()`, `filter_files_by_quarter()`: Apply filters to the file list
3. `download_file()`: Downloads a single file with progress tracking


## How It Works

The script follows these steps:

1. **Parse Command-Line Arguments**: Process user-provided options
2. **Connect to S3 Bucket**: Fetch the index.html file from the bucket
3. **Parse Available Files**: Extract file information from the XML index
4. **Apply Filters**: Filter the file list based on provided criteria
5. **Display Information**: Show file samples and total download size
6. **Display Summary**: Show download statistics after completion

## Advanced Usage

### Using with Different Data Sources

While designed for Divvy data, the script can work with any S3 bucket that provides an XML index:

```bash
python .\data-downloader\divvy_downloader.py --url "https://other-data-source.s3.amazonaws.com/"
```

### Custom Filter Patterns

The `--pattern` option accepts Python regular expressions for flexible filtering:

```bash
# Download only CSV files
python .\data-downloader\divvy_downloader.py --pattern "\.csv$"

# Download files from January-March of any year
python .\data-downloader\divvy_downloader.py --pattern "(01|02|03)-.*\.zip"
```

## Troubleshooting

### Connection Issues

If you encounter connection problems:
- Check your internet connection
- Verify the S3 bucket URL is correct
- Ensure you have proper permissions to access the bucket

### Download Errors

If downloads fail:
- The script will continue with other files
- Rerun the script to retry failed downloads
- Already successful downloads will be skipped

## License

This script is provided as open-source software for educational and research purposes.
