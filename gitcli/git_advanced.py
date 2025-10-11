import os
import time
from colorama import Fore
from yaspin import yaspin
from helpers import run_command, has_unstaged_changes, has_staged_changes

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
