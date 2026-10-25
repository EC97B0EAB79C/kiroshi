#!/bin/bash
# Install or update Kiroshi on a Raspberry Pi.
#
#   git clone https://github.com/EC97B0EAB79C/kiroshi && sudo kiroshi/install.sh
#
#   sudo ./install.sh                Install. Run again to repair; config is kept.
#   sudo ./install.sh --update       Get the latest code and restart the service.
#   sudo ./install.sh --auto-update  Install, and update one time each week.
#
# Set EPD=<name> to choose the display driver (default: epd7in3e on a Pi, else mock).
# Set EPD_HOST=<address> when an STM32 board drives the display (see README).

set -euo pipefail

SERVICE=kiroshi
APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RUN_USER="${SUDO_USER:-${USER:-root}}"
USER_HOME="$(getent passwd "$RUN_USER" | cut -d: -f6)"
CONFIG_DIR="$USER_HOME/.config/kiroshi"
ENV_FILE=/etc/kiroshi/env
VENV="$APP_DIR/.venv"
PYTHON="$VENV/bin/python"
SYSTEMD=/etc/systemd/system

APT_PACKAGES=(git python3-venv python3-pil python3-requests python3-icalendar
    python3-jsonschema python3-spidev python3-gpiozero python3-lgpio)

info() { echo -e "\033[0;34m==> $*\033[0m"; }
warn() { echo -e "\033[1;33mWARNING: $*\033[0m"; }
as_user() { runuser -u "$RUN_USER" -- "$@"; }

install_packages() {
    info "Installing system packages"
    apt-get update -q
    for package in "${APT_PACKAGES[@]}"; do
        apt-get install -y -q "$package" >/dev/null || warn "Cannot install $package"
    done
}

enable_spi() {
    info "Enabling SPI"
    if command -v raspi-config >/dev/null; then
        raspi-config nonint do_spi 0
    else
        warn "raspi-config not found. Enable SPI yourself."
    fi
    for group in spi gpio; do
        if getent group "$group" >/dev/null; then usermod -aG "$group" "$RUN_USER"; fi
    done
}

setup_venv() {
    info "Installing Python packages in $VENV"
    # System packages (Pillow, GPIO) are ready-built; pip installs only what is missing
    [ -x "$PYTHON" ] || as_user python3 -m venv --system-site-packages "$VENV"
    as_user "$VENV/bin/pip" install -q -r "$APP_DIR/requirements.txt"
}

setup_config() {
    if [ ! -f "$CONFIG_DIR/setting.json" ]; then
        info "Making config in $CONFIG_DIR"
        local epd="${EPD:-mock}"
        { [ -n "${EPD_HOST:-}" ] || grep -qs "Raspberry Pi" /proc/device-tree/model; } && epd="${EPD:-epd7in3e}"
        as_user mkdir -p "$CONFIG_DIR"
        as_user cp "$APP_DIR/example/setting.json" "$APP_DIR/example/panels.json" "$CONFIG_DIR/"
        as_user python3 - "$CONFIG_DIR" "$epd" <<'EOF'
import json, sys
config_dir, epd = sys.argv[1:]
path = f"{config_dir}/setting.json"
settings = json.load(open(path))
settings.update(panel_spec=f"{config_dir}/panels.json", epd=epd)
json.dump(settings, open(path, "w"), indent=2)
EOF
    else
        info "Keeping config in $CONFIG_DIR"
    fi

    if [ ! -f "$ENV_FILE" ]; then
        info "Making $ENV_FILE for API keys"
        mkdir -p "$(dirname "$ENV_FILE")"
        install -m 600 /dev/null "$ENV_FILE"
        cat > "$ENV_FILE" <<'EOF'
# Kiroshi API keys. Only root can read this file.
# Remove "#" and add your key. Then: sudo systemctl restart kiroshi
#GITHUB_TOKEN=
#TOGGL_API_KEY=
# Address of the STM32 board that drives the display (firmware/stm32)
#EPD_HOST=
EOF
    fi

    if [ -n "${EPD_HOST:-}" ]; then
        info "Using the STM32 board at $EPD_HOST"
        sed -i '/^#\?EPD_HOST=/d' "$ENV_FILE"
        echo "EPD_HOST=$EPD_HOST" >> "$ENV_FILE"
    fi
}

write_service() {
    info "Writing systemd service"
    local run="$PYTHON $APP_DIR/main.py -s $CONFIG_DIR/setting.json"
    cat > "$SYSTEMD/$SERVICE.service" <<EOF
[Unit]
Description=Kiroshi e-Paper dashboard
Wants=network-online.target
After=network-online.target

[Service]
User=$RUN_USER
WorkingDirectory=$APP_DIR
EnvironmentFile=-$ENV_FILE
ExecStart=$run
ExecStopPost=$run --clear
Restart=on-failure
RestartSec=30

[Install]
WantedBy=multi-user.target
EOF
}

write_update_timer() {
    info "Enabling weekly update"
    cat > "$SYSTEMD/$SERVICE-update.service" <<EOF
[Unit]
Description=Update Kiroshi
Wants=network-online.target
After=network-online.target

[Service]
Type=oneshot
Environment=SUDO_USER=$RUN_USER
ExecStart=$APP_DIR/install.sh --update
EOF
    cat > "$SYSTEMD/$SERVICE-update.timer" <<EOF
[Unit]
Description=Update Kiroshi one time each week

[Timer]
OnCalendar=weekly
RandomizedDelaySec=1h
Persistent=true

[Install]
WantedBy=timers.target
EOF
    systemctl daemon-reload
    systemctl enable --now "$SERVICE-update.timer"
}

test_display() {
    info "Test: drawing one panel (this can take 30 seconds)"
    # shellcheck source=/dev/null
    if (set -a; . "$ENV_FILE"; set +a; as_user "$PYTHON" "$APP_DIR/main.py" --once -s "$CONFIG_DIR/setting.json"); then
        info "Test OK"
    else
        warn "Test failed. Check the log above. If SPI was off before, reboot and run the test again."
    fi
}

update() {
    info "Updating code"
    as_user git -C "$APP_DIR" pull --ff-only
    setup_venv
    systemctl restart "$SERVICE"
    info "Updated and restarted"
}

# --- Main ---
# All code is in functions, so bash reads the full file before it runs.
# This keeps a running update safe when git pull changes this file.
main() {
    if [ "$EUID" -ne 0 ]; then
        warn "Run with sudo: sudo $0 $*"
        return 1
    fi
    if [ "$RUN_USER" = root ]; then
        warn "Run from your normal user with sudo, not as root."
        return 1
    fi

    if [ "${1:-}" = "--update" ]; then
        update
        return 0
    fi

    install_packages
    enable_spi
    setup_venv
    setup_config
    write_service
    systemctl daemon-reload
    test_display
    systemctl enable "$SERVICE"
    systemctl restart "$SERVICE"
    if [ "${1:-}" = "--auto-update" ]; then write_update_timer; fi

    info "Done. Kiroshi runs now and starts at boot."
    echo "  Config:   $CONFIG_DIR/setting.json and panels.json"
    echo "  API keys: sudo nano $ENV_FILE"
    echo "  Log:      journalctl -u $SERVICE -f"
    echo "  Update:   sudo $APP_DIR/install.sh --update"
}

main "$@"
