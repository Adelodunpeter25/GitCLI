import subprocess
import os
import platform
from colorama import Fore

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
