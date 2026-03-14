from sqlalchemy import create_engine, Float, String, Column, Date, Integer, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
from logger import logger  # <-- NEW IMPORT


# This physically reads the .env file and loads its contents into memory
load_dotenv()
Base = declarative_base()

# We will put the connection string here later!
# engine = create_engine("mssql+pyodbc://user:pass@server/db?driver=ODBC+Driver+18+for+SQL+Server")


class Client(Base):
    __tablename__ = "Clients"

    # The ID column must be set as the primary key
    id = Column(Integer, primary_key=True,autoincrement=True)
    
    company_name = Column(String(100),nullable=False)
    address = Column(String(100), nullable=False)
    ice_number = Column(String(100), unique=True,nullable=False)

class Product(Base):
    __tablename__ = "Products"

    id = Column(Integer, primary_key=True, autoincrement=True)
    description = Column(String(100), nullable=False)
    standard_price = Column(Float, default=0.0)

class Invoice(Base):
    __tablename__ = "Invoices"

    id = Column(Integer, primary_key=True, autoincrement=True)
    # ADDED ONDELETE HERE
    client_id = Column(Integer, ForeignKey("Clients.id", ondelete="CASCADE"), nullable=False)
    client = relationship("Client")
    
    invoice_number = Column(String(100), unique=True, nullable=False)
    date = Column(Date, nullable=False)
    total_ttc = Column(Float, default=0.0)

class Invoice_Item(Base):
    __tablename__ = "Invoice_Items"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    # ADDED ONDELETE HERE
    invoice_id = Column(Integer, ForeignKey("Invoices.id", ondelete="CASCADE"), nullable=False)
    invoice = relationship("Invoice")

    product_id = Column(Integer, ForeignKey("Products.id"), nullable=False)
    product = relationship("Product")
    quantity = Column(Integer, default=0)


# --- CONNECTION TO DATABASE ---

try:
    raw_url = os.getenv("DATABASE_URL")
    if not raw_url:
        logger.error("DATABASE_URL not found in .env file.") # <-- NEW LOG
        raise ValueError("DATABASE_URL is missing.")

    DATABASE_URL = raw_url.strip().strip('"').strip("'")
    
    engine = create_engine(DATABASE_URL)
    logger.info("Successfully connected to Azure SQL Database.") # <-- NEW LOG

    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

except Exception as e:
    logger.critical(f"Failed to connect to Database: {e}") # <-- NEW LOG
    raise e