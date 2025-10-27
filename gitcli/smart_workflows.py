"""
Smart workflows that automate common Git patterns
"""
import os
import subprocess
from colorama import Fore
from yaspin import yaspin
from .helpers import (
    run_command, get_current_branch, has_staged_changes,
    has_unstaged_changes, has_any_changes, has_remote, send_notification
)
from .git_conflicts import has_conflicts, resolve_conflicts
from .git_stash import stash_changes, stash_pop


def smart_save():
    """
    Intelligently save work based on current state:
    - Uncommitted changes → Ask: commit or stash
    - Committed changes → Push
    - Nothing to save → Inform user
    """
    branch = get_current_branch()
    
    # Check for conflicts first
    if has_conflicts():
        print(Fore.RED + "\n⚠️  You have unresolved conflicts!")
        print(Fore.CYAN + "💡 Resolve them first before saving.")
        resolve = input("Open conflict resolution helper? (Y/n): ").lower()
        if resolve != "n":
            resolve_conflicts()
        return
    
    # Check for uncommitted changes
    if has_any_changes():
        print(Fore.CYAN + f"\n💾 You have uncommitted changes on '{branch}'")
        print(Fore.CYAN + "What would you like to do?")
        print("  1. Commit and push (save permanently)")
        print("  2. Stash (save temporarily)")
        print("  3. Show changes first")
        print("  4. Cancel")
        
        choice = input("\nChoose option (1-4): ").strip()
        
        if choice == "1":
            # Commit and push workflow
            _commit_and_push()
        elif choice == "2":
            # Stash workflow
            print(Fore.CYAN + "\n📝 Enter stash message (optional):")
            message = input("> ").strip()
            cmd = "git stash push"
            if message:
                cmd += f' -m "{message}"'
            
            with yaspin(text="Stashing changes...", color="cyan") as spinner:
                result = run_command(cmd, capture_output=False)
                if result is not None:
                    spinner.ok("✅")
                    print(Fore.GREEN + "✅ Changes stashed successfully!")
                    send_notification("GitCLI", "Changes stashed")
                else:
                    spinner.fail("❌")
        elif choice == "3":
            # Show changes
            print(Fore.CYAN + "\n📝 Your changes:\n" + "-"*60)
            subprocess.run("git status -s", shell=True)
            print(Fore.CYAN + "-"*60)
            # Ask again
            smart_save()
        else:
            print(Fore.CYAN + "🚫 Save canceled.")
    else:
        # Check if there are unpushed commits
        if has_remote():
            ahead = run_command("git rev-list --count @{u}..HEAD 2>/dev/null")
            if ahead and int(ahead) > 0:
                print(Fore.CYAN + f"\n📤 You have {ahead} unpushed commit(s) on '{branch}'")
                push = input("Push to remote? (Y/n): ").lower()
                if push != "n":
                    _push_changes()
            else:
                print(Fore.GREEN + "\n✅ Everything is saved and up to date!")
        else:
            print(Fore.GREEN + "\n✅ No changes to save!")


def _commit_and_push():
    """Helper to commit and push changes"""
    branch = get_current_branch()
    
    # Stage all changes
    if has_unstaged_changes():
        print(Fore.CYAN + "\n📦 Staging all changes...")
        run_command("git add .", capture_output=False)
    
    # Get commit message
    print(Fore.CYAN + "\n📝 Enter commit message:")
    message = input("> ").strip()
    if not message:
        print(Fore.RED + "❌ Commit message cannot be empty.")
        return
    
    # Commit
    with yaspin(text="Committing...", color="cyan") as spinner:
        result = run_command(f'git commit -m "{message}"', capture_output=False)
        if result is not None:
            spinner.ok("✅")
            print(Fore.GREEN + "✅ Changes committed!")
        else:
            spinner.fail("❌")
            return
    
    # Push if remote exists
    if has_remote():
        push = input(Fore.CYAN + "Push to remote? (Y/n): ").lower()
        if push != "n":
            _push_changes()
    else:
        print(Fore.YELLOW + "💡 No remote configured. Changes committed locally.")


def _push_changes():
    """Helper to push changes"""
    branch = get_current_branch()
    
    with yaspin(text=f"Pushing to '{branch}'...", color="magenta") as spinner:
        result = subprocess.run("git push", shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            spinner.ok("🚀")
            print(Fore.GREEN + f"✅ Pushed to '{branch}'!")
            send_notification("GitCLI", f"Pushed to '{branch}'")
        else:
            spinner.fail("❌")
            if "rejected" in result.stderr and "non-fast-forward" in result.stderr:
                print(Fore.YELLOW + "\n⚠️  Push rejected: Your branch is behind remote.")
                print(Fore.CYAN + "💡 Run 'gitcli sync' to get latest changes first.")
            elif "no upstream" in result.stderr:
                print(Fore.YELLOW + "\n⚠️  No upstream branch set.")
                setup = input("Set upstream and push? (Y/n): ").lower()
                if setup != "n":
                    with yaspin(text="Setting upstream and pushing...", color="magenta") as spinner2:
                        result2 = run_command(f"git push -u origin {branch}", capture_output=False)
                        if result2 is not None:
                            spinner2.ok("🚀")
                            print(Fore.GREEN + f"✅ Pushed to '{branch}' and set upstream!")
                        else:
                            spinner2.fail("❌")
            else:
                print(Fore.RED + f"❌ Push failed: {result.stderr.strip()}")


def smart_work(branch_name=None):
    """
    Start working on a feature:
    - Stash current work if needed
    - Create/switch to branch
    - Pull latest if branch exists remotely
    """
    if not branch_name:
        print(Fore.CYAN + "\n🌿 Enter branch name to work on:")
        branch_name = input("> ").strip()
    
    if not branch_name:
        print(Fore.RED + "❌ Branch name cannot be empty.")
        return
    
    # Sanitize branch name
    branch_name = branch_name.strip().replace(" ", "-")
    current_branch = get_current_branch()
    
    # Check for uncommitted changes
    if has_any_changes():
        print(Fore.YELLOW + f"\n⚠️  You have uncommitted changes on '{current_branch}'")
        print(Fore.CYAN + "What would you like to do?")
        print("  1. Stash and switch")
        print("  2. Commit and switch")
        print("  3. Cancel")
        
        choice = input("\nChoose option (1-3): ").strip()
        
        if choice == "1":
            # Stash changes
            message = f"Auto-stash from {current_branch} before switching to {branch_name}"
            with yaspin(text="Stashing changes...", color="cyan") as spinner:
                result = run_command(f'git stash push -m "{message}"', capture_output=False)
                if result is not None:
                    spinner.ok("✅")
                    print(Fore.GREEN + "✅ Changes stashed!")
                else:
                    spinner.fail("❌")
                    return
        elif choice == "2":
            # Quick commit
            print(Fore.CYAN + "\n📝 Enter commit message:")
            msg = input("> ").strip()
            if not msg:
                print(Fore.RED + "❌ Commit message required.")
                return
            run_command("git add .", capture_output=False)
            run_command(f'git commit -m "{msg}"', capture_output=False)
            print(Fore.GREEN + "✅ Changes committed!")
        else:
            print(Fore.CYAN + "🚫 Canceled.")
            return
    
    # Check if branch exists locally
    branches = run_command("git branch --list")
    branch_exists = branch_name in branches if branches else False
    
    if branch_exists:
        # Switch to existing branch
        print(Fore.CYAN + f"\n🔀 Switching to existing branch '{branch_name}'...")
        with yaspin(text="Switching...", color="cyan") as spinner:
            result = run_command(f"git checkout {branch_name}", capture_output=False)
            if result is not None:
                spinner.ok("✅")
                print(Fore.GREEN + f"✅ Switched to '{branch_name}'")
            else:
                spinner.fail("❌")
                return
        
        # Pull latest if remote exists
        if has_remote():
            pull = input(Fore.CYAN + "Pull latest changes? (Y/n): ").lower()
            if pull != "n":
                with yaspin(text="Pulling...", color="cyan") as spinner:
                    result = subprocess.run("git pull", shell=True, capture_output=True, text=True)
                    if result.returncode == 0:
                        spinner.ok("✅")
                        print(Fore.GREEN + "✅ Up to date!")
                    else:
                        spinner.fail("❌")
                        if "CONFLICT" in result.stdout:
                            print(Fore.RED + "❌ Conflicts detected!")
                            resolve_conflicts()
    else:
        # Create new branch
        print(Fore.CYAN + f"\n🌿 Creating new branch '{branch_name}'...")
        
        # Ask which branch to base on
        print(Fore.CYAN + "Create from:")
        print(f"  1. Current branch ({current_branch})")
        print("  2. main")
        print("  3. master")
        
        choice = input("\nChoose option (1-3, default: 1): ").strip() or "1"
        
        base_branch = current_branch
        if choice == "2":
            base_branch = "main"
        elif choice == "3":
            base_branch = "master"
        
        # Switch to base branch if needed
        if base_branch != current_branch:
            run_command(f"git checkout {base_branch}", capture_output=False)
            if has_remote():
                run_command("git pull", capture_output=False)
        
        # Create and switch to new branch
        with yaspin(text=f"Creating branch '{branch_name}'...", color="cyan") as spinner:
            result = run_command(f"git checkout -b {branch_name}", capture_output=False)
            if result is not None:
                spinner.ok("✅")
                print(Fore.GREEN + f"✅ Created and switched to '{branch_name}'")
            else:
                spinner.fail("❌")
                return
    
    print(Fore.GREEN + f"\n🎉 Ready to work on '{branch_name}'!")


def smart_done():
    """
    Finish current work:
    - Commit all changes
    - Push to remote
    - Optionally switch back to main
    """
    branch = get_current_branch()
    
    if not has_any_changes():
        print(Fore.YELLOW + "\n⚠️  No uncommitted changes.")
        
        # Check for unpushed commits
        if has_remote():
            ahead = run_command("git rev-list --count @{u}..HEAD 2>/dev/null")
            if ahead and int(ahead) > 0:
                print(Fore.CYAN + f"You have {ahead} unpushed commit(s).")
                push = input("Push them? (Y/n): ").lower()
                if push != "n":
                    _push_changes()
            else:
                print(Fore.GREEN + "✅ Everything is already saved and pushed!")
        
        # Ask about switching back
        if branch not in ["main", "master"]:
            switch = input(Fore.CYAN + f"\nSwitch back to main? (y/N): ").lower()
            if switch == "y":
                _switch_to_main()
        return
    
    # Commit workflow
    print(Fore.CYAN + f"\n✅ Finishing work on '{branch}'")
    _commit_and_push()
    
    # Ask about switching back
    if branch not in ["main", "master"]:
        switch = input(Fore.CYAN + f"\nSwitch back to main? (y/N): ").lower()
        if switch == "y":
            _switch_to_main()
    
    print(Fore.GREEN + "\n🎉 Work completed!")


def _switch_to_main():
    """Helper to switch back to main/master"""
    # Determine main branch
    branches = run_command("git branch --list")
    if "main" in branches:
        main_branch = "main"
    elif "master" in branches:
        main_branch = "master"
    else:
        print(Fore.YELLOW + "⚠️  No main/master branch found.")
        return
    
    with yaspin(text=f"Switching to {main_branch}...", color="cyan") as spinner:
        result = run_command(f"git checkout {main_branch}", capture_output=False)
        if result is not None:
            spinner.ok("✅")
            print(Fore.GREEN + f"✅ Switched to '{main_branch}'")
            
            # Pull latest
            if has_remote():
                with yaspin(text="Pulling latest...", color="cyan") as spinner2:
                    run_command("git pull", capture_output=False)
                    spinner2.ok("✅")
        else:
            spinner.fail("❌")


def smart_sync():
    """
    Sync with remote:
    - Stash if needed
    - Pull latest
    - Handle conflicts automatically
    - Unstash if stashed
    - Push if ahead
    """
    branch = get_current_branch()
    
    if not has_remote():
        print(Fore.RED + "❌ No remote repository configured.")
        return
    
    print(Fore.CYAN + f"\n🔄 Syncing '{branch}' with remote...")
    
    # Stash if needed
    stashed = False
    if has_any_changes():
        print(Fore.YELLOW + "⚠️  You have uncommitted changes.")
        print(Fore.CYAN + "Stashing them temporarily...")
        with yaspin(text="Stashing...", color="cyan") as spinner:
            result = run_command('git stash push -m "Auto-stash for sync"', capture_output=False)
            if result is not None:
                spinner.ok("✅")
                stashed = True
            else:
                spinner.fail("❌")
                return
    
    # Pull
    with yaspin(text="Pulling latest changes...", color="cyan") as spinner:
        result = subprocess.run("git pull", shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            spinner.ok("✅")
            print(Fore.GREEN + "✅ Pull complete!")
        else:
            spinner.fail("❌")
            if "CONFLICT" in result.stdout or "CONFLICT" in result.stderr:
                print(Fore.RED + "❌ Conflicts detected!")
                resolve_conflicts()
                # Don't unstash if there were conflicts
                if stashed:
                    print(Fore.YELLOW + "\n💡 Your stashed changes are still saved.")
                    print(Fore.CYAN + "Run 'gitcli save' and choose 'Stash pop' after resolving conflicts.")
                return
            else:
                print(Fore.RED + f"❌ Pull failed: {result.stderr}")
                return
    
    # Unstash if we stashed
    if stashed:
        print(Fore.CYAN + "\n📤 Restoring your changes...")
        with yaspin(text="Applying stash...", color="cyan") as spinner:
            result = subprocess.run("git stash pop", shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                spinner.ok("✅")
                print(Fore.GREEN + "✅ Your changes restored!")
            else:
                spinner.fail("❌")
                if "CONFLICT" in result.stdout:
                    print(Fore.RED + "❌ Conflicts while restoring changes!")
                    resolve_conflicts()
                else:
                    print(Fore.YELLOW + "⚠️  Couldn't restore stash automatically.")
                    print(Fore.CYAN + "💡 Your changes are still in stash. Use 'gitcli save' to manage them.")
                return
    
    # Push if ahead
    ahead = run_command("git rev-list --count @{u}..HEAD 2>/dev/null")
    if ahead and int(ahead) > 0:
        print(Fore.CYAN + f"\n📤 You have {ahead} commit(s) to push.")
        push = input("Push now? (Y/n): ").lower()
        if push != "n":
            _push_changes()
    
    print(Fore.GREEN + "\n✅ Sync complete!")
    send_notification("GitCLI", f"Synced '{branch}'")


def smart_undo():
    """
    Smart undo last action:
    - Uncommitted changes → Discard
    - Last commit → Undo commit (keep changes)
    - Pushed commit → Warn and offer revert
    """
    print(Fore.CYAN + "\n↩️  Undo Last Action")
    
    if has_any_changes():
        print(Fore.YELLOW + "⚠️  You have uncommitted changes.")
        print(Fore.CYAN + "What would you like to undo?")
        print("  1. Discard all uncommitted changes")
        print("  2. Discard specific files")
        print("  3. Undo last commit (keep changes)")
        print("  4. Cancel")
        
        choice = input("\nChoose option (1-4): ").strip()
        
        if choice == "1":
            confirm = input(Fore.RED + "Discard ALL uncommitted changes? (yes/N): ").lower()
            if confirm == "yes":
                with yaspin(text="Discarding changes...", color="red") as spinner:
                    run_command("git reset --hard HEAD", capture_output=False)
                    run_command("git clean -fd", capture_output=False)
                    spinner.ok("✅")
                print(Fore.GREEN + "✅ All changes discarded!")
        elif choice == "2":
            print(Fore.CYAN + "\nModified files:")
            subprocess.run("git status -s", shell=True)
            files = input("\nEnter file paths (space-separated): ").strip()
            if files:
                run_command(f"git checkout -- {files}", capture_output=False)
                print(Fore.GREEN + f"✅ Changes discarded for: {files}")
        elif choice == "3":
            _undo_last_commit()
        else:
            print(Fore.CYAN + "🚫 Canceled.")
    else:
        # No uncommitted changes, undo last commit
        print(Fore.CYAN + "No uncommitted changes found.")
        _undo_last_commit()


def _undo_last_commit():
    """Helper to undo last commit"""
    # Check if there are commits
    result = run_command("git log -1 --oneline")
    if not result:
        print(Fore.YELLOW + "⚠️  No commits to undo.")
        return
    
    print(Fore.CYAN + "\nLast commit:")
    subprocess.run("git log -1 --oneline", shell=True)
    
    # Check if pushed
    if has_remote():
        pushed = run_command("git branch -r --contains HEAD")
        if pushed:
            print(Fore.RED + "\n⚠️  This commit has been pushed to remote!")
            print(Fore.YELLOW + "Undoing it will require force push and affect others.")
            print(Fore.CYAN + "\nSafer option: Create a revert commit instead?")
            print("  1. Revert (safe, creates new commit)")
            print("  2. Undo anyway (requires force push)")
            print("  3. Cancel")
            
            choice = input("\nChoose option (1-3): ").strip()
            
            if choice == "1":
                with yaspin(text="Creating revert commit...", color="cyan") as spinner:
                    run_command("git revert HEAD --no-edit", capture_output=False)
                    spinner.ok("✅")
                print(Fore.GREEN + "✅ Revert commit created!")
                return
            elif choice != "2":
                print(Fore.CYAN + "🚫 Canceled.")
                return
    
    confirm = input(Fore.YELLOW + "\nUndo last commit? (y/N): ").lower()
    if confirm == "y":
        with yaspin(text="Undoing commit...", color="yellow") as spinner:
            run_command("git reset --soft HEAD~1", capture_output=False)
            spinner.ok("✅")
        print(Fore.GREEN + "✅ Last commit undone! Changes are still staged.")


def smart_status():
    """
    Enhanced status showing everything relevant:
    - Current branch
    - Uncommitted changes
    - Unpushed commits
    - Stashes
    - Conflicts
    """
    branch = get_current_branch()
    
    print(Fore.CYAN + "\n" + "="*60)
    print(Fore.MAGENTA + f"  📊 Status for '{branch}'")
    print(Fore.CYAN + "="*60)
    
    # Check for conflicts
    if has_conflicts():
        print(Fore.RED + "\n⚠️  CONFLICTS DETECTED!")
        from .git_conflicts import get_conflicted_files
        files = get_conflicted_files()
        for f in files:
            print(f"  • {Fore.YELLOW}{f}")
        print(Fore.CYAN + "💡 Run 'gitcli sync' to resolve")
    
    # Show git status
    print(Fore.CYAN + "\n📝 Working Directory:")
    subprocess.run("git status -s", shell=True)
    
    # Check for unpushed commits
    if has_remote():
        ahead = run_command("git rev-list --count @{u}..HEAD 2>/dev/null")
        behind = run_command("git rev-list --count HEAD..@{u} 2>/dev/null")
        
        if ahead and int(ahead) > 0:
            print(Fore.YELLOW + f"\n📤 {ahead} commit(s) ahead of remote (not pushed)")
        if behind and int(behind) > 0:
            print(Fore.YELLOW + f"📥 {behind} commit(s) behind remote (need to pull)")
        
        if (not ahead or int(ahead) == 0) and (not behind or int(behind) == 0):
            if not has_any_changes():
                print(Fore.GREEN + "\n✅ Everything up to date!")
    
    # Show stashes
    stashes = run_command("git stash list")
    if stashes:
        stash_count = len(stashes.strip().split('\n'))
        print(Fore.CYAN + f"\n💾 {stash_count} stash(es) saved")
        print(Fore.CYAN + "💡 Run 'gitcli save' to manage stashes")
    
    # Show recent commits
    print(Fore.CYAN + "\n📜 Recent Commits:")
    subprocess.run("git log --oneline --graph --decorate -5", shell=True)
    
    print(Fore.CYAN + "\n" + "="*60 + "\n")
