# skincare-data-pipeline
Senior Data Analyst Technical Assessment for Veefyed. A Python-based project to scrape, structure, and enrich skincare product data using BeautifulSoup and the Google Custom Search API.

## 📌 Project Overview
This repository contains the solution for the 2-day technical assessment for the Senior Data Analyst role at Veefyed. The project focuses on building a pipeline to extract, structure, and enrich skincare product data using web scraping and API integration.

### Goals
* **Task 1:** Scrape 20–30 skincare products (Name, Brand, Ingredients, Image, etc.) from a target e-commerce platform and structure the data.
* **Task 2:** Enrich a sample of the dataset using the **Google Custom Search API** to validate brand legitimacy and retrieve additional product context.

## ⚙️ Setup & Installation
1. Prerequisites
Python 3.13+

2. Google Cloud Console Account (for Custom Search API) 

To run the Task 2 enrichment script, you must set up your Google Custom Search Engine (CSE) credentials.

  a. Get an API Key: Google Cloud Console [a link](https://console.cloud.google.com/apis/credentials)

  b. Get a Search Engine ID (CX): Programmable Search Engine [a link](https://programmablesearchengine.google.com/)
  
  c. Install Dependencies
  <pre> Bash pip install pandas requests beautifulsoup4 tqdm </pre>
  
  d. Set Environment Variables:
  <pre>
    powershell
    
    $env:CSE_API_KEY="your_api_key_here"
    $env:CSE_ID="your_cx_id_here"
  </pre>

## 🚀 Usage
**Part 1:**
Run the scraper to extract product data from the source. The script uses BeautifulSoup to parse HTML and collects product details including ingredients and images.
<pre>
  Bash
  python scripts/scraping-main.py
</pre>

**Output:** Generates data/product-data.csv containing ~30 raw product entries.

**Part 2**
Run the enrichment script to validate the data. This script randomly selects products from the Day 1 dataset and queries Google to find the official Brand Page and additional product snippets.
<pre>
  Bash
  python scripts/api-dataset-enrich.py
</pre>

**Output:** Generates data/product-data-enriched.csv with new columns: brand_page and additional_information.

## 🧠 Methodology
### Scraping Strategy
  **Politeness:** Implemented random sleep intervals (2-5 seconds) between requests to respect server load.

  **Error Handling:** Robust try-except blocks handle 404 errors or missing DOM elements gracefully.

  **Two-Phase Extraction:** First collects product URLs from the category page, then visits individual pages for detailed ingredient extraction.

### Enrichment Logic
**Validation:** Uses Google Search to confirm the existence of an "Official Page" for the brand.

**Augmentation:** Fetches snippets from search results to fill in missing descriptions or provide secondary validation for product claims.

## 📝 Disclaimer
This project is for educational and assessment purposes only. All scraped data is used strictly for this technical evaluation.
