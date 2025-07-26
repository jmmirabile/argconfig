# CLI Reference

Complete reference for the `argconfig-manage` command-line tool.

## Overview

`argconfig-manage` is a command-line tool for creating and managing YAML-based argument parser configurations. It provides an interactive way to build complex CLI interfaces without manually editing YAML files.

## Global Options

All commands support these global options:

- `--config`, `-c` - Path to the argconfig YAML file (default: `argconfig.yaml`)

## Commands

### setup

Create a new argconfig YAML file with basic structure.

**Syntax:**
```bash
argconfig-manage setup <app_name> [--config <file>]
```

**Arguments:**
- `app_name` - Name of your application (required)

**Options:**
- `--config`, `-c` - Output file path (default: `argconfig.yaml`)

**Example:**
```bash
argconfig-manage setup myapp
argconfig-manage setup dbtool --config db_cli.yaml
```

**Creates:**
- Basic parser configuration with app name
- Default `--log-level/-l` parent argument with `@logging_levels` resolver
- Empty arguments and subcommands sections

### list-parsers

Display the hierarchy of parsers and their arguments in a tree format.

**Syntax:**
```bash
argconfig-manage list-parsers [--config <file>]
```

**Options:**
- `--config`, `-c` - Config file to read (default: `argconfig.yaml`)

**Example:**
```bash
argconfig-manage list-parsers
argconfig-manage list-parsers --config my_cli.yaml
```

**Output Format:**
```
📋 Parser hierarchy for 'myapp':
==================================================
📁 myapp (main parser)
  📎 Parent arguments (shared):
    • --log-level/-l (str)
      Set logging level
  📝 Arguments:
    • input_file (str)
      Input file to process
  📂 Subcommands:
    📁 process -> myapp.process
      • --format
        Output format
```

### add-argument

Add an argument to a specific parser in the configuration.

**Syntax:**
```bash
argconfig-manage add-argument [options]
```

**Required Options:**
- `--parser-path` - Target parser path (e.g., `myapp`, `myapp.db.migrate`)
- `--arg` - Argument name (e.g., `--verbose`, `-v`, `input_file`)

**Core Options:**
- `--help-text` - Help text for the argument
- `--dest` - Destination variable name

**Type and Validation:**
- `--type` - Argument type: `str`, `int`, `float`, `bool`
- `--choices` - Valid choices (comma-separated or `@resolver`)
- `--action` - Action type (see Actions section below)

**Behavior Options:**
- `--default` - Default value
- `--required` - Make this argument required (flag)
- `--nargs` - Number of arguments (see Nargs section below)

**Additional Options:**
- `--const` - Constant value for `store_const`/`append_const` actions
- `--metavar` - Name for the argument in usage messages
- `--config`, `-c` - Config file to modify (default: `argconfig.yaml`)

## Parser Paths

Parser paths use dot notation to specify where arguments should be added:

| Path | Target | CLI Result |
|------|--------|------------|
| `myapp` | Main parser | `myapp --arg` |
| `myapp.db` | 'db' subcommand | `myapp db --arg` |
| `myapp.db.migrate` | 'migrate' sub-subcommand | `myapp db migrate --arg` |
| `myapp.file.convert` | 'convert' under 'file' | `myapp file convert --arg` |

**Auto-creation:** Missing subcommands are automatically created with default descriptions.

## Argument Types

### --type Options

| Type | Description | Example Value |
|------|-------------|---------------|
| `str` | String (default) | `"hello"` |
| `int` | Integer | `42` |
| `float` | Float | `3.14` |
| `bool` | Boolean | `true`/`false` |

**Note:** Type conversion is automatic. String values `"true"`/`"false"` become booleans, numeric strings become numbers.

## Actions

### --action Options

| Action | Description | Usage |
|--------|-------------|-------|
| `store` | Store argument value (default) | `--file config.txt` |
| `store_true` | Set to True when present | `--verbose` |
| `store_false` | Set to False when present | `--no-cache` |
| `append` | Append to list | `--include dir1 --include dir2` |
| `append_const` | Append constant to list | `--feature-x --feature-y` |
| `store_const` | Store constant value | `--mode=debug` |
| `count` | Count occurrences | `-vvv` (verbose level) |
| `help` | Show help and exit | `--help` |
| `version` | Show version and exit | `--version` |

### Action Examples

```bash
# store_true: Boolean flag
argconfig-manage add-argument --parser-path=myapp --arg="--verbose" --action=store_true

# append: Multiple values
argconfig-manage add-argument --parser-path=myapp --arg="--include" --action=append --help-text="Include directory"

# store_const: Constant value
argconfig-manage add-argument --parser-path=myapp --arg="--debug" --action=store_const --const="DEBUG" --dest="log_level"

# count: Counting occurrences
argconfig-manage add-argument --parser-path=myapp --arg="--verbose" --action=count --help-text="Increase verbosity"
```

## Choices

### Static Choices

Comma-separated list of valid values:

```bash
argconfig-manage add-argument --parser-path=myapp --arg="--format" --choices="json,yaml,xml" --default="json"
```

### Dynamic Choices (Resolvers)

Use `@resolver_name` for dynamic values:

```bash
argconfig-manage add-argument --parser-path=myapp --arg="--log-level" --choices="@logging_levels" --default="INFO"
```

**Available Choice Resolvers:**
- `@logging_levels` - All Python logging levels
- `@env_vars` - Environment variable names
- `@file_extensions` - Common file extensions
- `@python_versions` - Python version strings

## Nargs (Number of Arguments)

### --nargs Options

| Value | Description | Example |
|-------|-------------|---------|
| `?` | Optional (0 or 1) | `--config [file]` |
| `*` | Zero or more | `--files [file1 file2 ...]` |
| `+` | One or more | `--inputs file1 [file2 ...]` |
| `N` | Exactly N arguments | `--coords x y` (N=2) |

### Nargs Examples

```bash
# Optional argument
argconfig-manage add-argument --parser-path=myapp --arg="--config" --nargs="?" --default="config.yaml"

# Multiple files
argconfig-manage add-argument --parser-path=myapp --arg="--files" --nargs="*" --help-text="Input files"

# Required multiple
argconfig-manage add-argument --parser-path=myapp --arg="--inputs" --nargs="+" --help-text="At least one input"

# Exactly 2 coordinates
argconfig-manage add-argument --parser-path=myapp --arg="--position" --nargs="2" --metavar="X Y"
```

## Default Values

### Static Defaults

```bash
argconfig-manage add-argument --parser-path=myapp --arg="--timeout" --type=int --default="30"
```

### Dynamic Defaults (Resolvers)

```bash
argconfig-manage add-argument --parser-path=myapp --arg="--output-dir" --default="@current_dir"
```

**Available Default Resolvers:**
- `@current_user` - Current username
- `@current_dir` - Current working directory
- `@home_dir` - User home directory
- `@temp_dir` - System temp directory

## Complex Examples

### Database CLI Tool

```bash
# Setup
argconfig-manage setup dbtool

# Connection arguments (would typically be parent_arguments)
argconfig-manage add-argument --parser-path=dbtool.connect --arg="--host" --default="localhost" --help-text="Database host"
argconfig-manage add-argument --parser-path=dbtool.connect --arg="--port" --type=int --default="5432" --help-text="Database port"
argconfig-manage add-argument --parser-path=dbtool.connect --arg="--user" --default="@current_user" --help-text="Database user"

# Migration commands
argconfig-manage add-argument --parser-path=dbtool.migrate.up --arg="--steps" --type=int --help-text="Number of migrations"
argconfig-manage add-argument --parser-path=dbtool.migrate.down --arg="--steps" --type=int --required --help-text="Steps to rollback"
argconfig-manage add-argument --parser-path=dbtool.migrate --arg="--dry-run" --action=store_true --help-text="Show what would be done"

# Backup commands
argconfig-manage add-argument --parser-path=dbtool.backup --arg="backup_name" --help-text="Name for backup"
argconfig-manage add-argument --parser-path=dbtool.backup --arg="--format" --choices="sql,binary" --default="sql"
argconfig-manage add-argument --parser-path=dbtool.backup --arg="--compress" --action=store_true
```

**Resulting CLI:**
```bash
dbtool migrate up --steps 5 --dry-run
dbtool migrate down --steps 2
dbtool backup production_backup --format binary --compress
```

### File Processing Tool

```bash
# Setup
argconfig-manage setup fileproc

# Main arguments
argconfig-manage add-argument --parser-path=fileproc --arg="input_files" --nargs="+" --help-text="Input files to process"
argconfig-manage add-argument --parser-path=fileproc --arg="--output-dir" --default="@current_dir" --help-text="Output directory"
argconfig-manage add-argument --parser-path=fileproc --arg="--recursive" --action=store_true --help-text="Process recursively"

# Convert subcommand
argconfig-manage add-argument --parser-path=fileproc.convert --arg="--from-format" --choices="json,yaml,xml,csv" --required --help-text="Source format"
argconfig-manage add-argument --parser-path=fileproc.convert --arg="--to-format" --choices="json,yaml,xml,csv" --required --help-text="Target format"
argconfig-manage add-argument --parser-path=fileproc.convert --arg="--preserve-structure" --action=store_true

# Validate subcommand
argconfig-manage add-argument --parser-path=fileproc.validate --arg="--schema" --help-text="Schema file for validation"
argconfig-manage add-argument --parser-path=fileproc.validate --arg="--strict" --action=store_true --help-text="Strict validation mode"
argconfig-manage add-argument --parser-path=fileproc.validate --arg="--format" --choices="@file_extensions" --help-text="Expected format"
```

**Resulting CLI:**
```bash
fileproc file1.json file2.json --output-dir /tmp convert --from-format json --to-format yaml
fileproc *.xml --recursive validate --schema schema.xsd --strict
```

## Tips and Best Practices

### 1. Use Equals Syntax for Arguments Starting with Dashes

```bash
# Good
argconfig-manage add-argument --parser-path=myapp --arg="--verbose" --action=store_true

# Also good (equals syntax)
argconfig-manage add-argument --parser-path=myapp --arg="--verbose" --action=store_true
```

### 2. Leverage Resolvers for Common Patterns

```bash
# Instead of hardcoding choices
argconfig-manage add-argument --parser-path=myapp --arg="--log-level" --choices="DEBUG,INFO,WARNING,ERROR"

# Use resolver for all levels including CRITICAL, FATAL, etc.
argconfig-manage add-argument --parser-path=myapp --arg="--log-level" --choices="@logging_levels"
```

### 3. Use Descriptive Parser Paths

```bash
# Clear hierarchy
myapp.database.migrate.up
myapp.files.convert.images
myapp.api.server.start
```

### 4. Group Related Arguments

```bash
# Connection arguments
myapp.connect --host --port --user --password

# Processing arguments  
myapp.process --input --output --format --strict
```

### 5. Use list-parsers Frequently

Check your CLI structure as you build:

```bash
argconfig-manage add-argument --parser-path=myapp --arg="--verbose" --action=store_true
argconfig-manage list-parsers  # Check the structure
argconfig-manage add-argument --parser-path=myapp.process --arg="--format" --choices="json,yaml"
argconfig-manage list-parsers  # Check again
```

## Troubleshooting

### Common Issues

1. **"No configuration found"** - Run `argconfig-manage setup <app_name>` first

2. **Argument conflicts** - Use `argconfig-manage list-parsers` to see existing arguments

3. **Parser path not found** - Missing subcommands are auto-created, check spelling

4. **Invalid choices format** - Use comma-separated values: `"json,yaml,xml"`

5. **Boolean values** - Use `--action=store_true` instead of `--type=bool --default=false`

### Getting Help

```bash
# General help
argconfig-manage --help

# Command-specific help
argconfig-manage add-argument --help
argconfig-manage setup --help
argconfig-manage list-parsers --help
```