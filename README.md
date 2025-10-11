# GitCLI - Git Operations Automation

A user-friendly command-line interface for Git operations with interactive menus, visual feedback, and cross-platform support.

## Installation

### From PyPI (once published)
```bash
pip install gitcli-automation
```

### From Source
```bash
git clone https://github.com/Adelodunpeter25/GitCLI.git
cd gitcli
pip install -e .
```

## Usage

### Interactive Mode
```bash
gitcli
```

### Direct Command Mode
```bash
gitcli commit
gitcli push
gitcli status
gitcli qp  # quick push
gitcli sync  # pull then push
```

## Features

### Core Operations
- **commit** - Commit staged changes with interactive prompts
- **push** - Push changes to remote (with force push option on rejection)
- **pull** - Pull latest changes from remote
- **sync** - Pull then push in one command
- **fetch** - Fetch updates without merging
- **stage** - Stage changes (all or specific files)
- **status** - Show git status
- **log** - View commit history

### Branch Management
- **switch-branch** - Switch to another branch
- **add-branch** - Create new branch
- **delete-branch** - Delete a branch (with safety checks)
- **rename-branch** - Rename a branch
- **list-branch** - List all branches

### Advanced Features
- **quick-push (qp)** - Stage, commit & push in one go
- **diff** - Show unstaged changes
- **diff-staged** - Show staged changes
- **amend** - Amend last commit
- **reset** - Reset to previous commit
- **remotes** - Manage remote repositories
- **clone** - Clone a repository interactively

### User Experience
- 🎨 **Colored output** for better readability
- ⏳ **Loading spinners** for operations
- 🔔 **System notifications** (macOS/Linux/Windows)
- ⌨️ **Tab completion** in interactive mode
- 🛡️ **Safety checks** for destructive operations
- 🖥️ **Cross-platform** support (macOS, Linux, Windows)

## Project Structure

```
GitCLI/
├── gitcli/
│   ├── __init__.py
│   ├── cli.py              # Main entry point and CLI interface
│   ├── helpers.py          # Utility functions
│   ├── git_operations.py   # Core git operations
│   ├── git_branches.py     # Branch management
│   └── git_advanced.py     # Advanced operations
├── setup.py
├── pyproject.toml
├── LICENSE
├── README.md
└── requirements.txt
```

## Requirements

- Python 3.7+
- Git installed and configured
- colorama
- yaspin

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

Your Name - [GitHub](https://github.com/Adelodunpeter25)
