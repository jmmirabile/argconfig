"""
YAML Argument Parser - Create argparse parsers from YAML configuration files.

This module provides a simple way to define complex command-line interfaces
using YAML configuration files instead of writing repetitive argparse code.

Quick Start with CLI Tool:
    # Create a new configuration file
    argparse-yaml setup myapp
    
    # Add arguments interactively
    argparse-yaml add-argument --parser-path=myapp --arg=--verbose --action=store_true --help-text="Enable verbose output"
    argparse-yaml add-argument --parser-path=myapp --arg=--database-url --type=str --env-var=DATABASE_URL --help-text="Database connection URL"
    argparse-yaml add-argument --parser-path=myapp.process --arg=--format --choices="json,yaml" --default=json
    
    # View your parser structure
    argparse-yaml list-parsers

Basic Python Usage:
    from argparse_yaml import create_parser_from_yaml
    
    # Uses your app-specific config file
    parser = create_parser_from_yaml('myapp-argparse.yaml')
    args = parser.parse_args()

Create Initial Config Programmatically:
    from argparse_yaml import create_initial_config
    
    config_file = create_initial_config('my_cli_config.yaml')

Advanced Usage:
    from argparse_yaml import ArgumentConfig, create_parser_from_config
    
    config = ArgumentConfig.from_dict(yaml_data)
    parser = create_parser_from_config(config)

Built-in Resolvers:
    YAML configurations support dynamic values using @ resolvers:
    
    arguments:
      - name: "--log-level"
        choices: "@logging_levels"    # All Python logging levels
        default: "INFO"
      - name: "--output"
        default: "@current_dir"       # Current working directory

Features:
    - Parent parsers for shared arguments
    - Nested subcommands with dot notation (app.db.migrate)
    - Argument groups and mutually exclusive groups
    - Built-in resolvers for dynamic values
    - Environment variable support with precedence: CLI > env vars > YAML > defaults
    - Interactive CLI management tool
    - Full argparse feature support
"""

# Import main API functions
from .argparse_conf import (
    create_parser_from_yaml,
    create_parser_from_dict, 
    create_parser_from_config,
    create_initial_config,
    ArgumentParser
)

# Import data models for advanced usage
from .models import (
    ArgumentConfig,
    Argument,
    Subcommand,
    SubcommandConfig,
    ParserConfig,
    ArgumentGroup,
    MutuallyExclusiveGroup
)

# Import resolver system
from .resolvers import (
    resolver_registry,
    ChoiceResolvers,
    DefaultResolvers,
    ResolverRegistry
)

# Define public API
__all__ = [
    # Main functions (most commonly used)
    'create_parser_from_yaml',
    'create_parser_from_dict',
    'create_parser_from_config',
    'create_initial_config',
    
    # Classes for advanced usage
    'ArgumentParser',
    'ArgumentConfig',
    'Argument',
    'Subcommand',
    'SubcommandConfig', 
    'ParserConfig',
    'ArgumentGroup',
    'MutuallyExclusiveGroup',
    
    # Resolver system
    'resolver_registry',
    'ChoiceResolvers',
    'DefaultResolvers',
    'ResolverRegistry'
]

# Package metadata
from ._version import __version__
__author__ = 'Your Name'
__description__ = 'Create argparse parsers from YAML configuration files'