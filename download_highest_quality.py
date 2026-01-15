#!/usr/bin/env python3
"""
Script to download only the highest quality images from Il Ngwesi website.
This will replace any smaller versions with the full-size originals.
"""

import requests
from bs4 import BeautifulSoup
import os
from urllib.parse import urljoin, urlparse
import re

# URLs to scrape
urls = [
    "https://ilngwesi.com/content/visit/",
    "https://ilngwesi.com/content/visit/2016/04/04/staying-at-il-ngwesi/",
    "https://ilngwesi.com/content/visit/sample-page/how-to-book/"
]

# Create images directory
images_dir = "images"
os.makedirs(images_dir, exist_ok=True)

def sanitize_filename(filename):
    """Sanitize filename for filesystem."""
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    filename = filename.strip(' .')
    return filename

def get_base_image_name(url):
    """Extract base image name without dimensions."""
    # Remove dimension suffixes like -300x200, -1024x683, etc.
    base_name = re.sub(r'-\d+x\d+\.(jpg|jpeg|png|gif|webp)', r'.\1', url, flags=re.IGNORECASE)
    return base_name

def download_image(img_url, base_url, page_name, force=False):
    """Download an image from URL."""
    try:
        # Make absolute URL if relative
        if not img_url.startswith('http'):
            img_url = urljoin(base_url, img_url)
        
        # Get base image name (without dimensions)
        base_img_name = get_base_image_name(img_url)
        parsed = urlparse(base_img_name)
        base_filename = os.path.basename(parsed.path)
        
        if not base_filename or '.' not in base_filename:
            parsed_full = urlparse(img_url)
            base_filename = os.path.basename(parsed_full.path)
            if not base_filename or '.' not in base_filename:
                base_filename = f"image_{hash(img_url) % 10000}.jpg"
        
        # Sanitize filename
        base_filename = sanitize_filename(base_filename)
        
        # Add page prefix
        safe_page_name = sanitize_filename(page_name)
        filename = f"{safe_page_name}_{base_filename}"
        
        filepath = os.path.join(images_dir, filename)
        
        # Check if we already have this file
        if os.path.exists(filepath) and not force:
            existing_size = os.path.getsize(filepath)
            # Check server size
            try:
                head_response = requests.head(img_url, allow_redirects=True, timeout=30, headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                })
                server_size = int(head_response.headers.get('Content-Length', 0))
                if server_size > 0 and existing_size >= server_size * 0.95:  # Allow 5% tolerance
                    print(f"  Already have full-size: {base_filename}")
                    return True
            except:
                pass
        
        # Download image
        response = requests.get(img_url, timeout=30, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        response.raise_for_status()
        
        # Save image
        with open(filepath, 'wb') as f:
            f.write(response.content)
        
        # Remove any smaller versions of the same image
        base_pattern = re.escape(base_filename.replace('.jpg', '').replace('.jpeg', '').replace('.png', ''))
        for existing_file in os.listdir(images_dir):
            if existing_file.startswith(f"{safe_page_name}_{base_pattern}") and existing_file != filename:
                existing_path = os.path.join(images_dir, existing_file)
                existing_size = os.path.getsize(existing_path)
                if existing_size < len(response.content):
                    print(f"  Removing smaller version: {existing_file}")
                    os.remove(existing_path)
        
        print(f"  Downloaded: {base_filename} ({len(response.content):,} bytes)")
        return True
        
    except Exception as e:
        print(f"  Error downloading {img_url}: {e}")
        return False

def scrape_page(url):
    """Scrape a page and extract only the highest quality images."""
    print(f"\nScraping: {url}")
    
    try:
        response = requests.get(url, timeout=30, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        page_name = urlparse(url).path.strip('/').replace('/', '_') or 'home'
        
        img_tags = soup.find_all('img')
        print(f"  Found {len(img_tags)} <img> tags")
        
        downloaded_count = 0
        seen_bases = set()  # Track base image names to avoid duplicates
        
        for img in img_tags:
            # Check srcset for the largest available size
            srcset = img.get('srcset')
            largest_url = None
            largest_width = 0
            
            if srcset:
                # Parse srcset (format: "url1 300w, url2 768w, ...")
                srcset_parts = re.findall(r'(\S+)\s+(\d+)w', srcset)
                if srcset_parts:
                    srcset_parts.sort(key=lambda x: int(x[1]), reverse=True)
                    largest_url, largest_width = srcset_parts[0]
                    if not largest_url.startswith('http'):
                        largest_url = urljoin(url, largest_url)
            
            # Get base image name to check if we've already processed it
            if largest_url:
                base_name = get_base_image_name(largest_url)
                if base_name not in seen_bases:
                    if download_image(largest_url, url, page_name, force=True):
                        seen_bases.add(base_name)
                        downloaded_count += 1
            else:
                # Fall back to src
                img_url = (img.get('data-full-image') or 
                          img.get('data-full') or 
                          img.get('data-large') or
                          img.get('data-original') or
                          img.get('src') or 
                          img.get('data-src') or 
                          img.get('data-lazy-src'))
                
                if img_url:
                    if not img_url.startswith('http'):
                        img_url = urljoin(url, img_url)
                    
                    # Try to get full-size version
                    download_url = img_url
                    if re.search(r'-\d+x\d+\.(jpg|jpeg|png|gif|webp)', img_url, re.IGNORECASE):
                        download_url = re.sub(r'-\d+x\d+\.', '.', img_url, flags=re.IGNORECASE)
                    
                    base_name = get_base_image_name(download_url)
                    
                    if base_name not in seen_bases:
                        if download_image(download_url, url, page_name, force=True):
                            seen_bases.add(base_name)
                            downloaded_count += 1
        
        # Check background images
        elements_with_bg = soup.find_all(style=re.compile(r'background-image'))
        print(f"  Found {len(elements_with_bg)} elements with background-image")
        
        for elem in elements_with_bg:
            style = elem.get('style', '')
            match = re.search(r'url\(["\']?([^"\']+)["\']?\)', style)
            if match:
                img_url = match.group(1)
                if not img_url.startswith('http'):
                    img_url = urljoin(url, img_url)
                base_name = get_base_image_name(img_url)
                if base_name not in seen_bases:
                    if download_image(img_url, url, page_name, force=True):
                        seen_bases.add(base_name)
                        downloaded_count += 1
        
        print(f"  Total highest-quality images downloaded: {downloaded_count}")
        
    except Exception as e:
        print(f"  Error scraping {url}: {e}")

if __name__ == "__main__":
    print("Downloading highest quality images only...")
    print(f"Images will be saved to: {os.path.abspath(images_dir)}")
    print("Smaller versions will be removed.\n")
    
    for url in urls:
        scrape_page(url)
    
    print(f"\n\nDownload complete! Highest quality images saved to: {os.path.abspath(images_dir)}")

