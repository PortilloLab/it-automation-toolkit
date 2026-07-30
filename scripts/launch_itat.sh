#!/usr/bin/env bash
# Script lanzador interactivo para IT Automation Toolkit (ITAT)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

if [ -d "$PROJECT_DIR" ]; then
    cd "$PROJECT_DIR" || exit 1
    if [ -f "$PROJECT_DIR/.venv/bin/activate" ]; then
        source "$PROJECT_DIR/.venv/bin/activate"
    fi
    PYTHONPATH="$PROJECT_DIR/src" itat "$@"
else
    echo "Error: No se encontró el directorio del proyecto en $PROJECT_DIR"
    read -p "Presiona Enter para cerrar..."
fi
