#!/bin/bash
cd ~/structor-engine
if [[ -n $(git status -s) ]]; then
  git add .
  git commit -m "Auto-sync: $(date '+%Y-%m-%d %H:%M:%S')"
  git push origin main
fi
