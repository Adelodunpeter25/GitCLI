import os
import subprocess
from colorama import Fore
from yaspin import yaspin
from .helpers import run_command, display_command, has_any_changes

def stash_changes():
    """Stash uncommitted changes"""
    if not has_any_changes():
        print(Fore.YELLOW + "⚠️  No changes to stash.")
        return
    
    print(Fore.CYAN + "\n💾 Stash Changes")
    print(Fore.CYAN + "Enter stash message (optional, press Enter to skip):")
    message = input("> ").strip()
    
    cmd = "git stash push"
    if message:
        cmd += f' -m "{message}"'
    
    with yaspin(text="Stashing changes...", color="cyan") as spinner:
        result = run_command(cmd, capture_output=False)
        if result is not None:
            spinner.ok("✅")
            if message:
                print(Fore.GREEN + f"✅ Changes stashed with message: '{message}'")
            else:
                print(Fore.GREEN + "✅ Changes stashed successfully!")
        else:
            spinner.fail("❌")

def stash_pop():
    """Apply and remove the most recent stash"""
    # Check if there are stashes
    stashes = run_command("git stash list")
    if not stashes:
        print(Fore.YELLOW + "⚠️  No stashes found.")
        return
    
    print(Fore.CYAN + "\n📤 Pop Stash (apply and remove)")
    print(Fore.CYAN + "\nAvailable stashes:")
    display_command("git stash list")
    
    print(Fore.CYAN + "\nOptions:")
    print("  1. Pop most recent stash")
    print("  2. Pop specific stash")
    
    choice = input("\nChoose option (1/2): ").strip()
    
    if choice == "1":
        with yaspin(text="Popping stash...", color="cyan") as spinner:
            result = subprocess.run("git stash pop", shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                spinner.ok("✅")
                print(Fore.GREEN + "✅ Stash applied and removed!")
            else:
                spinner.fail("❌")
                if "CONFLICT" in result.stdout or "CONFLICT" in result.stderr:
                    print(Fore.RED + "❌ Conflicts detected while applying stash!")
                    print(Fore.YELLOW + "💡 Resolve conflicts and run 'gitcli resolve-conflicts'")
                else:
                    print(Fore.RED + f"❌ Failed to pop stash: {result.stderr}")
    
    elif choice == "2":
        stash_id = input("\nEnter stash ID (e.g., stash@{0}): ").strip()
        if not stash_id:
            print(Fore.RED + "❌ Stash ID cannot be empty.")
            return
        
        with yaspin(text=f"Popping {stash_id}...", color="cyan") as spinner:
            result = subprocess.run(f"git stash pop {stash_id}", shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                spinner.ok("✅")
                print(Fore.GREEN + f"✅ Stash {stash_id} applied and removed!")
            else:
                spinner.fail("❌")
                if "CONFLICT" in result.stdout or "CONFLICT" in result.stderr:
                    print(Fore.RED + "❌ Conflicts detected while applying stash!")
                    print(Fore.YELLOW + "💡 Resolve conflicts and run 'gitcli resolve-conflicts'")
                else:
                    print(Fore.RED + f"❌ Failed to pop stash: {result.stderr}")
    else:
        print(Fore.RED + "❌ Invalid option.")

def stash_apply():
    """Apply stash without removing it"""
    # Check if there are stashes
    stashes = run_command("git stash list")
    if not stashes:
        print(Fore.YELLOW + "⚠️  No stashes found.")
        return
    
    print(Fore.CYAN + "\n📥 Apply Stash (keep in stash list)")
    print(Fore.CYAN + "\nAvailable stashes:")
    display_command("git stash list")
    
    print(Fore.CYAN + "\nOptions:")
    print("  1. Apply most recent stash")
    print("  2. Apply specific stash")
    
    choice = input("\nChoose option (1/2): ").strip()
    
    if choice == "1":
        with yaspin(text="Applying stash...", color="cyan") as spinner:
            result = subprocess.run("git stash apply", shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                spinner.ok("✅")
                print(Fore.GREEN + "✅ Stash applied successfully!")
                print(Fore.CYAN + "💡 Stash is still saved. Use 'stash-drop' to remove it.")
            else:
                spinner.fail("❌")
                if "CONFLICT" in result.stdout or "CONFLICT" in result.stderr:
                    print(Fore.RED + "❌ Conflicts detected while applying stash!")
                    print(Fore.YELLOW + "💡 Resolve conflicts and run 'gitcli resolve-conflicts'")
                else:
                    print(Fore.RED + f"❌ Failed to apply stash: {result.stderr}")
    
    elif choice == "2":
        stash_id = input("\nEnter stash ID (e.g., stash@{0}): ").strip()
        if not stash_id:
            print(Fore.RED + "❌ Stash ID cannot be empty.")
            return
        
        with yaspin(text=f"Applying {stash_id}...", color="cyan") as spinner:
            result = subprocess.run(f"git stash apply {stash_id}", shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                spinner.ok("✅")
                print(Fore.GREEN + f"✅ Stash {stash_id} applied successfully!")
                print(Fore.CYAN + "💡 Stash is still saved. Use 'stash-drop' to remove it.")
            else:
                spinner.fail("❌")
                if "CONFLICT" in result.stdout or "CONFLICT" in result.stderr:
                    print(Fore.RED + "❌ Conflicts detected while applying stash!")
                    print(Fore.YELLOW + "💡 Resolve conflicts and run 'gitcli resolve-conflicts'")
                else:
                    print(Fore.RED + f"❌ Failed to apply stash: {result.stderr}")
    else:
        print(Fore.RED + "❌ Invalid option.")

def stash_list():
    """List all stashes"""
    stashes = run_command("git stash list")
    
    if not stashes:
        print(Fore.YELLOW + "\n⚠️  No stashes found.")
        return
    
    print(Fore.CYAN + "\n📋 Stash List:\n" + "-"*60)
    display_command("git stash list")
    print(Fore.CYAN + "-"*60)
    
    # Show details option
    show_details = input("\nShow details for a stash? (y/N): ").lower()
    if show_details == "y":
        stash_id = input("Enter stash ID (e.g., stash@{0}): ").strip()
        if stash_id:
            print(Fore.CYAN + f"\n📄 Details for {stash_id}:\n" + "-"*60)
            display_command(f"git stash show -p {stash_id}")

def stash_drop():
    """Remove a stash"""
    stashes = run_command("git stash list")
    if not stashes:
        print(Fore.YELLOW + "⚠️  No stashes found.")
        return
    
    print(Fore.CYAN + "\n🗑️  Drop Stash")
    print(Fore.CYAN + "\nAvailable stashes:")
    display_command("git stash list")
    
    print(Fore.CYAN + "\nOptions:")
    print("  1. Drop most recent stash")
    print("  2. Drop specific stash")
    print("  3. Drop all stashes")
    
    choice = input("\nChoose option (1-3): ").strip()
    
    if choice == "1":
        confirm = input(Fore.YELLOW + "Drop most recent stash? (y/N): ").lower()
        if confirm == "y":
            with yaspin(text="Dropping stash...", color="yellow") as spinner:
                result = run_command("git stash drop", capture_output=False)
                if result is not None:
                    spinner.ok("✅")
                    print(Fore.GREEN + "✅ Stash dropped!")
                else:
                    spinner.fail("❌")
    
    elif choice == "2":
        stash_id = input("\nEnter stash ID (e.g., stash@{0}): ").strip()
        if not stash_id:
            print(Fore.RED + "❌ Stash ID cannot be empty.")
            return
        
        confirm = input(Fore.YELLOW + f"Drop {stash_id}? (y/N): ").lower()
        if confirm == "y":
            with yaspin(text=f"Dropping {stash_id}...", color="yellow") as spinner:
                result = run_command(f"git stash drop {stash_id}", capture_output=False)
                if result is not None:
                    spinner.ok("✅")
                    print(Fore.GREEN + f"✅ Stash {stash_id} dropped!")
                else:
                    spinner.fail("❌")
    
    elif choice == "3":
        confirm = input(Fore.RED + "Drop ALL stashes? This cannot be undone! (yes/N): ").lower()
        if confirm == "yes":
            with yaspin(text="Dropping all stashes...", color="red") as spinner:
                result = run_command("git stash clear", capture_output=False)
                if result is not None:
                    spinner.ok("✅")
                    print(Fore.GREEN + "✅ All stashes cleared!")
                else:
                    spinner.fail("❌")
    else:
        print(Fore.RED + "❌ Invalid option.")

def stash_show():
    """Show changes in a stash"""
    stashes = run_command("git stash list")
    if not stashes:
        print(Fore.YELLOW + "⚠️  No stashes found.")
        return
    
    print(Fore.CYAN + "\n📄 Show Stash Contents")
    print(Fore.CYAN + "\nAvailable stashes:")
    display_command("git stash list")
    
    stash_id = input("\nEnter stash ID (e.g., stash@{0}, or press Enter for most recent): ").strip()
    
    cmd = "git stash show -p"
    if stash_id:
        cmd += f" {stash_id}"
    
    print(Fore.CYAN + f"\n📝 Stash Contents:\n" + "-"*60)
    display_command(cmd)
