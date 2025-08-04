# Argparse-YAML

[![PyPI version](https://badge.fury.io/py/argparse-yaml.svg)](https://badge.fury.io/py/argparse-yaml)
[![Python versions](https://img.shields.io/pypi/pyversions/argparse-yaml.svg)](https://pypi.org/project/argparse-yaml/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Create powerful command-line interfaces using YAML configuration files instead of writing repetitive argparse code.

## ✨ Features

- 🚀 **Interactive CLI Management** - Build CLIs with simple commands
- 🔍 **Smart Config Detection** - Auto-detects `{app}-argparse.yaml` files
- 📄 **YAML Configuration** - Define complex argument structures in YAML
- 🔧 **Built-in Resolvers** - Dynamic values like `@logging_levels`
- 🌳 **Nested Subcommands** - Multi-level command hierarchies  
- 🎯 **Parent Parsers** - Shared arguments across subcommands
- ⚡ **Full argparse Support** - All argparse features available
- 🖥️ **Cross-Platform** - Works on Windows, macOS, and Linux

## 🚀 Quick Start

### Installation

```bash
pip install argparse-yaml
```

### Create Your First CLI

```bash
# Create a new CLI configuration - creates myapp-argparse.yaml
argparse-yaml setup myapp

# Add arguments (auto-detects myapp-argparse.yaml)
argparse-yaml add-argument \
  --parser-path=myapp \
  --arg="--verbose" \
  --action=store_true \
  --help-text="Enable verbose output"

argparse-yaml add-argument \
  --parser-path=myapp \
  --arg="input_file" \
  --type=str \
  --help-text="Input file to process"

# Add subcommand (still auto-detects)
argparse-yaml add-argument \
  --parser-path=myapp.process \
  --arg="--format" \
  --choices="json,yaml,xml" \
  --default="json" \
  --help-text="Output format"

# View your CLI structure (auto-detects)
argparse-yaml list-parsers
```

### 🔍 Smart Config File Detection

Argparse-YAML automatically detects your config files:

```bash
# Creates webapp-argparse.yaml and makes it the default
argparse-yaml setup webapp

# Now uses webapp-argparse.yaml automatically  
argparse-yaml list-parsers

# But you can still work with other configs explicitly
argparse-yaml list-parsers --config=myapp-argparse.yaml
```

**Auto-detection rules:**
- Looks for `*-argparse.yaml` files in current directory
- Uses the most recently modified file if multiple exist
- Falls back to `argparse-yaml.yaml` if none found
- Override with `--config=filename.yaml` anytime

### Use in Python

```python
from argparse_yaml import create_parser_from_yaml

# Load your CLI configuration
parser = create_parser_from_yaml('argparse-yaml.yaml')
args = parser.parse_args()

# Use the parsed arguments
if args.verbose:
    print("Verbose mode enabled")

print(f"Processing: {args.input_file}")
```

**Result:** Your CLI now supports commands like:
```bash
myapp --verbose input.txt process --format yaml
```

## 📖 Documentation

- **[Installation Guide](docs/installation.md)** - Getting started with argconfig
- **[CLI Reference](docs/cli-reference.md)** - Complete argparse-yaml reference
- **[Python API](docs/python-api.md)** - Using argconfig in Python code
- **[Examples](docs/examples.md)** - Real-world CLI examples

## 🎯 Why Argconfig?

### Before (Traditional argparse)

```python
import argparse

parser = argparse.ArgumentParser(prog='myapp', description='My CLI app')
parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose output')
parser.add_argument('--log-level', '-l', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], 
                   default='INFO', help='Set logging level')
parser.add_argument('input_file', help='Input file to process')

subparsers = parser.add_subparsers(dest='command', help='Available commands')

process_parser = subparsers.add_parser('process', help='Process the file')
process_parser.add_argument('--format', choices=['json', 'yaml', 'xml'], 
                           default='json', help='Output format')
process_parser.add_argument('--strict', action='store_true', help='Strict processing')

validate_parser = subparsers.add_parser('validate', help='Validate the file')
validate_parser.add_argument('--schema', help='Schema file')
```

### After (Argconfig)

```bash
# One-time setup
argparse-yaml setup myapp
argparse-yaml add-argument --parser-path=myapp --arg="--verbose" --action=store_true --help-text="Enable verbose output"
argparse-yaml add-argument --parser-path=myapp --arg="--log-level" --choices="@logging_levels" --default="INFO" --help-text="Set logging level"
argparse-yaml add-argument --parser-path=myapp --arg="input_file" --help-text="Input file to process"
argparse-yaml add-argument --parser-path=myapp.process --arg="--format" --choices="json,yaml,xml" --default="json" --help-text="Output format"
argparse-yaml add-argument --parser-path=myapp.validate --arg="--schema" --help-text="Schema file"
```

```python
# Clean Python code
from argparse_yaml import create_parser_from_yaml

parser = create_parser_from_yaml('argparse-yaml.yaml')
args = parser.parse_args()
```

## 🔧 Built-in Resolvers

Use dynamic values with `@resolver_name`:

```yaml
arguments:
  - name: "--log-level"
    choices: "@logging_levels"    # All Python logging levels
    default: "INFO"
  - name: "--output-dir"
    default: "@current_dir"       # Current working directory
  - name: "--user"
    default: "@current_user"      # Current username
```

**Available Resolvers:**
- `@logging_levels` - Python logging levels (DEBUG, INFO, WARNING, etc.)
- `@env_vars` - Environment variable names
- `@current_user` - Current username
- `@current_dir` - Current working directory
- `@home_dir` - User home directory
- `@temp_dir` - System temp directory

## 📋 Examples

### Simple File Processor

```bash
argparse-yaml setup fileproc
argparse-yaml add-argument --parser-path=fileproc --arg="input_file" --type=str --help-text="Input file"
argparse-yaml add-argument --parser-path=fileproc.convert --arg="--format" --choices="json,yaml,xml" --default="json"
```

**Result:**
```bash
fileproc input.txt convert --format yaml
```

### Database Tool

```bash
argparse-yaml setup dbtool
argparse-yaml add-argument --parser-path=dbtool --arg="--host" --default="localhost" --help-text="Database host"
argparse-yaml add-argument --parser-path=dbtool.migrate --arg="--dry-run" --action=store_true --help-text="Dry run mode"
argparse-yaml add-argument --parser-path=dbtool.backup --arg="backup_name" --help-text="Backup name"
```

**Result:**
```bash
dbtool --host prod.db migrate --dry-run
dbtool backup production_backup
```

## 🎨 YAML Schema

The generated YAML follows a clear, intuitive structure:

```yaml
parser:
  prog: "myapp"
  description: "My CLI application"

parent_arguments:          # Shared across all subcommands
  - name: "--log-level"
    short: "-l"
    choices: "@logging_levels"
    default: "INFO"

arguments:                 # Main parser arguments
  - name: "input_file"
    type: "str"
    help: "Input file to process"

subcommands:              # Nested command structure
  title: "Available commands"
  dest: "command"
  commands:
    process:
      description: "Process the input file"
      arguments:
        - name: "--format"
          choices: ["json", "yaml", "xml"]
          default: "json"
```

## 🛠️ Advanced Features

### Nested Subcommands

```bash
# Create multi-level commands
argparse-yaml add-argument --parser-path=myapp.db.migrate.up --arg="--steps" --type=int
argparse-yaml add-argument --parser-path=myapp.db.migrate.down --arg="--steps" --type=int

# Results in: myapp db migrate up --steps 5
```

### Argument Groups

```yaml
argument_groups:
  - title: "Input Options"
    description: "Options for input processing"
    arguments:
      - "input_file"
      - "--format"
```

### Mutually Exclusive Groups

```yaml
mutually_exclusive:
  - title: "Operation Mode"
    required: false
    arguments:
      - "--batch"
      - "--interactive"
```

## 📚 Real-World Examples

See the [examples directory](docs/examples.md) for complete, working examples:

- **File Processor** - Convert between JSON, YAML, XML
- **Database Tool** - Migrations, backups, connections
- **Development Tool** - Git operations, testing, deployment
- **API Client** - REST API interactions with authentication

## 🤝 Contributing

We welcome contributions! Here's how to get started:

1. **Fork the repository**
2. **Create a virtual environment**: `python -m venv venv && source venv/bin/activate`
3. **Install in development mode**: `pip install -e .`
4. **Run tests**: `pytest`
5. **Submit a pull request**

### Development Setup

```bash
git clone https://github.com/your-username/argconfig.git
cd argconfig
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -e .
pytest
```

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 🙋 Support

- **Documentation**: [Full documentation](docs/)
- **Issues**: [GitHub Issues](https://github.com/your-username/argconfig/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-username/argconfig/discussions)

## ⭐ Star History

If you find argconfig useful, please consider giving it a star on GitHub!

---

**Made with ❤️ by developers, for developers.**