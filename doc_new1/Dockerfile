# Use a specific, lightweight Python version.
# Explicitly set the platform for compatibility as required.
FROM --platform=linux/amd64 python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
# --no-cache-dir reduces image size
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY process.py .

# Command to run the application
CMD ["python", "process.py"] 
