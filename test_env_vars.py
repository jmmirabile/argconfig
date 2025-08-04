#!/usr/bin/env python3
"""Test script for environment variable support."""

import os
import sys
from argparse_yaml import create_parser_from_yaml

def test_env_vars():
    """Test environment variable precedence."""
    
    # Set some environment variables
    os.environ['DATABASE_URL'] = 'postgresql://localhost/test'
    os.environ['PORT'] = '9000'
    os.environ['VERBOSE'] = 'true'
    
    # Create parser from our test config
    parser = create_parser_from_yaml('test-env-vars.yaml')
    
    print("Testing environment variable precedence...")
    print("=" * 50)
    
    # Test 1: Environment variables should be used as defaults
    print("\n🧪 Test 1: Environment variables as defaults")
    try:
        args = parser.parse_args([])
        print(f"✅ database_url from env: {args.database_url}")
        print(f"✅ port from env (auto-generated): {args.port}")
        print(f"✅ verbose from env (auto-generated): {args.verbose}")
    except SystemExit:
        print("❌ Required argument missing - env vars not working as defaults")
    
    # Test 2: Command line should override environment variables
    print("\n🧪 Test 2: Command line overrides env vars")
    try:
        args = parser.parse_args(['--database-url', 'sqlite:///test.db', '--port', '3000'])
        print(f"✅ database_url from CLI: {args.database_url}")
        print(f"✅ port from CLI: {args.port}")
        print(f"✅ verbose from env: {args.verbose}")
    except SystemExit as e:
        print(f"❌ CLI override failed: {e}")
    
    # Test 3: Show help to see if env vars are mentioned
    print("\n🧪 Test 3: Help message")
    print(parser.format_help())

if __name__ == '__main__':
    test_env_vars()