# Use official slim Python 3.10 image
FROM python:3.11

# Set working directory inside the container
WORKDIR /app

# Copy only requirements first for caching Docker layers
COPY requirements.txt /app/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all other project files
COPY . /app

# Expose backend port (9999) and frontend port (8501)
EXPOSE 9999
EXPOSE 8501

# Command to run both backend and frontend concurrently
# Using bash to run both services simultaneously
CMD ["bash", "-c", "uvicorn backend:app --host 0.0.0.0 --port 9999 & streamlit run frontend.py --server.port 8501 --server.address 0.0.0.0"]
