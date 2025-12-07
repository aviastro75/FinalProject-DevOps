FROM ubuntu:22.04

# Install dependencies
RUN apt-get update && apt-get install -y \
    apache2 \
    python3 \
    python3-pip \
    libapache2-mod-wsgi-py3 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /tmp/
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt

# Enable Apache WSGI module
RUN a2enmod wsgi

# Copy Apache configuration
COPY apache.conf /etc/apache2/sites-available/000-default.conf

# Copy application files
COPY . /var/www/flask_app

WORKDIR /var/www/flask_app

# Create data directory for NFS mount and ensure proper permissions
RUN mkdir -p /var/www/flask_app/data \
    && mkdir -p /var/www/flask_app/templates \
    && chown -R www-data:www-data /var/www/flask_app \
    && chmod -R 755 /var/www/flask_app

# Set environment variable for data directory
ENV DATA_DIR=/var/www/flask_app/data

# Expose port 80
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost/health || exit 1

CMD ["apache2ctl", "-D", "FOREGROUND"]

