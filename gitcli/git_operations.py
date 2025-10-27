import subprocess
import os
from colorama import Fore
from yaspin import yaspin
from .helpers import (
    run_command, send_notification, get_current_branch,
    has_staged_changes, has_unstaged_changes, has_any_changes, has_remote, display_command,
    get_config, generate_commit_message
)


def smart_save(commit_message=None):
    """
    Smart save command with configuration support:
    1. Automatically stage all changes
    2. Smart commit message with suggestions
    3. Configurable auto-push
    """
    branch = get_current_branch()
    config = get_config()
    
    # Check if there are any changes
    if not has_any_changes():
        # Check for unpushed commits
        if has_remote():
            ahead = run_command("git rev-list --count @{u}..HEAD 2>/dev/null")
            if ahead and int(ahead) > 0:
                print(Fore.CYAN + f"\n📤 You have {ahead} unpushed commit(s) on '{branch}'")
                
                if config.get("auto_push", True):
                    push = input("Push to remote? (Y/n): ").lower()
                    if push != "n":
                        push_changes()
                else:
                    print(Fore.YELLOW + "💡 Auto-push is disabled. Use 'gitcli push' to push manually.")
            else:
                print(Fore.GREEN + "\n✅ Everything is saved and up to date!")
        else:
            print(Fore.GREEN + "\n✅ No changes to save!")
        return
    
    # Step 1: Stage all changes
    if config.get("auto_stage", True):
        print(Fore.CYAN + "\n📦 Staging all changes...")
        with yaspin(text="Staging...", color="cyan") as spinner:
            run_command("git add .", capture_output=False)
            spinner.ok("✅")
        
        # Count staged files
        staged_files = run_command("git diff --cached --name-only")
        if staged_files:
            file_list = staged_files.strip().split('\n')
            file_count = len(file_list)
            print(Fore.GREEN + f"✅ {file_count} file(s) staged")
    
    # Step 2: Get commit message with smart suggestions
    if not commit_message:
        # Generate smart default message
        if config.get("learn_from_history", True):
            default_message = generate_commit_message()
        else:
            default_message = "Update files"
        
        print(Fore.CYAN + f"\n📝 Commit message (press Enter to use default):")
        print(Fore.YELLOW + f"Default: \"{default_message}\"")
        user_input = input(Fore.CYAN + "> " + Fore.WHITE).strip()
        
        if user_input:
            commit_message = user_input
        else:
            commit_message = default_message
            print(Fore.GREEN + f"✅ Using: \"{commit_message}\"")
    
    # Commit
    with yaspin(text="Committing...", color="cyan") as spinner:
        result = run_command(f'git commit -m "{commit_message}"', capture_output=False)
        if result is not None:
            spinner.ok("✅")
            print(Fore.GREEN + "✅ Changes committed!")
        else:
            spinner.fail("❌")
            return
    
    # Step 3: Push based on configuration
    if has_remote():
        if config.get("auto_push", True):
            push = input(Fore.CYAN + "\nPush to remote? (Y/n): ").lower()
            if push != "n":
                push_changes()
            else:
                print(Fore.GREEN + "\n✅ Staged and committed successfully!")
        else:
            print(Fore.GREEN + "\n✅ Staged and committed successfully!")
            print(Fore.YELLOW + "💡 Auto-push is disabled. Use 'gitcli push' to push manually.")
    else:
        print(Fore.YELLOW + "\n💡 No remote configured. Changes committed locally.")
        print(Fore.GREEN + "✅ Staged and committed successfully!")

def commit_changes():
    if not has_staged_changes():
        if has_unstaged_changes():
            print(Fore.CYAN + "📦 No staged changes. Staging all changes...")
            with yaspin(text="Staging all changes...", color="cyan") as spinner:
                run_command("git add .", capture_output=False)
                spinner.ok("✅")
            print(Fore.GREEN + "✅ All changes staged.")
        else:
            print(Fore.YELLOW + "⚠️  No changes to commit.")
            return
    
    print(Fore.CYAN + "\n📝 Enter commit message:")
    message = input("> ").strip()
    if not message:
        print(Fore.RED + "❌ Commit message cannot be empty.")
        return
    with yaspin(text="Committing changes...", color="cyan") as spinner:
        run_command(f'git commit -m "{message}"', capture_output=False)
        spinner.ok("✅")
    print(Fore.GREEN + f"✅ Changes committed with message: '{message}'")
    send_notification("GitCLI", f"Commit successful: {message[:30]}...")

def push_changes():
    branch = get_current_branch()
    
    if not has_remote():
        print(Fore.RED + "❌ No remote repository configured.")
        return
    
    # Check if there are uncommitted changes
    if has_unstaged_changes() or has_staged_changes():
        print(Fore.YELLOW + "⚠️  You have uncommitted changes. Commit them first or use 'qp' for quick push.")
        return
    
    # Now push (will push any commits that are ahead of remote)
    with yaspin(text=f"Pushing branch '{branch}'...", color="magenta") as spinner:
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
                        force_result = run_command("git push --force", capture_output=False)
                        if force_result is not None:
                            spinner2.ok("🚀")
                            print(Fore.GREEN + f"✅ Force pushed to '{branch}'!")
                            send_notification("GitCLI", f"Force push to '{branch}' complete!")
                        else:
                            spinner2.fail("❌")
                else:
                    print(Fore.CYAN + "🚫 Force push canceled.")
            else:
                print(Fore.RED + f"❌ Push failed: {result.stderr.strip()}")

def pull_changes():
    branch = get_current_branch()
    
    if not has_remote():
        print(Fore.RED + "❌ No remote repository configured.")
        return
    
    print(Fore.CYAN + f"\n⬇️  Pulling latest changes for '{branch}'...")
    with yaspin(text="Pulling...", color="cyan") as spinner:
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
            run_command("git add .", capture_output=False)
            spinner.ok("✅")
        print(Fore.GREEN + "✅ All changes staged.")
    elif choice == "2":
        print(Fore.CYAN + "\nUnstaged files:")
        display_command("git diff --name-only")
        print(Fore.CYAN + "\nEnter file paths (space-separated):")
        files = input("> ").strip()
        if not files:
            print(Fore.RED + "❌ No files specified.")
            return
        with yaspin(text="Staging files...", color="cyan") as spinner:
            run_command(f"git add {files}", capture_output=False)
            spinner.ok("✅")
        print(Fore.GREEN + f"✅ Files staged: {files}")
    else:
        print(Fore.RED + "❌ Invalid option.")

def show_status():
    print(Fore.CYAN + "\n📊 Git Status:\n" + "-"*30)
    display_command("git status")

def show_log():
    print(Fore.CYAN + "\n📜 Recent Commits:\n" + "-"*30)
    display_command("git log --oneline --graph --decorate -10")

def show_diff():
    """Show unstaged changes"""
    if not has_unstaged_changes():
        print(Fore.YELLOW + "⚠️  No unstaged changes to show.")
        return
    print(Fore.CYAN + "\n📝 Unstaged Changes:\n" + "-"*30)
    display_command("git diff")

def show_diff_staged():
    """Show staged changes"""
    if not has_staged_changes():
        print(Fore.YELLOW + "⚠️  No staged changes to show.")
        return
    print(Fore.CYAN + "\n📝 Staged Changes:\n" + "-"*30)
    display_command("git diff --cached")

def sync_changes():
    """Pull then push changes"""
    branch = get_current_branch()
    
    if not has_remote():
        print(Fore.RED + "❌ No remote repository configured.")
        return
    
    # Pull first
    print(Fore.CYAN + f"\n🔄 Syncing '{branch}': Pull → Push")
    with yaspin(text="Pulling latest changes...", color="cyan") as spinner:
        result = subprocess.run("git pull", shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            spinner.fail("❌")
            print(Fore.RED + f"❌ Pull failed: {result.stderr.strip()}")
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
        result = subprocess.run("git push", shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            spinner.ok("🚀")
            print(Fore.GREEN + f"✅ Sync complete!")
            send_notification("GitCLI", f"Sync to '{branch}' complete!")
        else:
            spinner.fail("❌")
            print(Fore.RED + f"❌ Push failed: {result.stderr.strip()}")

def fetch_changes():
    """Fetch updates from remote without merging"""
    if not has_remote():
        print(Fore.RED + "❌ No remote repository configured.")
        return
    
    print(Fore.CYAN + "\n📥 Fetching updates from remote...")
    with yaspin(text="Fetching...", color="cyan") as spinner:
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
        run_command(f'git commit -m "{message}"', capture_output=False)
        spinner.ok("✅")
    print(Fore.GREEN + f"✅ Changes committed with message: '{message}'")
    
    # Push
    with yaspin(text=f"Pushing to '{branch}'...", color="magenta") as spinner:
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
                        force_result = run_command("git push --force", capture_output=False)
                        if force_result is not None:
                            spinner2.ok("🚀")
                            print(Fore.GREEN + f"✅ Force pushed to '{branch}'!")
                            send_notification("GitCLI", f"Force push to '{branch}' complete!")
                        else:
                            spinner2.fail("❌")
                else:
                    print(Fore.CYAN + "🚫 Force push canceled.")
            else:
                print(Fore.RED + f"❌ Push failed: {result.stderr.strip()}")
