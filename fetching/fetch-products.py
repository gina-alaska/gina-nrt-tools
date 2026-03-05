import argparse
import logging
import os
from pathlib import Path
import requests
from datetime import datetime

NRT_SITE="http://nrt-status.gina.alaska.edu/products.txt?"
LOG_FILE=os.getenv("GINA_FETCH_LOG_FILE", "")

def retrieve_product_list(params: dict) -> list:
    """
    Retrieve a list of product URLs from GINA NRT server based on query parameters.
    
    Args:
        params: Dictionary of query parameters (satellites[], sensors[], etc.)
    
    Returns:
        List of product URLs from the API response
    
    Raises:
        requests.RequestException: If the HTTP request fails
    """
    response = requests.get(NRT_SITE, params=params)
    logging.info(f"Retrieving products from URL: {response.url}")
    response.raise_for_status()
    
    product_urls = response.text.strip().splitlines()
    return product_urls

def filter_by_wildcard(urls: list, wildcard: str) -> list:
    """
    Filter URLs by checking if they contain a wildcard string.
    
    Args:
        urls: List of URLs to filter
        wildcard: String to search for in URLs. If empty, returns all URLs.
    
    Returns:
        List of URLs containing the wildcard string
    """
    if not wildcard:
        return urls
    return [url for url in urls if wildcard in url]

def filter_by_suffix(urls: list, suffix: str) -> list:
    """
    Filter URLs by file suffix or extension.
    
    Args:
        urls: List of URLs to filter
        suffix: File suffix to match (e.g., '.png' or 'small.png'). If empty, returns all URLs.
    
    Returns:
        List of URLs ending with the specified suffix
    """
    if not suffix:
        return urls
    return [url for url in urls if url.endswith(suffix)]

def download_files(urls: list, output_dir: str, namespace: bool = False, create_done_file: bool = False, overwrite: bool = False) -> None:
    """
    Download multiple files from a list of URLs.
    
    Args:
        urls: List of file URLs to download
        output_dir: Directory to save downloaded files
        namespace: If True, organize files into subdirectories based on pass identifiers
        create_done_file: If True, create a timestamped .done marker file after all downloads complete
        overwrite: If False, skip files that already exist in output_dir (default: False)
    """
    for url in urls:
        if not url.strip():
            continue
        
        # Extract filename from URL
        filename = url.split('/')[-1]
        
        # Create subdirectory path if namespace is enabled
        if namespace:
            # Extract pass identifier from URL if possible
            parts = url.split('/')
            pass_dir = parts[-2] if len(parts) > 1 else "data"
            output_path = os.path.join(output_dir, pass_dir, filename)
        else:
            output_path = os.path.join(output_dir, filename)
        
        download_file(url, output_path, overwrite=overwrite)
        
    if create_done_file:
        done_file = datetime.now().strftime("%Y%m%d_%H%M%S") + ".done"
        Path(done_file).touch()
        logging.info(f"Created done file: {done_file}")

def download_file(url: str, output_path: str, overwrite: bool = False) -> None:
    """
    Download a single file from a URL and save it to the specified path.
    
    Args:
        url: URL of the file to download
        output_path: Local file path where the downloaded file will be saved
        overwrite: If False, skip download if file already exists (default: False)
    
    Note:
        Creates parent directories as needed. Logs errors without raising exceptions.
    """
    # Check if file already exists
    if os.path.exists(output_path) and not overwrite:
        logging.info(f"Skipped (file exists): {output_path}")
        return
    
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
        
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        logging.info(f"Downloaded: {output_path}")
    except requests.RequestException as e:
        logging.info(f"Error downloading {url}: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Fetch and download files from gina processing stack"
    )
    
    parser.add_argument(
        "-s", "--satellite",
        help="Fetch data for SATELLITE"
    )
    parser.add_argument(
        "-i", "--sensor",
        help="Fetch data for SENSOR"
    )
    parser.add_argument(
        "-f", "--facility",
        help="Fetch data for FACILITY"
    )
    parser.add_argument(
        "-p", "--processing-level",
        help="Fetch data for PROCESSING_LEVEL"
    )
    parser.add_argument(
        "-n", "--namespace",
        action="store_true",
        help="Namespace the data (Place in sub-directories for each pass)"
    )
    parser.add_argument(
        "-o", "--output",
        default=".",
        help="Path to write data to (Default: current directory)"
    )
    parser.add_argument(
        "-z", "--done-file",
        action="store_true",
        help="Create done file"
    )
    parser.add_argument(
        "--start-date",
        default="",
        help="Start date for filtering products (YYYY-MM-DD format)"
    )
    parser.add_argument(
        "--end-date",
        default="",
        help="End date for filtering products (YYYY-MM-DD format)"
    )
    parser.add_argument(
        "-w", "--wildcard",
        default="",
        help="Wildcard filter for filenames (only download files containing this string)"
    )
    parser.add_argument(
        "--suffix",
        default="",
        help="Filter by file suffix (e.g., '.png' or 'small.png')"
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing files (default: skip if file exists)"
    )
    
    args = parser.parse_args()
    
    # Check if at least one query filter is provided
    if not any([args.satellite, args.sensor, args.facility, args.processing_level]):
        parser.print_help()
        return
    
    params = {}
    if args.satellite:
        params["satellites[]"] = args.satellite
    if args.sensor:
        params["sensors[]"] = args.sensor
    if args.facility:
        params["facilities[]"] = args.facility
    if args.processing_level:
        params["processing_levels[]"] = args.processing_level
    if args.start_date:
        params["start_date"] = args.start_date
    if args.end_date:
        params["end_date"] = args.end_date
    
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s',
                        filename=LOG_FILE if LOG_FILE else None
                        )
    
    products = retrieve_product_list(params)
    
    if products:
        filtered_products = filter_by_wildcard(products, args.wildcard)
        filtered_products = filter_by_suffix(filtered_products, args.suffix)

        logging.info(f"Found {len(filtered_products)} product(s) matching filters")

        if filtered_products:
            download_files(
                filtered_products,
                args.output,
                namespace=args.namespace,
                create_done_file=args.done_file,
                overwrite=args.overwrite
            )
        else:
            logging.info("No products match the filters")
    else:
        logging.info("No products found")

if __name__ == "__main__":
    main()