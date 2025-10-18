# 🛒 E-Commerce Product Review ETL Pipeline  

End-to-end data engineering pipeline that extracts e-commerce product reviews via web scraping, stages data in MongoDB (NoSQL), cleans and transforms it using Python (Pandas, NLTK), and loads analytics-ready datasets into MySQL (RDBMS).  
Demonstrates ETL design, schema normalization, and data quality validation.  

---

## 📊 Data Flow Overview  

**E-Commerce Website → MongoDB (Raw) → Python ETL → MySQL (Processed)**  

![Pipeline Diagram](flipkart_pipeline_diagram.png)

---

## ⚙️ Tech Stack  

- **Python** — data extraction, cleaning, and transformation  
- **BeautifulSoup4** — HTML parsing for review extraction  
- **MongoDB** — raw/staging layer (NoSQL)  
- **Pandas & NLTK** — preprocessing, tokenization, and stopword removal  
- **MySQL** — analytical data storage  
- **SQLAlchemy** — database connection for structured loading  

---

## 📂 Project Structure  

ecommerce-product-review-pipeline/
│
├── flipkart_pipeline.py         # Main ETL pipeline script  
├── flipkart_pipeline_diagram.png # Data flow visualization  
├── README.md                    # Documentation  
└── LICENSE                      # Open source license  

---

## 🚀 Future Enhancements  

- 🧭 Add **Airflow DAGs** for scheduling and dependency management  
- ☁️ Move data storage to **AWS (S3 + Redshift)** for scalability  
- 📈 Build a **sentiment analysis dashboard** using Streamlit or Tableau  

---

## 🧠 Key Learnings  

- Hands-on practice in **ETL design principles**  
- Integration of **NoSQL + RDBMS** systems in one pipeline  
- Real-world data extraction and cleaning challenges  
- Data quality validation and schema mapping  

---

## 🧾 Author  

👤 **Madhav Nanda**  
📍 University of Missouri–Kansas City  
🔗 [GitHub Profile](https://github.com/madhav-nanda) | [LinkedIn](https://linkedin.com/in/madhav-nanda)
