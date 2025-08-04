"""
Data models for YAML argument configuration.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Union
from .resolvers import resolver_registry


@dataclass
class Argument:
    """Represents a single argument configuration."""
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
    env_var: Optional[str] = None
    
    def resolve_choices(self) -> Optional[List[str]]:
        """Resolve choices using built-in resolvers if needed."""
        if self.choices is None:
            return None
        
        if isinstance(self.choices, str) and resolver_registry.is_choice_resolver(self.choices):
            resolver_name = resolver_registry.get_choice_resolver_name(self.choices)
            return resolver_registry.resolve_choices(resolver_name)
        
        if isinstance(self.choices, list):
            return self.choices
        
        # If it's a string but not a resolver, treat as single choice
        return [str(self.choices)]
    
    def resolve_default(self) -> Any:
        """Resolve default value using built-in resolvers if needed."""
        if self.default is None:
            return None
        
        if isinstance(self.default, str) and resolver_registry.is_default_resolver(self.default):
            resolver_name = resolver_registry.get_default_resolver_name(self.default)
            return resolver_registry.resolve_default(resolver_name)
        
        return self.default
    
    def resolve_env_var(self) -> Any:
        """Resolve value from environment variable with precedence: env_var > auto-generated > None."""
        import os
        
        # First try explicit env_var
        if self.env_var:
            env_value = os.getenv(self.env_var)
            if env_value is not None:
                return self._convert_env_value(env_value)
        
        # Auto-generate env var name from argument name
        if self.name:
            env_name = self._generate_env_var_name(self.name)
            env_value = os.getenv(env_name)
            if env_value is not None:
                return self._convert_env_value(env_value)
        
        return None
    
    def _generate_env_var_name(self, arg_name: str) -> str:
        """Generate environment variable name from argument name."""
        # Remove leading dashes and convert to uppercase with underscores
        env_name = arg_name.lstrip('-').upper().replace('-', '_')
        return env_name
    
    def _convert_env_value(self, env_value: str) -> Any:
        """Convert environment variable string to appropriate type."""
        if not env_value:
            return env_value
        
        # Handle boolean actions
        if self.action in ('store_true', 'store_false'):
            return env_value.lower() in ('true', '1', 'yes', 'on')
        
        # Handle type conversion
        if self.type == 'int':
            try:
                return int(env_value)
            except ValueError:
                return env_value
        elif self.type == 'float':
            try:
                return float(env_value)
            except ValueError:
                return env_value
        elif self.type == 'bool':
            return env_value.lower() in ('true', '1', 'yes', 'on')
        
        return env_value
    
    def get_effective_default(self) -> Any:
        """Get the effective default value following precedence: env_var > YAML default > None."""
        # Try environment variable first
        env_value = self.resolve_env_var()
        if env_value is not None:
            return env_value
        
        # Fall back to YAML default
        return self.resolve_default()


@dataclass
class ArgumentGroup:
    """Represents an argument group for better help organization."""
    title: str
    description: Optional[str] = None
    arguments: List[str] = field(default_factory=list)


@dataclass
class MutuallyExclusiveGroup:
    """Represents a mutually exclusive argument group."""
    title: Optional[str] = None
    required: bool = False
    arguments: List[str] = field(default_factory=list)


@dataclass
class Subcommand:
    """Represents a subcommand configuration."""
    description: Optional[str] = None
    help: Optional[str] = None
    arguments: List[Argument] = field(default_factory=list)
    subcommands: Optional['SubcommandConfig'] = None
    argument_groups: List[ArgumentGroup] = field(default_factory=list)
    mutually_exclusive: List[MutuallyExclusiveGroup] = field(default_factory=list)


@dataclass
class SubcommandConfig:
    """Configuration for subcommands collection."""
    title: Optional[str] = None
    description: Optional[str] = None
    dest: Optional[str] = None
    commands: Dict[str, Subcommand] = field(default_factory=dict)


@dataclass
class ParserConfig:
    """Top-level parser configuration."""
    prog: Optional[str] = None
    description: Optional[str] = None
    epilog: Optional[str] = None


@dataclass
class ArgumentConfig:
    """Complete argument configuration from YAML."""
    parser: ParserConfig = field(default_factory=ParserConfig)
    parent_arguments: List[Argument] = field(default_factory=list)
    arguments: List[Argument] = field(default_factory=list)
    subcommands: Optional[SubcommandConfig] = None
    argument_groups: List[ArgumentGroup] = field(default_factory=list)
    mutually_exclusive: List[MutuallyExclusiveGroup] = field(default_factory=list)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ArgumentConfig':
        """Create ArgumentConfig from parsed YAML dictionary."""
        config = cls()
        
        # Parse parser configuration
        if 'parser' in data:
            parser_data = data['parser']
            config.parser = ParserConfig(
                prog=parser_data.get('prog'),
                description=parser_data.get('description'),
                epilog=parser_data.get('epilog')
            )
        
        # Parse parent arguments
        if 'parent_arguments' in data:
            config.parent_arguments = [
                cls._parse_argument(arg_data) 
                for arg_data in data['parent_arguments']
            ]
        
        # Parse direct arguments
        if 'arguments' in data:
            config.arguments = [
                cls._parse_argument(arg_data) 
                for arg_data in data['arguments']
            ]
        
        # Parse subcommands
        if 'subcommands' in data and data['subcommands'] is not None:
            config.subcommands = cls._parse_subcommands(data['subcommands'])
        
        # Parse argument groups
        if 'argument_groups' in data:
            config.argument_groups = [
                ArgumentGroup(
                    title=group.get('title', ''),
                    description=group.get('description'),
                    arguments=group.get('arguments', [])
                )
                for group in data['argument_groups']
            ]
        
        # Parse mutually exclusive groups
        if 'mutually_exclusive' in data:
            config.mutually_exclusive = [
                MutuallyExclusiveGroup(
                    title=group.get('title'),
                    required=group.get('required', False),
                    arguments=group.get('arguments', [])
                )
                for group in data['mutually_exclusive']
            ]
        
        return config
    
    @staticmethod
    def _parse_argument(arg_data: Dict[str, Any]) -> Argument:
        """Parse a single argument from dictionary."""
        return Argument(
            name=arg_data.get('name', ''),
            short=arg_data.get('short'),
            type=arg_data.get('type'),
            action=arg_data.get('action'),
            choices=arg_data.get('choices'),
            default=arg_data.get('default'),
            required=arg_data.get('required'),
            nargs=arg_data.get('nargs'),
            help=arg_data.get('help'),
            dest=arg_data.get('dest'),
            env_var=arg_data.get('env_var')
        )
    
    @staticmethod
    def _parse_subcommands(subcommands_data: Dict[str, Any]) -> SubcommandConfig:
        """Parse subcommands configuration."""
        subcommand_config = SubcommandConfig(
            title=subcommands_data.get('title'),
            description=subcommands_data.get('description'),
            dest=subcommands_data.get('dest')
        )
        
        if 'commands' in subcommands_data:
            for cmd_name, cmd_data in subcommands_data['commands'].items():
                subcommand = Subcommand(
                    description=cmd_data.get('description'),
                    help=cmd_data.get('help')
                )
                
                # Parse command arguments
                if 'arguments' in cmd_data:
                    subcommand.arguments = [
                        ArgumentConfig._parse_argument(arg_data)
                        for arg_data in cmd_data['arguments']
                    ]
                
                # Parse nested subcommands
                if 'subcommands' in cmd_data:
                    subcommand.subcommands = ArgumentConfig._parse_subcommands(cmd_data['subcommands'])
                
                # Parse argument groups for this subcommand
                if 'argument_groups' in cmd_data:
                    subcommand.argument_groups = [
                        ArgumentGroup(
                            title=group.get('title', ''),
                            description=group.get('description'),
                            arguments=group.get('arguments', [])
                        )
                        for group in cmd_data['argument_groups']
                    ]
                
                # Parse mutually exclusive groups for this subcommand
                if 'mutually_exclusive' in cmd_data:
                    subcommand.mutually_exclusive = [
                        MutuallyExclusiveGroup(
                            title=group.get('title'),
                            required=group.get('required', False),
                            arguments=group.get('arguments', [])
                        )
                        for group in cmd_data['mutually_exclusive']
                    ]
                
                subcommand_config.commands[cmd_name] = subcommand
        
        return subcommand_config