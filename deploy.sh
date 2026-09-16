#!/usr/bin/env bash
set -euo pipefail

branch=$(git rev-parse --abbrev-ref HEAD)

if [ "$branch" = "main" ]; then
  echo "On main branch -- deploying to production"
  wrangler deploy
else
  echo "On branch '$branch' -- uploading a preview version (production untouched)"
  wrangler versions upload
fi
