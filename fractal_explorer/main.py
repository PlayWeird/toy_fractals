"""Entry point for the Fractal Explorer application."""

import sys
import os

# Add parent directory to path for development
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fractal_explorer.app import FractalExplorer


def main():
    """Main entry point."""
    app = FractalExplorer()
    sys.exit(app.run())


if __name__ == "__main__":
    main()