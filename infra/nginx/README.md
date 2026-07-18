# Nginx Proxy and Server Configuration

This folder stores configuration files for the Nginx web server/reverse proxy.

## Contents
- `nginx.conf`: Directives establishing proxy buffers, connection timeouts, CORS allowance, compression, and routing maps.
- `/conf.d/`: Subdirectory for custom virtual host config files.

## Routing Rule
- `/api/` traffic must be forwarded directly to the upstream FastAPI server on port `8000`.
- All other requests should serve the pre-built, optimized React index file to support client-side Single Page Application (SPA) routing seamlessly.
