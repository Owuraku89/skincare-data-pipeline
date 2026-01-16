import os
import requests
import pandas as pd
import random
import time
import sys

from bs4 import BeautifulSoup
from tqdm import tqdm

# configuration variables
base_url = "https://qudobeauty.com/"
cat_url = base_url + "cat/wholesale-face-care/"
header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}
num_obs = 30


# Helper function: Search for ingredients
def scrape_sub_link(url):
    try:
        res = requests.get(url, timeout=10, headers=header)
        soup = BeautifulSoup(res.text, "html.parser")
    except requests.exceptions.RequestException as e:
        print(f"   --> Error on sub-link: {e}")
        return "Error" 
        
    # extract ingredients list    
    ingredients = []
    search_sec = soup.find("strong", string="Product contains:")
    if search_sec:
        for sib in search_sec.find_all_next("strong"):
            text = sib.text.strip()
            if text.startswith("Product effects:"):
                break
            ingredients.append(text)
        ingredients = ", ".join(ingredients)
    else:
        ingredients = None
        
    return ingredients
    
def scrap_product_links():
    # establish request 
    try:
        response = requests.get(cat_url, timeout=15)
        print(f"Status OK (Code: {response.status_code})")
    except requests.exceptions.RequestException as e: 
        print(f"Error Fetching page: {e}")
        return []
           
    soup = BeautifulSoup(response.text, "html.parser")
    # main search tags
    product_tags = soup.select("li.product")
    # add fallback
    if not product_tags:
        product_tags = soup.select("div.woocommerce-image__wrapper")
    
    print(f"\nPhase 1: Found {len(product_tags)} potential products.")
    # seed and shuffle 
    random.seed(42)
    random.shuffle(product_tags)
    data = []
    # extract prodeucts gnerator 
    for i, tag in tqdm(enumerate(product_tags[:num_obs])):
        try:
            # get product details 'locally'    
            products = tag.select("div.woocommerce-image__wrapper")
            if not products:
                print("\nproduct details not found")
                print(tag.prettify()[:300])
                continue
                
            for product in products:
                # link extraction
                link_tag = product.find("a") 
                if not link_tag: continue
                product_url = link_tag.get("href") if link_tag else "N/A"

                # image url
                img_tag = product.find("img")
                product_img = img_tag.get("src") if img_tag else "N/A"

                # product text
                text = img_tag.get("alt")   
                if "-" in text and "," in text:
                    print("normal split")
                    brand, product_name = text.split(" - ", 1)
                    product_name, size = product_name.rsplit(", ", 1)
                else:
                    print("non standard")
                    brand, product_name = text.split(" - ", 1)
                    product_name, size = product_name.rsplit(" ", 1)
                   
                
                print(f"\nextracting {i} {product_name}....")
                
                # get 'category' 
                cat_tag = soup.find("h1", "woocommerce-products-header__title page-title")
                category = cat_tag.text.strip() if cat_tag else None
        
                # get 'ingredients' sub page
                ingredients = scrape_sub_link(product_url)
                # insert data
                data.append(
                    {
                        "product_name": product_name,
                        "brand": brand,
                        "ingredients": ingredients,
                        "size": size,
                        "ingredients": ingredients,
                        "category": category,
                        "product_url": product_url,
                        "product_img": product_img
                    }
                )
        # error flag
        except Exception as e:
            print(f"Skipping product due to error: {e}")
            continue
            
         # Polite policy
        time.sleep(random.uniform(3, 5))
        
    return data

def main():
    print(f"\n-----Staring Products scrapping from {base_url}----")
    
    # get products from links
    scraped_data = scrap_product_links()

    if not scraped_data:
        print("***\nFAILED: no data collected***")
        sys.exit("Critical failure: No data collected")
        return 

    print(f"\nPhase 1 Complete. Collected {len(scraped_data)} products.")
    # convert to 'DataFrame'
    df = pd.DataFrame(scraped_data)
    print("shape of dataframe: ", df.shape)
    
    # write to location
    try:
        output_path = os.path.join("data", "product-data.csv")
        df.to_csv(output_path, mode="wb", index=False)
        print(f"✅ Success! Data saved to: {output_path}")
        print(f"Columns: {list(df.columns)}")
    except FileExistsError as e:
        print("File already exists!")

if __name__ == "__main__":
    main()