#!/usr/bin/env python3
"""
Argparse-YAML Management CLI Tool

This module provides a command-line interface for managing argparse-yaml YAML files
interactively. Users can create, modify, and inspect their CLI configurations
without manually editing YAML files.

Auto-Detection:
    When no --config is specified, automatically detects and uses app-specific
    config files (*-argparse.yaml) in the current directory. Uses the most
    recently modified file if multiple exist.

Usage:
    argparse-yaml setup <app_name>           # Create {app_name}-argparse.yaml
    argparse-yaml list-parsers               # Auto-detect config file
    argparse-yaml add-argument <options>     # Auto-detect config file
    argparse-yaml <command> --config=file   # Use specific config file
    
Examples:
    # Create myapp-argparse.yaml (becomes default)
    argparse-yaml setup myapp
    
    # Uses myapp-argparse.yaml automatically
    argparse-yaml list-parsers
    argparse-yaml add-argument --parser-path=myapp --arg="--verbose" --action=store_true
    
    # Work with specific config file
    argparse-yaml list-parsers --config=other-app-argparse.yaml
"""

import argparse
import os
import sys
import yaml
import glob
from typing import Dict, Any, List, Optional
from .models import ArgumentConfig, Argument
from ._version import __version__


class ArgparseYamlManager:
    """Manages argparse-yaml YAML files through CLI commands."""
    
    def __init__(self, config_file: str = "argparse-yaml.yaml"):
        self.config_file = config_file
        self._config_data: Optional[Dict[str, Any]] = None
        self._load_config()
    
    def _load_config(self):
        """Load existing config file or initialize empty structure."""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                self._config_data = yaml.safe_load(f) or {}
        else:
            self._config_data = {}
    
    def _save_config(self):
        """Save current config data to file."""
        with open(self.config_file, 'w') as f:
            yaml.dump(self._config_data, f, default_flow_style=False, sort_keys=False)
    
    def setup(self, app_name: str) -> str:
        """Create new base {app_name}-argparse.yaml file with application name.
        
        Args:
            app_name: Name of the application
            
        Returns:
            Path to created config file
        """
        # Update config file path to use app name
        self.config_file = f"{app_name}-argparse.yaml"
        self._config_data = {
            'parser': {
                'prog': app_name,
                'description': f'{app_name} - CLI application',
                'epilog': f'Use \'{app_name} --help\' for more information'
            },
            'parent_arguments': [
                {
                    'name': '--log-level',
                    'short': '-l',
                    'type': 'str',
                    'choices': '@logging_levels',
                    'default': 'INFO',
                    'help': 'Set logging level'
                }
            ],
            'arguments': [],
            'subcommands': None
        }
        
        self._save_config()
        print(f"✅ Created {self.config_file} for application '{app_name}'")
        return self.config_file
    
    def list_parsers(self):
        """Show hierarchy of parsers and arguments."""
        if not self._config_data:
            print("❌ No configuration found. Run 'argparse-yaml setup <app_name>' first.")
            return
        
        app_name = self._config_data.get('parser', {}).get('prog', 'app')
        print(f"📋 Parser hierarchy for '{app_name}':")
        print("=" * 50)
        
        # Show main parser
        print(f"📁 {app_name} (main parser)")
        
        # Show parent arguments
        parent_args = self._config_data.get('parent_arguments', [])
        if parent_args:
            print("  📎 Parent arguments (shared):")
            for arg in parent_args:
                self._print_argument(arg, indent="    ")
        
        # Show main arguments
        main_args = self._config_data.get('arguments', [])
        if main_args:
            print("  📝 Arguments:")
            for arg in main_args:
                self._print_argument(arg, indent="    ")
        
        # Show subcommands recursively
        subcommands = self._config_data.get('subcommands', {})
        if subcommands and 'commands' in subcommands:
            print("  📂 Subcommands:")
            self._print_subcommands(subcommands['commands'], app_name, indent="    ")
    
    def _print_argument(self, arg: Dict[str, Any], indent: str = ""):
        """Print argument information with formatting."""
        name = arg.get('name', 'unnamed')
        short = arg.get('short', '')
        arg_type = arg.get('type', '')
        required = arg.get('required', False)
        help_text = arg.get('help', '')
        
        # Format argument display
        display_name = name
        if short:
            display_name += f"/{short}"
        if arg_type:
            display_name += f" ({arg_type})"
        if required:
            display_name += " [required]"
        
        print(f"{indent}• {display_name}")
        if help_text:
            print(f"{indent}  {help_text}")
    
    def _print_subcommands(self, commands: Dict[str, Any], parent_path: str, indent: str = ""):
        """Recursively print subcommands."""
        for cmd_name, cmd_data in commands.items():
            cmd_path = f"{parent_path}.{cmd_name}"
            print(f"{indent}📁 {cmd_name} -> {cmd_path}")
            
            # Show command arguments
            cmd_args = cmd_data.get('arguments', [])
            if cmd_args:
                for arg in cmd_args:
                    self._print_argument(arg, indent + "  ")
            
            # Show nested subcommands
            nested_subs = cmd_data.get('subcommands', {})
            if nested_subs and 'commands' in nested_subs:
                self._print_subcommands(nested_subs['commands'], cmd_path, indent + "  ")
    
    def _validate_parser_path(self, parser_path: str) -> bool:
        """Validate that a parser path exists in the current configuration.
        
        Args:
            parser_path: The parser path to validate (e.g., 'app', 'app.db', 'app.db.migrate')
            
        Returns:
            True if the parser path is valid, False otherwise
        """
        if not self._config_data:
            return False
        
        path_parts = parser_path.split('.')
        app_name = self._config_data.get('parser', {}).get('prog', 'app')
        
        # Check if first part matches app name
        if len(path_parts) == 0 or path_parts[0] != app_name:
            return False
        
        # If it's just the app name, it's valid (main parser)
        if len(path_parts) == 1:
            return True
        
        # Check subcommand path exists
        subcommands = self._config_data.get('subcommands', {})
        if not subcommands or 'commands' not in subcommands:
            return False
        
        current = subcommands['commands']
        subcommand_path = path_parts[1:]  # Remove app name
        
        for i, part in enumerate(subcommand_path):
            if part not in current:
                return False
            
            # If this isn't the last part, move to next level
            if i < len(subcommand_path) - 1:
                nested_subs = current[part].get('subcommands', {})
                if 'commands' not in nested_subs:
                    return False
                current = nested_subs['commands']
        
        return True
    
    def add_argument(self, args):
        """Add argument to specified parser using argparse-style options.
        
        Args:
            args: Parsed arguments from argparse containing all the argument options
        """
        if not self._config_data:
            print("❌ No configuration found. Run 'argparse-yaml setup <app_name>' first.")
            return
        
        # Validate parser path exists
        if not self._validate_parser_path(args.parser_path):
            print(f"❌ Error: Parser path '{args.parser_path}' does not exist.")
            print("\n💡 Here are the available parser paths:")
            print("=" * 50)
            self.list_parsers()
            return
        
        # Build argument properties from parsed args
        arg_props = {'name': args.arg}
        
        # Add all non-None properties
        if args.help_text:
            arg_props['help'] = args.help_text
        if args.dest:
            arg_props['dest'] = args.dest
        if args.type:
            arg_props['type'] = args.type
        if args.choices:
            # Handle comma-separated choices or @resolvers
            if args.choices.startswith('@'):
                arg_props['choices'] = args.choices
            else:
                arg_props['choices'] = [choice.strip() for choice in args.choices.split(',')]
        if args.action:
            arg_props['action'] = args.action
        if args.default:
            arg_props['default'] = self._convert_value(args.default)
        if args.required:
            arg_props['required'] = True
        if args.nargs:
            arg_props['nargs'] = self._convert_value(args.nargs)
        if args.const:
            arg_props['const'] = self._convert_value(args.const)
        if args.metavar:
            arg_props['metavar'] = args.metavar
        
        # Determine target location
        path_parts = args.parser_path.split('.')
        app_name = self._config_data.get('parser', {}).get('prog', 'app')
        
        if len(path_parts) == 1 and path_parts[0] == app_name:
            # Add to main parser
            self._add_to_main_parser(arg_props)
        else:
            # Add to subcommand
            subcommand_path = path_parts[1:]  # Remove app name
            self._add_to_subcommand(subcommand_path, arg_props)
        
        self._save_config()
        print(f"✅ Added argument '{args.arg}' to parser '{args.parser_path}'")
    
    def _convert_value(self, value: str):
        """Convert string value to appropriate Python type."""
        if value.lower() in ('true', 'false'):
            return value.lower() == 'true'
        elif value.isdigit():
            return int(value)
        elif value.replace('.', '', 1).isdigit():
            return float(value)
        else:
            return value
    
    def _parse_properties(self, properties: List[str]) -> Dict[str, Any]:
        """Parse key=value properties into dictionary."""
        props = {}
        for prop in properties:
            if '=' in prop:
                key, value = prop.split('=', 1)
                props[key] = self._convert_value(value)
        return props
    
    def _add_to_main_parser(self, arg_props: Dict[str, Any]):
        """Add argument to main parser."""
        if 'arguments' not in self._config_data:
            self._config_data['arguments'] = []
        self._config_data['arguments'].append(arg_props)
    
    def _add_to_subcommand(self, subcommand_path: List[str], arg_props: Dict[str, Any]):
        """Add argument to specified subcommand."""
        # Ensure subcommands structure exists
        if 'subcommands' not in self._config_data or self._config_data['subcommands'] is None:
            self._config_data['subcommands'] = {
                'title': 'Available commands',
                'dest': 'command',
                'commands': {}
            }
        
        # Navigate to target subcommand
        current = self._config_data['subcommands']['commands']
        
        for i, part in enumerate(subcommand_path):
            if part not in current:
                # Create missing subcommand
                current[part] = {
                    'description': f'{part} command',
                    'help': f'Execute {part} operations',
                    'arguments': []
                }
            
            if i == len(subcommand_path) - 1:
                # Last part - add argument here
                if 'arguments' not in current[part]:
                    current[part]['arguments'] = []
                current[part]['arguments'].append(arg_props)
            else:
                # Navigate deeper
                if 'subcommands' not in current[part]:
                    current[part]['subcommands'] = {'commands': {}}
                current = current[part]['subcommands']['commands']


def find_default_config_file() -> str:
    """Auto-detect the default config file in the current directory.
    
    Returns:
        Path to the most recently modified *-argparse.yaml file, or 
        'argparse-yaml.yaml' if none found.
    """
    # Look for app-specific config files
    config_files = glob.glob("*-argparse.yaml")
    
    if not config_files:
        return "argparse-yaml.yaml"
    
    if len(config_files) == 1:
        return config_files[0]
    
    # If multiple files exist, use the most recently modified
    config_files_with_mtime = [
        (f, os.path.getmtime(f)) for f in config_files
    ]
    config_files_with_mtime.sort(key=lambda x: x[1], reverse=True)
    
    return config_files_with_mtime[0][0]


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog='argparse-yaml',
        description='Manage argparse-yaml YAML files interactively'
    )
    parser.add_argument('--version', action='version', version=f'argparse-yaml {__version__}')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Setup command
    setup_parser = subparsers.add_parser('setup', help='Create new argparse-yaml file')
    setup_parser.add_argument('app_name', help='Application name')
    setup_parser.add_argument('--config', '-c', default='argparse-yaml.yaml', 
                             help='Config file path (default: auto-detect *-argparse.yaml)')
    
    # List parsers command
    list_parser = subparsers.add_parser('list-parsers', help='Show parser hierarchy')
    list_parser.add_argument('--config', '-c', default='argparse-yaml.yaml',
                            help='Config file path (default: auto-detect *-argparse.yaml)')
    
    # Add argument command
    add_parser = subparsers.add_parser('add-argument', help='Add argument to parser')
    add_parser.add_argument('--config', '-c', default='argparse-yaml.yaml',
                           help='Config file path (default: auto-detect *-argparse.yaml)')
    add_parser.add_argument('--parser-path', required=True,
                           help='Parser path (e.g., app, app.db, app.db.migrate)')
    add_parser.add_argument('--arg', required=True,
                           help='Argument name (e.g., --verbose, -v, input_file)')
    
    # Core argparse options
    add_parser.add_argument('--help-text',
                           help='Help text for the argument')
    add_parser.add_argument('--dest',
                           help='Destination variable name')
    
    # Type and validation
    add_parser.add_argument('--type',
                           choices=['str', 'int', 'float', 'bool'],
                           help='Argument type')
    add_parser.add_argument('--choices',
                           help='Valid choices (comma-separated or @resolver)')
    add_parser.add_argument('--action',
                           choices=['store', 'store_true', 'store_false', 'append', 
                                   'append_const', 'store_const', 'count', 'help', 'version'],
                           help='Action to take when argument is encountered')
    
    # Behavior options
    add_parser.add_argument('--default',
                           help='Default value')
    add_parser.add_argument('--required', action='store_true',
                           help='Make this argument required')
    add_parser.add_argument('--nargs',
                           help='Number of arguments (?, *, +, or number)')
    
    # Additional options
    add_parser.add_argument('--const',
                           help='Constant value for store_const/append_const actions')
    add_parser.add_argument('--metavar',
                           help='Name for the argument in usage messages')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Initialize manager
    # Use auto-detection if config wasn't explicitly set
    if hasattr(args, 'config') and args.config == 'argparse-yaml.yaml':
        # Default value wasn't overridden, try auto-detection
        config_file = find_default_config_file()
    else:
        config_file = getattr(args, 'config', 'argparse-yaml.yaml')
    
    manager = ArgparseYamlManager(config_file)
    
    # Show which config file is being used (except for setup command)
    if args.command != 'setup' and config_file != 'argparse-yaml.yaml':
        print(f"📁 Using config file: {config_file}")
    
    try:
        if args.command == 'setup':
            manager.setup(args.app_name)
        elif args.command == 'list-parsers':
            manager.list_parsers()
        elif args.command == 'add-argument':
            manager.add_argument(args)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())