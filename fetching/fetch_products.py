"""Fetching script and functions for GINA's NRT system.

Requires python 3.9+ and requests package.

Allows searching, filtering, and downloading of GINA NRT data. See dropdown menus at "http://nrt-status.gina.alaska.edu/products?" for available parameters.
"""

import argparse
import logging
import os
from pathlib import Path
import requests
from dataclasses import dataclass
from typing import Optional
import re

NRT_SITE = "http://nrt-status.gina.alaska.edu/products.txt?"
LOG_FILE = os.getenv("GINA_FETCH_LOG_FILE", "")


@dataclass
class SearchParams:
    satellite: Optional[list[str]] = None
    sensor: Optional[list[str]] = None
    facility: Optional[list[str]] = None
    processing_level: Optional[list[str]] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None

    def to_query_params(self) -> dict:
        """Convert to API query param format, skipping unset fields."""
        mapping = {
            "satellite": "satellites[]",
            "sensor": "sensors[]",
            "facility": "facilities[]",
            "processing_level": "processing_levels[]",
            "start_date": "start_date",
            "end_date": "end_date",
        }
        return {mapping[k]: v for k, v in vars(self).items() if v is not None}


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
    response = requests.get(NRT_SITE, params=params, timeout=30)
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

def filter_by_regex_wildcard(urls: list, wildcard: str) -> list:
    """
    Filter URLS by checking if they match a regex.

    Args:
        urls: List of URLs to filter
        wildcard: A valid regex pattern to match URLs. If empty, returns all URLs.
    Returns:
        List of URLs matching wildcard regex
    """
    if not wildcard:
        return urls

    try:
        pattern = re.compile(wildcard)
    except re.error as e:
        logging.error(f"Bad regex pattern '{wildcard}': {e}")
        return []
        
    return [url for url in urls if pattern.search(url)]

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


def download_files(
    urls: list, output_dir: Path, namespace: bool = False, overwrite: bool = False
) -> None:
    """
    Download multiple files from a list of URLs.

    Args:
        urls: List of file URLs to download
        output_dir: Directory to save downloaded files
        namespace: If True, organize files into subdirectories based on pass identifiers
        overwrite: If False, skip files that already exist in output_dir (default: False)
    """
    for url in urls:
        if not url.strip():
            continue

        # Extract filename from URL
        filename = url.split("/")[-1]

        # Create subdirectory path if namespace is enabled
        if namespace:
            # Extract pass identifier from URL if possible
            parts = url.split("/")
            pass_dir = parts[-2] if len(parts) > 1 else "data"
            output_path = output_dir / pass_dir / filename
        else:
            output_path = output_dir / filename

        try:
            download_file(url, output_path, overwrite=overwrite)
        except DownloadError as e:
            logging.warning(e)


class DownloadError(Exception):
    """Raised when a file download fails."""


def download_file(url: str, output_path: Path, overwrite: bool = False) -> Path:
    """
    Download a single file from a URL and save it to the specified path.

    Args:
        url: URL of the file to download
        output_path: Local file path where the downloaded file will be saved
        overwrite: If False, skip download if file already exists (default: False)

    Note:
        Creates parent directories as needed. Raises custom DownloadError exception upon request failure.
    """
    # Check if file already exists
    if output_path.exists() and not overwrite:
        logging.info(f"Skipped (file exists): {output_path}")
        return output_path

    try:
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()

        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        logging.info(f"Downloaded: {output_path} from {url}")
        return output_path
    except requests.RequestException as e:
        raise DownloadError(f"Error downloading {url}: {e}") from e


def main():
    parser = argparse.ArgumentParser(
        description="Fetch and download files from gina processing stack"
    )

    parser.add_argument("-s", "--satellite", nargs="+", help="Fetch data for SATELLITE")
    parser.add_argument("-i", "--sensor", nargs="+", help="Fetch data for SENSOR")
    parser.add_argument("-f", "--facility", nargs="+", help="Fetch data for FACILITY")
    parser.add_argument(
        "-p", "--processing-level", nargs="+", help="Fetch data for PROCESSING_LEVEL"
    )
    parser.add_argument(
        "-n",
        "--namespace",
        action="store_true",
        help="Namespace the data (Place in sub-directories for each pass)",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("."),
        help="Path to write data to (Default: current directory)",
    )
    parser.add_argument(
        "--start-date",
        default="",
        help="Start date for filtering products (YYYY-MM-DD format)",
    )
    parser.add_argument(
        "--end-date",
        default="",
        help="End date for filtering products (YYYY-MM-DD format)",
    )
    parser.add_argument(
        "-w",
        "--wildcard",
        default="",
        help="Wildcard filter for filenames (only download files containing this string)",
    )
    parser.add_argument(
        "-r", 
        "--regex",
        default="",
        help="Wildcard filter in valid regex format for filenames (only download files matching this regex pattern)",
    )
    parser.add_argument(
        "--suffix",
        default="",
        help="Filter by file suffix (e.g., '.png' or 'small.png')",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing files (default: skip if file exists)",
    )

    args = parser.parse_args()

    # Check if at least one query filter is provided
    if not any([args.satellite, args.sensor, args.facility, args.processing_level]):
        parser.print_help()
        return

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        filename=LOG_FILE if LOG_FILE else None,
    )

    params = SearchParams(
        satellite=args.satellite,
        sensor=args.sensor,
        facility=args.facility,
        processing_level=args.processing_level,
        start_date=args.start_date,
        end_date=args.end_date,
    ).to_query_params()

    products = retrieve_product_list(params)

    if products:
        filtered_products = filter_by_wildcard(products, args.wildcard)
        filtered_products = filter_by_regex_wildcard(products, args.regex)
        filtered_products = filter_by_suffix(filtered_products, args.suffix)

        logging.info(f"Found {len(filtered_products)} product(s) matching filters")

        if filtered_products:
            download_files(
                filtered_products,
                args.output,
                namespace=args.namespace,
                overwrite=args.overwrite,
            )
        else:
            logging.info("No products match the filters")
    else:
        logging.info("No products found")


if __name__ == "__main__":
    main()
