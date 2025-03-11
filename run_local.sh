#!/bin/bash
# Build the Docker image and tag it "my-app"
docker build --no-cache -t my-app .

# Run the container locally:
# - The -p flag maps port 5000 on your host to port 5000 in the container.
# - The -e flag sets the PORT environment variable (adjust if needed)
docker run --rm -e PORT=5000 -p 5000:5000 my-app
#!/bin/bash
# Build the Docker image and tag it "my-app"
docker build --no-cache -t my-app .

# Run the container locally:
# - The -p flag maps port 5000 on your host to port 5000 in the container.
# - The -e flag sets the PORT environment variable (adjust if needed)
docker run --rm -e PORT=5000 -p 5000:5000 my-app
