from bs4 import BeautifulSoup
from urllib.parse import urlparse
import requests
import argparse
import os

session = requests.Session()
img_out_dir = "./img/"


def download_favicon(url, filename=None):
    parsed_url = urlparse(url)

    if not filename:
        # use second-level domain (SLD) for filename
        filename = parsed_url.netloc.split(".")[-2]

    # check if favicon already exists
    favicon_output_filename = img_out_dir + filename + ".ico"
    if os.path.exists(favicon_output_filename):
        print(favicon_output_filename + " already exists!")
        return

    # get url without path
    url = parsed_url.scheme + "://" + parsed_url.netloc
    print(url)
    response = session.get(url)

    # parse and get the favicon URL from the HTML content
    soup = BeautifulSoup(response.content, "html.parser")
    favicon_url = get_favicon_url_from_html(soup, url)

    if favicon_url:
        # download the favicon
        response = session.get(favicon_url)
        with open(favicon_output_filename, "wb") as f:
            f.write(response.content)
    else:
        print("Could not find favicon URL")


def get_favicon_url_from_html(soup, url):
    favicon_url = None
    for link in soup.find_all("link", {"rel": ["shortcut icon", "icon"]}):
        favicon_url = link.get("href")
        break
    if favicon_url and not favicon_url.startswith("http"):
        favicon_url = url + favicon_url

    return favicon_url


def download_favicons(links):
    for link in links:
        download_favicon(link)


def process_input(default):
    parser = argparse.ArgumentParser(description="Process a file or link")

    # Add optional arguments (flags)
    parser.add_argument("-f", "--file", type=str, help="Path to the file")
    parser.add_argument("-l", "--link", type=str, help="URL or link to process")

    args = parser.parse_args()

    # Handle the file option (-f or --file)
    if args.file:
        if os.path.isfile(args.file):
            with open(args.file, "r") as file:
                urls = [url.strip() for url in file.read().splitlines()]
                return urls
        else:
            print(f"File '{args.file}' not found!")
            return None

    # Handle the link option (-l or --link)
    if args.link:
        return [str(args.link).strip()]

    print("No file or link provided. Using default.")
    return default


if __name__ == "__main__":
    default_urls_to_download = ["https://www.github.com/"]
    urls = process_input(default_urls_to_download)
    download_favicons(urls)
