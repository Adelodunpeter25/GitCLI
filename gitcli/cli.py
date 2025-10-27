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
from .git_stash import (
    stash_changes, stash_pop, stash_apply, stash_list, 
    stash_drop, stash_show
)
from .git_conflicts import resolve_conflicts, check_conflicts
from .git_operations import smart_save
from .helpers import get_config, save_config

# Initialize colorama
init(autoreset=True)

# Tab completion
COMMANDS = [
    "save", "config", "commit", "push", "pull", "status", "stage", "log", "diff", "diff-staged",
    "switch-branch", "add-branch", "delete-branch", "rename-branch", "list-branch", 
    "quick-push", "qp", "sync", "fetch", "clone", "remotes", "reset", 
    "amend", "hooks", "list-hooks", "stash", "stash-pop", "stash-apply", 
    "stash-list", "stash-drop", "stash-show", "resolve-conflicts", "check-conflicts",
    "help", "quit"
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
    print(Fore.GREEN + "\n🚀 Quick Start:")
    print(Fore.CYAN + "  save" + Fore.WHITE + "           - Stage, commit, and push")
    print(Fore.CYAN + "  save <message>" + Fore.WHITE + " - Save with commit message")
    print(Fore.YELLOW + "\n💡 Type 'help' for all commands | Press Tab for auto-complete\n")

def show_help():
    """Display all available commands"""
    print("\n" + Fore.CYAN + Style.BRIGHT + "📚 GitCLI Commands")
    print(Fore.CYAN + "=" * 60)
    
    print(Fore.MAGENTA + Style.BRIGHT + "\n🚀 Quick Commands")
    print(Fore.CYAN + "-" * 60)
    smart_commands = [
        ("save", "Stage, commit, and push"),
        ("save <message>", "Save with inline commit message"),
        ("config", "Manage GitCLI settings"),
    ]
    for cmd, desc in smart_commands:
        print(Fore.GREEN + f"  {cmd.ljust(20)}" + Fore.WHITE + f"{desc}")
    
    print(Fore.YELLOW + Style.BRIGHT + "\n⚙️  Advanced Commands")
    print(Fore.CYAN + "-" * 60)
    advanced_commands = [
        ("commit", "Commit staged changes"),
        ("push", "Push changes to remote"),
        ("pull", "Pull latest changes"),
        ("stage", "Stage changes for commit"),
        ("log", "View commit history"),
        ("diff", "Show unstaged changes"),
        ("diff-staged", "Show staged changes"),
        ("quick-push / qp", "Stage, commit & push in one go"),
    ]
    for cmd, desc in advanced_commands:
        print(Fore.GREEN + f"  {cmd.ljust(20)}" + Fore.WHITE + f"{desc}")
    
    print(Fore.YELLOW + Style.BRIGHT + "\n🌿 Branch Management")
    print(Fore.CYAN + "-" * 60)
    branch_commands = [
        ("switch-branch", "Switch to another branch"),
        ("add-branch", "Create new branch"),
        ("delete-branch", "Delete a branch"),
        ("rename-branch", "Rename a branch"),
        ("list-branch", "List all branches"),
    ]
    for cmd, desc in branch_commands:
        print(Fore.GREEN + f"  {cmd.ljust(20)}" + Fore.WHITE + f"{desc}")
    
    print(Fore.YELLOW + Style.BRIGHT + "\n💾 Stash Management")
    print(Fore.CYAN + "-" * 60)
    stash_commands = [
        ("stash", "Stash uncommitted changes"),
        ("stash-pop", "Apply and remove stash"),
        ("stash-apply", "Apply stash (keep it)"),
        ("stash-list", "List all stashes"),
        ("stash-drop", "Remove a stash"),
        ("stash-show", "Show stash contents"),
    ]
    for cmd, desc in stash_commands:
        print(Fore.GREEN + f"  {cmd.ljust(20)}" + Fore.WHITE + f"{desc}")
    
    print(Fore.YELLOW + Style.BRIGHT + "\n🔧 Conflict & Hooks")
    print(Fore.CYAN + "-" * 60)
    other_commands = [
        ("resolve-conflicts", "Resolve merge conflicts"),
        ("check-conflicts", "Check for conflicts"),
        ("hooks", "Manage Git hooks"),
        ("list-hooks", "List installed hooks"),
    ]
    for cmd, desc in other_commands:
        print(Fore.GREEN + f"  {cmd.ljust(20)}" + Fore.WHITE + f"{desc}")
    
    print(Fore.YELLOW + Style.BRIGHT + "\n🛠️  Other")
    print(Fore.CYAN + "-" * 60)
    misc_commands = [
        ("fetch", "Fetch updates without merging"),
        ("clone", "Clone a repository"),
        ("remotes", "Manage remote repositories"),
        ("reset", "Reset to previous commit"),
        ("amend", "Amend last commit"),
        ("help", "Show this help message"),
        ("quit", "Exit GitCLI"),
    ]
    for cmd, desc in misc_commands:
        print(Fore.GREEN + f"  {cmd.ljust(20)}" + Fore.WHITE + f"{desc}")
    
    print(Fore.CYAN + "\n" + "=" * 60)
    print(Fore.YELLOW + "💡 Tip: Use 'gitcli save' for quick stage, commit, and push!")
    print(Fore.CYAN + "=" * 60 + "\n")

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
        "stashpop": "stash-pop",
        "stashapply": "stash-apply",
        "stashlist": "stash-list",
        "stashdrop": "stash-drop",
        "stashshow": "stash-show",
        "resolveconflicts": "resolve-conflicts",
        "checkconflicts": "check-conflicts",
    }
    
    return command_map.get(cmd, cmd)

def execute_command(command, args=None):
    """Execute a single command"""
    # Smart workflows
    if command == "save":
        # Handle inline commit message: gitcli save commit message here
        commit_msg = " ".join(args) if args else None
        smart_save(commit_msg)
    # Original commands
    elif command == "commit":
        commit_changes()
    elif command == "push":
        push_changes()
    elif command == "pull":
        pull_changes()
    elif command == "fetch":
        fetch_changes()
    elif command == "clone":
        clone_repository()
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
    elif command == "stash":
        stash_changes()
    elif command == "stash-pop":
        stash_pop()
    elif command == "stash-apply":
        stash_apply()
    elif command == "stash-list":
        stash_list()
    elif command == "stash-drop":
        stash_drop()
    elif command == "stash-show":
        stash_show()
    elif command == "resolve-conflicts":
        resolve_conflicts()
    elif command == "check-conflicts":
        check_conflicts()
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
    elif command == "config":
        manage_config()
    elif command == "help":
        show_help()
    else:
        return False
    return True


def manage_config():
    """Manage GitCLI configuration"""
    config = get_config()
    
    print(Fore.CYAN + "\n⚙️  GitCLI Configuration")
    print(Fore.CYAN + "="*60)
    print(Fore.CYAN + "\nCurrent Settings:")
    print(f"  1. Auto-stage changes: {Fore.GREEN if config.get('auto_stage', True) else Fore.RED}{config.get('auto_stage', True)}")
    print(f"  2. Auto-push prompt: {Fore.GREEN if config.get('auto_push', True) else Fore.RED}{config.get('auto_push', True)}")
    print(f"  3. Learn from commit history: {Fore.GREEN if config.get('learn_from_history', True) else Fore.RED}{config.get('learn_from_history', True)}")
    print(Fore.CYAN + "\n" + "="*60)
    
    print(Fore.CYAN + "\nOptions:")
    print("  1. Toggle auto-stage")
    print("  2. Toggle auto-push prompt")
    print("  3. Toggle learn from history")
    print("  4. Reset to defaults")
    print("  5. Back")
    
    choice = input("\nChoose option (1-5): ").strip()
    
    if choice == "1":
        config["auto_stage"] = not config.get("auto_stage", True)
        save_config(config)
        status = "enabled" if config["auto_stage"] else "disabled"
        print(Fore.GREEN + f"✅ Auto-stage {status}!")
    elif choice == "2":
        config["auto_push"] = not config.get("auto_push", True)
        save_config(config)
        status = "enabled" if config["auto_push"] else "disabled"
        print(Fore.GREEN + f"✅ Auto-push prompt {status}!")
    elif choice == "3":
        config["learn_from_history"] = not config.get("learn_from_history", True)
        save_config(config)
        status = "enabled" if config["learn_from_history"] else "disabled"
        print(Fore.GREEN + f"✅ Learn from history {status}!")
    elif choice == "4":
        config = {
            "auto_push": True,
            "auto_stage": True,
            "learn_from_history": True
        }
        save_config(config)
        print(Fore.GREEN + "✅ Configuration reset to defaults!")
    elif choice == "5":
        return
    else:
        print(Fore.RED + "❌ Invalid option.")

def main():
    # Check for command-line arguments
    if len(sys.argv) > 1:
        # Parse command and arguments
        raw_command = sys.argv[1]
        command_args = sys.argv[2:] if len(sys.argv) > 2 else None
        
        # Normalize command (but keep args separate)
        command = normalize_command(raw_command)
        
        if not os.path.isdir(".git") and command not in ["clone", "help"]:
            print(Fore.RED + "❌ Not a git repository.")
            sys.exit(1)
        
        # Execute command directly
        if execute_command(command, command_args):
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
        user_input = input(show_prompt()).strip()
        
        if not user_input:
            continue
        
        # Parse input
        parts = user_input.split()
        command = normalize_command(parts[0])
        args = parts[1:] if len(parts) > 1 else None
        
        if command == "quit":
            print(Fore.CYAN + "👋 Exiting GitCLI...")
            break
        elif not execute_command(command, args):
            print(Fore.RED + "❌ Unknown command. Type 'help' to see available commands or press Tab for auto-complete.")

if __name__ == "__main__":
    main()
