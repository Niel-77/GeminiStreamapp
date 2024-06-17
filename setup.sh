#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Update package lists
sudo apt-get update

# Install FEniCS without recommended packages
sudo apt-get install --no-install-recommends -y fenics

# post_setup.sh
curl -s http://fenicsproject.org/fenics-install.sh | bash


# Verify FEniCS installation
fenics-version
