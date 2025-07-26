# Installation Guide

This guide covers installing argconfig and setting up your development environment.

## Requirements

- Python 3.7 or higher
- PyYAML 5.1 or higher (automatically installed)

## Installation Methods

### 1. Install from PyPI (Recommended)

```bash
pip install argconfig
```

This installs the latest stable version from the Python Package Index.

### 2. Install from Source

#### Development Installation

For development or to get the latest features:

```bash
# Clone the repository
git clone https://github.com/your-username/argconfig.git
cd argconfig

# Install in development mode
pip install -e .
```

#### Regular Installation from Source

```bash
# Clone and install
git clone https://github.com/your-username/argconfig.git
cd argconfig
pip install .
```

### 3. Install Specific Version

```bash
# Install specific version
pip install argconfig==0.1.0

# Install with version constraints
pip install "argconfig>=0.1.0,<0.2.0"
```

## Verify Installation

After installation, verify that argconfig is working correctly:

### 1. Check Python Import

```python
python -c "from argconfig import create_parser_from_yaml; print('argconfig installed successfully')"
```

### 2. Check CLI Tool

```bash
# Check if the management tool is available
argconfig-manage --help
```

You should see the help output for the argconfig management tool.

### 3. Create Test Configuration

```bash
# Create a test configuration
mkdir test_argconfig
cd test_argconfig

# Setup a simple CLI
argconfig-manage setup testapp

# Verify the file was created
cat argconfig.yaml
```

## Dependencies

Argconfig has minimal dependencies:

### Required Dependencies

- **PyYAML** (≥5.1) - YAML file parsing
  ```bash
  pip install "PyYAML>=5.1"
  ```

### Optional Dependencies

None currently. Argconfig is designed to work with Python's standard library.

## Virtual Environment Setup

It's recommended to use argconfig within a virtual environment:

### Using venv (Python 3.3+)

```bash
# Create virtual environment
python -m venv argconfig_env

# Activate (Linux/macOS)
source argconfig_env/bin/activate

# Activate (Windows)
argconfig_env\Scripts\activate

# Install argconfig
pip install argconfig

# Deactivate when done
deactivate
```

### Using conda

```bash
# Create conda environment
conda create -n argconfig_env python=3.9

# Activate environment
conda activate argconfig_env

# Install argconfig
pip install argconfig

# Deactivate when done
conda deactivate
```

## Platform-Specific Notes

### Windows

Argconfig works on Windows with both Command Prompt and PowerShell:

```cmd
# Command Prompt
pip install argconfig
argconfig-manage --help

# PowerShell
pip install argconfig
argconfig-manage --help
```

**Note**: The `--` syntax for argument names works the same on Windows as on Unix systems.

### macOS

Installation on macOS is straightforward:

```bash
# Using system Python (not recommended)
sudo pip install argconfig

# Using Homebrew Python (recommended)
brew install python
pip3 install argconfig

# Using pyenv (recommended for development)
pyenv install 3.9.0
pyenv global 3.9.0
pip install argconfig
```

### Linux

Most Linux distributions work out of the box:

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3-pip
pip3 install argconfig

# CentOS/RHEL/Fedora
sudo yum install python3-pip  # CentOS/RHEL
sudo dnf install python3-pip  # Fedora
pip3 install argconfig

# Arch Linux
sudo pacman -S python-pip
pip install argconfig
```

## Docker Installation

You can use argconfig in Docker containers:

### Dockerfile Example

```dockerfile
FROM python:3.9-slim

# Install argconfig
RUN pip install argconfig

# Copy your application
COPY . /app
WORKDIR /app

# Your application setup
RUN argconfig-manage setup myapp

ENTRYPOINT ["python", "myapp.py"]
```

### Docker Compose Example

```yaml
version: '3.8'
services:
  myapp:
    build: .
    volumes:
      - ./argconfig.yaml:/app/argconfig.yaml
    environment:
      - LOG_LEVEL=INFO
```

## IDE Integration

### VS Code

For the best development experience with VS Code:

1. **Install Python extension**
2. **Setup workspace settings** (`.vscode/settings.json`):
   ```json
   {
     "python.defaultInterpreterPath": "./venv/bin/python",
     "python.linting.enabled": true,
     "python.linting.pylintEnabled": true
   }
   ```

3. **YAML extension** for syntax highlighting:
   ```bash
   code --install-extension redhat.vscode-yaml
   ```

### PyCharm

1. **Configure Python interpreter** to your virtual environment
2. **Install YAML plugin** for better YAML support
3. **Setup external tools** for argconfig-manage:
   - File → Settings → Tools → External Tools
   - Add new tool with program: `argconfig-manage`

## Troubleshooting Installation

### Common Issues

#### 1. PyYAML Installation Fails

```bash
# On some systems, you might need development headers
# Ubuntu/Debian
sudo apt install python3-dev libyaml-dev

# CentOS/RHEL
sudo yum install python3-devel libyaml-devel

# Then reinstall
pip install --force-reinstall PyYAML
```

#### 2. Permission Errors

```bash
# Use user installation
pip install --user argconfig

# Or use virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate     # Windows
pip install argconfig
```

#### 3. Command Not Found: argconfig-manage

```bash
# Check if it's in your PATH
which argconfig-manage

# If not found, try
python -m argconfig.manage --help

# Or add to PATH (bash/zsh)
export PATH="$HOME/.local/bin:$PATH"

# Or add to PATH (fish)
set -gx PATH $HOME/.local/bin $PATH
```

#### 4. Import Errors

```python
# Check Python path
import sys
print(sys.path)

# Check installed packages
import pkg_resources
print([p.project_name for p in pkg_resources.working_set])

# Reinstall if needed
pip uninstall argconfig
pip install argconfig
```

### Getting Help

If you encounter issues:

1. **Check the version**:
   ```bash
   pip show argconfig
   python -c "import argconfig; print(argconfig.__version__)"
   ```

2. **Update to latest version**:
   ```bash
   pip install --upgrade argconfig
   ```

3. **Clean installation**:
   ```bash
   pip uninstall argconfig
   pip cache purge
   pip install argconfig
   ```

4. **Report bugs**: Create an issue on the GitHub repository with:
   - Operating system and version
   - Python version (`python --version`)
   - Argconfig version
   - Full error message and traceback

## Development Setup

For contributing to argconfig development:

### 1. Fork and Clone

```bash
# Fork the repository on GitHub, then:
git clone https://github.com/your-username/argconfig.git
cd argconfig
```

### 2. Setup Development Environment

```bash
# Create virtual environment
python -m venv dev_env
source dev_env/bin/activate  # Linux/macOS
# or
dev_env\Scripts\activate     # Windows

# Install in development mode with dev dependencies
pip install -e ".[dev]"

# Or install manually
pip install -e .
pip install pytest pytest-cov black flake8 mypy
```

### 3. Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=argconfig --cov-report=html

# Run specific test
pytest tests/test_parser.py::test_basic_parser
```

### 4. Code Quality

```bash
# Format code
black argconfig/

# Check linting
flake8 argconfig/

# Type checking
mypy argconfig/
```

### 5. Build Documentation

```bash
# Install documentation dependencies
pip install mkdocs mkdocs-material

# Serve documentation locally
mkdocs serve

# Build documentation
mkdocs build
```

This comprehensive installation guide should help users get argconfig running in any environment, from simple local development to complex production deployments.