import os
from colorama import Fore
from yaspin import yaspin
from .helpers import run_command, get_current_branch, sanitize_name, display_command

def switch_branch():
    print(Fore.CYAN + "\n🔀 Available branches:")
    display_command("git branch")
    branch = input("\nEnter branch name to switch to: ").strip()
    if not branch:
        print(Fore.RED + "❌ Branch name cannot be empty.")
        return
    
    # Check if branch exists
    branches = run_command("git branch --list")
    if not branches or branch not in branches:
        print(Fore.YELLOW + f"⚠️  Branch '{branch}' doesn't exist locally.")
        create = input("Would you like to create it? (y/N): ").lower()
        if create == "y":
            add_branch(branch)
            return
        else:
            print(Fore.CYAN + "🚫 Switch canceled.")
            return
    
    with yaspin(text=f"Switching to '{branch}'...", color="cyan") as spinner:
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
    display_command("git branch --all")
