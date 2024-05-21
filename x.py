import os
import sys
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from colorama import Fore, Style
from tqdm import tqdm

# Function to download a file
def download_file(url, folder):
    local_filename = os.path.join(folder, os.path.basename(url))
    local_filename = local_filename.split('?')[0]  # Remove query parameters from filename
    os.makedirs(folder, exist_ok=True)
    with requests.get(url, stream=True) as r:
        if r.status_code == 200:
            total_size = int(r.headers.get('content-length', 0))
            with open(local_filename, 'wb') as f, tqdm(
                desc=os.path.basename(url),
                total=total_size,
                unit='B',
                unit_scale=True,
                unit_divisor=1024,
                dynamic_ncols=True,
                ascii=True,
                leave=True
            ) as progress_bar:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
                    progress_bar.update(len(chunk))
            return local_filename
        else:
            print(Fore.RED + f"Failed to download {url}, status code: {r.status_code}" + Style.RESET_ALL)
            return None

# Function to save HTML content
def save_html(content, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

# Function to get all assets (CSS, JS, Images) from the HTML
def get_assets(soup, base_url):
    assets = {
        'css': [],
        'js': [],
        'images': []
    }

    # Get CSS files
    for link in soup.find_all('link', href=True):
        if 'stylesheet' in link.get('rel', []):
            full_url = urljoin(base_url, link['href'])
            assets['css'].append(full_url)

    # Get JS files
    for script in soup.find_all('script', src=True):
        full_url = urljoin(base_url, script['src'])
        assets['js'].append(full_url)

    # Get images
    for img in soup.find_all('img', src=True):
        full_url = urljoin(base_url, img['src'])
        assets['images'].append(full_url)

    return assets

# Main function to download the website
def download_website(url):
    print(Fore.GREEN + "Downloading website..." + Style.RESET_ALL)
    response = requests.get(url)
    if response.status_code == 200:
        parsed_url = urlparse(url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        soup = BeautifulSoup(response.content, 'html.parser')

        download_dir = os.path.join(os.path.expanduser('~'), 'Downloads', 'website_download')
        os.makedirs(download_dir, exist_ok=True)

        # Save the main HTML file
        save_html(response.text, os.path.join(download_dir, 'index.html'))

        # Get all assets and download them
        assets = get_assets(soup, base_url)
        
        for asset_type, urls in assets.items():
            asset_dir = os.path.join(download_dir, asset_type)
            for asset_url in urls:
                download_file(asset_url, asset_dir)

        print(Fore.GREEN + f"Website downloaded successfully to {download_dir}" + Style.RESET_ALL)

    else:
        print(Fore.RED + f"Failed to access {url}, status code: {response.status_code}" + Style.RESET_ALL)

if __name__ == "__main__":
    try:
        from colorama import init
        init(autoreset=True)  # Initialize colorama for automatic reset of colors
        from tqdm import tqdm  # Import tqdm for progress bar
        url = input("Enter the website URL: ")
        download_website(url)
    except KeyboardInterrupt:
        print(Fore.YELLOW + "\nDownload cancelled by user." + Style.RESET_ALL)
    except Exception as e:
        print(Fore.RED + f"\nAn error occurred: {e}" + Style.RESET_ALL)
