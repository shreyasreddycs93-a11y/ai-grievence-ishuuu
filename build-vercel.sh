#!/bin/bash
# Builds the three frontends and assembles them into out/ for Vercel.
set -e
for d in Frontend OfficerFrontend Landing; do
  (cd "$d" && npm ci && npm run build)
done
rm -rf out
mkdir -p out/citizen out/officer
cp -r Landing/dist/. out/
cp -r Frontend/dist/. out/citizen/
cp -r OfficerFrontend/dist/. out/officer/
