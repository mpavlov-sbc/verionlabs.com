# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    # For psycopg2
    libpq-dev \
    # For build tools
    gcc \
    # For Pillow (image processing)
    libjpeg-dev zlib1g-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project code
COPY . /app/

# Collect static files
RUN python manage.py collectstatic --noinput --settings=verionlabs_django.settings

# Expose port 8000
EXPOSE 8000

# Run gunicorn
CMD exec gunicorn --bind :8000 --workers 2 --threads 4 --worker-class gthread verionlabs_django.wsgi:application