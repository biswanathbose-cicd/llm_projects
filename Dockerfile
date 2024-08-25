# FROM python:3.10-slim
FROM --platform=linux/amd64 python:3.10-slim


WORKDIR /app 

# Upgrade pip to the latest version
RUN python -m pip install --upgrade pip

# Copy requirements from host, to docker container in /app 
COPY requirements.txt .
# Copy everything from ./src directory to /app in the containe
COPY . .
# Set the PYTHONPATH so that src can be found
ENV PYTHONPATH=/app/src
#RUN apt-get update && apt-get install -y build-essential cmake
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install faiss-cpu 


EXPOSE 8000 

# Run the application in the port 8000
CMD ["uvicorn", "--host", "0.0.0.0", "--port", "8000", "src.main:app"]