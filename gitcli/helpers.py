import subprocess
import os
import platform
import json
from colorama import Fore

CONFIG_FILE = ".gitcli-config.json"

def run_command(cmd, capture_output=True):
    """Run a shell command safely and return output."""
    try:
        result = subprocess.run(
            cmd, shell=True, check=True,
            capture_output=capture_output, text=True
        )
        return result.stdout.strip() if capture_output else ""
    except subprocess.CalledProcessError as e:
        if capture_output:
            error_msg = e.stderr.strip() if e.stderr else str(e)
            print(Fore.RED + f"❌ Command failed: {error_msg}")
        return None

def display_command(cmd):
    """Run a command and display output directly (for status, log, diff, etc.)"""
    subprocess.run(cmd, shell=True)

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
    branch = run_command("git rev-parse --abbrev-ref HEAD")
    return branch if branch else "main"

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

def get_config():
    """Load GitCLI configuration"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return {
        "auto_push": True,
        "auto_stage": True,
        "commit_message_template": None,
        "learn_from_history": True,
        "pre_save_validation": True,
        "auto_pull_before_push": True,
        "auto_fix_formatting": False,
        "confirm_force_push": True,
        "validation_rules": {
            "check_debug": True,
            "check_secrets": True,
            "check_conflicts": True,
            "check_large_files": True,
            "max_file_size_mb": 10
        }
    }

def save_config(config):
    """Save GitCLI configuration"""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)

def get_commit_history_pattern():
    """Analyze last 5 commits to learn user's pattern"""
    result = run_command("git log -5 --pretty=format:%s")
    if not result:
        return None
    
    commits = result.strip().split('\n')
    if len(commits) < 2:
        return None
    
    # Check if user uses conventional commits
    conventional_count = 0
    for commit in commits:
        if any(commit.startswith(prefix) for prefix in ['feat:', 'fix:', 'docs:', 'style:', 'refactor:', 'test:', 'chore:']):
            conventional_count += 1
    
    if conventional_count >= 3:
        return "conventional"
    
    # Check if user uses WIP pattern
    wip_count = sum(1 for c in commits if c.lower().startswith('wip'))
    if wip_count >= 3:
        return "wip"
    
    return None

def generate_commit_message():
    """Generate smart commit message based on changes"""
    # Get changed files
    staged_files = run_command("git diff --cached --name-only")
    if not staged_files:
        return "Update files"
    
    files = staged_files.strip().split('\n')
    file_count = len(files)
    
    # Get file names only (no paths)
    file_names = [os.path.basename(f) for f in files[:3]]
    
    # Check user's pattern
    pattern = get_commit_history_pattern()
    
    if pattern == "conventional":
        # Determine type based on files
        if any('test' in f.lower() for f in files):
            prefix = "test"
        elif any(f.endswith('.md') or 'readme' in f.lower() for f in files):
            prefix = "docs"
        elif file_count == 1:
            prefix = "feat"
        else:
            prefix = "chore"
        
        if file_count == 1:
            return f"{prefix}: update {file_names[0]}"
        else:
            return f"{prefix}: update {file_count} files"
    
    elif pattern == "wip":
        return "WIP"
    
    else:
        # Simple descriptive message
        if file_count == 1:
            return f"Update {file_names[0]}"
        elif file_count <= 3:
            return f"Update {', '.join(file_names)}"
        else:
            return f"Update {file_count} files"


def check_for_conflicts():
    """Check if there are merge conflicts in working directory"""
    result = run_command("git diff --name-only --diff-filter=U")
    return bool(result and result.strip())


def validate_changes(validation_rules=None):
    """
    Validate changes before committing
    Returns: (is_valid, issues_list)
    """
    if validation_rules is None:
        config = get_config()
        validation_rules = config.get("validation_rules", {})
    
    issues = []
    
    # Get all changed files (both staged and unstaged)
    changed_files = run_command("git diff --name-only HEAD")
    if not changed_files:
        return True, []
    
    files = changed_files.strip().split('\n')
    
    # Check each file for issues
    for filepath in files:
        if not os.path.exists(filepath):
            continue
        
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Check for conflict markers
            if validation_rules.get("check_conflicts", True):
                if any(marker in content for marker in ['<<<<<<<', '>>>>>>>', '=======']):
                    issues.append(f"Conflict markers found in: {filepath}")
            
            # Check for debug statements
            if validation_rules.get("check_debug", True):
                debug_patterns = [
                    'console.log(',
                    'console.debug(',
                    'debugger;',
                    'print(',
                    'pdb.set_trace()',
                    'import pdb',
                    'binding.pry',
                    'var_dump(',
                    'dd(',
                ]
                
                for pattern in debug_patterns:
                    if pattern in content:
                        issues.append(f"Debug statement '{pattern}' found in: {filepath}")
                        break
            
            # Check for common secret patterns
            if validation_rules.get("check_secrets", True):
                secret_patterns = [
                    ('API_KEY', 'API key'),
                    ('SECRET_KEY', 'Secret key'),
                    ('PASSWORD', 'Password'),
                    ('PRIVATE_KEY', 'Private key'),
                    ('ACCESS_TOKEN', 'Access token'),
                ]
                
                for pattern, name in secret_patterns:
                    # Look for pattern = "value" or pattern: "value"
                    if f'{pattern} = "' in content or f'{pattern}: "' in content or f'{pattern}="' in content:
                        # Check if it's not a placeholder
                        if 'your_' not in content.lower() and 'example' not in content.lower():
                            issues.append(f"Possible {name} found in: {filepath}")
                            break
        
        except Exception:
            # Skip files that can't be read (binary, etc.)
            continue
    
    return len(issues) == 0, issues


def check_large_files(max_size_mb=None):
    """Check for large files"""
    if max_size_mb is None:
        config = get_config()
        max_size_mb = config.get("validation_rules", {}).get("max_file_size_mb", 10)
    
    large_files = []
    changed_files = run_command("git diff --name-only HEAD")
    
    if not changed_files:
        return []
    
    files = changed_files.strip().split('\n')
    
    for filepath in files:
        if os.path.exists(filepath):
            size_mb = os.path.getsize(filepath) / (1024 * 1024)
            if size_mb > max_size_mb:
                large_files.append((filepath, size_mb))
    
    return large_files


def run_formatter():
    """Run code formatter if available"""
    # Check for common formatters
    formatters = {
        'black': 'black .',
        'prettier': 'prettier --write .',
        'rustfmt': 'cargo fmt',
        'gofmt': 'gofmt -w .',
    }
    
    formatted = False
    for formatter, command in formatters.items():
        # Check if formatter is available
        check_cmd = f"command -v {formatter}"
        result = subprocess.run(check_cmd, shell=True, capture_output=True)
        if result.returncode == 0:
            print(Fore.CYAN + f"  → Running {formatter}...")
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                formatted = True
    
    return formatted
