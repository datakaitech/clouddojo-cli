# scenarios/nginx-broken-config/Dockerfile
FROM ubuntu:22.04

# Install nginx and tools
RUN apt-get update && apt-get install -y \
    nginx \
    curl \
    wget \
    procps \
    systemd \
    vim \
    nano \
    net-tools \
    && rm -rf /var/lib/apt/lists/*

# Create broken nginx configuration
RUN mkdir -p /etc/nginx/sites-available /etc/nginx/sites-enabled

# Create broken main nginx.conf
COPY nginx.conf.broken /etc/nginx/nginx.conf.broken
COPY nginx.conf.broken /etc/nginx/nginx.conf

# Create broken site configuration
COPY default.broken /etc/nginx/sites-available/default.broken
COPY default.broken /etc/nginx/sites-available/default

# Create a working backup for reset functionality
COPY nginx.conf.working /etc/nginx/nginx.conf.working
COPY default.working /etc/nginx/sites-available/default.working

# Create a simple index.html
RUN echo '<h1>SadServers - Nginx Fixed!</h1><p>Congratulations! You successfully fixed the nginx configuration.</p>' > /var/www/html/index.html

# Set incorrect permissions on some config files (part of the challenge)
RUN chmod 600 /etc/nginx/nginx.conf
RUN chown nobody:nogroup /etc/nginx/sites-available/default

# Expose port 80
EXPOSE 80

# Start with bash (nginx intentionally broken)
CMD ["/bin/bash", "-c", "tail -f /dev/null"]