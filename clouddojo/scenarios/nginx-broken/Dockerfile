# filepath: ./sadservers/scenarios/nginx-broken-symlink/Dockerfile
FROM nginx:alpine

# Create sites-available and sites-enabled like on Debian-based distros
RUN mkdir -p /etc/nginx/sites-available /etc/nginx/sites-enabled

# Copy both configs
COPY default.broken /etc/nginx/sites-available/default.broken
COPY default.working /etc/nginx/sites-available/default.working

# Copy the HTML page into the default web root
COPY index.html /usr/share/nginx/html/index.html

# Simulate a broken symlink (points to a non-existent file initially)
RUN ln -s /etc/nginx/sites-available/nonexistent /etc/nginx/sites-enabled/default

# Run nginx in foreground
CMD ["nginx", "-g", "daemon off;"]