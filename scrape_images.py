#!/usr/bin/env python3
"""
Script to scrape Il Ngwesi website pages and download all images.
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
    # Remove or replace invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Remove leading/trailing spaces and dots
    filename = filename.strip(' .')
    return filename

def download_image(img_url, base_url, page_name):
    """Download an image from URL."""
    try:
        # Make absolute URL if relative
        if not img_url.startswith('http'):
            img_url = urljoin(base_url, img_url)
        
        # Get filename from URL
        parsed = urlparse(img_url)
        filename = os.path.basename(parsed.path)
        
        # If no filename, generate one
        if not filename or '.' not in filename:
            filename = f"image_{hash(img_url) % 10000}.jpg"
        
        # Sanitize filename
        filename = sanitize_filename(filename)
        
        # Add page prefix to avoid conflicts
        safe_page_name = sanitize_filename(page_name)
        filename = f"{safe_page_name}_{filename}"
        
        filepath = os.path.join(images_dir, filename)
        
        # Skip if already downloaded
        if os.path.exists(filepath):
            print(f"  Skipping (already exists): {filename}")
            return
        
        # Download image
        response = requests.get(img_url, timeout=30, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        response.raise_for_status()
        
        # Save image
        with open(filepath, 'wb') as f:
            f.write(response.content)
        
        print(f"  Downloaded: {filename} ({len(response.content)} bytes)")
        
    except Exception as e:
        print(f"  Error downloading {img_url}: {e}")

def scrape_page(url):
    """Scrape a page and extract all images."""
    print(f"\nScraping: {url}")
    
    try:
        response = requests.get(url, timeout=30, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract page name for filename prefix
        page_name = urlparse(url).path.strip('/').replace('/', '_') or 'home'
        
        # Find all img tags
        img_tags = soup.find_all('img')
        print(f"  Found {len(img_tags)} <img> tags")
        
        downloaded_count = 0
        seen_images = set()  # Track images we've already downloaded to avoid duplicates
        
        for img in img_tags:
            # First, check srcset for the largest available size
            srcset = img.get('srcset')
            largest_url = None
            largest_width = 0
            
            if srcset:
                # Parse srcset properly (format: "url1 300w, url2 768w, ...")
                srcset_parts = re.findall(r'(\S+)\s+(\d+)w', srcset)
                if srcset_parts:
                    # Sort by width and get the largest
                    srcset_parts.sort(key=lambda x: int(x[1]), reverse=True)
                    largest_url, largest_width = srcset_parts[0]
                    # Make absolute URL if needed
                    if not largest_url.startswith('http'):
                        largest_url = urljoin(url, largest_url)
            
            # If we found a large image in srcset, use it
            if largest_url and largest_url not in seen_images:
                download_image(largest_url, url, page_name)
                seen_images.add(largest_url)
                downloaded_count += 1
            else:
                # Fall back to src attribute
                img_url = (img.get('data-full-image') or 
                          img.get('data-full') or 
                          img.get('data-large') or
                          img.get('data-original') or
                          img.get('src') or 
                          img.get('data-src') or 
                          img.get('data-lazy-src'))
                
                if img_url:
                    # Make absolute URL if needed
                    if not img_url.startswith('http'):
                        img_url = urljoin(url, img_url)
                    
                    # Try to get full-size version by removing dimension suffixes
                    if re.search(r'-\d+x\d+\.(jpg|jpeg|png|gif|webp)', img_url, re.IGNORECASE):
                        # Try full-size version (without dimensions)
                        full_size_url = re.sub(r'-\d+x\d+\.', '.', img_url, flags=re.IGNORECASE)
                        if full_size_url not in seen_images:
                            download_image(full_size_url, url, page_name)
                            seen_images.add(full_size_url)
                            downloaded_count += 1
                    elif img_url not in seen_images:
                        download_image(img_url, url, page_name)
                        seen_images.add(img_url)
                        downloaded_count += 1
        
        # Also check for background images in style attributes
        elements_with_bg = soup.find_all(style=re.compile(r'background-image'))
        print(f"  Found {len(elements_with_bg)} elements with background-image")
        
        for elem in elements_with_bg:
            style = elem.get('style', '')
            match = re.search(r'url\(["\']?([^"\']+)["\']?\)', style)
            if match:
                img_url = match.group(1)
                download_image(img_url, url, page_name)
                downloaded_count += 1
        
        # Check CSS files for images
        css_links = soup.find_all('link', rel='stylesheet')
        for css_link in css_links:
            css_url = css_link.get('href')
            if css_url:
                try:
                    css_url = urljoin(url, css_url)
                    css_response = requests.get(css_url, timeout=30, headers={
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                    })
                    css_response.raise_for_status()
                    
                    # Find image URLs in CSS
                    css_images = re.findall(r'url\(["\']?([^"\']+\.(?:jpg|jpeg|png|gif|webp|svg))["\']?\)', 
                                          css_response.text, re.IGNORECASE)
                    for img_url in css_images:
                        download_image(img_url, css_url, page_name)
                        downloaded_count += 1
                except Exception as e:
                    print(f"  Error processing CSS {css_url}: {e}")
        
        print(f"  Total images processed: {downloaded_count}")
        
    except Exception as e:
        print(f"  Error scraping {url}: {e}")

if __name__ == "__main__":
    print("Starting image scraping...")
    print(f"Images will be saved to: {os.path.abspath(images_dir)}")
    
    for url in urls:
        scrape_page(url)
    
    print(f"\n\nScraping complete! Images saved to: {os.path.abspath(images_dir)}")

