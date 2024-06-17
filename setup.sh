#!/bin/bash

# Add FEniCS repository
sudo add-apt-repository ppa:fenics-packages/fenics -y
sudo apt-get update

# Install FEniCS
sudo apt-get install fenics -y
