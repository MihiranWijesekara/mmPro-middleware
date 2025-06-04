# Use Python 3.12-slim as the base image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy the requirements file
COPY requirements.txt /app/

# Upgrade pip and install dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt --verbose

# Copy the rest of the application code
COPY . /app/

# Expose Flask port
EXPOSE 5000

# Command to run the application
CMD ["python", "app.py"]
