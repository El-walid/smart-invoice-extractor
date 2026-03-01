# 1. Start with a lightweight Python Linux image
FROM python:3.11-slim

# 2. Install the necessary Linux system tools for pyodbc and Microsoft drivers
RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    unixodbc-dev \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# 3. Download and install the Microsoft ODBC Driver 18 for Linux
RUN curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor -o /usr/share/keyrings/microsoft-prod.gpg \
    && curl https://packages.microsoft.com/config/debian/12/prod.list > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql18 \
    && rm -rf /var/lib/apt/lists/*

# 4. Set up the working directory inside the container
WORKDIR /app

# 5. Copy requirements and install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copy the rest of your application code
COPY . .

# 7. Start the FastAPI server
CMD ["uvicorn", "extractor:app", "--host", "0.0.0.0", "--port", "8000"]