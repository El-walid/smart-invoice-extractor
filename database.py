from sqlalchemy import create_engine, Float, String, Column, Date, Integer, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

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
    client_id = Column(Integer, ForeignKey("Clients.id"), nullable=False)

    client = relationship("Client")

    invoice_number = Column(String(100), unique=True,nullable=False)
    date = Column(Date, nullable=False)
    total_ttc = Column(Float, default=0.0)

class Invoice_Item(Base):
    __tablename__ = "Invoice_Items"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    invoice_id = Column(Integer, ForeignKey("Invoices.id"), nullable=False)
    invoice = relationship("Invoice")

    product_id = Column(Integer, ForeignKey("Products.id"), nullable=False)
    product = relationship("Product")
    quantity = Column(Integer, default=0)




from sqlalchemy.orm import sessionmaker

# 1. Add your actual Azure connection string here
DATABASE_URL = "mssql+pyodbc://YOUR_USERNAME:YOUR_PASSWORD@YOUR_SERVER_NAME.database.windows.net/invoice-db?driver=ODBC+Driver+18+for+SQL+Server"

engine = create_engine(DATABASE_URL)

# 2. Tell the construction crew to build the tables in Azure
Base.metadata.create_all(engine)

# 3. Create the session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)