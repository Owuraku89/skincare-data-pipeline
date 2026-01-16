import sys
import os
import requests
import random
import pandas as pd

from tqdm import tqdm

# configuration 
BASE_URL = "https://www.googleapis.com/customsearch/v1"
CX_ID = os.getenv("CSE_ID")
API_KEY = os.getenv("CSE_API_KEY")
HEADER = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def google_search(query):
    """
    send request to API for JSON response
    
      Parameters
    ----------
    path : str
        search query. 

     Returns
    -------
    request.json
        response metadata from the google CS JSON API
    """
    try:
        url = BASE_URL
        params = {"key": API_KEY, "cx": CX_ID, "q": query}
        response = requests.get(url, params=params, headers=HEADER)
        print(f"status OK (Code: {response.status_code})")
        return response.json()
        
    except requests.exceptions.RequestException as e:
        print(f"request failed: {e}")
        return False

def enrich_data(path):
    """
    Enrich scraped product data with external information via Google Custom Search API.

    Parameters
    ----------
    path : str
        Path to the CSV file containing the Day 1 scraped dataset. 
        Expected columns: 'product_name', 'brand', 'size', 'category', 'product_url', 'product_img', 'ingredients'.

    Process
    -------
    1. Reads the dataset into a pandas DataFrame.
    2. Adds enrichment columns: 'brand_page' and 'additional_information'.
    3. Randomly selects between 10 and 15 products (unique indices).
    4. For each selected product:
        - Performs a Google CSE query to retrieve the official brand/manufacturer page.
        - Performs a second query to retrieve third-party information (e.g., ingredients list, extra description).
    5. Updates the DataFrame with enrichment results.

    Returns
    -------
    pandas.DataFrame
        The enriched dataset with additional columns populated for the sampled products.

    Notes
    -----
    - API key and CSE ID must be set as environment variables (CSE_API_KEY, CSE_ID).
    - Randomness ensures uniqueness of enriched products; optional seeding can be added for reproducibility.
    - Results may vary depending on Google CSE configuration and query refinement.
    """
    try:
        # read csv to DataFrame
        df = pd.read_csv(path)
    except os.path.exceptions.FileExistsError as e:
        print(f"no {path} exists: Run scraping script first")
        return 

    # additional cols 
    new_cols = ["brand_page", "additional_information"]
    for col in new_cols:
        df[col] = None
        
    # enrich data by random selection
    random.seed(42)
    num_obs = random.randrange(10, 14)
    indices = random.sample(range(len(df)), num_obs)
    counter = 0
    
    for i in tqdm(indices):
        # search via CSE
        brand = df.loc[i, "brand"]
        product_name = df.loc[i, "product_name"]

        # first search 'brand official site'
        res = google_search(f"{brand} official page")
        if "items" in res.keys():
            link = res["items"][0]["link"]
            df.loc[i, "brand_page"] = link
            print(f"{brand}, site added")
        else:
            print(f"\nNO link found for {brand}")
            
        # second search "additional information"
        res2 = google_search(product_name)
        if "items" in res2.keys():
            snippet = res2["items"][0]["snippet"]
            df.loc[i, "additional_information"] = snippet
            print(f"additional info added for product_ID: {i}")
        else:
            print(f"no additional info found for product_ID: {i}")
            
        counter += 1
        
    print(f"\nSuccessfully enrcihed dataset for {counter} products")
    print(f"\nColumns added: {new_cols[:]}")
    
    return df

def main():
    try:
        df_original = pd.read_csv("data/product-data.csv")
    except FileExistsError as e:
        print("\nrun scrapping script first")
    
    # read data
    df_enriched = enrich_data("data/product-data.csv")
    if (len(df_original.columns.tolist())) == (len(df_enriched.columns.tolist())):   
        sys.exit("Failure: no additions ware done")
        return 
    # write to location
    try:
        output_path = os.path.join("data", "product-data-enriched.csv")
        df_enriched.to_csv(output_path, mood="xb", index=False)
        print(f"\n✅ Success! Data saved to: {output_path}")
    except FileExistsError as e:
        print("File already exists!")

if __name__ == "__main__":
    main()