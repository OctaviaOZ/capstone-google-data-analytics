"""
Simple Divvy Tripdata Downloader

A straightforward script to download Divvy bike trip data from:
https://divvy-tripdata.s3.amazonaws.com/index.html

Features:
- File discovery via URL pattern testing
- Year and quarter filtering
- Progress tracking during downloads
- Skips already downloaded files

Python 3.9.12 compatible
"""

import os
import re
import argparse
import requests
from urllib.parse import urljoin
from tqdm import tqdm


def get_available_files(base_url):
    """
    Discover available Divvy data files using pattern-based URL testing.
    
    Args:
        base_url: Base URL of the Divvy data repository
        
    Returns:
        List of dictionaries containing file information
    """
    session = requests.Session()
    discovered_files = []
    
    print("Discovering available files...")
    
    # Test for monthly files (most common format)
    for year in range(2013, 2025):
        for month in range(1, 13):
            filename = f"{year}{month:02d}-divvy-tripdata.zip"
            url = urljoin(base_url, filename)
            
            try:
                # Make a HEAD request to check if file exists
                head_response = session.head(url, timeout=5)
                if head_response.status_code == 200:
                    # File exists
                    content_length = head_response.headers.get('Content-Length', '0')
                    size = int(content_length) if content_length.isdigit() else 0
                    size_mb = round(size / (1024 * 1024), 2)
                    
                    discovered_files.append({
                        "filename": filename,
                        "url": url,
                        "size": size,
                        "size_mb": size_mb,
                        "year": year,
                        "month": month
                    })
                    print(f"Found file: {filename} ({size_mb} MB)")
            except requests.exceptions.RequestException:
                # File doesn't exist or connection error - skip silently
                pass
    
    # Sort files by year and month
    discovered_files.sort(key=lambda x: (x["year"], x["month"]))
    return discovered_files


def filter_files_by_year(files, year):
    """
    Filter files list to include only those from the specified year.
    
    Args:
        files: List of file dictionaries
        year: Year to filter by (as integer)
        
    Returns:
        Filtered list of files
    """
    if not year:
        return files
        
    return [file for file in files if file["year"] == year]


def filter_files_by_quarter(files, year, quarter):
    """
    Filter files list to include only those from the specified year and quarter.
    
    Args:
        files: List of file dictionaries
        year: Year to filter by (as integer)
        quarter: Quarter to filter by (1-4)
        
    Returns:
        Filtered list of files
    """
    if not year or not quarter:
        return files
        
    if quarter not in [1, 2, 3, 4]:
        raise ValueError("Quarter must be 1, 2, 3, or 4")
    
    # Define month ranges for each quarter
    quarter_months = {
        1: [1, 2, 3],
        2: [4, 5, 6],
        3: [7, 8, 9],
        4: [10, 11, 12]
    }
    
    return [
        file for file in files 
        if file["year"] == year and file["month"] in quarter_months[quarter]
    ]


def download_file(url, output_path, session=None):
    """
    Download a single file with progress tracking.
    
    Args:
        url: URL of the file to download
        output_path: Local path to save the file
        session: Requests session (creates new one if None)
        
    Returns:
        True if download successful, False otherwise
    """
    if session is None:
        session = requests.Session()
    
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Download with progress bar
        response = session.get(url, stream=True)
        response.raise_for_status()
        
        # Get total file size for progress bar
        total_size = int(response.headers.get('Content-Length', 0))
        
        with open(output_path, 'wb') as f, tqdm(
            desc=os.path.basename(output_path),
            total=total_size,
            unit='B',
            unit_scale=True,
            unit_divisor=1024
        ) as pbar:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    pbar.update(len(chunk))
        
        return True
    
    except Exception as e:
        print(f"Error downloading {url}: {str(e)}")
        # Remove partial file if download failed
        if os.path.exists(output_path):
            os.remove(output_path)
        return False


def main():
    """Main function to run the script."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Download Divvy bike trip data"
    )
    parser.add_argument(
        "--url",
        type=str,
        default="https://divvy-tripdata.s3.amazonaws.com/",
        help="Base URL of the Divvy data repository"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="data",
        help="Directory to save downloaded files"
    )
    parser.add_argument(
        "--year",
        type=int,
        help="Filter files by year (e.g., 2023)"
    )
    parser.add_argument(
        "--quarter",
        type=int,
        choices=[1, 2, 3, 4],
        help="Filter files by quarter (1-4)"
    )
    parser.add_argument(
        "--list-only",
        action="store_true",
        help="Only list available files without downloading"
    )
    args = parser.parse_args()
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Get available files
    all_files = get_available_files(args.url)
    if not all_files:
        print("No files found. Please check the URL.")
        return
    
    print(f"Found {len(all_files)} files in total")
    
    # Apply filters if specified
    filtered_files = all_files
    if args.year:
        filtered_files = filter_files_by_year(filtered_files, args.year)
        print(f"Filtered by year {args.year}: {len(filtered_files)} files")
    
    if args.year and args.quarter:
        filtered_files = filter_files_by_quarter(filtered_files, args.year, args.quarter)
        print(f"Filtered by {args.year} Q{args.quarter}: {len(filtered_files)} files")
    
    if not filtered_files:
        print("No files match the specified filters.")
        return
    
    # Calculate total download size
    total_size_mb = sum(file["size_mb"] for file in filtered_files)
    print(f"Total download size: {total_size_mb:.2f} MB")
    
    # List mode - just show files and exit
    if args.list_only:
        print("\nAvailable files:")
        for file in filtered_files:
            print(f"{file['filename']} - {file['size_mb']} MB")
        return
    
    # Download files one by one
    print(f"\nDownloading {len(filtered_files)} files to {args.output_dir}")
    session = requests.Session()
    
    successful_downloads = 0
    for file in filtered_files:
        output_path = os.path.join(args.output_dir, file["filename"])
        
        # Skip if file already exists with correct size
        if os.path.exists(output_path):
            if os.path.getsize(output_path) == file["size"]:
                print(f"Skipping {file['filename']} (already downloaded)")
                successful_downloads += 1
                continue
        
        print(f"Downloading {file['filename']} ({file['size_mb']} MB)")
        if download_file(file["url"], output_path, session):
            successful_downloads += 1
    
    # Print summary
    print(f"\nDownload complete: {successful_downloads} of {len(filtered_files)} files downloaded")
    print(f"Files saved to: {os.path.abspath(args.output_dir)}")


if __name__ == "__main__":
    main()