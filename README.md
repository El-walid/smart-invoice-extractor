📑 Smart Invoice Extractor & Data Pipeline
An automated ETL (Extract, Transform, Load) pipeline designed to process complex PDF invoices and sync them with a cloud-based relational database. This project was built to solve manual data entry challenges for businesses in the Sidi Ghanem industrial zone.

🚀 Features
Automated Extraction: Uses pdfplumber and Regex to pull structured data from messy PDF layouts.

Relational Mapping: Implements SQLAlchemy ORM to manage Clients, Products, and Invoices with full referential integrity.

Cloud Ready: Integrated with Microsoft Azure SQL Database for persistent storage.

Containerized: Fully Dockerized with necessary Linux ODBC drivers for easy deployment in any environment.

Secure: Uses environment variables (.env) to protect sensitive cloud credentials.

🛠️ Tech Stack
Language: Python 3.11

API Framework: FastAPI

Database: Azure SQL (MSSQL)

ORM: SQLAlchemy

DevOps: Docker

Library: pdfplumber (PDF parsing), pyodbc (SQL connection)

🏗️ Architecture
The system follows a classic 3-tier architecture:

Entry: FastAPI endpoint receives the PDF as a binary stream in RAM (no disk storage needed).

Process: The "Brain" extracts header data and table items, cleaning strings into integers/floats.

Storage: The "Memory" (SQLAlchemy) performs an Upsert—checking if clients/products exist before creating new records to avoid duplication.

🚦 Getting Started
1. Prerequisites
Docker Desktop installed.

An Azure SQL instance with a configured firewall for your IP.

2. Environment Setup
Create a .env file in the root directory:

Bash
DATABASE_URL=mssql+pyodbc://<user>:<pass>@<server>.database.windows.net:1433/<db>?driver=ODBC+Driver+18+for+SQL+Server
3. Run with Docker
Bash
# Build the image
docker build -t smart-invoice-extractor .

# Run the container
docker run -p 8000:8000 --env-file .env smart-invoice-extractor
📈 Future Roadmap
[ ] Power BI Integration: Connect the Azure SQL database to a live dashboard for financial analytics.

[ ] Streamlit UI: Build a user-friendly drag-and-drop web interface for non-technical staff.

[ ] CI/CD: Automate builds and testing using GitHub Actions.
