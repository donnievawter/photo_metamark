#!/bin/bash

INPUT=${1:-~/Pictures}
OUTPUT=${2:-~/PicturesOut}
shift 2

docker run --rm \
  -v "$INPUT":/input \
  -v "$OUTPUT":/output \
  ghcr.io/donnievawter/metamark:latest \
  /entrypoint.sh --input /input --output /output "$@"

