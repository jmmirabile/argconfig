"""
Parser builder that converts YAML configuration models to argparse objects.
"""
import argparse
from typing import Dict, List, Any, Optional, Union
from .models import ArgumentConfig, Argument, Subcommand, SubcommandConfig, ArgumentGroup, MutuallyExclusiveGroup


class ArgumentParser:
    """Builds argparse.ArgumentParser from YAML configuration."""
    
    def __init__(self, config: ArgumentConfig):
        self.config = config
        self._parent_parser: Optional[argparse.ArgumentParser] = None
        self._main_parser: Optional[argparse.ArgumentParser] = None
    
    def build(self) -> argparse.ArgumentParser:
        """Build the complete argument parser."""
        # Create parent parser for shared arguments
        self._parent_parser = self._create_parent_parser()
        
        # Create main parser
        parents = [self._parent_parser] if self._parent_parser else []
        self._main_parser = argparse.ArgumentParser(
            prog=self.config.parser.prog,
            description=self.config.parser.description,
            epilog=self.config.parser.epilog,
            parents=parents,
            add_help=True
        )
        
        # Add direct arguments to main parser only if no subcommands
        if not self.config.subcommands:
            self._add_arguments(self._main_parser, self.config.arguments)
        
        # Add argument groups only if no subcommands
        if not self.config.subcommands:
            self._add_argument_groups(self._main_parser, self.config.argument_groups, self.config.arguments)
            
            # Add mutually exclusive groups
            self._add_mutually_exclusive_groups(self._main_parser, self.config.mutually_exclusive, self.config.arguments)
        
        # Add subcommands
        if self.config.subcommands:
            self._add_subcommands(self._main_parser, self.config.subcommands)
        
        return self._main_parser
    
    def _create_parent_parser(self) -> Optional[argparse.ArgumentParser]:
        """Create parent parser with shared arguments."""
        if not self.config.parent_arguments:
            return None
        
        parent = argparse.ArgumentParser(add_help=False)
        self._add_arguments(parent, self.config.parent_arguments)
        return parent
    
    def _add_arguments(self, parser: argparse.ArgumentParser, arguments: List[Argument]):
        """Add arguments to a parser."""
        for arg in arguments:
            self._add_single_argument(parser, arg)
    
    def _add_single_argument(self, parser: argparse.ArgumentParser, arg: Argument):
        """Add a single argument to parser."""
        # Build argument names
        names = []
        if arg.name:
            names.append(arg.name)
        if arg.short:
            names.append(arg.short)
        
        if not names:
            raise ValueError(f"Argument must have either 'name' or 'short' specified")
        
        # Build keyword arguments for add_argument
        kwargs = {}
        
        if arg.type:
            kwargs['type'] = self._get_type_converter(arg.type)
        
        if arg.action:
            kwargs['action'] = arg.action
        
        # Resolve choices using resolvers
        resolved_choices = arg.resolve_choices()
        if resolved_choices:
            kwargs['choices'] = resolved_choices
        
        # Resolve default using precedence: env_var > YAML default > None
        effective_default = arg.get_effective_default()
        if effective_default is not None:
            kwargs['default'] = effective_default
        
        # Handle required flag - if we have an env var providing a value, don't require CLI input
        if arg.required is not None:
            # If we have an effective default from env var, the argument is no longer required
            if effective_default is not None:
                kwargs['required'] = False
            else:
                kwargs['required'] = arg.required
        
        if arg.nargs is not None:
            kwargs['nargs'] = arg.nargs
        
        if arg.help:
            kwargs['help'] = arg.help
        
        if arg.dest:
            kwargs['dest'] = arg.dest
        
        # Add the argument
        parser.add_argument(*names, **kwargs)
    
    def _get_type_converter(self, type_name: str):
        """Get type converter function from string name."""
        type_map = {
            'str': str,
            'int': int,
            'float': float,
            'bool': bool,
        }
        
        if type_name in type_map:
            return type_map[type_name]
        
        # For custom types, try to import and use them
        try:
            # Handle module.function format
            if '.' in type_name:
                module_name, func_name = type_name.rsplit('.', 1)
                module = __import__(module_name, fromlist=[func_name])
                return getattr(module, func_name)
            
            # Handle built-in types
            return eval(type_name)
        except (ImportError, AttributeError, NameError):
            raise ValueError(f"Unknown type: {type_name}")
    
    def _add_argument_groups(self, parser: argparse.ArgumentParser, groups: List[ArgumentGroup], all_arguments: List[Argument]):
        """Add argument groups to parser."""
        # Create a mapping of argument names to Argument objects
        arg_map = {arg.name: arg for arg in all_arguments if arg.name}
        arg_map.update({arg.short: arg for arg in all_arguments if arg.short})
        
        for group_config in groups:
            group = parser.add_argument_group(
                title=group_config.title,
                description=group_config.description
            )
            
            # Add arguments that belong to this group
            for arg_name in group_config.arguments:
                if arg_name in arg_map:
                    self._add_single_argument(group, arg_map[arg_name])
    
    def _add_mutually_exclusive_groups(self, parser: argparse.ArgumentParser, groups: List[MutuallyExclusiveGroup], all_arguments: List[Argument]):
        """Add mutually exclusive groups to parser."""
        # Create a mapping of argument names to Argument objects
        arg_map = {arg.name: arg for arg in all_arguments if arg.name}
        arg_map.update({arg.short: arg for arg in all_arguments if arg.short})
        
        for group_config in groups:
            group = parser.add_mutually_exclusive_group(required=group_config.required)
            
            # Add arguments that belong to this group
            for arg_name in group_config.arguments:
                if arg_name in arg_map:
                    self._add_single_argument(group, arg_map[arg_name])
    
    def _add_subcommands(self, parser: argparse.ArgumentParser, subcommands_config: SubcommandConfig):
        """Add subcommands to parser."""
        subparsers = parser.add_subparsers(
            title=subcommands_config.title,
            description=subcommands_config.description,
            dest=subcommands_config.dest
        )
        
        for cmd_name, cmd_config in subcommands_config.commands.items():
            self._add_single_subcommand(subparsers, cmd_name, cmd_config)
    
    def _add_single_subcommand(self, subparsers, cmd_name: str, cmd_config: Subcommand):
        """Add a single subcommand."""
        # Create parent parser if we have one
        parents = [self._parent_parser] if self._parent_parser else []
        
        subparser = subparsers.add_parser(
            cmd_name,
            description=cmd_config.description,
            help=cmd_config.help,
            parents=parents,
            add_help=True
        )
        
        # Add arguments specific to this subcommand
        self._add_arguments(subparser, cmd_config.arguments)
        
        # Add argument groups for this subcommand
        self._add_argument_groups(subparser, cmd_config.argument_groups, cmd_config.arguments)
        
        # Add mutually exclusive groups for this subcommand
        self._add_mutually_exclusive_groups(subparser, cmd_config.mutually_exclusive, cmd_config.arguments)
        
        # Add nested subcommands if they exist
        if cmd_config.subcommands:
            self._add_subcommands(subparser, cmd_config.subcommands)


def create_parser_from_yaml(yaml_file: str) -> argparse.ArgumentParser:
    """Create argparse.ArgumentParser from YAML configuration file.
    
    This function reads a YAML file containing argument configuration and converts
    it into a fully configured argparse.ArgumentParser object. The YAML file should
    follow the argconfig schema format.
    
    Args:
        yaml_file (str): Path to the YAML configuration file. The file should contain
            a valid argconfig schema with parser configuration, arguments, subcommands,
            and other argparse features.
    
    Returns:
        argparse.ArgumentParser: A fully configured ArgumentParser object ready to
            parse command-line arguments.
    
    Raises:
        ImportError: If PyYAML is not installed. Install with: pip install PyYAML
        FileNotFoundError: If the specified YAML file does not exist.
        yaml.YAMLError: If the YAML file contains invalid YAML syntax.
        ValueError: If the YAML configuration contains invalid argument definitions.
    
    Example:
        Basic usage with a YAML file:
        
        >>> parser = create_parser_from_yaml('cli_config.yaml')
        >>> args = parser.parse_args()
        
        Example YAML configuration:
        
        ```yaml
        parser:
          prog: "mytool"
          description: "A sample CLI tool"
        
        parent_arguments:
          - name: "--verbose"
            short: "-v"
            action: "store_true"
            help: "Enable verbose output"
        
        arguments:
          - name: "input_file"
            type: "str"
            help: "Input file to process"
        
        subcommands:
          title: "Commands"
          dest: "command"
          commands:
            process:
              description: "Process the input file"
              arguments:
                - name: "--format"
                  choices: ["json", "yaml"]
                  default: "json"
        ```
        
        Built-in resolvers can be used for dynamic values:
        
        ```yaml
        arguments:
          - name: "--log-level"
            choices: "@logging_levels"  # Resolves to all Python logging levels
            default: "INFO"
        ```
    
    Note:
        - The function supports all argparse features including subcommands, argument
          groups, mutually exclusive groups, and parent parsers.
        - Built-in resolvers (prefixed with @) provide dynamic values like logging
          levels, environment variables, and file paths.
        - Parent arguments are automatically inherited by all subcommands.
    
    See Also:
        create_parser_from_dict: Create parser from dictionary instead of file
        create_parser_from_config: Create parser from ArgumentConfig object
    """
    import yaml
    
    with open(yaml_file, 'r') as f:
        data = yaml.safe_load(f)
    
    config = ArgumentConfig.from_dict(data)
    builder = ArgumentParser(config)
    return builder.build()


def create_parser_from_dict(data: Dict[str, Any]) -> argparse.ArgumentParser:
    """Create argparse.ArgumentParser from configuration dictionary.
    
    This function takes a dictionary containing argument configuration (typically
    from parsed YAML/JSON) and converts it into a fully configured argparse.ArgumentParser object. This is useful when you already have the
    configuration data in memory or want to programmatically build configurations.
    
    Args:
        data (Dict[str, Any]): Dictionary containing argument configuration that
            follows the argconfig schema format. Should contain keys like 'parser',
            'parent_arguments', 'arguments', 'subcommands', etc.
    
    Returns:
        argparse.ArgumentParser: A fully configured ArgumentParser object ready to
            parse command-line arguments.
    
    Raises:
        ValueError: If the dictionary contains invalid argument definitions or
            unsupported configuration options.
        KeyError: If required configuration keys are missing from the dictionary.
    
    Example:
        Basic usage with a configuration dictionary:
        
        >>> config_dict = {
        ...     'parser': {
        ...         'prog': 'mytool',
        ...         'description': 'A sample CLI tool'
        ...     },
        ...     'parent_arguments': [
        ...         {
        ...             'name': '--verbose',
        ...             'short': '-v',
        ...             'action': 'store_true',
        ...             'help': 'Enable verbose output'
        ...         }
        ...     ],
        ...     'arguments': [
        ...         {
        ...             'name': 'input_file',
        ...             'type': 'str',
        ...             'help': 'Input file to process'
        ...         }
        ...     ]
        ... }
        >>> parser = create_parser_from_dict(config_dict)
        >>> args = parser.parse_args(['--verbose', 'myfile.txt'])
        
        With built-in resolvers:
        
        >>> config_dict = {
        ...     'arguments': [
        ...         {
        ...             'name': '--log-level',
        ...             'choices': '@logging_levels',
        ...             'default': 'INFO'
        ...         }
        ...     ]
        ... }
        >>> parser = create_parser_from_dict(config_dict)
    
    Note:
        - This function is useful when integrating with existing configuration
          management systems or when building configurations programmatically.
        - The dictionary structure should match the YAML schema format exactly.
        - Built-in resolvers (prefixed with @) work the same as in YAML files.
    
    See Also:
        create_parser_from_yaml: Create parser from YAML file
        create_parser_from_config: Create parser from ArgumentConfig object
    """
    config = ArgumentConfig.from_dict(data)
    builder = ArgumentParser(config)
    return builder.build()


def create_parser_from_config(config: ArgumentConfig) -> argparse.ArgumentParser:
    """Create argparse.ArgumentParser from ArgumentConfig object.
    
    This function takes a pre-built ArgumentConfig object and converts it into
    a fully configured argparse.ArgumentParser. This is the most direct method
    when you want to work with the typed configuration objects or perform
    advanced manipulation of the configuration before building the parser.
    
    Args:
        config (ArgumentConfig): A fully configured ArgumentConfig object containing
            all the parser settings, arguments, subcommands, and other configuration.
            This object can be created manually or via ArgumentConfig.from_dict().
    
    Returns:
        argparse.ArgumentParser: A fully configured ArgumentParser object ready to
            parse command-line arguments.
    
    Raises:
        ValueError: If the ArgumentConfig object contains invalid argument
            definitions or configuration conflicts.
        AttributeError: If required attributes are missing from the config object.
    
    Example:
        Basic usage with ArgumentConfig object:
        
        >>> from argconfig import ArgumentConfig, Argument, ParserConfig
        >>> 
        >>> # Create configuration objects manually
        >>> parser_config = ParserConfig(
        ...     prog='mytool',
        ...     description='A sample CLI tool'
        ... )
        >>> 
        >>> arguments = [
        ...     Argument(
        ...         name='--verbose',
        ...         short='-v',
        ...         action='store_true',
        ...         help='Enable verbose output'
        ...     ),
        ...     Argument(
        ...         name='input_file',
        ...         type='str',
        ...         help='Input file to process'
        ...     )
        ... ]
        >>> 
        >>> config = ArgumentConfig(
        ...     parser=parser_config,
        ...     arguments=arguments
        ... )
        >>> 
        >>> parser = create_parser_from_config(config)
        >>> args = parser.parse_args(['--verbose', 'myfile.txt'])
        
        Programmatic configuration building:
        
        >>> # Build config from dictionary first
        >>> config = ArgumentConfig.from_dict(yaml_data)
        >>> 
        >>> # Modify configuration programmatically
        >>> config.arguments.append(Argument(
        ...     name='--debug',
        ...     action='store_true',
        ...     help='Enable debug mode'
        ... ))
        >>> 
        >>> # Build parser with modified config
        >>> parser = create_parser_from_config(config)
    
    Note:
        - This is the most flexible method for advanced use cases where you need
          to programmatically modify configurations before building the parser.
        - All resolver functionality (like @logging_levels) is processed during
          parser building, not during config creation.
        - This method provides the best type safety when building configurations.
    
    See Also:
        create_parser_from_yaml: Create parser from YAML file
        create_parser_from_dict: Create parser from dictionary
        ArgumentConfig.from_dict: Create ArgumentConfig from dictionary
    """
    builder = ArgumentParser(config)
    return builder.build()


def create_initial_config(output_path: Optional[str] = None) -> str:
    """Create an initial argconfig.yaml file with basic structure.
    
    Creates a starter YAML configuration file with common arguments like
    file input (-f) and log level (-l). This provides a good starting point
    for users to build their CLI configuration.
    
    Args:
        output_path (Optional[str]): Path where to create the config file.
            If None, prompts user for location. Defaults to 'argconfig.yaml'
            in the current directory.
    
    Returns:
        str: Path to the created configuration file.
    
    Example:
        >>> from argconfig import create_initial_config
        >>> config_file = create_initial_config()
        >>> print(f"Created config file: {config_file}")
    """
    import os
    
    # Default configuration template
    config_template = '''# Argconfig YAML Configuration
# This file defines your command-line interface using YAML
---
# Top-level parser configuration
parser:
  prog: "myapp"
  description: "My CLI application"
  epilog: "Use 'myapp --help' for more information"

# Parent arguments (shared across all subcommands)
parent_arguments:
  - name: "--log-level"
    short: "-l"
    type: "str"
    choices: "@logging_levels"  # Built-in resolver for all logging levels
    default: "INFO"
    help: "Set logging level"

# Main arguments
arguments:
  - name: "--file"
    short: "-f"
    type: "str"
    help: "Input file to process"
    required: true
    
  - name: "--output"
    short: "-o"
    type: "str"
    help: "Output file path"

# Example subcommands (uncomment and modify as needed)
# subcommands:
#   title: "Available commands"
#   description: "Choose a command to run"
#   dest: "command"
#   
#   commands:
#     process:
#       description: "Process the input file"
#       help: "Process input file with various options"
#       arguments:
#         - name: "--format"
#           type: "str"
#           choices: ["json", "yaml", "xml"]
#           default: "json"
#           help: "Output format"
#           
#     validate:
#       description: "Validate file syntax"
#       help: "Validate the syntax of the input file"
#       arguments:
#         - name: "--strict"
#           action: "store_true"
#           help: "Enable strict validation"

# Argument groups (for better help organization)
# argument_groups:
#   - title: "Input Options"
#     description: "Options for input processing"
#     arguments:
#       - "--file"
#       
#   - title: "Output Options"
#     description: "Options for output formatting"
#     arguments:
#       - "--output"

# Mutually exclusive groups
# mutually_exclusive:
#   - title: "Operation Mode"
#     required: false
#     arguments:
#       - "--batch"
#       - "--interactive"
'''

    # Determine output path
    if output_path is None:
        output_path = _prompt_for_output_path()
    
    # Ensure directory exists
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Write the configuration file
    with open(output_path, 'w') as f:
        f.write(config_template)
    
    print(f"✅ Created argconfig file: {output_path}")
    print("\n📝 Next steps:")
    print("1. Edit the file to customize your CLI interface")
    print("2. Uncomment and modify subcommands as needed")
    print("3. Add argument groups and mutually exclusive groups if desired")
    print("4. Use the config in your code:")
    print(f"   from argconfig import create_parser_from_yaml")
    print(f"   parser = create_parser_from_yaml('{output_path}')")
    
    return output_path


def _prompt_for_output_path() -> str:
    """Prompt user for output path with sensible default."""
    import os
    
    default_name = "argconfig.yaml"
    current_dir = os.getcwd()
    default_path = os.path.join(current_dir, default_name)
    
    print(f"🔧 Argconfig Setup")
    print(f"=" * 20)
    print(f"Creating initial configuration file...")
    print(f"Default location: {default_path}")
    print()
    
    while True:
        user_input = input(f"Output path (press Enter for default '{default_name}'): ").strip()
        
        if not user_input:
            # Use default
            output_path = default_path
            break
        
        # Handle relative and absolute paths
        if not os.path.isabs(user_input):
            output_path = os.path.join(current_dir, user_input)
        else:
            output_path = user_input
        
        # Ensure .yaml extension
        if not output_path.lower().endswith(('.yaml', '.yml')):
            output_path += '.yaml'
        
        # Check if file exists
        if os.path.exists(output_path):
            overwrite = input(f"File {output_path} already exists. Overwrite? (y/n): ").strip().lower()
            if overwrite in ('y', 'yes'):
                break
            else:
                continue
        else:
            break
    
    return output_path