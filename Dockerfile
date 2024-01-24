# Use the official Python 3.10 image as the base image
FROM python:3.10

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    gettext \
    && apt-get -y clean \
    && rm -rf /var/lib/apt/lists/

# Create and set the working directory
RUN mkdir /app
WORKDIR /app

# Copy requirements.txt and install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Django project
COPY . /app/

# Expose the port Gunicorn will run on
EXPOSE 8000
EXPOSE 8080

# Set entrypoint.sh as the entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]