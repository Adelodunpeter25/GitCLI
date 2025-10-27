# GitCLI - Git Operations Automation

GitCLI is a user-friendly command-line tool for Git that simplifies everyday operations. Perfect for developers who want powerful Git functionality without the complexity.

## Features

- 🚀 **Smart Save** - `gitcli save` handles everything with intelligent defaults
- 🤖 **Smart Commit Messages** - Learns from your history and suggests messages
- 🛡️ **Pre-save Validation** - Detects debug code, secrets, conflicts, and large files
- 🔄 **Auto-pull Before Push** - Prevents conflicts automatically
- ⚙️ **Fully Configurable** - Customize every behavior to match your style
- 🪝 **Git Hooks Management** - Built-in templates for linting, testing, formatting
- 🔧 **Conflict Resolution** - Interactive helper for merge conflicts
- �️ **Crosss-platform** - macOS, Linux, Windows

## Installation

### Quick Install (Recommended)

**One-line installer:**
```bash
curl -sSL https://raw.githubusercontent.com/Adelodunpeter25/GitCLI/main/install.sh | bash
```

### Alternative Methods

**Using pipx (recommended for Python users):**
```bash
pipx install gitcli-automation
```

**Using pip:**
```bash
pip install gitcli-automation
```

**From source:**
```bash
git clone https://github.com/Adelodunpeter25/GitCLI.git
cd GitCLI
pip install -e .
```

### Uninstall

```bash
curl -sSL https://raw.githubusercontent.com/Adelodunpeter25/GitCLI/main/uninstall.sh | bash
```

## Quick Start

```bash
# Make changes, then save everything
gitcli save

# Or with custom message
gitcli save "fix: resolve login bug"

# Configure behavior
gitcli config

# Interactive mode
gitcli
```

## Key Commands

**Smart Commands:**
- `save` / `save <message>` - Stage, commit, push with smart defaults
- `config` - Configure behavior

**Core:** `commit`, `push`, `pull`, `sync`, `status`, `log`, `diff`, `stage`, `qp`

**Branches:** `switch-branch`, `add-branch`, `delete-branch`, `list-branch`

**Stash:** `stash`, `stash-pop`, `stash-apply`, `stash-list`

**Advanced:** `hooks`, `resolve-conflicts`, `amend`, `reset`, `remotes`

Type `gitcli help` for full list.


## Examples

```bash
# Daily workflow
gitcli save                              # Smart save with auto-message
gitcli save "feat: add authentication"   # Custom message

# Branch workflow
gitcli add-branch feature-x
gitcli save
gitcli switch-branch main

# Stash workflow
gitcli stash
gitcli switch-branch main
gitcli stash-pop

# Hooks
gitcli hooks              # Setup automation
gitcli list-hooks         # View active hooks
```

## Requirements

- Python 3.7+
- Git installed and configured

## Git Hooks

Built-in templates for automation:
- **Pre-commit:** Linting, formatting, tests, debug detection
- **Pre-push:** Full tests, branch protection, build verification
- **Commit-msg:** Conventional commits, message validation
- **Post-commit:** Notifications, auto-backup

```bash
gitcli hooks       # Setup
gitcli list-hooks  # View active
```

## Configuration

Run `gitcli config` to customize behavior:

- **auto_stage** - Auto-stage all changes (default: true)
- **auto_push** - Prompt to push after commit (default: true)
- **learn_from_history** - Smart commit messages (default: true)
- **pre_save_validation** - Validate before commit (default: true)
- **auto_pull_before_push** - Sync before push (default: true)
- **auto_fix_formatting** - Run formatters (default: false)
- **confirm_force_push** - Confirm force push (default: true)

**Validation rules:** Detects debug code, secrets, conflicts, large files (configurable)

Config stored in `.gitcli-config.json`



## License

MIT License - see [LICENSE](LICENSE) file for details.

## Author

Adelodunpeter - [GitHub](https://github.com/Adelodunpeter25)
