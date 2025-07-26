# Examples

This document provides complete, working examples of using argconfig for various types of CLI applications.

## Table of Contents

1. [Simple File Processor](#simple-file-processor)
2. [Database Management Tool](#database-management-tool)
3. [Development Workflow Tool](#development-workflow-tool)
4. [API Client Tool](#api-client-tool)
5. [Configuration Management Tool](#configuration-management-tool)
6. [Log Analysis Tool](#log-analysis-tool)

## Simple File Processor

A basic tool for processing files with format conversion.

### CLI Setup

```bash
# Create the configuration
argconfig-manage setup fileproc

# Add main arguments
argconfig-manage add-argument \
  --parser-path=fileproc \
  --arg="input_file" \
  --type=str \
  --help-text="Input file to process"

argconfig-manage add-argument \
  --parser-path=fileproc \
  --arg="--output" \
  --type=str \
  --default="@current_dir" \
  --help-text="Output directory"

# Add convert subcommand
argconfig-manage add-argument \
  --parser-path=fileproc.convert \
  --arg="--from-format" \
  --choices="json,yaml,xml,csv" \
  --required \
  --help-text="Source format"

argconfig-manage add-argument \
  --parser-path=fileproc.convert \
  --arg="--to-format" \
  --choices="json,yaml,xml,csv" \
  --required \
  --help-text="Target format"

# Add validate subcommand
argconfig-manage add-argument \
  --parser-path=fileproc.validate \
  --arg="--schema" \
  --help-text="Schema file for validation"

argconfig-manage add-argument \
  --parser-path=fileproc.validate \
  --arg="--strict" \
  --action=store_true \
  --help-text="Enable strict validation"
```

### Generated Configuration

```yaml
parser:
  prog: fileproc
  description: fileproc - CLI application
  epilog: Use 'fileproc --help' for more information

parent_arguments:
- name: --log-level
  short: -l
  type: str
  choices: '@logging_levels'
  default: INFO
  help: Set logging level

arguments:
- name: input_file
  type: str
  help: Input file to process
- name: --output
  type: str
  default: '@current_dir'
  help: Output directory

subcommands:
  title: Available commands
  dest: command
  commands:
    convert:
      description: convert command
      help: Execute convert operations
      arguments:
      - name: --from-format
        help: Source format
        choices:
        - json
        - yaml
        - xml
        - csv
        required: true
      - name: --to-format
        help: Target format
        choices:
        - json
        - yaml
        - xml
        - csv
        required: true
    validate:
      description: validate command
      help: Execute validate operations
      arguments:
      - name: --schema
        help: Schema file for validation
      - name: --strict
        action: store_true
        help: Enable strict validation
```

### Python Implementation

```python
#!/usr/bin/env python3
"""
File processor CLI tool using argconfig.
"""
import sys
import json
import yaml
import logging
from pathlib import Path
from argconfig import create_parser_from_yaml


def setup_logging(level: str):
    """Setup logging configuration."""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(levelname)s - %(message)s'
    )


def convert_file(args):
    """Convert file from one format to another."""
    logging.info(f"Converting {args.input_file} from {args.from_format} to {args.to_format}")
    
    input_path = Path(args.input_file)
    output_path = Path(args.output) / f"{input_path.stem}.{args.to_format}"
    
    # Load data based on source format
    with open(input_path) as f:
        if args.from_format == 'json':
            data = json.load(f)
        elif args.from_format == 'yaml':
            data = yaml.safe_load(f)
        else:
            raise ValueError(f"Unsupported source format: {args.from_format}")
    
    # Save data in target format
    with open(output_path, 'w') as f:
        if args.to_format == 'json':
            json.dump(data, f, indent=2)
        elif args.to_format == 'yaml':
            yaml.dump(data, f, default_flow_style=False)
        else:
            raise ValueError(f"Unsupported target format: {args.to_format}")
    
    logging.info(f"Converted file saved to {output_path}")


def validate_file(args):
    """Validate file format and optionally against schema."""
    logging.info(f"Validating {args.input_file}")
    
    input_path = Path(args.input_file)
    
    try:
        with open(input_path) as f:
            if input_path.suffix == '.json':
                json.load(f)
            elif input_path.suffix in ['.yaml', '.yml']:
                yaml.safe_load(f)
            else:
                raise ValueError(f"Unsupported file format: {input_path.suffix}")
        
        logging.info("File validation passed")
        
        if args.schema:
            logging.info(f"Schema validation against {args.schema}")
            # Schema validation logic would go here
            
    except Exception as e:
        logging.error(f"Validation failed: {e}")
        return False
    
    return True


def main():
    """Main entry point."""
    try:
        parser = create_parser_from_yaml('argconfig.yaml')
        args = parser.parse_args()
        
        setup_logging(args.log_level)
        
        if hasattr(args, 'command'):
            if args.command == 'convert':
                convert_file(args)
            elif args.command == 'validate':
                if not validate_file(args):
                    sys.exit(1)
        else:
            parser.print_help()
            
    except Exception as e:
        logging.error(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
```

### Usage Examples

```bash
# Convert JSON to YAML
fileproc data.json convert --from-format json --to-format yaml

# Validate a file
fileproc config.yaml validate --strict

# Validate with schema
fileproc data.json validate --schema schema.json --log-level DEBUG
```

## Database Management Tool

A comprehensive database management CLI with connection handling, migrations, and backups.

### CLI Setup

```bash
# Create the configuration
argconfig-manage setup dbtool

# Add database connection arguments to main parser
argconfig-manage add-argument \
  --parser-path=dbtool \
  --arg="--host" \
  --default="localhost" \
  --help-text="Database host"

argconfig-manage add-argument \
  --parser-path=dbtool \
  --arg="--port" \
  --type=int \
  --default=5432 \
  --help-text="Database port"

argconfig-manage add-argument \
  --parser-path=dbtool \
  --arg="--database" \
  --required \
  --help-text="Database name"

argconfig-manage add-argument \
  --parser-path=dbtool \
  --arg="--user" \
  --default="@current_user" \
  --help-text="Database user"

# Migration subcommands
argconfig-manage add-argument \
  --parser-path=dbtool.migrate.up \
  --arg="--steps" \
  --type=int \
  --help-text="Number of migrations to apply"

argconfig-manage add-argument \
  --parser-path=dbtool.migrate.down \
  --arg="--steps" \
  --type=int \
  --required \
  --help-text="Number of migrations to rollback"

argconfig-manage add-argument \
  --parser-path=dbtool.migrate \
  --arg="--dry-run" \
  --action=store_true \
  --help-text="Show what would be done without executing"

# Backup subcommand
argconfig-manage add-argument \
  --parser-path=dbtool.backup \
  --arg="backup_name" \
  --help-text="Name for the backup file"

argconfig-manage add-argument \
  --parser-path=dbtool.backup \
  --arg="--format" \
  --choices="sql,binary,csv" \
  --default="sql" \
  --help-text="Backup format"

argconfig-manage add-argument \
  --parser-path=dbtool.backup \
  --arg="--compress" \
  --action=store_true \
  --help-text="Compress the backup file"

# Restore subcommand
argconfig-manage add-argument \
  --parser-path=dbtool.restore \
  --arg="backup_file" \
  --help-text="Backup file to restore from"

argconfig-manage add-argument \
  --parser-path=dbtool.restore \
  --arg="--force" \
  --action=store_true \
  --help-text="Force restore without confirmation"
```

### Python Implementation

```python
#!/usr/bin/env python3
"""
Database management tool using argconfig.
"""
import sys
import logging
import subprocess
from pathlib import Path
from argconfig import create_parser_from_yaml


class DatabaseManager:
    """Database management operations."""
    
    def __init__(self, args):
        self.args = args
        self.connection_params = {
            'host': args.host,
            'port': args.port,
            'database': args.database,
            'user': args.user
        }
    
    def get_connection_string(self):
        """Build database connection string."""
        return f"postgresql://{self.args.user}@{self.args.host}:{self.args.port}/{self.args.database}"
    
    def run_command(self, cmd, check=True):
        """Run shell command with logging."""
        logging.info(f"Executing: {' '.join(cmd)}")
        if hasattr(self.args, 'dry_run') and self.args.dry_run:
            logging.info("DRY RUN: Command not executed")
            return
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=check)
        if result.stdout:
            logging.info(result.stdout)
        if result.stderr:
            logging.error(result.stderr)
        return result


def migrate_up(manager):
    """Apply database migrations."""
    steps = getattr(manager.args, 'steps', None)
    
    cmd = ['migrate', '-database', manager.get_connection_string(), 'up']
    if steps:
        cmd.append(str(steps))
    
    logging.info(f"Applying migrations (steps: {steps or 'all'})")
    manager.run_command(cmd)


def migrate_down(manager):
    """Rollback database migrations."""
    steps = manager.args.steps
    
    cmd = ['migrate', '-database', manager.get_connection_string(), 'down', str(steps)]
    
    logging.info(f"Rolling back {steps} migration(s)")
    manager.run_command(cmd)


def backup_database(manager):
    """Create database backup."""
    backup_name = manager.args.backup_name
    backup_format = manager.args.format
    
    if backup_format == 'sql':
        output_file = f"{backup_name}.sql"
        cmd = [
            'pg_dump',
            '-h', manager.args.host,
            '-p', str(manager.args.port),
            '-U', manager.args.user,
            '-d', manager.args.database,
            '-f', output_file
        ]
    elif backup_format == 'binary':
        output_file = f"{backup_name}.dump"
        cmd = [
            'pg_dump',
            '-h', manager.args.host,
            '-p', str(manager.args.port),
            '-U', manager.args.user,
            '-d', manager.args.database,
            '-Fc',  # Custom format
            '-f', output_file
        ]
    else:
        raise ValueError(f"Unsupported backup format: {backup_format}")
    
    logging.info(f"Creating {backup_format} backup: {output_file}")
    manager.run_command(cmd)
    
    if manager.args.compress and backup_format == 'sql':
        logging.info("Compressing backup...")
        manager.run_command(['gzip', output_file])


def restore_database(manager):
    """Restore database from backup."""
    backup_file = Path(manager.args.backup_file)
    
    if not backup_file.exists():
        logging.error(f"Backup file not found: {backup_file}")
        return False
    
    if not manager.args.force:
        response = input(f"This will replace the database '{manager.args.database}'. Continue? (y/N): ")
        if response.lower() != 'y':
            logging.info("Restore cancelled")
            return False
    
    if backup_file.suffix == '.sql':
        cmd = [
            'psql',
            '-h', manager.args.host,
            '-p', str(manager.args.port),
            '-U', manager.args.user,
            '-d', manager.args.database,
            '-f', str(backup_file)
        ]
    elif backup_file.suffix == '.dump':
        cmd = [
            'pg_restore',
            '-h', manager.args.host,
            '-p', str(manager.args.port),
            '-U', manager.args.user,
            '-d', manager.args.database,
            str(backup_file)
        ]
    else:
        raise ValueError(f"Unsupported backup file format: {backup_file.suffix}")
    
    logging.info(f"Restoring from backup: {backup_file}")
    manager.run_command(cmd)


def main():
    """Main entry point."""
    try:
        parser = create_parser_from_yaml('argconfig.yaml')
        args = parser.parse_args()
        
        # Setup logging
        logging.basicConfig(
            level=getattr(logging, args.log_level.upper()),
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        
        manager = DatabaseManager(args)
        
        if hasattr(args, 'command'):
            if args.command == 'migrate':
                if hasattr(args, 'migrate_action'):
                    if args.migrate_action == 'up':
                        migrate_up(manager)
                    elif args.migrate_action == 'down':
                        migrate_down(manager)
                else:
                    logging.error("Migration action required (up/down)")
            elif args.command == 'backup':
                backup_database(manager)
            elif args.command == 'restore':
                restore_database(manager)
        else:
            parser.print_help()
            
    except Exception as e:
        logging.error(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
```

### Usage Examples

```bash
# Apply all pending migrations
dbtool --database myapp_prod migrate up

# Apply specific number of migrations with dry run
dbtool --database myapp_dev migrate up --steps 3 --dry-run

# Rollback migrations
dbtool --database myapp_dev migrate down --steps 2

# Create compressed SQL backup
dbtool --database myapp_prod backup prod_backup_20241127 --format sql --compress

# Create binary backup
dbtool --database myapp_prod backup prod_backup_20241127 --format binary

# Restore from backup
dbtool --database myapp_dev restore prod_backup_20241127.sql --force
```

## Development Workflow Tool

A tool for managing development workflows with Git integration, testing, and deployment.

### CLI Setup

```bash
# Create the configuration
argconfig-manage setup devtool

# Add project path argument
argconfig-manage add-argument \
  --parser-path=devtool \
  --arg="--project-path" \
  --default="@current_dir" \
  --help-text="Path to project directory"

# Git operations
argconfig-manage add-argument \
  --parser-path=devtool.git.commit \
  --arg="message" \
  --help-text="Commit message"

argconfig-manage add-argument \
  --parser-path=devtool.git.commit \
  --arg="--all" \
  --action=store_true \
  --help-text="Add all files before committing"

argconfig-manage add-argument \
  --parser-path=devtool.git.branch \
  --arg="branch_name" \
  --help-text="Branch name to create or switch to"

argconfig-manage add-argument \
  --parser-path=devtool.git.branch \
  --arg="--create" \
  --action=store_true \
  --help-text="Create new branch"

# Testing operations
argconfig-manage add-argument \
  --parser-path=devtool.test \
  --arg="--coverage" \
  --action=store_true \
  --help-text="Run with coverage report"

argconfig-manage add-argument \
  --parser-path=devtool.test \
  --arg="--pattern" \
  --default="test_*.py" \
  --help-text="Test file pattern"

argconfig-manage add-argument \
  --parser-path=devtool.test \
  --arg="--parallel" \
  --type=int \
  --help-text="Number of parallel test processes"

# Build operations
argconfig-manage add-argument \
  --parser-path=devtool.build \
  --arg="--clean" \
  --action=store_true \
  --help-text="Clean build artifacts first"

argconfig-manage add-argument \
  --parser-path=devtool.build \
  --arg="--target" \
  --choices="development,staging,production" \
  --default="development" \
  --help-text="Build target environment"

# Deploy operations
argconfig-manage add-argument \
  --parser-path=devtool.deploy \
  --arg="environment" \
  --choices="staging,production" \
  --help-text="Deployment environment"

argconfig-manage add-argument \
  --parser-path=devtool.deploy \
  --arg="--no-tests" \
  --action=store_true \
  --help-text="Skip running tests before deployment"

argconfig-manage add-argument \
  --parser-path=devtool.deploy \
  --arg="--force" \
  --action=store_true \
  --help-text="Force deployment without confirmation"
```

### Python Implementation

```python
#!/usr/bin/env python3
"""
Development workflow tool using argconfig.
"""
import os
import sys
import logging
import subprocess
from pathlib import Path
from argconfig import create_parser_from_yaml


class DevTool:
    """Development workflow operations."""
    
    def __init__(self, args):
        self.args = args
        self.project_path = Path(args.project_path)
        
        # Change to project directory
        os.chdir(self.project_path)
        logging.info(f"Working in: {self.project_path}")
    
    def run_command(self, cmd, check=True, shell=False):
        """Run command with logging."""
        cmd_str = cmd if isinstance(cmd, str) else ' '.join(cmd)
        logging.info(f"Running: {cmd_str}")
        
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            check=check,
            shell=shell
        )
        
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        
        return result


def git_commit(devtool):
    """Commit changes to git."""
    if devtool.args.all:
        devtool.run_command(['git', 'add', '.'])
    
    devtool.run_command(['git', 'commit', '-m', devtool.args.message])
    logging.info("Changes committed successfully")


def git_branch(devtool):
    """Create or switch git branch."""
    branch_name = devtool.args.branch_name
    
    if devtool.args.create:
        devtool.run_command(['git', 'checkout', '-b', branch_name])
        logging.info(f"Created and switched to branch: {branch_name}")
    else:
        devtool.run_command(['git', 'checkout', branch_name])
        logging.info(f"Switched to branch: {branch_name}")


def run_tests(devtool):
    """Run project tests."""
    cmd = ['python', '-m', 'pytest']
    
    if devtool.args.coverage:
        cmd.extend(['--cov', '--cov-report', 'html'])
    
    if devtool.args.pattern:
        cmd.extend(['-k', devtool.args.pattern])
    
    if devtool.args.parallel:
        cmd.extend(['-n', str(devtool.args.parallel)])
    
    result = devtool.run_command(cmd, check=False)
    
    if result.returncode == 0:
        logging.info("All tests passed")
        return True
    else:
        logging.error("Some tests failed")
        return False


def build_project(devtool):
    """Build the project."""
    if devtool.args.clean:
        logging.info("Cleaning build artifacts...")
        devtool.run_command(['rm', '-rf', 'build/', 'dist/', '*.egg-info/'], shell=True)
    
    target = devtool.args.target
    logging.info(f"Building for {target} environment...")
    
    # Set environment variable for build target
    env = os.environ.copy()
    env['BUILD_TARGET'] = target
    
    # Run build command
    cmd = ['python', 'setup.py', 'build']
    
    result = subprocess.run(
        cmd,
        env=env,
        capture_output=True,
        text=True,
        check=False
    )
    
    if result.returncode == 0:
        logging.info("Build completed successfully")
        return True
    else:
        logging.error("Build failed")
        print(result.stderr, file=sys.stderr)
        return False


def deploy_project(devtool):
    """Deploy the project to specified environment."""
    environment = devtool.args.environment
    
    # Run tests first unless explicitly skipped
    if not devtool.args.no_tests:
        logging.info("Running tests before deployment...")
        if not run_tests(devtool):
            logging.error("Tests failed, deployment aborted")
            return False
    
    # Confirm deployment
    if not devtool.args.force:
        response = input(f"Deploy to {environment}? (y/N): ")
        if response.lower() != 'y':
            logging.info("Deployment cancelled")
            return False
    
    logging.info(f"Deploying to {environment}...")
    
    # Deployment logic would go here
    # This could involve Docker, Kubernetes, cloud providers, etc.
    deploy_script = f"scripts/deploy_{environment}.sh"
    
    if Path(deploy_script).exists():
        devtool.run_command(['bash', deploy_script])
    else:
        logging.warning(f"Deployment script not found: {deploy_script}")
        logging.info("Manual deployment steps required")
    
    logging.info(f"Deployment to {environment} completed")


def main():
    """Main entry point."""
    try:
        parser = create_parser_from_yaml('argconfig.yaml')
        args = parser.parse_args()
        
        # Setup logging
        logging.basicConfig(
            level=getattr(logging, args.log_level.upper()),
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        
        devtool = DevTool(args)
        
        if hasattr(args, 'command'):
            if args.command == 'git':
                if hasattr(args, 'git_action'):
                    if args.git_action == 'commit':
                        git_commit(devtool)
                    elif args.git_action == 'branch':
                        git_branch(devtool)
            elif args.command == 'test':
                run_tests(devtool)
            elif args.command == 'build':
                build_project(devtool)
            elif args.command == 'deploy':
                deploy_project(devtool)
        else:
            parser.print_help()
            
    except Exception as e:
        logging.error(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
```

### Usage Examples

```bash
# Git operations
devtool git commit "Add new feature" --all
devtool git branch feature/new-ui --create

# Testing
devtool test --coverage --parallel 4
devtool test --pattern "test_auth*"

# Building
devtool build --clean --target production
devtool build --target staging

# Deployment
devtool deploy staging --no-tests
devtool deploy production --force
```

These examples demonstrate the power and flexibility of argconfig for building sophisticated CLI tools. Each example shows:

1. **CLI Setup** - How to use `argconfig-manage` to build the configuration
2. **Generated YAML** - The resulting configuration structure
3. **Python Implementation** - Complete working code that uses the configuration
4. **Usage Examples** - Real command-line usage patterns

The examples progress from simple to complex, showing how argconfig scales from basic file processing tools to sophisticated development and deployment workflows.