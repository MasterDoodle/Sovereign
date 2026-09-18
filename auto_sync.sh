#!/bin/bash
cd ~/structor-engine

# Verify Python syntax before committing
python3 -m py_compile run_local.py interface.py bridge_node.py 2>/dev/null
if [ $? -ne 0 ]; then
  echo "Syntax check failed. Aborting commit."
  exit 1
fi

if [[ -n $(git status -s) ]]; then
  git add .
  git commit -m "Auto-sync: $(date '+%Y-%m-%d %H:%M:%S')"
  git push origin main
fi
