#!/bin/sh
# Docker entrypoint script for frontend
# Replaces environment variables in the built JavaScript files

# Replace placeholder with actual API URL if provided
if [ -n "$VITE_API_URL" ]; then
    # Find and replace in all JS files
    find /usr/share/nginx/html -type f -name "*.js" -exec sed -i "s|VITE_API_URL_PLACEHOLDER|${VITE_API_URL}|g" {} \;
fi

# Execute the main command (nginx)
exec "$@"
