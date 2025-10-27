# GitCLI - Git Operations Automation

GitCLI is a user-friendly command-line tool for Git that simplifies everyday operations. Perfect for developers who want powerful Git functionality without the complexity.

## Features

- 🎨 Colored output and loading spinners
- 🔔 System notifications (macOS/Linux/Windows)
- ⌨️ Tab completion in interactive mode
- 🛡️ Safety checks for destructive operations
- 🖥️ Cross-platform (macOS, Linux, Windows)
- 🚀 Direct command execution or interactive mode
- 🪝 Git hooks management with built-in templates

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
- `hooks` - Manage Git hooks (automation)
- `list-hooks` - List installed hooks

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

**Git Hooks automation:**
```bash
gitcli hooks              # Manage hooks
gitcli list-hooks         # See installed hooks
```

## Requirements

- Python 3.7+
- Git installed and configured

## Git Hooks Automation

GitCLI includes powerful Git hooks management to automate your workflow:

### Available Hook Templates

**Pre-commit Hooks:**
- Code Linting - Run linters before each commit
- Auto-formatting - Format code automatically
- Run Tests - Execute test suite before commit
- Block Debug Code - Prevent commits with debug statements

**Pre-push Hooks:**
- Run Full Test Suite - Ensure all tests pass before push
- Protect Main Branch - Prevent direct pushes to main/master
- Build Before Push - Verify project builds successfully

**Commit Message Hooks:**
- Conventional Commits - Enforce conventional commit format
- Minimum Message Length - Require descriptive messages
- Block WIP Commits - Prevent work-in-progress commits

**Post-commit Hooks:**
- Commit Notification - Get notified after each commit
- Auto Backup - Create automatic backups

### Using Hooks

```bash
# Open hooks management menu
gitcli hooks

# View installed hooks
gitcli list-hooks
```

Hooks are stored in `.git/hooks/` and configuration is saved in `.gitcli-hooks.json` for easy sharing with your team.

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
