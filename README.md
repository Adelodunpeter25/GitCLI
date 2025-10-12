# GitCLI - Git Operations Automation

GitCLI is a user-friendly command-line tool for Git that simplifies everyday operations. Perfect for developers who want powerful Git functionality without the complexity.

## Features

- 🎨 Colored output and loading spinners
- 🔔 System notifications (macOS/Linux/Windows)
- ⌨️ Tab completion in interactive mode
- 🛡️ Safety checks for destructive operations
- 🖥️ Cross-platform (macOS, Linux, Windows)
- 🚀 Direct command execution or interactive mode

## Installation

```bash
pip install gitcli-automation
```

## Quick Start

### Interactive Mode
```bash
gitcli
```

### Direct Commands
```bash
gitcli status
gitcli commit
gitcli push
gitcli qp              # quick push: stage + commit + push
gitcli sync            # pull + push
```

## Available Commands

### Core Operations
- `commit` - Commit staged changes
- `push` - Push to remote (with force push option)
- `pull` - Pull latest changes
- `sync` - Pull then push in one command
- `fetch` - Fetch updates without merging
- `stage` - Stage changes (all or specific files)
- `status` - Show git status
- `log` - View commit history
- `diff` - Show unstaged changes
- `diff-staged` - Show staged changes

### Branch Management
- `switch-branch` - Switch to another branch
- `add-branch` - Create new branch
- `delete-branch` - Delete a branch
- `rename-branch` - Rename a branch
- `list-branch` - List all branches

### Quick Operations
- `quick-push` or `qp` - Stage, commit & push in one go

### Advanced
- `amend` - Amend last commit
- `reset` - Reset to previous commit
- `remotes` - Manage remote repositories
- `clone` - Clone a repository

## Command Flexibility

Commands work with spaces, hyphens, or no spaces:
```bash
gitcli list-branch    # ✅
gitcli listbranch     # ✅
gitcli list branch    # ✅
```

## Examples

**Quick workflow:**
```bash
gitcli qp
```

**Standard workflow:**
```bash
gitcli status
gitcli diff
gitcli stage
gitcli commit
gitcli push
```

**Branch workflow:**
```bash
gitcli add-branch feature-x
# ... make changes ...
gitcli qp
gitcli switch-branch main
```

## Requirements

- Python 3.7+
- Git installed and configured

## Safety Features

- Confirmation prompts for destructive operations
- Branch protection (can't delete current branch)
- Remote validation before push/pull

## Contributing

Contributions welcome! Visit the [GitHub repository](https://github.com/Adelodunpeter25/GitCLI).

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Author

Adelodunpeter - [GitHub](https://github.com/Adelodunpeter25)
