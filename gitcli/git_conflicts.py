import os
import subprocess
import platform
from colorama import Fore
from yaspin import yaspin
from .helpers import run_command, display_command

def has_conflicts():
    """Check if there are merge conflicts"""
    result = run_command("git diff --name-only --diff-filter=U")
    return bool(result and result.strip())

def get_conflicted_files():
    """Get list of files with conflicts"""
    result = run_command("git diff --name-only --diff-filter=U")
    if result:
        return result.strip().split('\n')
    return []

def show_conflict_markers(filepath):
    """Show conflict markers in a file"""
    try:
        with open(filepath, 'r') as f:
            lines = f.readlines()
        
        in_conflict = False
        conflict_count = 0
        
        for i, line in enumerate(lines, 1):
            if line.startswith('<<<<<<<'):
                in_conflict = True
                conflict_count += 1
                print(Fore.RED + f"{i:4d} | {line.rstrip()}")
            elif line.startswith('======='):
                print(Fore.YELLOW + f"{i:4d} | {line.rstrip()}")
            elif line.startswith('>>>>>>>'):
                in_conflict = False
                print(Fore.GREEN + f"{i:4d} | {line.rstrip()}")
            elif in_conflict:
                print(Fore.WHITE + f"{i:4d} | {line.rstrip()}")
        
        return conflict_count
    except Exception as e:
        print(Fore.RED + f"❌ Error reading file: {e}")
        return 0

def open_in_editor(filepath):
    """Open file in default editor"""
    system = platform.system()
    
    try:
        if system == "Darwin":  # macOS
            # Try VS Code first, then fall back to default
            if subprocess.run(["which", "code"], capture_output=True).returncode == 0:
                subprocess.run(["code", "-w", filepath])
            else:
                subprocess.run(["open", "-t", filepath])
        elif system == "Linux":
            # Try common editors
            editors = ["code", "gedit", "nano", "vim"]
            for editor in editors:
                if subprocess.run(["which", editor], capture_output=True).returncode == 0:
                    if editor in ["nano", "vim"]:
                        subprocess.run([editor, filepath])
                    else:
                        subprocess.run([editor, filepath])
                    break
        elif system == "Windows":
            # Try VS Code first, then notepad
            if subprocess.run(["where", "code"], capture_output=True).returncode == 0:
                subprocess.run(["code", "-w", filepath])
            else:
                subprocess.run(["notepad", filepath])
        
        return True
    except Exception as e:
        print(Fore.RED + f"❌ Error opening editor: {e}")
        return False

def resolve_conflicts():
    """Interactive conflict resolution helper"""
    if not has_conflicts():
        print(Fore.GREEN + "\n✅ No conflicts detected!")
        return
    
    conflicted_files = get_conflicted_files()
    
    print(Fore.RED + "\n⚠️  Merge Conflicts Detected!")
    print(Fore.CYAN + f"\n📋 Conflicted Files ({len(conflicted_files)}):\n" + "-"*60)
    
    for i, filepath in enumerate(conflicted_files, 1):
        print(f"  {i}. {Fore.YELLOW}{filepath}")
    
    print(Fore.CYAN + "-"*60)
    
    print(Fore.CYAN + "\n🔧 Conflict Resolution Options:")
    print("  1. View conflicts in each file")
    print("  2. Open file in editor")
    print("  3. Accept ours (current branch)")
    print("  4. Accept theirs (incoming branch)")
    print("  5. Mark as resolved")
    print("  6. Abort merge")
    print("  7. Exit")
    
    while True:
        choice = input(f"\n{Fore.CYAN}Choose option (1-7): ").strip()
        
        if choice == "1":
            # View conflicts
            file_num = input(f"Enter file number (1-{len(conflicted_files)}): ").strip()
            try:
                idx = int(file_num) - 1
                if 0 <= idx < len(conflicted_files):
                    filepath = conflicted_files[idx]
                    print(Fore.CYAN + f"\n📄 Conflicts in {filepath}:\n" + "-"*60)
                    conflict_count = show_conflict_markers(filepath)
                    print(Fore.CYAN + "-"*60)
                    print(Fore.YELLOW + f"Found {conflict_count} conflict(s)")
                    print(Fore.CYAN + "\nLegend:")
                    print(Fore.RED + "  <<<<<<< Current changes (yours)")
                    print(Fore.YELLOW + "  ======= Separator")
                    print(Fore.GREEN + "  >>>>>>> Incoming changes (theirs)")
                else:
                    print(Fore.RED + "❌ Invalid file number.")
            except ValueError:
                print(Fore.RED + "❌ Invalid input.")
        
        elif choice == "2":
            # Open in editor
            file_num = input(f"Enter file number (1-{len(conflicted_files)}): ").strip()
            try:
                idx = int(file_num) - 1
                if 0 <= idx < len(conflicted_files):
                    filepath = conflicted_files[idx]
                    print(Fore.CYAN + f"\n📝 Opening {filepath} in editor...")
                    print(Fore.YELLOW + "💡 Remove conflict markers and save the file.")
                    if open_in_editor(filepath):
                        print(Fore.GREEN + "✅ Editor closed.")
                        mark = input("Mark this file as resolved? (y/N): ").lower()
                        if mark == "y":
                            result = run_command(f"git add {filepath}", capture_output=False)
                            if result is not None:
                                print(Fore.GREEN + f"✅ {filepath} marked as resolved!")
                                conflicted_files.remove(filepath)
                                if not conflicted_files:
                                    print(Fore.GREEN + "\n🎉 All conflicts resolved!")
                                    complete_merge()
                                    break
                else:
                    print(Fore.RED + "❌ Invalid file number.")
            except ValueError:
                print(Fore.RED + "❌ Invalid input.")
        
        elif choice == "3":
            # Accept ours
            file_num = input(f"Enter file number (1-{len(conflicted_files)}, or 'all'): ").strip()
            if file_num.lower() == "all":
                confirm = input(Fore.YELLOW + "Accept current branch version for ALL files? (y/N): ").lower()
                if confirm == "y":
                    with yaspin(text="Accepting ours for all files...", color="cyan") as spinner:
                        result = run_command("git checkout --ours .", capture_output=False)
                        if result is not None:
                            run_command("git add .", capture_output=False)
                            spinner.ok("✅")
                            print(Fore.GREEN + "✅ All files resolved with current branch version!")
                            complete_merge()
                            break
                        else:
                            spinner.fail("❌")
            else:
                try:
                    idx = int(file_num) - 1
                    if 0 <= idx < len(conflicted_files):
                        filepath = conflicted_files[idx]
                        confirm = input(Fore.YELLOW + f"Accept current branch version for {filepath}? (y/N): ").lower()
                        if confirm == "y":
                            result = run_command(f"git checkout --ours {filepath}", capture_output=False)
                            if result is not None:
                                run_command(f"git add {filepath}", capture_output=False)
                                print(Fore.GREEN + f"✅ {filepath} resolved with current branch version!")
                                conflicted_files.remove(filepath)
                                if not conflicted_files:
                                    print(Fore.GREEN + "\n🎉 All conflicts resolved!")
                                    complete_merge()
                                    break
                    else:
                        print(Fore.RED + "❌ Invalid file number.")
                except ValueError:
                    print(Fore.RED + "❌ Invalid input.")
        
        elif choice == "4":
            # Accept theirs
            file_num = input(f"Enter file number (1-{len(conflicted_files)}, or 'all'): ").strip()
            if file_num.lower() == "all":
                confirm = input(Fore.YELLOW + "Accept incoming branch version for ALL files? (y/N): ").lower()
                if confirm == "y":
                    with yaspin(text="Accepting theirs for all files...", color="cyan") as spinner:
                        result = run_command("git checkout --theirs .", capture_output=False)
                        if result is not None:
                            run_command("git add .", capture_output=False)
                            spinner.ok("✅")
                            print(Fore.GREEN + "✅ All files resolved with incoming branch version!")
                            complete_merge()
                            break
                        else:
                            spinner.fail("❌")
            else:
                try:
                    idx = int(file_num) - 1
                    if 0 <= idx < len(conflicted_files):
                        filepath = conflicted_files[idx]
                        confirm = input(Fore.YELLOW + f"Accept incoming branch version for {filepath}? (y/N): ").lower()
                        if confirm == "y":
                            result = run_command(f"git checkout --theirs {filepath}", capture_output=False)
                            if result is not None:
                                run_command(f"git add {filepath}", capture_output=False)
                                print(Fore.GREEN + f"✅ {filepath} resolved with incoming branch version!")
                                conflicted_files.remove(filepath)
                                if not conflicted_files:
                                    print(Fore.GREEN + "\n🎉 All conflicts resolved!")
                                    complete_merge()
                                    break
                    else:
                        print(Fore.RED + "❌ Invalid file number.")
                except ValueError:
                    print(Fore.RED + "❌ Invalid input.")
        
        elif choice == "5":
            # Mark as resolved
            file_num = input(f"Enter file number (1-{len(conflicted_files)}): ").strip()
            try:
                idx = int(file_num) - 1
                if 0 <= idx < len(conflicted_files):
                    filepath = conflicted_files[idx]
                    result = run_command(f"git add {filepath}", capture_output=False)
                    if result is not None:
                        print(Fore.GREEN + f"✅ {filepath} marked as resolved!")
                        conflicted_files.remove(filepath)
                        if not conflicted_files:
                            print(Fore.GREEN + "\n🎉 All conflicts resolved!")
                            complete_merge()
                            break
                else:
                    print(Fore.RED + "❌ Invalid file number.")
            except ValueError:
                print(Fore.RED + "❌ Invalid input.")
        
        elif choice == "6":
            # Abort merge
            confirm = input(Fore.RED + "Abort merge and return to pre-merge state? (yes/N): ").lower()
            if confirm == "yes":
                with yaspin(text="Aborting merge...", color="red") as spinner:
                    result = run_command("git merge --abort", capture_output=False)
                    if result is not None:
                        spinner.ok("✅")
                        print(Fore.GREEN + "✅ Merge aborted!")
                    else:
                        spinner.fail("❌")
                break
        
        elif choice == "7":
            # Exit
            print(Fore.CYAN + "👋 Exiting conflict resolution.")
            print(Fore.YELLOW + "💡 Run 'gitcli resolve-conflicts' to continue later.")
            break
        
        else:
            print(Fore.RED + "❌ Invalid option.")

def complete_merge():
    """Complete the merge after conflicts are resolved"""
    print(Fore.CYAN + "\n🎯 Ready to complete merge!")
    
    # Check if it's a merge in progress
    if os.path.exists(".git/MERGE_HEAD"):
        print(Fore.CYAN + "Enter merge commit message (or press Enter for default):")
        message = input("> ").strip()
        
        with yaspin(text="Completing merge...", color="cyan") as spinner:
            if message:
                result = run_command(f'git commit -m "{message}"', capture_output=False)
            else:
                result = run_command("git commit --no-edit", capture_output=False)
            
            if result is not None:
                spinner.ok("✅")
                print(Fore.GREEN + "✅ Merge completed successfully!")
            else:
                spinner.fail("❌")
    else:
        print(Fore.GREEN + "✅ Changes staged. Use 'gitcli commit' to commit.")

def check_conflicts():
    """Quick check for conflicts"""
    if has_conflicts():
        conflicted_files = get_conflicted_files()
        print(Fore.RED + f"\n⚠️  {len(conflicted_files)} file(s) with conflicts:")
        for filepath in conflicted_files:
            print(f"  • {Fore.YELLOW}{filepath}")
        print(Fore.CYAN + "\n💡 Run 'gitcli resolve-conflicts' to resolve them.")
        return True
    else:
        print(Fore.GREEN + "\n✅ No conflicts detected!")
        return False
