#!/usr/bin/env python3
import os
import sys
import readline
import platform
from colorama import Fore, Style, init
from yaspin import yaspin

# Import modules
from .helpers import run_command, get_current_branch, get_repo_name
from .git_operations import (
    commit_changes, push_changes, pull_changes, stage_changes,
    show_status, show_log, show_diff, show_diff_staged,
    sync_changes, fetch_changes, clone_repository, quick_push
)
from .git_branches import (
    switch_branch, add_branch, delete_branch, rename_branch, list_branches
)
from .git_advanced import manage_remotes, reset_commit, amend_commit
from .git_hooks import manage_hooks, list_installed_hooks

# Initialize colorama
init(autoreset=True)

# Tab completion
COMMANDS = [
    "commit", "push", "pull", "status", "stage", "log", "diff", "diff-staged",
    "switch-branch", "add-branch", "delete-branch", "rename-branch", "list-branch", 
    "quick-push", "qp", "sync", "fetch", "clone", "remotes", "reset", 
    "amend", "hooks", "list-hooks", "help", "quit"
]

def completer(text, state):
    matches = [c for c in COMMANDS if c.startswith(text)]
    return matches[state] if state < len(matches) else None

readline.set_completer(completer)
# Cross-platform readline configuration
if platform.system() == "Windows":
    readline.parse_and_bind("tab: complete")
else:
    readline.parse_and_bind("bind ^I rl_complete")

def show_welcome():
    """Show welcome screen only once at startup"""
    repo = get_repo_name()
    branch = get_current_branch()
    
    print("\n" + Fore.MAGENTA + Style.BRIGHT + "=" * 60)
    print(Fore.MAGENTA + Style.BRIGHT + "  🚀 GitCLI - Git Operations Automation")
    print(Fore.MAGENTA + Style.BRIGHT + "=" * 60)
    print(Fore.CYAN + f"  Repository: " + Fore.WHITE + f"{repo}")
    print(Fore.CYAN + f"  Branch: " + Fore.WHITE + f"{branch}")
    print(Fore.MAGENTA + Style.BRIGHT + "=" * 60)
    print(Fore.YELLOW + "\n💡 Type 'help' to see available commands")
    print(Fore.YELLOW + "💡 Press Tab for auto-complete\n")

def show_help():
    """Display all available commands"""
    print("\n" + Fore.CYAN + Style.BRIGHT + "📚 Available Commands:")
    print(Fore.CYAN + "-" * 60)
    
    commands = [
        ("commit", "Commit staged changes"),
        ("push", "Push changes to remote"),
        ("pull", "Pull latest changes"),
        ("sync", "Pull then push in one command"),
        ("fetch", "Fetch updates without merging"),
        ("status", "Show git status"),
        ("stage", "Stage changes for commit"),
        ("log", "View commit history"),
        ("diff", "Show unstaged changes"),
        ("diff-staged", "Show staged changes"),
        ("switch-branch", "Switch to another branch"),
        ("add-branch", "Create new branch"),
        ("delete-branch", "Delete a branch"),
        ("rename-branch", "Rename a branch"),
        ("list-branch", "List all branches"),
        ("quick-push / qp", "Stage, commit & push in one go"),
        ("clone", "Clone a repository"),
        ("remotes", "Manage remote repositories"),
        ("reset", "Reset to previous commit"),
        ("amend", "Amend last commit"),
        ("hooks", "Manage Git hooks"),
        ("list-hooks", "List installed hooks"),
        ("help", "Show this help message"),
        ("quit", "Exit GitCLI"),
    ]
    
    for cmd, desc in commands:
        print(Fore.GREEN + f"  {cmd.ljust(16)}" + Fore.WHITE + f"{desc}")
    
    print(Fore.CYAN + "-" * 60 + "\n")

def show_prompt():
    """Show simple prompt with current branch"""
    branch = get_current_branch()
    return Fore.MAGENTA + f"[{branch}] " + Fore.CYAN + "> "

def normalize_command(cmd):
    """Normalize command to handle various formats (listbranch -> list-branch)"""
    cmd = cmd.strip().lower().replace(" ", "-")
    
    # Map common variations to standard commands
    command_map = {
        "listbranch": "list-branch",
        "switchbranch": "switch-branch",
        "addbranch": "add-branch",
        "deletebranch": "delete-branch",
        "renamebranch": "rename-branch",
        "quickpush": "quick-push",
        "diffstaged": "diff-staged",
        "listhooks": "list-hooks",
    }
    
    return command_map.get(cmd, cmd)

def execute_command(command):
    """Execute a single command"""
    if command == "commit":
        commit_changes()
    elif command == "push":
        push_changes()
    elif command == "pull":
        pull_changes()
    elif command == "sync":
        sync_changes()
    elif command == "fetch":
        fetch_changes()
    elif command == "clone":
        clone_repository()
    elif command == "status":
        show_status()
    elif command == "stage":
        stage_changes()
    elif command == "log":
        show_log()
    elif command == "diff":
        show_diff()
    elif command == "diff-staged":
        show_diff_staged()
    elif command in ["quick-push", "qp"]:
        quick_push()
    elif command == "remotes":
        manage_remotes()
    elif command == "reset":
        reset_commit()
    elif command == "amend":
        amend_commit()
    elif command == "hooks":
        manage_hooks()
    elif command == "list-hooks":
        list_installed_hooks()
    elif command == "switch-branch":
        switch_branch()
    elif command == "add-branch":
        add_branch()
    elif command == "delete-branch":
        delete_branch()
    elif command == "rename-branch":
        rename_branch()
    elif command == "list-branch":
        list_branches()
    elif command == "help":
        show_help()
    else:
        return False
    return True

def main():
    # Check for command-line arguments
    if len(sys.argv) > 1:
        # Join all arguments to handle "gitcli list branch" or "gitcli quick push"
        command = normalize_command(" ".join(sys.argv[1:]))
        
        if not os.path.isdir(".git") and command not in ["clone", "help"]:
            print(Fore.RED + "❌ Not a git repository.")
            sys.exit(1)
        
        # Execute command directly
        if execute_command(command):
            sys.exit(0)
        else:
            print(Fore.RED + f"❌ Unknown command: {command}")
            print(Fore.CYAN + "💡 Type 'gitcli help' to see available commands.")
            sys.exit(1)
    
    # Interactive mode
    if not os.path.isdir(".git"):
        print(Fore.YELLOW + "⚠️  Not a git repository.")
        print(Fore.CYAN + "Options:")
        print("  1. Initialize git in current directory (git init)")
        print("  2. Clone a repository")
        print("  3. Exit")
        
        choice = input("\nChoose option (1-3): ").strip()
        
        if choice == "1":
            confirm = input(f"Initialize git in {os.getcwd()}? (y/N): ").lower()
            if confirm == "y":
                with yaspin(text="Initializing git repository...", color="cyan") as spinner:
                    result = run_command("git init", capture_output=False)
                    if result is not None:
                        spinner.ok("✅")
                        print(Fore.GREEN + "✅ Git repository initialized!")
                    else:
                        spinner.fail("❌")
                        sys.exit(1)
            else:
                print(Fore.CYAN + "🚫 Initialization canceled.")
                sys.exit(0)
        elif choice == "2":
            clone_repository()
            sys.exit(0)
        else:
            sys.exit(0)
    
    # Show welcome screen once
    show_welcome()
    
    while True:
        choice = normalize_command(input(show_prompt()))
        
        if choice == "quit":
            print(Fore.CYAN + "👋 Exiting GitCLI...")
            break
        elif not execute_command(choice):
            print(Fore.RED + "❌ Unknown command. Type 'help' to see available commands or press Tab for auto-complete.")

if __name__ == "__main__":
    main()
