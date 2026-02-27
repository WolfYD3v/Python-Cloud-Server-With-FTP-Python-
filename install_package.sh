#!/bin/bash

read -p "Package to install: " package_name

if [ -n "$package_name" ]; then
    echo ""
    echo "$package_name installation begin..."
    echo ""
    uv add $package_name
    uv run $package_name check
    uv lock
    uv sync
else
    echo "No package name inputed, cannot begin installation."
fi
