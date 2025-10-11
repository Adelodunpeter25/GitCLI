#!/usr/bin/env python3
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
            try:
                from win10toast import ToastNotifier
                toaster = ToastNotifier()
                toaster.show_toast(title, message, duration=3, threaded=True)
            except ImportError:
                pass  # Silently skip if win10toast not installed
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
        result = subprocess.run("git push", shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            spinner.ok("🚀")
            print(Fore.GREEN + f"✅ Changes pushed to '{branch}'!")
            send_notification("GitCLI", f"Push to '{branch}' complete!")
        else:
            spinner.fail("❌")
            if "rejected" in result.stderr and "non-fast-forward" in result.stderr:
                print(Fore.YELLOW + "\n⚠️  Push rejected: Your branch is behind the remote branch.")
                force = input(Fore.RED + "Do you want to force push and overwrite the remote? (yes/N): ").lower()
                if force == "yes":
                    with yaspin(text=f"Force pushing to '{branch}'...", color="red") as spinner2:
                        time.sleep(0.7)
                        force_result = run_command("git push --force", capture_output=False)
                        if force_result is not None:
                            spinner2.ok("🚀")
                            print(Fore.GREEN + f"✅ Force pushed to '{branch}'!")
                            send_notification("GitCLI", f"Force push to '{branch}' complete!")
                        else:
                            spinner2.fail("❌")
                else:
                    print(Fore.CYAN + "🚫 Force push canceled.")

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

def show_diff():
    """Show unstaged changes"""
    if not has_unstaged_changes():
        print(Fore.YELLOW + "⚠️  No unstaged changes to show.")
        return
    print(Fore.CYAN + "\n📝 Unstaged Changes:\n" + "-"*30)
    os.system("git diff")

def show_diff_staged():
    """Show staged changes"""
    if not has_staged_changes():
        print(Fore.YELLOW + "⚠️  No staged changes to show.")
        return
    print(Fore.CYAN + "\n📝 Staged Changes:\n" + "-"*30)
    os.system("git diff --cached")

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

def sync_changes():
    """Pull then push changes"""
    branch = get_current_branch()
    
    if not has_remote():
        print(Fore.RED + "❌ No remote repository configured.")
        return
    
    # Pull first
    print(Fore.CYAN + f"\n🔄 Syncing '{branch}': Pull → Push")
    with yaspin(text="Pulling latest changes...", color="cyan") as spinner:
        time.sleep(0.7)
        result = subprocess.run("git pull", shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            spinner.fail("❌")
            print(Fore.RED + "❌ Pull failed. Resolve conflicts before syncing.")
            return
        spinner.ok("✅")
    print(Fore.GREEN + "✅ Pull complete.")
    
    # Check if there's anything to push
    if not has_any_changes():
        # Check if local is ahead of remote
        ahead = run_command("git rev-list --count @{u}..HEAD")
        if ahead and int(ahead) > 0:
            print(Fore.CYAN + f"\n📤 Local branch is {ahead} commit(s) ahead. Pushing...")
        else:
            print(Fore.YELLOW + "⚠️  Already up to date. Nothing to push.")
            return
    
    # Push
    with yaspin(text=f"Pushing to '{branch}'...", color="magenta") as spinner:
        time.sleep(0.7)
        result = subprocess.run("git push", shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            spinner.ok("🚀")
            print(Fore.GREEN + f"✅ Sync complete!")
            send_notification("GitCLI", f"Sync to '{branch}' complete!")
        else:
            spinner.fail("❌")

def fetch_changes():
    """Fetch updates from remote without merging"""
    if not has_remote():
        print(Fore.RED + "❌ No remote repository configured.")
        return
    
    print(Fore.CYAN + "\n📥 Fetching updates from remote...")
    with yaspin(text="Fetching...", color="cyan") as spinner:
        time.sleep(0.7)
        result = run_command("git fetch", capture_output=False)
        if result is not None:
            spinner.ok("✅")
            print(Fore.GREEN + "✅ Fetch complete.")
            
            # Show if branch is behind
            branch = get_current_branch()
            behind = run_command("git rev-list --count HEAD..@{u}")
            if behind and int(behind) > 0:
                print(Fore.YELLOW + f"⚠️  Your branch is {behind} commit(s) behind remote.")
                print(Fore.CYAN + "💡 Use 'pull' to merge remote changes.")
        else:
            spinner.fail("❌")

def clone_repository():
    """Clone a repository interactively"""
    print(Fore.CYAN + "\n📦 Clone Repository")
    url = input("Enter repository URL: ").strip()
    if not url:
        print(Fore.RED + "❌ URL cannot be empty.")
        return
    
    folder = input("Enter folder name (leave empty for default): ").strip()
    
    cmd = f"git clone {url}"
    if folder:
        cmd += f" {folder}"
    
    print(Fore.CYAN + f"\n⬇️  Cloning repository...")
    with yaspin(text="Cloning...", color="cyan") as spinner:
        time.sleep(0.7)
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            spinner.ok("✅")
            print(Fore.GREEN + "✅ Repository cloned successfully!")
            if folder:
                print(Fore.CYAN + f"💡 Navigate to folder: cd {folder}")
            else:
                # Extract folder name from URL
                repo_name = url.rstrip('/').split('/')[-1].replace('.git', '')
                print(Fore.CYAN + f"💡 Navigate to folder: cd {repo_name}")
        else:
            spinner.fail("❌")
            print(Fore.RED + f"❌ Clone failed: {result.stderr}")

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
        result = subprocess.run("git push", shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            spinner.ok("🚀")
            print(Fore.GREEN + f"✅ Successfully pushed to '{branch}'!")
            send_notification("GitCLI", f"Quick push to '{branch}' complete!")
        else:
            spinner.fail("❌")
            if "rejected" in result.stderr and "non-fast-forward" in result.stderr:
                print(Fore.YELLOW + "\n⚠️  Push rejected: Your branch is behind the remote branch.")
                force = input(Fore.RED + "Do you want to force push and overwrite the remote? (yes/N): ").lower()
                if force == "yes":
                    with yaspin(text=f"Force pushing to '{branch}'...", color="red") as spinner2:
                        time.sleep(0.7)
                        force_result = run_command("git push --force", capture_output=False)
                        if force_result is not None:
                            spinner2.ok("🚀")
                            print(Fore.GREEN + f"✅ Force pushed to '{branch}'!")
                            send_notification("GitCLI", f"Force push to '{branch}' complete!")
                        else:
                            spinner2.fail("❌")
                else:
                    print(Fore.CYAN + "🚫 Force push canceled.")

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
    "commit", "push", "pull", "status", "stage", "log", "diff", "diff-staged",
    "switch-branch", "add-branch", "delete-branch", "rename-branch", "list-branch", 
    "quick-push", "qp", "sync", "fetch", "clone", "remotes", "reset", 
    "amend", "help", "quit"
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
    # Check for command-line arguments
    if len(sys.argv) > 1:
        if not os.path.isdir(".git") and sys.argv[1] not in ["clone", "help"]:
            print(Fore.RED + "❌ Not a git repository.")
            sys.exit(1)
        
        command = sys.argv[1].lower().replace(" ", "-")
        
        # Execute command directly
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
            print(Fore.RED + f"❌ Unknown command: {command}")
            print(Fore.CYAN + "💡 Type 'gitcli help' to see available commands.")
            sys.exit(1)
        sys.exit(0)
    
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
                    time.sleep(0.5)
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
        choice = input(show_prompt()).strip().lower().replace(" ", "-")
        
        if choice == "commit":
            commit_changes()
        elif choice == "push":
            push_changes()
        elif choice == "pull":
            pull_changes()
        elif choice == "sync":
            sync_changes()
        elif choice == "fetch":
            fetch_changes()
        elif choice == "clone":
            clone_repository()
        elif choice == "status":
            show_status()
        elif choice == "stage":
            stage_changes()
        elif choice == "log":
            show_log()
        elif choice == "diff":
            show_diff()
        elif choice == "diff-staged":
            show_diff_staged()
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
