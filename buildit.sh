#!/bin/bash
docker buildx create --use
docker buildx build --platform linux/amd64,linux/arm64 \
  -t metamark:latest -f docker/Dockerfile.slim  \
  --output "type=oci,dest=metamark-linux.tar" \
  --output "type=oci,dest=metamark-mac.tar" \
  .


