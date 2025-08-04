"""
Built-in resolvers for dynamic argument configuration values.
"""
import logging
import os
import sys
from typing import List, Any, Dict, Callable


class ChoiceResolvers:
    """Built-in resolvers for argument choices."""
    
    @staticmethod
    def logging_levels() -> List[str]:
        """Get all available Python logging levels."""
        return list(logging._nameToLevel.keys())
    
    @staticmethod
    def env_vars() -> List[str]:
        """Get all environment variable names."""
        return list(os.environ.keys())
    
    @staticmethod
    def file_extensions() -> List[str]:
        """Common file extensions."""
        return ['.txt', '.json', '.yaml', '.yml', '.xml', '.csv', '.log']
    
    @staticmethod
    def python_versions() -> List[str]:
        """Python version formats."""
        return ['3.8', '3.9', '3.10', '3.11', '3.12']


class DefaultResolvers:
    """Built-in resolvers for argument defaults."""
    
    @staticmethod
    def current_user() -> str:
        """Get current username."""
        return os.getenv('USER', os.getenv('USERNAME', 'unknown'))
    
    @staticmethod
    def current_dir() -> str:
        """Get current working directory."""
        return os.getcwd()
    
    @staticmethod
    def home_dir() -> str:
        """Get user home directory."""
        return os.path.expanduser('~')
    
    @staticmethod
    def temp_dir() -> str:
        """Get system temp directory."""
        import tempfile
        return tempfile.gettempdir()


class ResolverRegistry:
    """Registry for all built-in resolvers."""
    
    def __init__(self):
        self._choice_resolvers: Dict[str, Callable[[], List[Any]]] = {}
        self._default_resolvers: Dict[str, Callable[[], Any]] = {}
        self._register_builtin_resolvers()
    
    def _register_builtin_resolvers(self):
        """Register all built-in resolvers."""
        # Register choice resolvers
        for name in dir(ChoiceResolvers):
            if not name.startswith('_'):
                resolver = getattr(ChoiceResolvers, name)
                if callable(resolver):
                    self._choice_resolvers[name] = resolver
        
        # Register default resolvers
        for name in dir(DefaultResolvers):
            if not name.startswith('_'):
                resolver = getattr(DefaultResolvers, name)
                if callable(resolver):
                    self._default_resolvers[name] = resolver
    
    def resolve_choices(self, resolver_name: str) -> List[Any]:
        """Resolve choices using a registered resolver."""
        if resolver_name not in self._choice_resolvers:
            raise ValueError(f"Unknown choice resolver: {resolver_name}")
        
        return self._choice_resolvers[resolver_name]()
    
    def resolve_default(self, resolver_name: str) -> Any:
        """Resolve default value using a registered resolver."""
        if resolver_name not in self._default_resolvers:
            raise ValueError(f"Unknown default resolver: {resolver_name}")
        
        return self._default_resolvers[resolver_name]()
    
    def is_choice_resolver(self, value: str) -> bool:
        """Check if a value is a choice resolver pattern (@resolver_name)."""
        return isinstance(value, str) and value.startswith('@') and value[1:] in self._choice_resolvers
    
    def is_default_resolver(self, value: str) -> bool:
        """Check if a value is a default resolver pattern (@resolver_name)."""
        return isinstance(value, str) and value.startswith('@') and value[1:] in self._default_resolvers
    
    def get_choice_resolver_name(self, value: str) -> str:
        """Extract resolver name from choice resolver pattern."""
        if self.is_choice_resolver(value):
            return value[1:]  # Remove @ prefix
        raise ValueError(f"Not a valid choice resolver pattern: {value}")
    
    def get_default_resolver_name(self, value: str) -> str:
        """Extract resolver name from default resolver pattern."""
        if self.is_default_resolver(value):
            return value[1:]  # Remove @ prefix
        raise ValueError(f"Not a valid default resolver pattern: {value}")
    
    def list_choice_resolvers(self) -> List[str]:
        """Get list of available choice resolvers."""
        return list(self._choice_resolvers.keys())
    
    def list_default_resolvers(self) -> List[str]:
        """Get list of available default resolvers."""
        return list(self._default_resolvers.keys())


# Global resolver registry instance
resolver_registry = ResolverRegistry()