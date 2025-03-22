# Base image
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy only the dependency file first to leverage Docker cache
COPY requirements.txt .

# Install dependencies (make sure python-dotenv and gunicorn are in requirements.txt)
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application files
COPY . .

# Expose the port your app runs on
EXPOSE 7860

# Command to run the application
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:7860", "app:app"]