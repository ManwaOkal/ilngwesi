#!/usr/bin/env python3
"""
Script to scrape Maasai product images from Mawu Africa collection pages.
"""

import requests
from bs4 import BeautifulSoup
import os
from urllib.parse import urljoin, urlparse
import re
import json
import time

# URLs to scrape (multiple pages)
urls = [
    "https://mawuafrica.com/en-us/collections/maasai-inspired-collection",
    "https://mawuafrica.com/en-us/collections/maasai-inspired-collection?page=2",
    "https://mawuafrica.com/en-us/collections/maasai-inspired-collection?page=3",
    "https://mawuafrica.com/en-us/collections/maasai-inspired-collection?page=4",
    "https://mawuafrica.com/en-us/collections/maasai-inspired-collection?page=5",
    "https://mawuafrica.com/en-us/collections/maasai-inspired-collection?page=6"
]

# Create products directory
products_dir = "products"
os.makedirs(products_dir, exist_ok=True)

def sanitize_filename(filename):
    """Sanitize filename for filesystem."""
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    filename = filename.strip(' .')
    return filename

def download_image(img_url, product_name):
    """Download an image from URL."""
    try:
        if not img_url.startswith('http'):
            img_url = urljoin('https://mawuafrica.com', img_url)
        
        parsed = urlparse(img_url)
        filename = os.path.basename(parsed.path)
        
        if not filename or '.' not in filename:
            filename = f"{product_name.replace(' ', '_')}.jpg"
        
        filename = sanitize_filename(filename)
        filename = f"{product_name.replace(' ', '_')}_{filename}"
        
        filepath = os.path.join(products_dir, filename)
        
        if os.path.exists(filepath):
            print(f"  Skipping (already exists): {filename}")
            return filename
        
        response = requests.get(img_url, timeout=30, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        response.raise_for_status()
        
        with open(filepath, 'wb') as f:
            f.write(response.content)
        
        print(f"  Downloaded: {filename} ({len(response.content)} bytes)")
        return filename
        
    except Exception as e:
        print(f"  Error downloading {img_url}: {e}")
        return None

def scrape_products_from_url(url):
    """Scrape products from a single Mawu Africa page."""
    print(f"\nScraping: {url}")
    
    try:
        response = requests.get(url, timeout=30, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        products = []
        seen_images = set()
        
        # Look for product images - try multiple selectors
        img_tags = soup.find_all('img')
        print(f"  Found {len(img_tags)} <img> tags")
        
        # Also look for product cards/containers
        product_containers = soup.find_all(['div', 'article', 'li', 'a'], class_=re.compile(r'product|item|card|grid', re.I))
        print(f"  Found {len(product_containers)} potential product containers")
        
        for img in img_tags:
            # Try multiple image source attributes
            img_url = (img.get('src') or 
                      img.get('data-src') or 
                      img.get('data-lazy-src') or
                      img.get('data-original') or
                      img.get('data-full-image'))
            
            if not img_url:
                continue
                
            # Make absolute URL
            if not img_url.startswith('http'):
                img_url = urljoin(url, img_url)
            
            # Skip if we've seen this image
            if img_url in seen_images:
                continue
            
            # Check if it's a product image (not logo, icon, etc.)
            img_url_lower = img_url.lower()
            if any(skip in img_url_lower for skip in ['logo', 'icon', 'avatar', 'banner', 'header', 'footer']):
                continue
            
            # Get product name from alt text or nearby text
            alt_text = img.get('alt', '')
            
            # Try to find product name from parent elements
            if not alt_text or alt_text in ['', 'Product image', 'Image']:
                parent = img.find_parent(['div', 'article', 'a', 'li'])
                if parent:
                    # Look for product name in headings or links
                    name_elem = parent.find(['h2', 'h3', 'h4', 'a'], class_=re.compile(r'product|title|name', re.I))
                    if name_elem:
                        alt_text = name_elem.get_text(strip=True)
            
            # Clean up the name
            if alt_text:
                alt_text = alt_text.strip()
                # Remove common prefixes/suffixes
                alt_text = re.sub(r'^Maasai\s+', '', alt_text, flags=re.I)
                alt_text = re.sub(r'\s*-\s*Authentic.*$', '', alt_text)
                alt_text = alt_text[:100]  # Limit length
            
            if alt_text and len(alt_text) > 3:
                seen_images.add(img_url)
                filename = download_image(img_url, alt_text)
                if filename:
                    products.append({
                        'name': alt_text,
                        'image': filename,
                        'url': url
                    })
                    time.sleep(0.5)  # Be respectful with requests
        
        print(f"  Products found on this page: {len(products)}")
        return products
        
    except Exception as e:
        print(f"  Error scraping {url}: {e}")
        return []

if __name__ == "__main__":
    print("Starting Maasai product image scraping...")
    print(f"Images will be saved to: {os.path.abspath(products_dir)}")
    
    all_products = []
    seen_names = set()
    
    for url in urls:
        products = scrape_products_from_url(url)
        
        # Filter out duplicates by name
        for product in products:
            name_key = product['name'].lower().strip()
            if name_key not in seen_names and len(name_key) > 3:
                seen_names.add(name_key)
                all_products.append(product)
        
        time.sleep(1)  # Be respectful between pages
    
    # Save product list
    with open(os.path.join(products_dir, 'products.json'), 'w') as f:
        json.dump(all_products, f, indent=2)
    
    print(f"\n\nScraping complete!")
    print(f"Total unique products: {len(all_products)}")
    print(f"Images saved to: {os.path.abspath(products_dir)}")
