#!/bin/bash

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# --- Parameters ---
# Project parameters
GIT_REPO_URL="https://github.com/EC97B0EAB79C/kiroshi"
SERVICE_NAME="kiroshi"
PYTHON_SCRIPT="main.py"
PYTHON_SCRIPT_CLEAR="clear.py"
RUN_USER="${SUDO_USER:-$USER}"

# Path
USER_HOME=$(eval echo "~$RUN_USER")
LOCAL_BIN="$USER_HOME/.local/bin"
INSTALL_DIR="$LOCAL_BIN/$SERVICE_NAME"
SERVICE_FILE="/etc/systemd/system/$SERVICE_NAME.service"
WRAPPER_SCRIPT_PATH_START="$INSTALL_DIR/start.sh"

# --- Pre-check ---
# Check if the script is run with sudo privileges
if [ "$EUID" -ne 0 ]; then
  echo -e "${YELLOW}Please run this script with sudo privileges.${NC}"
  echo "Usage: sudo ./setup_service.sh"
  exit 1
fi

# Check if python3 is installed
if ! command -v python3 &> /dev/null; then
  echo -e "${YELLOW}Python 3 is not installed. Please install it and try again.${NC}"
  exit 1
fi

# --- Clone repository ---
if [ -d "$INSTALL_DIR/.git" ]; then
  echo -e "${YELLOW}Removing existing installation...${NC}"
  rm -rf "$INSTALL_DIR"
fi
mkdir -p "$INSTALL_DIR"
git clone "$GIT_REPO_URL" "$INSTALL_DIR"
git config --global --add safe.directory "$INSTALL_DIR"
chown -R "$RUN_USER:$RUN_USER" "$INSTALL_DIR"

# --- Install dependencies ---
pip install -r "$INSTALL_DIR/requirements.txt" --break-system-packages


# --- Create wrapper script ---
cat <<EOF > "$WRAPPER_SCRIPT_PATH_START"
#!/bin/bash
set -e

cd "$INSTALL_DIR" || exit

git checkout main
git pull
pip install -r "$INSTALL_DIR/requirements.txt"

python3 "$INSTALL_DIR/$PYTHON_SCRIPT"
EOF

chmod +x "$WRAPPER_SCRIPT_PATH_START"
chown "$RUN_USER:$RUN_USER" "$WRAPPER_SCRIPT_PATH_START"


# Create the systemd service file
cat <<EOF > "$SERVICE_FILE"
[Unit]
Description=$SERVICE_NAME
After=network.target

[Service]
User=$RUN_USER
Group=$RUN_USER

WorkingDirectory=$INSTALL_DIR
ExecStart=$WRAPPER_SCRIPT_PATH_START
ExecStopPost=python3 "$INSTALL_DIR/$PYTHON_SCRIPT_CLEAR"

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable and start the service
systemctl daemon-reload
systemctl enable "$SERVICE_NAME.service"
systemctl start "$SERVICE_NAME.service"

