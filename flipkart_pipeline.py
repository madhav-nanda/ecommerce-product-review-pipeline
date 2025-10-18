"""
E-Commerce Product Review ETL Pipeline
-------------------------------------
Extracts product reviews (case study: iPhone 16 Pro) from an e-commerce site,
stages raw data in MongoDB, transforms and cleans text using Python (Pandas, NLTK),
and loads the analytics-ready dataset into MySQL.
"""

# ---------- IMPORTS ----------
import requests
from bs4 import BeautifulSoup as bs
import csv
import time
from pymongo import MongoClient
import os
import pandas as pd
import pymongo
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from datetime import datetime
from sqlalchemy import create_engine

# Download NLTK resources (run once)
nltk.download('stopwords')
nltk.download('punkt')

# ---------- EXTRACT ----------
# Define base product-review URL
base_review_url = (
    "https://www.flipkart.com/apple-iphone-16-pro-desert-titanium-128-gb/"
    "product-reviews/itm5a8453e89cbd4?pid=MOBH4DQFSDYNVH5U&lid=LSTMOBH4DQFSDYNVH5UFZYHLF"
    "&marketplace=FLIPKART&page=3"
)

# Request first page and parse HTML
response = requests.get(base_review_url)
response.encoding = "utf-8"
soup = bs(response.text, "html.parser")

# Find total number of review pages
try:
    total_pages_tag = soup.find("div", {"class": "_1G0WLw mpIySA"}).find("span")
    total_pages = int(total_pages_tag.get_text(strip=True).split()[-1]) if total_pages_tag else 1
except Exception as e:
    print(f"Error extracting total pages: {e}")
    total_pages = 1

all_reviews = []

# Loop through each page and collect reviews
for page in range(1, total_pages + 1):
    print(f"Fetching page {page}/{total_pages}...")
    page_url = f"{base_review_url}&page={page}"

    try:
        page_response = requests.get(page_url)
        page_response.encoding = 'utf-8'
        page_soup = bs(page_response.text, "html.parser")
        review_boxes = page_soup.find_all('div', {'class': 'col EPCmJX Ma1fCG'})

        # Extract review fields from each box
        for box in review_boxes:
            try:
                rating = box.find('div', {'class': 'XQDdHH Ga3i8K'})
                title = box.find('p', {'class': 'z9E0IG'})
                review_text = box.find('div', {'class': 'ZmyHeo'})
                reviewer_name = box.find('p', {'class': '_2NsDsF AwS1CA'})
                location = box.find('p', {'class': 'MztJPv'})
                date_tags = box.find_all('p', {'class': '_2NsDsF'})
                date = date_tags[-1] if date_tags else None

                all_reviews.append({
                    "rating": rating.get_text(strip=True) if rating else "N/A",
                    "title": title.get_text(strip=True) if title else "N/A",
                    "review_text": review_text.get_text(strip=True) if review_text else "N/A",
                    "reviewer_name": reviewer_name.get_text(strip=True) if reviewer_name else "N/A",
                    "location": location.get_text(strip=True) if location else "N/A",
                    "date": date.get_text(strip=True) if date else "N/A"
                })
            except Exception as e:
                print(f"Error parsing review: {e}")

        time.sleep(1)  # polite delay to avoid server overload

    except Exception as e:
        print(f"Error fetching page {page}: {e}")

# ---------- SAVE TO CSV ----------
# Save all raw reviews locally for backup / validation
with open("flipkart_finalreviews.csv", mode="w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(file, fieldnames=["rating", "title", "review_text", "reviewer_name", "location", "date"])
    writer.writeheader()
    writer.writerows(all_reviews)

print("Saved to flipkart_finalreviews.csv")

# ---------- LOAD TO MONGODB ----------
# Stage raw data into MongoDB (acts as a NoSQL landing zone)
try:
    client = MongoClient("mongodb://localhost:27017/")
    db = client["flipkart"]
    collection = db["flipkart_finalreview"]
    if all_reviews:
        collection.insert_many(all_reviews)
    print(f"Inserted {len(all_reviews)} reviews into MongoDB.")
except Exception as e:
    print(f"Error uploading to MongoDB: {e}")

# ---------- TRANSFORM ----------
# Load staged data from MongoDB into Pandas for cleaning
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["flipkart"]
collection = db["flipkart_finalreview"]
data = list(collection.find())
df = pd.DataFrame(data)

# --- Text preprocessing ---
def preprocess_review(text):
    """Clean and normalize review text."""
    if pd.isna(text):
        return text
    text = str(text).lower()
    text = re.sub(r"\s*(read\s*more)[^\w]*$", "", text, flags=re.IGNORECASE)
    text = re.sub(r"[^\w\s]", "", text)
    tokens = word_tokenize(text)
    stop_words = set(stopwords.words("english"))
    tokens = [word for word in tokens if word not in stop_words]
    return " ".join(tokens)

df["processed_review"] = df["review_text"].apply(preprocess_review)
df.to_csv("processed_review1.csv", index=False)

# --- Location split ---
def split_location(location_str):
    """Split 'Certified Buyer, City' into separate fields."""
    if pd.isna(location_str):
        return pd.Series([pd.NA, pd.NA])
    parts = [p.strip() for p in str(location_str).split(",")]
    if len(parts) >= 2:
        return pd.Series([parts[0], parts[1].lower()])
    return pd.Series([parts[0], pd.NA])

df[['buyer_status', 'location_clean']] = df['location'].apply(split_location)

# --- Date normalization ---
def process_date(date_val):
    """Convert date string to datetime; replace invalids with current date."""
    try:
        parsed_date = pd.to_datetime(date_val, errors="coerce")
        return datetime.now() if pd.isna(parsed_date) else parsed_date
    except Exception:
        return datetime.now()

df["processed_date"] = df["date"].apply(process_date)

# Drop redundant / raw columns
df.drop(columns=["_id", "review_text", "location", "date"], inplace=True)

# ---------- LOAD TO MYSQL ----------
# Push cleaned, structured data into MySQL for analytics
engine = create_engine(
    "mysql+pymysql://{user}:{pw}@localhost/{db}".format(
        user="user1", pw="user1", db="reviews_db"
    )
)

df.to_sql("flipkart_reviews_transformed", con=engine, if_exists="replace", chunksize=100, index=False)
print("Successfully loaded processed data into MySQL")
