import os
import stat
import json
import glob
from colorama import Fore
from .helpers import run_command, display_command
from .hook_templates import HOOKS_DIR, CONFIG_FILE, LANGUAGE_TOOLS, HOOK_TEMPLATES


# Utility functions
def get_hooks_config():
    """Load hooks configuration"""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {"enabled_hooks": {}}


def save_hooks_config(config):
    """Save hooks configuration"""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)


def make_executable(filepath):
    """Make a file executable"""
    st = os.stat(filepath)
    os.chmod(filepath, st.st_mode | stat.S_IEXEC)


def detect_languages():
    """Detect languages used in the current repository"""
    detected = []
    for lang, info in LANGUAGE_TOOLS.items():
        for pattern in info["detection"]:
            if "*" in pattern:
                # File pattern
                if glob.glob(pattern, recursive=True):
                    detected.append(lang)
                    break
            else:
                # Specific file
                if os.path.exists(pattern):
                    detected.append(lang)
                    break
    return detected


# Hook script generation
def generate_hook_script(hook_type, template_key, config):
    """Generate hook script based on configuration"""
    template = HOOK_TEMPLATES[hook_type]["templates"][template_key]
    
    # If template has a static script, use it
    if "script" in template:
        return template["script"]
    
    # Generate dynamic script based on config
    script_lines = [
        "#!/bin/sh",
        f"# GitCLI: {template['name']} Hook",
        "",
    ]
    
    if template_key == "linting":
        script_lines.append('echo "🔍 Running linters..."')
        script_lines.append("")
        
        for lang, tools in config.get("languages", {}).items():
            if "linters" in tools and tools["linters"]:
                lang_name = LANGUAGE_TOOLS[lang]["name"]
                script_lines.append(f"# {lang_name}")
                for tool in tools["linters"]:
                    cmd = LANGUAGE_TOOLS[lang]["linters"][tool]
                    tool_bin = tool.split()[0] if " " in tool else tool
                    script_lines.append(f"if command -v {tool_bin} >/dev/null 2>&1; then")
                    script_lines.append(f'    echo "  → Running {tool}..."')
                    script_lines.append(f"    {cmd} || exit 1")
                    script_lines.append("fi")
                script_lines.append("")
        
        script_lines.append('echo "✅ Linting passed!"')
    
    elif template_key == "formatting":
        script_lines.append('echo "🎨 Auto-formatting code..."')
        script_lines.append("")
        
        for lang, tools in config.get("languages", {}).items():
            if "formatters" in tools and tools["formatters"]:
                lang_name = LANGUAGE_TOOLS[lang]["name"]
                script_lines.append(f"# {lang_name}")
                for tool in tools["formatters"]:
                    cmd = LANGUAGE_TOOLS[lang]["formatters"][tool]
                    tool_bin = tool.split()[0] if " " in tool else tool
                    script_lines.append(f"if command -v {tool_bin} >/dev/null 2>&1; then")
                    script_lines.append(f'    echo "  → Formatting with {tool}..."')
                    script_lines.append(f"    {cmd}")
                    script_lines.append("    git add -u")
                    script_lines.append("fi")
                script_lines.append("")
        
        script_lines.append('echo "✅ Formatting complete!"')
    
    elif template_key == "tests":
        script_lines.append('echo "🧪 Running tests..."')
        script_lines.append("")
        
        for lang, tools in config.get("languages", {}).items():
            if "test_runners" in tools and tools["test_runners"]:
                lang_name = LANGUAGE_TOOLS[lang]["name"]
                script_lines.append(f"# {lang_name}")
                for tool in tools["test_runners"]:
                    cmd = LANGUAGE_TOOLS[lang]["test_runners"][tool]
                    tool_bin = tool.split()[0] if " " in tool else tool
                    script_lines.append(f"if command -v {tool_bin} >/dev/null 2>&1; then")
                    script_lines.append(f'    echo "  → Running {tool}..."')
                    script_lines.append(f"    {cmd} || exit 1")
                    script_lines.append("fi")
                script_lines.append("")
        
        script_lines.append('echo "✅ Tests passed!"')
    
    elif template_key == "build":
        script_lines.append('echo "🔨 Building project..."')
        script_lines.append("")
        
        for lang, tools in config.get("languages", {}).items():
            if "build_commands" in tools and tools["build_commands"]:
                lang_name = LANGUAGE_TOOLS[lang]["name"]
                script_lines.append(f"# {lang_name}")
                for cmd in tools["build_commands"]:
                    script_lines.append(f'echo "  → {cmd}"')
                    script_lines.append(f"{cmd} || exit 1")
                script_lines.append("")
        
        script_lines.append('echo "✅ Build successful!"')
    
    elif template_key == "custom":
        script_lines.append('echo "⚙️  Running custom commands..."')
        script_lines.append("")
        
        for cmd in config.get("custom_commands", []):
            script_lines.append(f'echo "  → {cmd}"')
            script_lines.append(f"{cmd} || exit 1")
        
        script_lines.append("")
        script_lines.append('echo "✅ Custom commands completed!"')
    
    return "\n".join(script_lines) + "\n"


# Hook installation/management
def install_hook(hook_type, template_key, hook_config=None):
    """Install a specific hook template"""
    if not os.path.exists(HOOKS_DIR):
        print(Fore.RED + "❌ Not a git repository or hooks directory not found.")
        return False
    
    template = HOOK_TEMPLATES[hook_type]["templates"][template_key]
    hook_path = os.path.join(HOOKS_DIR, hook_type)
    
    # Backup existing hook
    if os.path.exists(hook_path):
        backup_path = f"{hook_path}.backup"
        print(Fore.YELLOW + f"⚠️  Existing {hook_type} hook found. Creating backup...")
        os.rename(hook_path, backup_path)
        print(Fore.GREEN + f"✅ Backup created: {backup_path}")
    
    # Generate script
    if hook_config:
        script = generate_hook_script(hook_type, template_key, hook_config)
    else:
        script = template.get("script", "")
    
    # Write new hook
    with open(hook_path, 'w') as f:
        f.write(script)
    
    # Make executable
    make_executable(hook_path)
    
    # Update config
    config = get_hooks_config()
    if "enabled_hooks" not in config:
        config["enabled_hooks"] = {}
    if hook_type not in config["enabled_hooks"]:
        config["enabled_hooks"][hook_type] = {}
    
    config["enabled_hooks"][hook_type] = {
        "template": template_key,
        "config": hook_config or {}
    }
    save_hooks_config(config)
    
    return True


def uninstall_hook(hook_type):
    """Uninstall a hook"""
    hook_path = os.path.join(HOOKS_DIR, hook_type)
    
    if not os.path.exists(hook_path):
        print(Fore.YELLOW + f"⚠️  Hook {hook_type} is not installed.")
        return False
    
    # Check for backup
    backup_path = f"{hook_path}.backup"
    if os.path.exists(backup_path):
        print(Fore.CYAN + "Restoring backup...")
        os.remove(hook_path)
        os.rename(backup_path, hook_path)
        print(Fore.GREEN + "✅ Backup restored.")
    else:
        os.remove(hook_path)
        print(Fore.GREEN + f"✅ Hook {hook_type} removed.")
    
    # Update config
    config = get_hooks_config()
    if hook_type in config["enabled_hooks"]:
        del config["enabled_hooks"][hook_type]
        save_hooks_config(config)
    
    return True


# Configuration functions
def configure_language_tools(template_key):
    """Configure language-specific tools for a template"""
    # Detect languages
    detected = detect_languages()
    
    if not detected:
        print(Fore.YELLOW + "\n⚠️  No supported languages detected in this repository.")
        print(Fore.CYAN + "Supported languages: " + ", ".join(LANGUAGE_TOOLS.keys()))
        manual = input("Would you like to manually select languages? (y/N): ").lower()
        if manual != "y":
            return None
        available_langs = list(LANGUAGE_TOOLS.keys())
    else:
        print(Fore.GREEN + f"\n✅ Detected languages: {', '.join([LANGUAGE_TOOLS[l]['name'] for l in detected])}")
        use_detected = input("Use detected languages? (Y/n): ").lower()
        if use_detected != "n":
            available_langs = detected
        else:
            available_langs = list(LANGUAGE_TOOLS.keys())
    
    # Select languages
    print(Fore.CYAN + "\n📋 Select languages to configure:")
    for i, lang in enumerate(available_langs, 1):
        marker = "✓" if lang in detected else " "
        print(f"  {i}. [{marker}] {LANGUAGE_TOOLS[lang]['name']}")
    
    selections = input(f"\nEnter numbers (space-separated, e.g., '1 2'): ").strip()
    if not selections:
        print(Fore.RED + "❌ No languages selected.")
        return None
    
    try:
        indices = [int(x) - 1 for x in selections.split()]
        selected_langs = [available_langs[i] for i in indices if 0 <= i < len(available_langs)]
    except (ValueError, IndexError):
        print(Fore.RED + "❌ Invalid input.")
        return None
    
    if not selected_langs:
        print(Fore.RED + "❌ No valid languages selected.")
        return None
    
    # Configure tools for each language
    config = {"languages": {}}
    
    for lang in selected_langs:
        print(Fore.CYAN + f"\n⚙️  Configuring {LANGUAGE_TOOLS[lang]['name']}:")
        lang_config = {}
        
        # Configure based on template type
        if template_key in ["linting", "tests", "formatting"]:
            if template_key == "linting" and "linters" in LANGUAGE_TOOLS[lang]:
                print(Fore.CYAN + "  Available linters:")
                linters = list(LANGUAGE_TOOLS[lang]["linters"].keys())
                for i, tool in enumerate(linters, 1):
                    print(f"    {i}. {tool}")
                
                choices = input(f"  Select linters (space-separated, e.g., '1 2'): ").strip()
                if choices:
                    try:
                        selected = [linters[int(x) - 1] for x in choices.split() if 0 < int(x) <= len(linters)]
                        lang_config["linters"] = selected
                    except (ValueError, IndexError):
                        print(Fore.YELLOW + "  ⚠️  Invalid selection, skipping.")
            
            elif template_key == "formatting" and "formatters" in LANGUAGE_TOOLS[lang]:
                print(Fore.CYAN + "  Available formatters:")
                formatters = list(LANGUAGE_TOOLS[lang]["formatters"].keys())
                for i, tool in enumerate(formatters, 1):
                    print(f"    {i}. {tool}")
                
                choices = input(f"  Select formatters (space-separated, e.g., '1'): ").strip()
                if choices:
                    try:
                        selected = [formatters[int(x) - 1] for x in choices.split() if 0 < int(x) <= len(formatters)]
                        lang_config["formatters"] = selected
                    except (ValueError, IndexError):
                        print(Fore.YELLOW + "  ⚠️  Invalid selection, skipping.")
            
            elif template_key == "tests" and "test_runners" in LANGUAGE_TOOLS[lang]:
                print(Fore.CYAN + "  Available test runners:")
                runners = list(LANGUAGE_TOOLS[lang]["test_runners"].keys())
                for i, tool in enumerate(runners, 1):
                    print(f"    {i}. {tool}")
                
                choices = input(f"  Select test runner (enter number): ").strip()
                if choices:
                    try:
                        idx = int(choices) - 1
                        if 0 <= idx < len(runners):
                            lang_config["test_runners"] = [runners[idx]]
                    except ValueError:
                        print(Fore.YELLOW + "  ⚠️  Invalid selection, skipping.")
        
        if lang_config:
            config["languages"][lang] = lang_config
    
    return config if config["languages"] else None


def configure_custom_commands():
    """Configure custom commands"""
    print(Fore.CYAN + "\n⚙️  Custom Commands Configuration")
    print(Fore.YELLOW + "Enter commands to run (one per line, empty line to finish):")
    
    commands = []
    while True:
        cmd = input(Fore.CYAN + "> " + Fore.WHITE).strip()
        if not cmd:
            break
        commands.append(cmd)
    
    if not commands:
        print(Fore.RED + "❌ No commands entered.")
        return None
    
    return {"custom_commands": commands}


# UI functions
def list_installed_hooks():
    """List all installed hooks"""
    if not os.path.exists(HOOKS_DIR):
        print(Fore.RED + "❌ Not a git repository.")
        return
    
    print(Fore.CYAN + "\n🪝 Installed Git Hooks:\n" + "-"*60)
    
    config = get_hooks_config()
    enabled_hooks = config.get("enabled_hooks", {})
    
    hooks_found = False
    for hook_file in os.listdir(HOOKS_DIR):
        hook_path = os.path.join(HOOKS_DIR, hook_file)
        if os.path.isfile(hook_path) and not hook_file.endswith('.sample') and not hook_file.endswith('.backup'):
            hooks_found = True
            # Check if executable
            is_executable = os.access(hook_path, os.X_OK)
            status = Fore.GREEN + "✅ Active" if is_executable else Fore.YELLOW + "⚠️  Not executable"
            print(f"  {Fore.WHITE}{hook_file.ljust(20)} {status}")
            
            # Show configuration if available
            if hook_file in enabled_hooks:
                hook_info = enabled_hooks[hook_file]
                template_name = hook_info.get("template", "unknown")
                print(f"    {Fore.CYAN}Template: {template_name}")
                
                hook_config = hook_info.get("config", {})
                if "languages" in hook_config:
                    langs = list(hook_config["languages"].keys())
                    print(f"    {Fore.CYAN}Languages: {', '.join(langs)}")
                    for lang, tools in hook_config["languages"].items():
                        for tool_type, tool_list in tools.items():
                            if tool_list:
                                print(f"      {Fore.YELLOW}{lang} {tool_type}: {', '.join(tool_list)}")
                
                if "custom_commands" in hook_config:
                    print(f"    {Fore.CYAN}Custom commands:")
                    for cmd in hook_config["custom_commands"]:
                        print(f"      {Fore.YELLOW}• {cmd}")
    
    if not hooks_found:
        print(Fore.YELLOW + "  No hooks installed.")
    
    print(Fore.CYAN + "-"*60 + "\n")


def manage_hooks():
    """Main hooks management interface"""
    print(Fore.CYAN + "\n🪝 Git Hooks Management:")
    print("  1. Install hook")
    print("  2. Uninstall hook")
    print("  3. List installed hooks")
    print("  4. View hook templates")
    print("  5. Back")
    
    choice = input("\nChoose option (1-5): ").strip()
    
    if choice == "1":
        install_hook_menu()
    elif choice == "2":
        uninstall_hook_menu()
    elif choice == "3":
        list_installed_hooks()
    elif choice == "4":
        view_templates()
    elif choice == "5":
        return
    else:
        print(Fore.RED + "❌ Invalid option.")


def install_hook_menu():
    """Menu for installing hooks"""
    print(Fore.CYAN + "\n📋 Available Hook Types:")
    hook_types = list(HOOK_TEMPLATES.keys())
    
    for i, hook_type in enumerate(hook_types, 1):
        hook_info = HOOK_TEMPLATES[hook_type]
        print(f"  {i}. {Fore.WHITE}{hook_info['name']}{Fore.CYAN} - {hook_info['description']}")
    
    choice = input(f"\nChoose hook type (1-{len(hook_types)}): ").strip()
    
    try:
        hook_index = int(choice) - 1
        if hook_index < 0 or hook_index >= len(hook_types):
            print(Fore.RED + "❌ Invalid option.")
            return
        
        hook_type = hook_types[hook_index]
        select_template(hook_type)
    except ValueError:
        print(Fore.RED + "❌ Invalid input.")


def select_template(hook_type):
    """Select a template for a hook type"""
    templates = HOOK_TEMPLATES[hook_type]["templates"]
    template_keys = list(templates.keys())
    
    print(Fore.CYAN + f"\n📝 Available Templates for {HOOK_TEMPLATES[hook_type]['name']}:")
    
    for i, key in enumerate(template_keys, 1):
        template = templates[key]
        print(f"  {i}. {Fore.WHITE}{template['name']}{Fore.CYAN} - {template['description']}")
    
    choice = input(f"\nChoose template (1-{len(template_keys)}): ").strip()
    
    try:
        template_index = int(choice) - 1
        if template_index < 0 or template_index >= len(template_keys):
            print(Fore.RED + "❌ Invalid option.")
            return
        
        template_key = template_keys[template_index]
        template = templates[template_key]
        
        # Check if template requires configuration
        hook_config = None
        if template.get("requires_config"):
            if template_key == "custom":
                hook_config = configure_custom_commands()
            else:
                hook_config = configure_language_tools(template_key)
            
            if not hook_config:
                print(Fore.RED + "❌ Configuration required. Installation canceled.")
                return
        
        print(Fore.CYAN + f"\n🔧 Installing {template['name']}...")
        if install_hook(hook_type, template_key, hook_config):
            print(Fore.GREEN + f"✅ Hook installed successfully!")
            print(Fore.YELLOW + f"💡 This hook will run automatically on {hook_type}")
    except ValueError:
        print(Fore.RED + "❌ Invalid input.")


def uninstall_hook_menu():
    """Menu for uninstalling hooks"""
    if not os.path.exists(HOOKS_DIR):
        print(Fore.RED + "❌ Not a git repository.")
        return
    
    # Get installed hooks
    installed = []
    for hook_file in os.listdir(HOOKS_DIR):
        hook_path = os.path.join(HOOKS_DIR, hook_file)
        if os.path.isfile(hook_path) and not hook_file.endswith('.sample'):
            installed.append(hook_file)
    
    if not installed:
        print(Fore.YELLOW + "⚠️  No hooks installed.")
        return
    
    print(Fore.CYAN + "\n🗑️  Installed Hooks:")
    for i, hook in enumerate(installed, 1):
        print(f"  {i}. {hook}")
    
    choice = input(f"\nChoose hook to uninstall (1-{len(installed)}): ").strip()
    
    try:
        hook_index = int(choice) - 1
        if hook_index < 0 or hook_index >= len(installed):
            print(Fore.RED + "❌ Invalid option.")
            return
        
        hook_type = installed[hook_index]
        confirm = input(Fore.YELLOW + f"Are you sure you want to uninstall {hook_type}? (y/N): ").lower()
        
        if confirm == "y":
            if uninstall_hook(hook_type):
                print(Fore.GREEN + f"✅ Hook {hook_type} uninstalled successfully!")
        else:
            print(Fore.CYAN + "🚫 Uninstall canceled.")
    except ValueError:
        print(Fore.RED + "❌ Invalid input.")


def view_templates():
    """View all available hook templates"""
    print(Fore.CYAN + "\n📚 Available Hook Templates:\n" + "="*60)
    
    for hook_type, hook_info in HOOK_TEMPLATES.items():
        print(Fore.MAGENTA + f"\n{hook_info['name']} ({hook_type})")
        print(Fore.CYAN + f"{hook_info['description']}")
        print(Fore.CYAN + "-"*60)
        
        for template_key, template in hook_info["templates"].items():
            print(f"  • {Fore.WHITE}{template['name']}{Fore.CYAN} - {template['description']}")
    
    print(Fore.CYAN + "\n" + "="*60 + "\n")

