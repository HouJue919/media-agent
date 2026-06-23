from __future__ import annotations

import argparse
from pathlib import Path


PROJECT_DIR = Path("/Users/adanhou/Documents/素材筛选ai")
LAUNCHER_NAME = "Media Agent GUI.command"
PRIVACY_NOTICE = "All processing runs locally. Media files are not uploaded."


def build_launcher_content(project_dir: Path = PROJECT_DIR) -> str:
    project_path = str(project_dir)
    return f"""#!/bin/zsh
set -e

PROJECT_DIR="{project_path}"

echo "Media Agent GUI"
echo "Local photo and video asset management for creators."
echo "{PRIVACY_NOTICE}"
echo ""

cd "$PROJECT_DIR"

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 was not found. Please install Python 3 and try again."
  read -r "?Press Enter to close."
  exit 1
fi

if [ ! -f "requirements-gui.txt" ]; then
  echo "requirements-gui.txt was not found in $PROJECT_DIR."
  read -r "?Press Enter to close."
  exit 1
fi

if ! python3 -c "import streamlit" >/dev/null 2>&1; then
  echo "Streamlit is not installed."
  echo "Run this command first:"
  echo "pip install -r requirements-gui.txt"
  read -r "?Press Enter to close."
  exit 1
fi

echo "Starting Streamlit GUI..."
echo ""
streamlit run app.py
"""


def create_launcher(desktop_dir: Path | None = None, project_dir: Path = PROJECT_DIR) -> Path:
    desktop = desktop_dir or (Path.home() / "Desktop")
    desktop.mkdir(parents=True, exist_ok=True)
    launcher_path = desktop / LAUNCHER_NAME
    launcher_path.write_text(build_launcher_content(project_dir), encoding="utf-8")
    launcher_path.chmod(0o755)
    return launcher_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create a macOS desktop launcher for Media Agent GUI.")
    parser.add_argument(
        "--desktop-dir",
        default=None,
        help="Desktop directory where the .command launcher should be written. Defaults to ~/Desktop.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    desktop_dir = Path(args.desktop_dir).expanduser() if args.desktop_dir else None
    launcher_path = create_launcher(desktop_dir=desktop_dir)
    print(f"Created launcher: {launcher_path}")
    print("Double-click it to start Media Agent GUI.")


if __name__ == "__main__":
    main()
