#!/bin/bash

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Parameters
GIT_REPO_URL="https://github.com/EC97B0EAB79C/kiroshi"
PYTHON_SCRIPT="main.py"
SERVICE_NAME="kiroshi"
RUN_USER="pi"

# Pre-check
if [ "$EUID" -ne 0 ]; then
  echo -e "${YELLOW}Please run this script with sudo privileges.${NC}"
  echo "Usage: sudo ./setup_service.sh"
  exit 1
fi

# Clone repository


# Install dependencies


# Create wrapper script


# Create the systemd service file


# Enable and start the service
