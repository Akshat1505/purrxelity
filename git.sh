#!/bin/bash

read -r -p "Enter the commit message _> " commit 

if [ -z "${commit}" ]; then 
  echo "No commit message passed"
  exit 1
fi

echo "Git Branch _> $(git branch)"
# read -r -p "Which branch to push ? " branch

git add . 
git status
git commit -m "${commit}"
git push 
