# 🧩 E-Commerce Product Review Data Pipeline (iPhone 16 Pro Case Study)

An end-to-end **Data Engineering pipeline** that automates the extraction of product reviews from an e-commerce website, stages data in **MongoDB (NoSQL)**, performs **data transformation and text preprocessing** using **Python (Pandas, NLTK)**, and loads analytics-ready datasets into **MySQL (RDBMS)**.  

This project demonstrates **ETL architecture**, **schema normalization**, and **data quality validation**, forming a foundational example of a real-world data engineering workflow.

---

## 🧠 Key Highlights

- 🔹 Web Scraping with `requests` and `BeautifulSoup`
- 🔹 Data Staging in **MongoDB**
- 🔹 Text Cleaning & NLP Preprocessing using **NLTK**
- 🔹 Data Transformation using **Pandas**
- 🔹 Data Load into **MySQL** via **SQLAlchemy**
- 🔹 Implements **ETL pipeline structure** (Extract → Transform → Load)

---

## 🛠️ Tech Stack

| Layer | Technology Used |
|-------|------------------|
| **Data Extraction** | Python, Requests, BeautifulSoup |
| **Data Staging** | MongoDB (NoSQL) |
| **Data Transformation** | Pandas, NLTK |
| **Data Storage** | MySQL (RDBMS) |
| **Orchestration (Future Scope)** | Apache Airflow |
| **Visualization (Future Scope)** | Power BI / Streamlit |

---

## 📊 Data Flow Overview

**E-Commerce Website → MongoDB (Raw) → Python ETL → MySQL (Processed)**  

```mermaid
flowchart LR
A[E-Commerce Reviews] --> B[MongoDB (Raw Layer)]
B --> C[Python Transformations]
C --> D[MySQL (Analytics Layer)]

Added Future Enhancements section to README

## 🚀 Future Enhancements

- 🧾 Add **Airflow** DAGs for scheduling and dependency management  
- ☁️ Move data storage to **AWS** (S3 for raw, Redshift for warehouse)  
- 📈 Build a sentiment analysis **dashboard** using Streamlit or Tableau  

