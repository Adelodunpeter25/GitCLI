#!/Users/techclub/scripts/automation/venv/bin/python3
import subprocess
import os
import sys
import readline
import platform
from colorama import Fore, Style, init
from yaspin import yaspin
import time

# Initialize colorama
init(autoreset=True)

# -----------------------------
# Helper Functions
# -----------------------------
def run_command(cmd, capture_output=True):
    """Run a shell command safely and return output."""
    try:
        result = subprocess.run(
            cmd, shell=True, check=True,
            capture_output=capture_output, text=True
        )
        return result.stdout.strip() if capture_output else ""
    except subprocess.CalledProcessError as e:
        print(Fore.RED + f"⚠️  Command failed: {cmd}")
        if e.stdout:
            print(Fore.RED + e.stdout)
        if e.stderr:
            print(Fore.RED + e.stderr)
        return None

def send_notification(title, message):
    """Send system notification (cross-platform)."""
    try:
        system = platform.system()
        if system == "Darwin":  # macOS
            os.system(f'''osascript -e 'display notification "{message}" with title "{title}"' ''')
        elif system == "Linux":
            os.system(f'notify-send "{title}" "{message}"')
        elif system == "Windows":
            # Windows notification (requires win10toast or similar)
            pass
    except:
        pass

def get_current_branch():
    return run_command("git rev-parse --abbrev-ref HEAD") or "unknown"

def get_repo_name():
    return os.path.basename(os.getcwd())

def has_staged_changes():
    status = run_command("git diff --cached --name-only")
    return bool(status.strip())

def has_unstaged_changes():
    status = run_command("git diff --name-only")
    return bool(status.strip())

def has_any_changes():
    return has_staged_changes() or has_unstaged_changes()

def sanitize_name(name):
    return name.strip().replace(" ", "-")

def has_remote():
    remote = run_command("git remote")
    return bool(remote)

# -----------------------------
# Git Operations
# -----------------------------
def commit_changes():
    if not has_staged_changes():
        if has_unstaged_changes():
            print(Fore.YELLOW + "⚠️  No staged changes found.")
            choice = input("Do you want to stage all changes and commit? (y/N): ").lower()
            if choice == "y":
                with yaspin(text="Staging all changes...", color="cyan") as spinner:
                    time.sleep(0.5)
                    run_command("git add .", capture_output=False)
                    spinner.ok("✅")
                print(Fore.GREEN + "✅ All changes staged.")
            else:
                print(Fore.CYAN + "🚫 Commit canceled.")
                return
        else:
            print(Fore.YELLOW + "⚠️  No changes to commit.")
            return
    
    print(Fore.CYAN + "\n📝 Enter commit message:")
    message = input("> ").strip()
    if not message:
        print(Fore.RED + "❌ Commit message cannot be empty.")
        return
    with yaspin(text="Committing changes...", color="cyan") as spinner:
        time.sleep(0.7)
        run_command(f'git commit -m "{message}"', capture_output=False)
        spinner.ok("✅")
    print(Fore.GREEN + f"✅ Changes committed with message: '{message}'")
    send_notification("GitCLI", f"Commit successful: {message[:30]}...")

def push_changes():
    branch = get_current_branch()
    
    # Check if remote exists
    if not has_remote():
        print(Fore.RED + "❌ No remote repository configured.")
        return
    
    if not has_staged_changes() and not has_unstaged_changes():
        print(Fore.YELLOW + "⚠️  No changes to push.")
        return
    if not has_staged_changes():
        print(Fore.YELLOW + "⚠️  No staged commits.")
        choice = input("Do you want to stage all changes and commit before pushing? (y/N): ").lower()
        if choice == "y":
            run_command("git add .", capture_output=False)
            print(Fore.CYAN + "Enter commit message for staged changes:")
            message = input("> ").strip()
            if not message:
                print(Fore.RED + "❌ Commit message cannot be empty. Push canceled.")
                return
            with yaspin(text="Committing changes...", color="cyan") as spinner:
                time.sleep(0.7)
                run_command(f'git commit -m "{message}"', capture_output=False)
                spinner.ok("✅")
            print(Fore.GREEN + f"✅ Changes committed with message: '{message}'")
        else:
            print(Fore.CYAN + "🚫 Push canceled.")
            return
    with yaspin(text=f"Pushing branch '{branch}'...", color="magenta") as spinner:
        time.sleep(0.7)
        result = run_command("git push", capture_output=False)
        if result is not None:
            spinner.ok("🚀")
            print(Fore.GREEN + f"✅ Changes pushed to '{branch}'!")
            send_notification("GitCLI", f"Push to '{branch}' complete!")
        else:
            spinner.fail("❌")

def pull_changes():
    branch = get_current_branch()
    
    # Check if remote exists
    if not has_remote():
        print(Fore.RED + "❌ No remote repository configured.")
        return
    
    print(Fore.CYAN + f"\n⬇️  Pulling latest changes for '{branch}'...")
    with yaspin(text="Pulling...", color="cyan") as spinner:
        time.sleep(0.7)
        result = run_command("git pull", capture_output=False)
        if result is not None:
            spinner.ok("✅")
            print(Fore.GREEN + f"✅ Successfully pulled latest changes!")
            send_notification("GitCLI", f"Pull from '{branch}' complete!")
        else:
            spinner.fail("❌")

def stage_changes():
    """Stage changes with options"""
    if not has_unstaged_changes():
        print(Fore.YELLOW + "⚠️  No unstaged changes to stage.")
        return
    
    print(Fore.CYAN + "\n📂 Stage options:")
    print("  1. Stage all changes (git add .)")
    print("  2. Stage specific files")
    
    choice = input("Choose option (1/2): ").strip()
    
    if choice == "1":
        with yaspin(text="Staging all changes...", color="cyan") as spinner:
            time.sleep(0.5)
            run_command("git add .", capture_output=False)
            spinner.ok("✅")
        print(Fore.GREEN + "✅ All changes staged.")
    elif choice == "2":
        print(Fore.CYAN + "\nUnstaged files:")
        os.system("git diff --name-only")
        print(Fore.CYAN + "\nEnter file paths (space-separated):")
        files = input("> ").strip()
        if not files:
            print(Fore.RED + "❌ No files specified.")
            return
        with yaspin(text="Staging files...", color="cyan") as spinner:
            time.sleep(0.5)
            run_command(f"git add {files}", capture_output=False)
            spinner.ok("✅")
        print(Fore.GREEN + f"✅ Files staged: {files}")
    else:
        print(Fore.RED + "❌ Invalid option.")
def show_status():
    print(Fore.CYAN + "\n📊 Git Status:\n" + "-"*30)
    os.system("git status")

def show_log():
    print(Fore.CYAN + "\n📜 Recent Commits:\n" + "-"*30)
    os.system("git log --oneline --graph --decorate -10")

def switch_branch():
    print(Fore.CYAN + "\n🔀 Available branches:")
    os.system("git branch")
    branch = input("\nEnter branch name to switch to: ").strip()
    if not branch:
        print(Fore.RED + "❌ Branch name cannot be empty.")
        return
    
    # Check if branch exists
    branches = run_command("git branch --list")
    if branch not in branches:
        print(Fore.YELLOW + f"⚠️  Branch '{branch}' doesn't exist locally.")
        create = input("Would you like to create it? (y/N): ").lower()
        if create == "y":
            add_branch(branch)
            return
        else:
            print(Fore.CYAN + "🚫 Switch canceled.")
            return
    
    with yaspin(text=f"Switching to '{branch}'...", color="cyan") as spinner:
        time.sleep(0.5)
        result = run_command(f"git checkout {branch}", capture_output=False)
        if result is not None:
            spinner.ok("✅")
            print(Fore.GREEN + f"✅ Switched to branch '{branch}'")
        else:
            spinner.fail("❌")

def add_branch(branch_name=None):
    if not branch_name:
        print(Fore.CYAN + "\n🌿 Enter new branch name:")
        branch = sanitize_name(input("> "))
    else:
        branch = sanitize_name(branch_name)
    
    if not branch:
        print(Fore.RED + "❌ Branch name cannot be empty.")
        return
    run_command(f"git checkout -b {branch}", capture_output=False)
    print(Fore.GREEN + f"✅ Branch '{branch}' created and switched to it.")

def delete_branch():
    print(Fore.CYAN + "\n🗑 Enter branch name to delete:")
    branch = sanitize_name(input("> "))
    if not branch:
        print(Fore.RED + "❌ Branch name cannot be empty.")
        return
    current = get_current_branch()
    if branch == current:
        print(Fore.RED + "❌ Cannot delete the branch you are currently on.")
        return
    
    print(Fore.YELLOW + "Delete options:")
    print("  1. Normal delete (safe)")
    print("  2. Force delete (-D)")
    option = input("Choose option (1/2): ").strip()
    
    flag = "-d" if option == "1" else "-D"
    
    confirm = input(f"Are you sure you want to delete branch '{branch}'? (y/N): ").lower()
    if confirm != "y":
        print(Fore.CYAN + "🚫 Delete canceled.")
        return
    run_command(f"git branch {flag} {branch}", capture_output=False)
    print(Fore.GREEN + f"✅ Branch '{branch}' deleted.")

def rename_branch():
    print(Fore.CYAN + "\n🔀 Enter branch name to rename (leave empty for current branch):")
    old_name = input("> ").strip()
    if not old_name:
        old_name = get_current_branch()
    new_name = sanitize_name(input("Enter new branch name: ").strip())
    if not new_name:
        print(Fore.RED + "❌ New branch name cannot be empty.")
        return
    run_command(f"git branch -m {old_name} {new_name}", capture_output=False)
    print(Fore.GREEN + f"✅ Branch '{old_name}' renamed to '{new_name}'")

def list_branches():
    print(Fore.CYAN + "\n🌿 Branches:\n" + "-"*30)
    os.system("git branch --all")

def quick_push():
    """Stage all, commit, and push in one command"""
    branch = get_current_branch()
    
    # Check if remote exists
    if not has_remote():
        print(Fore.RED + "❌ No remote repository configured.")
        return
    
    # Check if there are any changes
    if not has_any_changes():
        print(Fore.YELLOW + "⚠️  No changes to commit and push.")
        return
    
    # Stage all changes
    print(Fore.CYAN + "\n🚀 Quick Push: Stage → Commit → Push")
    with yaspin(text="Staging all changes...", color="cyan") as spinner:
        time.sleep(0.5)
        run_command("git add .", capture_output=False)
        spinner.ok("✅")
    print(Fore.GREEN + "✅ All changes staged.")
    
    # Get commit message
    print(Fore.CYAN + "\n📝 Enter commit message:")
    message = input("> ").strip()
    if not message:
        print(Fore.RED + "❌ Commit message cannot be empty. Quick push canceled.")
        return
    
    # Commit
    with yaspin(text="Committing changes...", color="cyan") as spinner:
        time.sleep(0.7)
        run_command(f'git commit -m "{message}"', capture_output=False)
        spinner.ok("✅")
    print(Fore.GREEN + f"✅ Changes committed with message: '{message}'")
    
    # Push
    with yaspin(text=f"Pushing to '{branch}'...", color="magenta") as spinner:
        time.sleep(0.7)
        result = run_command("git push", capture_output=False)
        if result is not None:
            spinner.ok("🚀")
            print(Fore.GREEN + f"✅ Successfully pushed to '{branch}'!")
            send_notification("GitCLI", f"Quick push to '{branch}' complete!")
        else:
            spinner.fail("❌")

def manage_remotes():
    """Manage git remotes"""
    print(Fore.CYAN + "\n🌐 Remote Management:")
    print("  1. List remotes")
    print("  2. Add remote")
    print("  3. Remove remote")
    print("  4. View remote URLs")
    
    choice = input("\nChoose option (1-4): ").strip()
    
    if choice == "1":
        print(Fore.CYAN + "\n📋 Remotes:\n" + "-"*30)
        os.system("git remote -v")
    elif choice == "2":
        print(Fore.CYAN + "\n➕ Add Remote")
        name = input("Enter remote name (e.g., origin): ").strip()
        if not name:
            print(Fore.RED + "❌ Remote name cannot be empty.")
            return
        url = input("Enter remote URL: ").strip()
        if not url:
            print(Fore.RED + "❌ Remote URL cannot be empty.")
            return
        run_command(f"git remote add {name} {url}", capture_output=False)
        print(Fore.GREEN + f"✅ Remote '{name}' added successfully.")
    elif choice == "3":
        print(Fore.CYAN + "\n➖ Remove Remote")
        os.system("git remote -v")
        name = input("\nEnter remote name to remove: ").strip()
        if not name:
            print(Fore.RED + "❌ Remote name cannot be empty.")
            return
        confirm = input(f"Are you sure you want to remove remote '{name}'? (y/N): ").lower()
        if confirm != "y":
            print(Fore.CYAN + "🚫 Remove canceled.")
            return
        run_command(f"git remote remove {name}", capture_output=False)
        print(Fore.GREEN + f"✅ Remote '{name}' removed successfully.")
    elif choice == "4":
        print(Fore.CYAN + "\n🔗 Remote URLs:\n" + "-"*30)
        os.system("git remote -v")
    else:
        print(Fore.RED + "❌ Invalid option.")

def reset_commit():
    """Reset to a previous commit"""
    print(Fore.CYAN + "\n⚠️  Reset Options:")
    print("  1. Reset to last commit (hard reset)")
    print("  2. Reset to specific commit ID")
    print(Fore.YELLOW + "\n⚠️  WARNING: Hard reset will discard all uncommitted changes!")
    
    choice = input("\nChoose option (1-2): ").strip()
    
    if choice == "1":
        confirm = input(Fore.RED + "Are you sure? This will discard ALL uncommitted changes! (yes/N): ").lower()
        if confirm != "yes":
            print(Fore.CYAN + "🚫 Reset canceled.")
            return
        with yaspin(text="Resetting to last commit...", color="yellow") as spinner:
            time.sleep(0.5)
            run_command("git reset --hard HEAD", capture_output=False)
            spinner.ok("✅")
        print(Fore.GREEN + "✅ Reset to last commit successfully.")
    elif choice == "2":
        print(Fore.CYAN + "\n📜 Recent commits:")
        os.system("git log --oneline -10")
        commit_id = input("\nEnter commit ID to reset to: ").strip()
        if not commit_id:
            print(Fore.RED + "❌ Commit ID cannot be empty.")
            return
        confirm = input(Fore.RED + f"Are you sure? This will reset to '{commit_id}' and discard all changes after it! (yes/N): ").lower()
        if confirm != "yes":
            print(Fore.CYAN + "🚫 Reset canceled.")
            return
        with yaspin(text=f"Resetting to commit {commit_id}...", color="yellow") as spinner:
            time.sleep(0.5)
            result = run_command(f"git reset --hard {commit_id}", capture_output=False)
            if result is not None:
                spinner.ok("✅")
                print(Fore.GREEN + f"✅ Reset to commit '{commit_id}' successfully.")
            else:
                spinner.fail("❌")
    else:
        print(Fore.RED + "❌ Invalid option.")

def amend_commit():
    """Amend the last commit"""
    # Check if there are any commits
    result = run_command("git log -1 --oneline")
    if not result:
        print(Fore.RED + "❌ No commits to amend.")
        return
    
    print(Fore.CYAN + "\n✏️  Amend Last Commit")
    print(Fore.CYAN + "\nCurrent last commit:")
    os.system("git log -1 --oneline")
    
    print(Fore.CYAN + "\nAmend options:")
    print("  1. Change commit message only")
    print("  2. Add more changes to commit (keep message)")
    print("  3. Add more changes and update message")
    
    choice = input("\nChoose option (1-3): ").strip()
    
    if choice == "1":
        print(Fore.CYAN + "\n📝 Enter new commit message:")
        message = input("> ").strip()
        if not message:
            print(Fore.RED + "❌ Commit message cannot be empty.")
            return
        with yaspin(text="Amending commit...", color="cyan") as spinner:
            time.sleep(0.5)
            run_command(f'git commit --amend -m "{message}"', capture_output=False)
            spinner.ok("✅")
        print(Fore.GREEN + "✅ Commit message updated successfully.")
    elif choice == "2":
        if not has_unstaged_changes() and not has_staged_changes():
            print(Fore.YELLOW + "⚠️  No changes to add to the commit.")
            return
        # Stage changes if needed
        if has_unstaged_changes():
            stage_all = input("Stage all changes? (y/N): ").lower()
            if stage_all == "y":
                run_command("git add .", capture_output=False)
                print(Fore.GREEN + "✅ Changes staged.")
            else:
                print(Fore.YELLOW + "💡 Stage specific files using the 'stage' command first.")
                return
        with yaspin(text="Amending commit...", color="cyan") as spinner:
            time.sleep(0.5)
            run_command('git commit --amend --no-edit', capture_output=False)
            spinner.ok("✅")
        print(Fore.GREEN + "✅ Changes added to last commit.")
    elif choice == "3":
        if not has_unstaged_changes() and not has_staged_changes():
            print(Fore.YELLOW + "⚠️  No changes to add to the commit.")
            return
        # Stage changes if needed
        if has_unstaged_changes():
            stage_all = input("Stage all changes? (y/N): ").lower()
            if stage_all == "y":
                run_command("git add .", capture_output=False)
                print(Fore.GREEN + "✅ Changes staged.")
            else:
                print(Fore.YELLOW + "💡 Stage specific files using the 'stage' command first.")
                return
        print(Fore.CYAN + "\n📝 Enter new commit message:")
        message = input("> ").strip()
        if not message:
            print(Fore.RED + "❌ Commit message cannot be empty.")
            return
        with yaspin(text="Amending commit...", color="cyan") as spinner:
            time.sleep(0.5)
            run_command(f'git commit --amend -m "{message}"', capture_output=False)
            spinner.ok("✅")
        print(Fore.GREEN + "✅ Commit amended successfully.")
    else:
        print(Fore.RED + "❌ Invalid option.")
    
    # Warning about force push if already pushed
    print(Fore.YELLOW + "\n⚠️  Note: If you already pushed this commit, you'll need to force push (git push --force)")

# -----------------------------
# Tab completion
# -----------------------------
COMMANDS = [
    "commit", "push", "pull", "status", "stage", "log", "switch-branch",
    "add-branch", "delete-branch", "rename-branch", "list-branch", 
    "quick-push", "qp", "remotes", "reset", "amend", "help", "quit"
]

def completer(text, state):
    matches = [c for c in COMMANDS if c.startswith(text)]
    return matches[state] if state < len(matches) else None

readline.set_completer(completer)
# macOS readline/libedit fix
readline.parse_and_bind("bind ^I rl_complete")

# -----------------------------
# Menu display
# -----------------------------
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
        ("status", "Show git status"),
        ("stage", "Stage changes for commit"),
        ("log", "View commit history"),
        ("switch-branch", "Switch to another branch"),
        ("add-branch", "Create new branch"),
        ("delete-branch", "Delete a branch"),
        ("rename-branch", "Rename a branch"),
        ("list-branch", "List all branches"),
        ("quick-push / qp", "Stage, commit & push in one go"),
        ("remotes", "Manage remote repositories"),
        ("reset", "Reset to previous commit"),
        ("amend", "Amend last commit"),
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

# -----------------------------
# Main loop
# -----------------------------
def main():
    if not os.path.isdir(".git"):
        print(Fore.RED + "❌ Not a git repository. Navigate into one first.")
        sys.exit(1)
    
    # Show welcome screen once
    show_welcome()
    
    while True:
        choice = input(show_prompt()).strip().lower().replace(" ", "-")
        
        if choice == "commit":
            commit_changes()
        elif choice == "push":
            push_changes()
        elif choice == "pull":
            pull_changes()
        elif choice == "status":
            show_status()
        elif choice == "stage":
            stage_changes()
        elif choice == "log":
            show_log()
        elif choice in ["quick-push", "qp"]:
            quick_push()
        elif choice == "remotes":
            manage_remotes()
        elif choice == "reset":
            reset_commit()
        elif choice == "amend":
            amend_commit()
        elif choice == "switch-branch":
            switch_branch()
        elif choice == "add-branch":
            add_branch()
        elif choice == "delete-branch":
            delete_branch()
        elif choice == "rename-branch":
            rename_branch()
        elif choice == "list-branch":
            list_branches()
        elif choice == "help":
            show_help()
        elif choice == "quit":
            print(Fore.CYAN + "👋 Exiting GitCLI...")
            break
        else:
            print(Fore.RED + "❌ Unknown command. Type 'help' to see available commands or press Tab for auto-complete.")

if __name__ == "__main__":
    main()
