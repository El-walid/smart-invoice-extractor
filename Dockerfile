# 1. Start with a lightweight Linux/Python foundation
FROM python:3.12-slim

# 2. Set the working directory inside the container
WORKDIR /app

# 3. Copy your requirements and install them
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copy the rest of your code into the container
COPY . .

# 5. Tell the container how to start the API
CMD ["uvicorn", "extractor:app", "--host", "0.0.0.0", "--port", "8000"]