# GitCLI - Git Operations Automation

A user-friendly command-line interface for Git operations with interactive menus, visual feedback, and cross-platform support.

## Features

- 🎨 **Colored output** for better readability
- ⏳ **Loading spinners** for operations
- 🔔 **System notifications** (macOS/Linux/Windows)
- ⌨️ **Tab completion** in interactive mode
- 🛡️ **Safety checks** for destructive operations
- 🖥️ **Cross-platform** support (macOS, Linux, Windows)
- 🚀 **Direct command execution** or interactive mode

## Installation

### From PyPI
```bash
pip3 install gitcli-automation
# Windows: pip install gitcli-automation
```

### From Source
```bash
git clone https://github.com/Adelodunpeter25/GitCLI.git
cd gitcli
pip install -e .
```

## Usage

### Interactive Mode
Launch the interactive menu:
```bash
gitcli
```

### Direct Command Mode
Execute commands directly:
```bash
gitcli <command>
# e.g., gitcli commit
```

## Available Commands

### Core Operations

#### `commit`
Commit staged changes with an interactive prompt for the commit message.
```bash
gitcli commit
```
- Automatically offers to stage all changes if nothing is staged
- Validates commit message is not empty
- Shows visual feedback with spinners

#### `push`
Push commits to the remote repository.
```bash
gitcli push
```
- Checks for remote repository configuration
- Offers to commit unstaged changes before pushing
- Handles push rejections with force push option
- Prompts for confirmation on force push (requires typing "yes")

#### `pull`
Pull latest changes from the remote repository.
```bash
gitcli pull
```
- Fetches and merges changes from remote
- Shows success/failure notifications

#### `sync`
Pull then push in one command - keeps your branch synchronized.
```bash
gitcli sync
```
- Pulls latest changes first
- Automatically pushes if local branch is ahead
- Stops if pull fails (e.g., merge conflicts)

#### `fetch`
Fetch updates from remote without merging.
```bash
gitcli fetch
```
- Updates remote tracking branches
- Shows how many commits behind you are
- Suggests using `pull` to merge changes

#### `stage`
Stage changes for commit with options.
```bash
gitcli stage
```
Options:
1. Stage all changes (`git add .`)
2. Stage specific files (interactive file selection)

#### `status`
Show the current git status.
```bash
gitcli status
```
- Displays branch information
- Shows staged/unstaged changes
- Lists untracked files

#### `log`
View recent commit history.
```bash
gitcli log
```
- Shows last 10 commits
- Displays as a graph with decorations
- One-line format for easy reading

### Diff Operations

#### `diff`
Show unstaged changes (what you've modified but not staged).
```bash
gitcli diff
```
- Color-coded diff output
- Shows line-by-line changes

#### `diff-staged`
Show staged changes (what will be committed).
```bash
gitcli diff-staged
```
- Preview changes before committing
- Helps verify what you're about to commit

### Branch Management

#### `switch-branch`
Switch to another branch.
```bash
gitcli switch-branch
```
- Lists all available branches
- Offers to create branch if it doesn't exist
- Interactive branch selection

#### `add-branch`
Create a new branch and switch to it.
```bash
gitcli add-branch
```
- Prompts for branch name
- Automatically sanitizes name (replaces spaces with hyphens)
- Switches to new branch immediately

#### `delete-branch`
Delete a branch with safety checks.
```bash
gitcli delete-branch
```
- Prevents deleting current branch
- Options for safe delete or force delete
- Requires confirmation

#### `rename-branch`
Rename a branch.
```bash
gitcli rename-branch
```
- Can rename current branch or specify another
- Sanitizes new branch name
- Updates branch reference

#### `list-branch`
List all branches (local and remote).
```bash
gitcli list-branch
```
- Shows current branch highlighted
- Displays remote tracking branches

### Quick Operations

#### `quick-push` or `qp`
Stage all changes, commit, and push in one command.
```bash
gitcli qp
# or
gitcli quick-push
```
- Stages all changes automatically
- Prompts for commit message
- Pushes to remote
- Handles force push if needed
- Perfect for quick updates

### Advanced Operations

#### `amend`
Amend the last commit.
```bash
gitcli amend
```
Options:
1. Change commit message only
2. Add more changes to commit (keep message)
3. Add more changes and update message

Warns about force push if commit was already pushed.

#### `reset`
Reset to a previous commit.
```bash
gitcli reset
```
Options:
1. Reset to last commit (hard reset)
2. Reset to specific commit ID

⚠️ **Warning**: Hard reset discards all uncommitted changes!
- Requires typing "yes" for confirmation
- Shows recent commits for reference

#### `remotes`
Manage remote repositories.
```bash
gitcli remotes
```
Options:
1. List remotes
2. Add remote
3. Remove remote
4. View remote URLs

#### `clone`
Clone a repository interactively.
```bash
gitcli clone
```
- Prompts for repository URL
- Optional custom folder name
- Shows navigation hint after cloning
- Works even outside a git repository

### Utility Commands

#### `help`
Display all available commands with descriptions.
```bash
gitcli help
```

#### `quit`
Exit GitCLI (interactive mode only).
```
quit
```

## Command Examples

### Typical Workflow
```bash
# Check status
gitcli status

# View changes
gitcli diff

# Stage and commit
gitcli stage
gitcli commit

# Push to remote
gitcli push
```

### Quick Workflow
```bash
# Stage, commit, and push in one command
gitcli qp
```

### Sync Workflow
```bash
# Pull latest changes and push yours
gitcli sync
```

### Branch Workflow
```bash
# Create new feature branch
gitcli add-branch

# Work on changes...
gitcli qp

# Switch back to main
gitcli switch-branch
```

## Interactive Mode Features

When running `gitcli` without arguments:
- **Tab completion**: Press Tab to autocomplete commands
- **Branch indicator**: Shows current branch in prompt
- **Persistent session**: Run multiple commands without restarting
- **Command history**: Use arrow keys to navigate previous commands

## Safety Features

- **Confirmation prompts** for destructive operations (delete, reset, force push)
- **"yes" requirement** for dangerous operations (not just "y")
- **Branch protection**: Can't delete current branch
- **Change detection**: Warns about uncommitted changes
- **Remote checks**: Validates remote exists before push/pull operations

## Project Structure

```
GitCLI/
├── gitcli/
│   ├── __init__.py         # Package initialization
│   ├── cli.py              # Main entry point and CLI interface
│   ├── helpers.py          # Utility functions
│   ├── git_operations.py   # Core git operations
│   ├── git_branches.py     # Branch management
│   └── git_advanced.py     # Advanced operations
├── setup.py                # Package configuration
├── pyproject.toml          # Modern Python packaging
├── LICENSE                 # MIT License
├── README.md               
└── requirements.txt        # Dependencies
```

## Requirements

- Python 3.7+
- Git installed and configured
- colorama (for colored output)
- yaspin (for loading spinners)
- win10toast (optional, for Windows notifications)

## Platform Support

- ✅ **macOS**: Full support with native notifications
- ✅ **Linux**: Full support with notify-send
- ✅ **Windows**: Full support (install win10toast for notifications)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`gitcli add-branch feature-name`)
3. Commit your changes (`gitcli commit`)
4. Push to the branch (`gitcli push`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

Adelodunpeter - [GitHub](https://github.com/Adelodunpeter25)

## Troubleshooting

**Command not found after installation?**
- Ensure pip install location is in your PATH
- Try `python -m gitcli.cli` as alternative

**Import errors?**
- Verify all dependencies are installed: `pip install -r requirements.txt`

**Git errors?**
- Ensure Git is installed: `git --version`
- Verify you're in a Git repository or use `gitcli clone`

**Notifications not working?**
- macOS/Linux: Should work out of the box
- Windows: Install win10toast: `pip install win10toast`
