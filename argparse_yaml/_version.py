"""Version information for argparse-yaml."""

import subprocess
import sys
from pathlib import Path

def get_version():
    """Get version from git tag or fallback to hardcoded version."""
    try:
        # Try to get version from git tag
        result = subprocess.run(
            ['git', 'describe', '--tags', '--abbrev=0'],
            cwd=Path(__file__).parent.parent,
            capture_output=True,  
            text=True,
            check=True
        )
        version = result.stdout.strip()
        # Remove 'v' prefix if present
        if version.startswith('v'):
            version = version[1:]
        return version
    except (subprocess.CalledProcessError, FileNotFoundError):
        # Fallback version if git is not available or no tags exist
        return "0.2.0"

__version__ = get_version()