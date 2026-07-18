# Stage 1: Build the React application
FROM node:22-alpine AS builder

WORKDIR /app

# Copy package and lock files
COPY package.json package-lock.json ./

# Install dependencies
RUN npm ci

# Copy source code and config files
COPY tsconfig.json vite.config.ts eslint.config.js index.html ./
COPY src ./src

# Build production bundle
RUN npm run build

# Stage 2: Serve the application using Nginx
FROM nginx:alpine AS runner

# Copy static files to nginx default html directory
COPY --from=builder /app/dist /usr/share/nginx/html

# Expose port 80
EXPOSE 80

# Healthcheck
HEALTHCHECK --interval=10s --timeout=5s --start-period=5s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost/ || exit 1

CMD ["nginx", "-g", "daemon off;"]
