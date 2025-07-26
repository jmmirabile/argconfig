#!/usr/bin/env python3
"""
Example usage of the argconfig module.

This script demonstrates how to use YAML configuration files to create
complex command-line interfaces with argparse.
"""

import sys
import os
import yaml
sys.path.insert(0, os.path.dirname(__file__))
from argconfig import create_parser_from_yaml


def main():
    """Example main function demonstrating argconfig usage."""
    
    # Create parser from YAML configuration
    try:
        parser = create_parser_from_yaml('argconfig/data/schema_example.yaml')
    except FileNotFoundError:
        print("Error: schema_example.yaml not found!")
        print("Make sure you're running this from the project root directory.")
        return 1
    except Exception as e:
        print(f"Error creating parser: {e}")
        return 1
    
    # Parse command line arguments
    args = parser.parse_args()
    
    # Display parsed arguments
    print("Parsed arguments:")
    print("-" * 40)
    
    # Show all parsed arguments
    for key, value in vars(args).items():
        print(f"{key:15} = {value}")
    
    print("-" * 40)
    
    # Example of using the parsed arguments
    if hasattr(args, 'command'):
        print(f"\nCommand: {args.command}")
        
        if args.command == 'db':
            if hasattr(args, 'db_action'):
                print(f"Database action: {args.db_action}")
                if args.db_action == 'migrate':
                    print("Running database migration...")
                    if hasattr(args, 'dry_run') and args.dry_run:
                        print("(dry run mode)")
                elif args.db_action == 'backup':
                    if hasattr(args, 'backup_name'):
                        print(f"Creating backup: {args.backup_name}")
        
        elif args.command == 'file':
            if hasattr(args, 'file_action'):
                print(f"File action: {args.file_action}")
                if args.file_action == 'convert':
                    if hasattr(args, 'source') and hasattr(args, 'target'):
                        print(f"Converting {args.source} to {args.target}")
    
    # Show global configuration
    if hasattr(args, 'config'):
        print(f"\nUsing config file: {args.config}")
    
    if hasattr(args, 'log_level'):
        print(f"Log level: {args.log_level}")
    
    return 0


def demo_commands():
    """Print example commands that can be tested."""
    print("Example commands to try:")
    print("-" * 50)
    print("python example.py -h")
    print("python example.py --log-level DEBUG")
    print("python example.py --config myconfig.yaml db -h")
    print("python example.py db --host mydb.com migrate --dry-run")
    print("python example.py db backup mybackup --compress")
    print("python example.py file convert input.json output.yaml --format yaml")
    print("python example.py file validate config1.yaml config2.yaml --schema schema.json")
    print("-" * 50)


if __name__ == '__main__':
    if len(sys.argv) == 1:
        print("YAML Argument Parser Example")
        print("=" * 30)
        demo_commands()
        print("\nAdd arguments to see the parser in action!")
        sys.exit(0)
    
    sys.exit(main())
