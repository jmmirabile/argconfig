# Argconfig - YAML Argument Parser

Create powerful command-line interfaces using YAML configuration files instead of writing repetitive argparse code.

## Features

- 🚀 **Interactive CLI Management** - Build CLIs with simple commands
- 📄 **YAML Configuration** - Define complex argument structures in YAML
- 🔧 **Built-in Resolvers** - Dynamic values like `@logging_levels`
- 🌳 **Nested Subcommands** - Multi-level command hierarchies
- 🎯 **Parent Parsers** - Shared arguments across subcommands
- ⚡ **Full argparse Support** - All argparse features available

## Quick Start

### 1. Installation

```bash
pip install argconfig
```

### 2. Create Your First CLI

```bash
# Create a new CLI configuration
argconfig-manage setup myapp

# Add arguments
argconfig-manage add-argument --parser-path=myapp --arg="--verbose" --action=store_true --help-text="Enable verbose output"

argconfig-manage add-argument --parser-path=myapp --arg="input_file" --type=str --help-text="Input file to process"

# Add subcommand arguments
argconfig-manage add-argument --parser-path=myapp.process --arg="--format" --choices="json,yaml,xml" --default="json" --help-text="Output format"

# View your CLI structure
argconfig-manage list-parsers
```

### 3. Use in Your Python Code

```python
from argconfig import create_parser_from_yaml

# Load your CLI configuration
parser = create_parser_from_yaml('argconfig.yaml')

# Parse arguments
args = parser.parse_args()

# Use the parsed arguments
if args.verbose:
    print("Verbose mode enabled")

print(f"Processing: {args.input_file}")

if hasattr(args, 'format'):
    print(f"Output format: {args.format}")
```

## CLI Management Tool

The `argconfig-manage` tool helps you build and maintain CLI configurations interactively.

### Available Commands

```bash
# Create new configuration
argconfig-manage setup <app_name>

# View parser hierarchy
argconfig-manage list-parsers

# Add arguments to parsers
argconfig-manage add-argument [options]
```

### Parser Paths

Use dot notation to specify where arguments should be added:

- `myapp` - Main parser
- `myapp.db` - 'db' subcommand
- `myapp.db.migrate` - 'migrate' sub-subcommand

### Add Argument Options

All standard argparse options are supported:

```bash
argconfig-manage add-argument \
  --parser-path=myapp \
  --arg="--log-level" \
  --type=str \
  --choices="@logging_levels" \
  --default="INFO" \
  --help-text="Set logging level"
```

**Available Options:**
- `--arg` - Argument name (required)
- `--parser-path` - Where to add the argument (required)  
- `--type` - str, int, float, bool
- `--action` - store, store_true, store_false, append, etc.
- `--choices` - Comma-separated or @resolver
- `--default` - Default value
- `--required` - Make argument required
- `--help-text` - Help description
- `--nargs` - Number of arguments (?, *, +, number)
- `--dest` - Destination variable name
- `--const` - Constant value for store_const actions
- `--metavar` - Name in usage messages

## Built-in Resolvers

Use `@resolver_name` syntax for dynamic values:

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

**Choice Resolvers:**
- `@logging_levels` - DEBUG, INFO, WARNING, ERROR, CRITICAL, etc.
- `@env_vars` - All environment variable names
- `@file_extensions` - Common file extensions
- `@python_versions` - Python version strings

**Default Resolvers:**
- `@current_user` - Current username
- `@current_dir` - Current working directory  
- `@home_dir` - User home directory
- `@temp_dir` - System temp directory

## Examples

### Simple File Processor

```bash
# Setup
argconfig-manage setup fileproc

# Add main arguments
argconfig-manage add-argument --parser-path=fileproc --arg="input_file" --type=str --help-text="Input file"
argconfig-manage add-argument --parser-path=fileproc --arg="--output" --type=str --help-text="Output file"

# Add processing subcommand
argconfig-manage add-argument --parser-path=fileproc.convert --arg="--format" --choices="json,yaml,xml" --default="json"
argconfig-manage add-argument --parser-path=fileproc.validate --arg="--strict" --action=store_true
```

**Resulting CLI:**
```bash
fileproc input.txt --output result.txt convert --format yaml
fileproc config.json validate --strict
```

### Database Tool

```bash
# Setup
argconfig-manage setup dbtool

# Add connection arguments (shared across all subcommands)
# Note: These would go in parent_arguments in the YAML

# Add database operations
argconfig-manage add-argument --parser-path=dbtool.migrate --arg="--dry-run" --action=store_true
argconfig-manage add-argument --parser-path=dbtool.backup --arg="backup_name" --type=str --help-text="Backup name"
argconfig-manage add-argument --parser-path=dbtool.backup --arg="--compress" --action=store_true
```

**Resulting CLI:**
```bash
dbtool --log-level DEBUG migrate --dry-run
dbtool backup production_backup --compress
```

## Python API

For programmatic usage:

### Basic Usage

```python
from argconfig import create_parser_from_yaml

parser = create_parser_from_yaml('cli_config.yaml')
args = parser.parse_args()
```

### From Dictionary

```python
from argconfig import create_parser_from_dict

config = {
    'parser': {'prog': 'mytool', 'description': 'My CLI tool'},
    'arguments': [
        {'name': '--verbose', 'action': 'store_true', 'help': 'Verbose output'}
    ]
}

parser = create_parser_from_dict(config)
args = parser.parse_args()
```

### Create Initial Config

```python
from argconfig import create_initial_config

# Create starter configuration
config_file = create_initial_config('my_cli_config.yaml')
```

### Advanced Usage

```python
from argconfig import ArgumentConfig, create_parser_from_config

# Load and modify configuration
config = ArgumentConfig.from_dict(yaml_data)

# Add arguments programmatically
from argconfig import Argument
config.arguments.append(Argument(
    name='--debug',
    action='store_true',
    help='Enable debug mode'
))

parser = create_parser_from_config(config)
```

## YAML Schema

The YAML configuration follows this structure:

```yaml
# Parser configuration
parser:
  prog: "myapp"
  description: "My CLI application"
  epilog: "Use 'myapp --help' for more information"

# Shared arguments (inherited by all subcommands)
parent_arguments:
  - name: "--log-level"
    short: "-l"
    type: "str"
    choices: "@logging_levels"
    default: "INFO"
    help: "Set logging level"

# Main parser arguments
arguments:
  - name: "input_file"
    type: "str"
    help: "Input file to process"
    
  - name: "--output"
    short: "-o"
    type: "str"
    help: "Output file path"

# Subcommands
subcommands:
  title: "Available commands"
  description: "Choose a command to run"
  dest: "command"
  
  commands:
    process:
      description: "Process the input file"
      help: "Process input file with various options"
      arguments:
        - name: "--format"
          type: "str"
          choices: ["json", "yaml", "xml"]
          default: "json"
          help: "Output format"
          
    validate:
      description: "Validate file syntax"
      help: "Validate the syntax of the input file"
      arguments:
        - name: "--strict"
          action: "store_true"
          help: "Enable strict validation"

# Argument groups (optional)
argument_groups:
  - title: "Input Options"
    description: "Options for input processing"
    arguments:
      - "input_file"
      - "--format"

# Mutually exclusive groups (optional)
mutually_exclusive:
  - title: "Operation Mode"
    required: false
    arguments:
      - "--batch"
      - "--interactive"
```

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT License - see [LICENSE](LICENSE) for details.