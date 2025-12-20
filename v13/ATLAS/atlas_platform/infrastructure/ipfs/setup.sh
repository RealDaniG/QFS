#!/bin/bash

# ATLAS IPFS Setup Script
# This script initializes and configures the IPFS node for ATLAS

set -e

echo "🚀 Setting up ATLAS IPFS infrastructure..."

# Create necessary directories
mkdir -p data/ipfs data/ipfs-cluster config/ipfs

# Generate cluster secret if not exists
if [ ! -f .env ]; then
  echo "Generating IPFS cluster secret..."
  CLUSTER_SECRET=$(od -vN 32 -An -tx1 /dev/urandom | tr -d ' \n')
  echo "CLUSTER_SECRET=$CLUSTER_SECRET" > .env
  echo "✅ Cluster secret generated and saved to .env"
fi

# Start IPFS services
echo "Starting IPFS services..."
docker-compose up -d

# Wait for IPFS to be ready
echo "Waiting for IPFS to initialize..."
sleep 10

# Configure IPFS
echo "Configuring IPFS node..."

# Enable experimental features
docker exec atlas-ipfs ipfs config --json Experimental.FilestoreEnabled true
docker exec atlas-ipfs ipfs config --json Experimental.UrlstoreEnabled true
docker exec atlas-ipfs ipfs config --json Experimental.Libp2pStreamMounting true

# Configure Gateway
docker exec atlas-ipfs ipfs config --json Gateway.HTTPHeaders.Access-Control-Allow-Origin '["*"]'
docker exec atlas-ipfs ipfs config --json Gateway.HTTPHeaders.Access-Control-Allow-Methods '["GET", "POST", "PUT"]'

# Set storage limits (adjust as needed)
docker exec atlas-ipfs ipfs config Datastore.StorageMax 100GB

# Enable garbage collection
docker exec atlas-ipfs ipfs config --json Datastore.GCPeriod '"24h"'

# Restart to apply settings
docker-compose restart ipfs

echo "✅ IPFS setup complete!"
echo ""
echo "IPFS endpoints:"
echo "  - API: http://localhost:5001"
echo "  - Gateway: http://localhost:8080"
echo "  - Cluster API: http://localhost:9094"
echo ""
echo "Test with: curl http://localhost:5001/api/v0/id"
