# Use an official Python runtime as the base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Install PostgreSQL client and other necessary tools
RUN apt-get update && apt-get install -y postgresql-client libpq-dev gcc

# Copy the rest of the application code
COPY . .

# Run the data ingestion script
RUN python ingest_data.py /data/bc_datos.xlsx

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Define environment variable for PostgreSQL connection
ENV DATABASE_URL=postgresql://user:password@db/dbname

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]