#!/bin/bash
mkdir -p /tmp/foodlog/css
rm /tmp/foodlog/*.html
mkdir -p /tmp/thumbs
cp -t /tmp/foodlog/css ../../css/*.css 
cp -t /tmp/thumbs *.jpg
for filename in ./*.py; do
    echo "$filename"
    python3 "$filename" > /tmp/foodlog/$(basename "$filename" .py).html
done

