#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Update package lists
sudo apt-get update

# Install FEniCS without recommended packages
sudo apt-get install --no-install-recommends -y fenics

# Verify FEniCS installation
fenics-version
