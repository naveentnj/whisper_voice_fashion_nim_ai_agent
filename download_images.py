"""
VALENTI AI - Fashion Product Image Downloader
Downloads stock images from Unsplash into local /static/images/ folders
and updates products.json to reference local paths.
"""
import os
import json
import time
import requests

PRODUCTS_FILE = os.path.join(os.path.dirname(__file__), "products.json")
IMAGES_DIR = os.path.join(os.path.dirname(__file__), "static", "images")

# Curated high-quality Unsplash photo URLs for each product category
# Each URL is a direct Unsplash image link (free license)
CURATED_IMAGES = {
    "shirt": [
        "https://images.unsplash.com/photo-1596755094514-f87e34085b2c?w=600&auto=format&fit=crop&q=80",
        "https://images.unsplash.com/photo-1598033129183-c4f50c736f10?w=600&auto=format&fit=crop&q=80",
        "https://images.unsplash.com/photo-1576995853123-5a10305d93c0?w=600&auto=format&fit=crop&q=80",
        "https://images.unsplash.com/photo-1603252109303-2751441dd157?w=600&auto=format&fit=crop&q=80",
        "https://images.unsplash.com/photo-1602810318383-e386cc2a3ccf?w=600&auto=format&fit=crop&q=80",
    ],
    "watch": [
        "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=600&auto=format&fit=crop&q=80",
        "https://images.unsplash.com/photo-1579586337278-3befd40fd17a?w=600&auto=format&fit=crop&q=80",
        "https://images.unsplash.com/photo-1547996160-81dfa63595aa?w=600&auto=format&fit=crop&q=80",
        "https://images.unsplash.com/photo-1522312346375-d1a52e2b99b3?w=600&auto=format&fit=crop&q=80",
        "https://images.unsplash.com/photo-1524592094714-0f0654e20314?w=600&auto=format&fit=crop&q=80",
    ],
    "pant": [
        "https://images.unsplash.com/photo-1542272604-787c3835535d?w=600&auto=format&fit=crop&q=80",
        "https://images.unsplash.com/photo-1541099649105-f69ad21f3246?w=600&auto=format&fit=crop&q=80",
        "https://images.unsplash.com/photo-1624378439575-d8705ad7ae80?w=600&auto=format&fit=crop&q=80",
        "https://images.unsplash.com/photo-1594633312681-425c7b97ccd1?w=600&auto=format&fit=crop&q=80",
        "https://images.unsplash.com/photo-1473966968600-fa801b869a1a?w=600&auto=format&fit=crop&q=80",
    ],
    "shoes": [
        "https://images.unsplash.com/photo-1549298916-b41d501d3772?w=600&auto=format&fit=crop&q=80",
        "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=600&auto=format&fit=crop&q=80",
        "https://images.unsplash.com/photo-1608256246200-53e635b5b65f?w=600&auto=format&fit=crop&q=80",
        "https://images.unsplash.com/photo-1520639888713-7851133b1ed0?w=600&auto=format&fit=crop&q=80",
        "https://images.unsplash.com/photo-1460353581641-37baddab0fa2?w=600&auto=format&fit=crop&q=80",
    ],
    "jacket": [
        "https://images.unsplash.com/photo-1551028719-00167b16eac5?w=600&auto=format&fit=crop&q=80",
        "https://images.unsplash.com/photo-1544923246-77307dd654cb?w=600&auto=format&fit=crop&q=80",
        "https://images.unsplash.com/photo-1591047139829-d91aecb6caea?w=600&auto=format&fit=crop&q=80",
        "https://images.unsplash.com/photo-1611312449412-6cefac5dc3e4?w=600&auto=format&fit=crop&q=80",
        "https://images.unsplash.com/photo-1548883354-7622d03aca27?w=600&auto=format&fit=crop&q=80",
    ],
    "bag": [
        "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=600&auto=format&fit=crop&q=80",
        "https://images.unsplash.com/photo-1548036328-c9fa89d128fa?w=600&auto=format&fit=crop&q=80",
        "https://images.unsplash.com/photo-1584917865442-de89df76afd3?w=600&auto=format&fit=crop&q=80",
        "https://images.unsplash.com/photo-1622560480605-d83c853bc5c3?w=600&auto=format&fit=crop&q=80",
        "https://images.unsplash.com/photo-1590874103328-eac38a683ce7?w=600&auto=format&fit=crop&q=80",
    ],
    "hat": [
        "https://images.unsplash.com/photo-1514327605112-b887c0e61c0a?w=600&auto=format&fit=crop&q=80",
        "https://images.unsplash.com/photo-1588850561407-ed78c282e89b?w=600&auto=format&fit=crop&q=80",
        "https://images.unsplash.com/photo-1576871337622-98d48d4aa53e?w=600&auto=format&fit=crop&q=80",
        "https://images.unsplash.com/photo-1533461502717-83546291a5e4?w=600&auto=format&fit=crop&q=80",
        "https://images.unsplash.com/photo-1521572267360-ee0c2909d518?w=600&auto=format&fit=crop&q=80",
    ],
    "sunglasses": [
        "https://images.unsplash.com/photo-1511499767150-a48a237f0083?w=600&auto=format&fit=crop&q=80",
        "https://images.unsplash.com/photo-1572635196237-14b3f281503f?w=600&auto=format&fit=crop&q=80",
        "https://images.unsplash.com/photo-1577803645773-f96470509666?w=600&auto=format&fit=crop&q=80",
        "https://images.unsplash.com/photo-1602525963773-55a90f3efb29?w=600&auto=format&fit=crop&q=80",
        "https://images.unsplash.com/photo-1473496169904-658ba7c44d8a?w=600&auto=format&fit=crop&q=80",
    ],
    "belt": [
        "https://images.unsplash.com/photo-1624222247344-550fb8ec5519?w=600&auto=format&fit=crop&q=80",
        "https://images.unsplash.com/photo-1617137968427-85924c800a22?w=600&auto=format&fit=crop&q=80",
        "https://images.unsplash.com/photo-1585856331427-1cba517f52ea?w=600&auto=format&fit=crop&q=80",
        "https://images.unsplash.com/photo-1560243563-062bfc001d68?w=600&auto=format&fit=crop&q=80",
        "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=600&auto=format&fit=crop&q=80",
    ],
    "socks": [
        "https://images.unsplash.com/photo-1582966772680-860e372bb558?w=600&auto=format&fit=crop&q=80",
        "https://images.unsplash.com/photo-1586350977771-b3b0abd50c82?w=600&auto=format&fit=crop&q=80",
        "https://images.unsplash.com/photo-1631541909061-71e349d1f203?w=600&auto=format&fit=crop&q=80",
        "https://images.unsplash.com/photo-1556306535-0f09a537f0a3?w=600&auto=format&fit=crop&q=80",
        "https://images.unsplash.com/photo-1489987707025-afc232f7ea0f?w=600&auto=format&fit=crop&q=80",
    ],
}

def download_image(url: str, save_path: str) -> bool:
    """Download a single image from URL to local path."""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        resp = requests.get(url, headers=headers, timeout=15, stream=True)
        if resp.status_code == 200:
            with open(save_path, "wb") as f:
                for chunk in resp.iter_content(8192):
                    f.write(chunk)
            size_kb = os.path.getsize(save_path) / 1024
            print(f"  OK  {os.path.basename(save_path)} ({size_kb:.0f} KB)")
            return True
        else:
            print(f"  FAIL HTTP {resp.status_code} -> {os.path.basename(save_path)}")
            return False
    except Exception as e:
        print(f"  FAIL {os.path.basename(save_path)}: {e}")
        return False

def main():
    print("=" * 60)
    print("VALENTI AI - Fashion Stock Image Downloader")
    print("Source: Unsplash (Free License)")
    print("=" * 60)

    # Load products
    with open(PRODUCTS_FILE, "r") as f:
        products = json.load(f)

    total = 0
    success = 0

    # Download images for each category
    for category, urls in CURATED_IMAGES.items():
        cat_dir = os.path.join(IMAGES_DIR, category)
        os.makedirs(cat_dir, exist_ok=True)

        print(f"\n[{category.upper()}] Downloading {len(urls)} images...")

        # Find matching products for this category
        cat_products = [p for p in products if p["category"] == category]

        for i, url in enumerate(urls):
            total += 1
            if i < len(cat_products):
                product_id = cat_products[i]["id"]
            else:
                product_id = f"{category}_{i+1}"

            filename = f"{product_id}.jpg"
            save_path = os.path.join(cat_dir, filename)

            # Skip if already downloaded
            if os.path.exists(save_path) and os.path.getsize(save_path) > 1000:
                print(f"  SKIP {filename} (already exists)")
                success += 1
                # Update product image path
                for p in products:
                    if p["id"] == product_id:
                        p["image"] = f"/static/images/{category}/{filename}"
                continue

            if download_image(url, save_path):
                success += 1
                # Update product image path to local
                for p in products:
                    if p["id"] == product_id:
                        p["image"] = f"/static/images/{category}/{filename}"
            
            time.sleep(0.3)  # Be polite to Unsplash servers

    # Save updated products.json with local image paths
    with open(PRODUCTS_FILE, "w") as f:
        json.dump(products, f, indent=2)
    print(f"\nUpdated products.json with local image paths.")

    print(f"\n{'=' * 60}")
    print(f"Download complete: {success}/{total} images saved")
    print(f"Images folder: {IMAGES_DIR}")
    print(f"{'=' * 60}")

if __name__ == "__main__":
    main()
