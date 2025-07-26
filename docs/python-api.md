# Python API Reference

Complete reference for using argconfig in Python code.

## Overview

The argconfig Python API provides several ways to create argparse parsers from YAML configurations:

1. **File-based** - Load from YAML files
2. **Dictionary-based** - Use parsed data structures  
3. **Object-based** - Work with typed configuration objects
4. **Template-based** - Generate initial configurations

## Quick Reference

```python
# Most common usage
from argconfig import create_parser_from_yaml
parser = create_parser_from_yaml('cli_config.yaml')
args = parser.parse_args()

# From dictionary
from argconfig import create_parser_from_dict
parser = create_parser_from_dict(config_dict)

# Generate initial config
from argconfig import create_initial_config
create_initial_config('my_config.yaml')
```

## Core Functions

### create_parser_from_yaml

Create an ArgumentParser from a YAML configuration file.

```python
def create_parser_from_yaml(yaml_file: str) -> argparse.ArgumentParser
```

**Parameters:**
- `yaml_file` (str) - Path to YAML configuration file

**Returns:**
- `argparse.ArgumentParser` - Configured parser ready to parse arguments

**Raises:**
- `ImportError` - If PyYAML is not installed
- `FileNotFoundError` - If YAML file doesn't exist
- `yaml.YAMLError` - If YAML syntax is invalid
- `ValueError` - If configuration is invalid

**Example:**
```python
from argconfig import create_parser_from_yaml

# Load configuration and create parser
parser = create_parser_from_yaml('cli_config.yaml')

# Parse command line arguments
args = parser.parse_args()

# Access parsed values
if args.verbose:
    print("Verbose mode enabled")

print(f"Input file: {args.input_file}")
```

### create_parser_from_dict

Create an ArgumentParser from a configuration dictionary.

```python
def create_parser_from_dict(data: Dict[str, Any]) -> argparse.ArgumentParser
```

**Parameters:**
- `data` (Dict[str, Any]) - Configuration dictionary following argconfig schema

**Returns:**
- `argparse.ArgumentParser` - Configured parser

**Raises:**
- `ValueError` - If dictionary contains invalid configuration
- `KeyError` - If required keys are missing

**Example:**
```python
from argconfig import create_parser_from_dict

config = {
    'parser': {
        'prog': 'mytool',
        'description': 'My CLI tool'
    },
    'parent_arguments': [
        {
            'name': '--verbose',
            'short': '-v',
            'action': 'store_true',
            'help': 'Enable verbose output'
        }
    ],
    'arguments': [
        {
            'name': 'input_file',
            'type': 'str',
            'help': 'Input file to process'
        }
    ],
    'subcommands': {
        'title': 'Commands',
        'dest': 'command',
        'commands': {
            'process': {
                'description': 'Process the file',
                'arguments': [
                    {
                        'name': '--format',
                        'choices': ['json', 'yaml', 'xml'],
                        'default': 'json',
                        'help': 'Output format'
                    }
                ]
            }
        }
    }
}

parser = create_parser_from_dict(config)
args = parser.parse_args(['--verbose', 'input.txt', 'process', '--format', 'yaml'])
```

### create_parser_from_config

Create an ArgumentParser from a typed ArgumentConfig object.

```python
def create_parser_from_config(config: ArgumentConfig) -> argparse.ArgumentParser
```

**Parameters:**
- `config` (ArgumentConfig) - Typed configuration object

**Returns:**
- `argparse.ArgumentParser` - Configured parser

**Example:**
```python
from argconfig import (
    create_parser_from_config,
    ArgumentConfig, Argument, ParserConfig
)

# Create configuration objects
parser_config = ParserConfig(
    prog='mytool',
    description='My CLI tool'
)

arguments = [
    Argument(
        name='--verbose',
        short='-v',
        action='store_true',
        help='Enable verbose output'
    ),
    Argument(
        name='input_file',
        type='str',
        help='Input file to process'
    )
]

config = ArgumentConfig(
    parser=parser_config,
    arguments=arguments
)

parser = create_parser_from_config(config)
```

### create_initial_config

Create a starter YAML configuration file.

```python
def create_initial_config(output_path: Optional[str] = None) -> str
```

**Parameters:**
- `output_path` (Optional[str]) - Where to create the file. If None, prompts user

**Returns:**
- `str` - Path to created configuration file

**Example:**
```python
from argconfig import create_initial_config

# Create with specific path
config_file = create_initial_config('my_cli_config.yaml')

# Interactive creation (prompts for path)
config_file = create_initial_config()
```

## Configuration Classes

### ArgumentConfig

Main configuration class containing all parser settings.

```python
@dataclass
class ArgumentConfig:
    parser: ParserConfig = field(default_factory=ParserConfig)
    parent_arguments: List[Argument] = field(default_factory=list)
    arguments: List[Argument] = field(default_factory=list)
    subcommands: Optional[SubcommandConfig] = None
    argument_groups: List[ArgumentGroup] = field(default_factory=list)
    mutually_exclusive: List[MutuallyExclusiveGroup] = field(default_factory=list)
```

**Methods:**

```python
@classmethod
def from_dict(cls, data: Dict[str, Any]) -> 'ArgumentConfig'
```

Create ArgumentConfig from dictionary (typically from parsed YAML).

**Example:**
```python
import yaml
from argconfig import ArgumentConfig

with open('config.yaml') as f:
    data = yaml.safe_load(f)

config = ArgumentConfig.from_dict(data)

# Modify configuration
config.arguments.append(Argument(
    name='--debug',
    action='store_true',
    help='Enable debug mode'
))

# Create parser
parser = create_parser_from_config(config)
```

### Argument

Represents a single argument configuration.

```python
@dataclass
class Argument:
    name: str
    short: Optional[str] = None
    type: Optional[str] = None
    action: Optional[str] = None
    choices: Optional[Union[List[str], str]] = None
    default: Optional[Any] = None
    required: Optional[bool] = None
    nargs: Optional[Union[str, int]] = None
    help: Optional[str] = None
    dest: Optional[str] = None
```

**Methods:**

```python
def resolve_choices(self) -> Optional[List[str]]
```
Resolve choices using built-in resolvers if needed.

```python
def resolve_default(self) -> Any
```
Resolve default value using built-in resolvers if needed.

**Example:**
```python
from argconfig import Argument

# Simple flag
verbose_arg = Argument(
    name='--verbose',
    short='-v',
    action='store_true',
    help='Enable verbose output'
)

# With choices and resolver
log_level_arg = Argument(
    name='--log-level',
    short='-l',
    type='str',
    choices='@logging_levels',  # Resolver
    default='INFO',
    help='Set logging level'
)

# Positional argument
file_arg = Argument(
    name='input_file',
    type='str',
    help='Input file to process',
    nargs='?'  # Optional
)
```

### ParserConfig

Top-level parser configuration.

```python
@dataclass
class ParserConfig:
    prog: Optional[str] = None
    description: Optional[str] = None
    epilog: Optional[str] = None
```

**Example:**
```python
from argconfig import ParserConfig

config = ParserConfig(
    prog='mytool',
    description='A powerful CLI tool',
    epilog='For more help, visit https://example.com/docs'
)
```

### SubcommandConfig

Configuration for subcommands collection.

```python
@dataclass
class SubcommandConfig:
    title: Optional[str] = None
    description: Optional[str] = None
    dest: Optional[str] = None
    commands: Dict[str, Subcommand] = field(default_factory=dict)
```

### Subcommand

Individual subcommand configuration.

```python
@dataclass
class Subcommand:
    description: Optional[str] = None
    help: Optional[str] = None
    arguments: List[Argument] = field(default_factory=list)
    subcommands: Optional[SubcommandConfig] = None
    argument_groups: List[ArgumentGroup] = field(default_factory=list)
    mutually_exclusive: List[MutuallyExclusiveGroup] = field(default_factory=list)
```

**Example:**
```python
from argconfig import Subcommand, Argument

process_cmd = Subcommand(
    description='Process input files',
    help='Process files with various options',
    arguments=[
        Argument(
            name='--format',
            choices=['json', 'yaml', 'xml'],
            default='json',
            help='Output format'
        ),
        Argument(
            name='--strict',
            action='store_true',
            help='Enable strict processing'
        )
    ]
)
```

## Built-in Resolvers

### Choice Resolvers

Dynamic choice generation using `@resolver_name` syntax.

```python
from argconfig import resolver_registry

# Available choice resolvers
choice_resolvers = resolver_registry.list_choice_resolvers()
print(choice_resolvers)
# ['logging_levels', 'env_vars', 'file_extensions', 'python_versions']

# Resolve choices manually
levels = resolver_registry.resolve_choices('logging_levels')
print(levels)
# ['CRITICAL', 'FATAL', 'ERROR', 'WARN', 'WARNING', 'INFO', 'DEBUG', 'NOTSET']
```

**Available Choice Resolvers:**

| Resolver | Description | Example Values |
|----------|-------------|----------------|
| `@logging_levels` | Python logging levels | `['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']` |
| `@env_vars` | Environment variable names | `['PATH', 'HOME', 'USER', ...]` |
| `@file_extensions` | Common file extensions | `['.txt', '.json', '.yaml', '.xml', '.csv']` |
| `@python_versions` | Python version strings | `['3.8', '3.9', '3.10', '3.11', '3.12']` |

### Default Resolvers

Dynamic default value generation.

```python
# Available default resolvers
default_resolvers = resolver_registry.list_default_resolvers()
print(default_resolvers)
# ['current_user', 'current_dir', 'home_dir', 'temp_dir']

# Resolve defaults manually
current_dir = resolver_registry.resolve_default('current_dir')
print(current_dir)
# '/home/user/projects/myproject'
```

**Available Default Resolvers:**

| Resolver | Description | Example Value |
|----------|-------------|---------------|
| `@current_user` | Current username | `'johndoe'` |
| `@current_dir` | Current working directory | `'/home/user/project'` |
| `@home_dir` | User home directory | `'/home/user'` |
| `@temp_dir` | System temp directory | `'/tmp'` |

### Custom Resolvers

You can check if a value is a resolver and process it manually:

```python
from argconfig import resolver_registry

# Check if value is a resolver
if resolver_registry.is_choice_resolver('@logging_levels'):
    choices = resolver_registry.resolve_choices('logging_levels')

if resolver_registry.is_default_resolver('@current_dir'):
    default = resolver_registry.resolve_default('current_dir')
```

## Advanced Usage

### Configuration Validation

```python
from argconfig import ArgumentConfig, create_parser_from_config

def validate_config(config_dict):
    """Validate configuration before creating parser."""
    try:
        config = ArgumentConfig.from_dict(config_dict)
        
        # Custom validation
        for arg in config.arguments:
            if arg.required and arg.default is not None:
                raise ValueError(f"Argument {arg.name} cannot be both required and have a default")
        
        # Test parser creation
        parser = create_parser_from_config(config)
        return True
        
    except Exception as e:
        print(f"Configuration validation failed: {e}")
        return False
```

### Dynamic Configuration Building

```python
from argconfig import ArgumentConfig, Argument, ParserConfig, Subcommand, SubcommandConfig

def build_database_cli():
    """Build a database CLI configuration programmatically."""
    
    # Base configuration
    config = ArgumentConfig(
        parser=ParserConfig(
            prog='dbtool',
            description='Database management tool'
        )
    )
    
    # Add connection arguments
    connection_args = [
        Argument(name='--host', default='localhost', help='Database host'),
        Argument(name='--port', type='int', default=5432, help='Database port'),
        Argument(name='--user', default='@current_user', help='Database user'),
    ]
    config.parent_arguments.extend(connection_args)
    
    # Add subcommands
    subcommands = SubcommandConfig(
        title='Database Operations',
        dest='operation',
        commands={}
    )
    
    # Migration subcommand
    migrate_cmd = Subcommand(
        description='Database migration operations',
        arguments=[
            Argument(name='--dry-run', action='store_true', help='Show what would be done'),
            Argument(name='--steps', type='int', help='Number of migration steps'),
        ]
    )
    subcommands.commands['migrate'] = migrate_cmd
    
    # Backup subcommand
    backup_cmd = Subcommand(
        description='Database backup operations',
        arguments=[
            Argument(name='backup_name', help='Name for the backup'),
            Argument(name='--format', choices=['sql', 'binary'], default='sql'),
            Argument(name='--compress', action='store_true'),
        ]
    )
    subcommands.commands['backup'] = backup_cmd
    
    config.subcommands = subcommands
    return config

# Use the configuration
config = build_database_cli()
parser = create_parser_from_config(config)
```

### Integration with Existing Code

```python
import argparse
from argconfig import create_parser_from_yaml

def setup_logging(args):
    """Setup logging based on parsed arguments."""
    import logging
    
    level = getattr(logging, args.log_level.upper())
    format_str = '%(asctime)s - %(levelname)s - %(message)s'
    
    if args.verbose:
        format_str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    logging.basicConfig(level=level, format=format_str)

def main():
    """Main application entry point."""
    # Load CLI configuration
    parser = create_parser_from_yaml('cli_config.yaml')
    args = parser.parse_args()
    
    # Setup based on parsed arguments
    setup_logging(args)
    
    # Route to appropriate handler
    if hasattr(args, 'command'):
        if args.command == 'process':
            handle_process(args)
        elif args.command == 'validate':
            handle_validate(args)
    else:
        # No subcommand, handle main operation
        handle_main(args)

def handle_process(args):
    """Handle the 'process' subcommand."""
    logging.info(f"Processing {args.input_file} in {args.format} format")
    # Process logic here

def handle_validate(args):
    """Handle the 'validate' subcommand."""
    strict_mode = getattr(args, 'strict', False)
    logging.info(f"Validating {args.input_file} (strict={strict_mode})")
    # Validation logic here

def handle_main(args):
    """Handle main operation when no subcommand is used."""
    logging.info(f"Main operation on {args.input_file}")
    # Main logic here

if __name__ == '__main__':
    main()
```

### Error Handling

```python
import sys
from argconfig import create_parser_from_yaml

def safe_create_parser(yaml_file):
    """Safely create parser with proper error handling."""
    try:
        return create_parser_from_yaml(yaml_file)
    except ImportError:
        print("Error: PyYAML is required. Install with: pip install PyYAML")
        sys.exit(1)
    except FileNotFoundError:
        print(f"Error: Configuration file '{yaml_file}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error loading configuration: {e}")
        sys.exit(1)

def main():
    parser = safe_create_parser('cli_config.yaml')
    
    try:
        args = parser.parse_args()
    except SystemExit as e:
        # argparse calls sys.exit() on error
        sys.exit(e.code)
    
    # Process arguments
    process_args(args)
```

## Best Practices

### 1. Use Type Hints

```python
from typing import Dict, Any
from argconfig import ArgumentConfig, create_parser_from_dict

def create_custom_parser(config_data: Dict[str, Any]) -> argparse.ArgumentParser:
    """Create parser with proper type hints."""
    return create_parser_from_dict(config_data)
```

### 2. Validate Configurations

```python
def load_and_validate_config(yaml_file: str) -> ArgumentConfig:
    """Load configuration with validation."""
    import yaml
    
    with open(yaml_file) as f:
        data = yaml.safe_load(f)
    
    config = ArgumentConfig.from_dict(data)
    
    # Validate required fields
    if not config.parser.prog:
        raise ValueError("Parser program name is required")
    
    return config
```

### 3. Handle Resolvers Gracefully

```python
from argconfig import Argument, resolver_registry

def create_log_level_argument() -> Argument:
    """Create log level argument with fallback choices."""
    try:
        # Try to use resolver
        return Argument(
            name='--log-level',
            choices='@logging_levels',
            default='INFO'
        )
    except Exception:
        # Fallback to static choices
        return Argument(
            name='--log-level',
            choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
            default='INFO'
        )
```

### 4. Organize Complex Configurations

```python
from argconfig import ArgumentConfig, Subcommand

class ConfigBuilder:
    """Helper class for building complex configurations."""
    
    def __init__(self, prog: str, description: str):
        self.config = ArgumentConfig(
            parser=ParserConfig(prog=prog, description=description)
        )
    
    def add_common_args(self):
        """Add common arguments to parent_arguments."""
        common_args = [
            Argument(name='--verbose', short='-v', action='store_true'),
            Argument(name='--log-level', choices='@logging_levels', default='INFO'),
            Argument(name='--config', short='-c', help='Config file path'),
        ]
        self.config.parent_arguments.extend(common_args)
        return self
    
    def add_subcommand(self, name: str, subcommand: Subcommand):
        """Add a subcommand."""
        if not self.config.subcommands:
            self.config.subcommands = SubcommandConfig(commands={})
        self.config.subcommands.commands[name] = subcommand
        return self
    
    def build(self) -> ArgumentConfig:
        """Return the built configuration."""
        return self.config

# Usage
config = (ConfigBuilder('mytool', 'My CLI tool')
          .add_common_args()
          .add_subcommand('process', process_subcommand)
          .add_subcommand('validate', validate_subcommand)
          .build())
```

This comprehensive Python API allows you to integrate argconfig into any Python application, from simple scripts to complex CLI tools.