#!/usr/bin/env python3
"""
Simple example showing basic argconfig usage.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from argconfig import create_parser_from_dict


def main():
    """Simple example with inline configuration."""
    
    # Define CLI configuration as a dictionary
    config = {
        'parser': {
            'prog': 'simple-tool',
            'description': 'A simple example tool',
        },
        
        'parent_arguments': [
            {
                'name': '--verbose',
                'short': '-v',
                'action': 'store_true',
                'help': 'Enable verbose output'
            },
            {
                'name': '--log-level',
                'short': '-l', 
                'type': 'str',
                'choices': '@logging_levels',  # Built-in resolver
                'default': 'INFO',
                'help': 'Set logging level'
            }
        ],
        
        'arguments': [
            {
                'name': 'input_file',
                'type': 'str',
                'help': 'Input file to process'
            },
            {
                'name': '--output',
                'short': '-o',
                'type': 'str',
                'default': '@current_dir',  # Built-in resolver for current directory
                'help': 'Output directory'
            }
        ],
        
        'subcommands': {
            'title': 'Available commands',
            'dest': 'command',
            'commands': {
                'process': {
                    'description': 'Process the input file',
                    'help': 'Process input file with various options',
                    'arguments': [
                        {
                            'name': '--format',
                            'type': 'str',
                            'choices': ['json', 'yaml', 'xml'],
                            'default': 'json',
                            'help': 'Output format'
                        }
                    ]
                }
            }
        }
    }
    
    # Create parser from configuration
    parser = create_parser_from_dict(config)
    
    # Parse arguments
    args = parser.parse_args()
    
    # Display results
    print("Simple Tool Results:")
    print("-" * 25)
    for key, value in vars(args).items():
        print(f"{key:12} = {value}")
    
    return 0


if __name__ == '__main__':
    if len(sys.argv) == 1:
        print("Simple YAML Argument Parser Example")
        print("=" * 40)
        print("Try these commands:")
        print("  python simple_example.py -h")
        print("  python simple_example.py --verbose input.txt")
        print("  python simple_example.py input.txt process --format yaml")
        print("  python simple_example.py -l DEBUG input.txt --output /tmp")
        sys.exit(0)
    
    sys.exit(main())