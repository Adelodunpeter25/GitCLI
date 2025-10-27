"""
Git hook templates and language tool configurations
"""

HOOKS_DIR = ".git/hooks"
CONFIG_FILE = ".gitcli-hooks.json"

# Language-specific commands
LANGUAGE_TOOLS = {
    "python": {
        "name": "Python",
        "linters": {
            "ruff": "ruff check .",
            "flake8": "flake8 .",
            "pylint": "pylint **/*.py",
            "mypy": "mypy .",
        },
        "formatters": {
            "ruff": "ruff format .",
            "black": "black .",
            "autopep8": "autopep8 --in-place --recursive .",
        },
        "test_runners": {
            "pytest": "pytest",
            "unittest": "python -m unittest discover",
        },
        "detection": ["*.py", "setup.py", "pyproject.toml", "requirements.txt"]
    },
    "javascript": {
        "name": "JavaScript/TypeScript",
        "linters": {
            "eslint": "eslint .",
            "tslint": "tslint -c tslint.json '**/*.ts'",
        },
        "formatters": {
            "prettier": "prettier --write .",
            "eslint-fix": "eslint --fix .",
        },
        "test_runners": {
            "jest": "jest",
            "npm-test": "npm test",
            "vitest": "vitest run",
        },
        "detection": ["*.js", "*.ts", "package.json", "tsconfig.json"]
    },
    "go": {
        "name": "Go",
        "linters": {
            "golint": "golint ./...",
            "go-vet": "go vet ./...",
            "staticcheck": "staticcheck ./...",
        },
        "formatters": {
            "gofmt": "gofmt -w .",
            "goimports": "goimports -w .",
        },
        "test_runners": {
            "go-test": "go test ./...",
        },
        "detection": ["*.go", "go.mod"]
    },
    "rust": {
        "name": "Rust",
        "linters": {
            "clippy": "cargo clippy -- -D warnings",
        },
        "formatters": {
            "rustfmt": "cargo fmt",
        },
        "test_runners": {
            "cargo-test": "cargo test",
        },
        "detection": ["*.rs", "Cargo.toml"]
    },
    "ruby": {
        "name": "Ruby",
        "linters": {
            "rubocop": "rubocop",
        },
        "formatters": {
            "rubocop-fix": "rubocop -a",
        },
        "test_runners": {
            "rspec": "rspec",
            "minitest": "ruby -Itest test/**/*_test.rb",
        },
        "detection": ["*.rb", "Gemfile"]
    },
}

# Hook templates
HOOK_TEMPLATES = {
    "pre-commit": {
        "name": "Pre-commit Hook",
        "description": "Runs before each commit",
        "templates": {
            "linting": {
                "name": "Code Linting",
                "description": "Run linters before commit",
                "requires_config": True,
            },
            "formatting": {
                "name": "Auto-format Code",
                "description": "Auto-format code before commit",
                "requires_config": True,
            },
            "tests": {
                "name": "Run Tests",
                "description": "Run test suite before commit",
                "requires_config": True,
            },
            "no-debug": {
                "name": "Block Debug Code",
                "description": "Prevent commits with debug statements",
                "script": """#!/bin/sh
# GitCLI: Block Debug Code Pre-commit Hook

echo "🔍 Checking for debug statements..."

# Check for common debug patterns
if git diff --cached | grep -E "(console\\.log|debugger|pdb\\.set_trace|import pdb|binding\\.pry)" >/dev/null 2>&1; then
    echo "❌ Debug statements found in staged files!"
    echo "Please remove debug code before committing."
    exit 1
fi

echo "✅ No debug statements found!"
"""
            },
            "custom": {
                "name": "Custom Commands",
                "description": "Run your own custom commands",
                "requires_config": True,
            }
        }
    },
    "pre-push": {
        "name": "Pre-push Hook",
        "description": "Runs before pushing to remote",
        "templates": {
            "tests": {
                "name": "Run Full Test Suite",
                "description": "Run all tests before push",
                "requires_config": True,
            },
            "protect-main": {
                "name": "Protect Main Branch",
                "description": "Prevent direct pushes to main/master",
                "script": """#!/bin/sh
# GitCLI: Protect Main Branch Pre-push Hook

current_branch=$(git symbolic-ref HEAD | sed -e 's,.*/\\(.*\\),\\1,')

if [ "$current_branch" = "main" ] || [ "$current_branch" = "master" ]; then
    echo "❌ Direct push to $current_branch is not allowed!"
    echo "Please create a feature branch and submit a pull request."
    exit 1
fi

echo "✅ Branch check passed!"
"""
            },
            "build": {
                "name": "Build Before Push",
                "description": "Ensure project builds successfully",
                "requires_config": True,
            },
            "custom": {
                "name": "Custom Commands",
                "description": "Run your own custom commands",
                "requires_config": True,
            }
        }
    },
    "commit-msg": {
        "name": "Commit Message Hook",
        "description": "Validates commit message format",
        "templates": {
            "conventional": {
                "name": "Conventional Commits",
                "description": "Enforce conventional commit format",
                "script": """#!/bin/sh
# GitCLI: Conventional Commits Hook

commit_msg_file=$1
commit_msg=$(cat "$commit_msg_file")

# Check for conventional commit format: type(scope): message
if ! echo "$commit_msg" | grep -qE "^(feat|fix|docs|style|refactor|test|chore|perf|ci|build|revert)(\\(.+\\))?: .{1,}"; then
    echo "❌ Invalid commit message format!"
    echo ""
    echo "Commit message must follow Conventional Commits format:"
    echo "  type(scope): description"
    echo ""
    echo "Types: feat, fix, docs, style, refactor, test, chore, perf, ci, build, revert"
    echo ""
    echo "Examples:"
    echo "  feat(auth): add login functionality"
    echo "  fix(api): resolve null pointer exception"
    echo "  docs: update README"
    exit 1
fi

echo "✅ Commit message format valid!"
"""
            },
            "min-length": {
                "name": "Minimum Message Length",
                "description": "Require minimum commit message length",
                "script": """#!/bin/sh
# GitCLI: Minimum Message Length Hook

commit_msg_file=$1
commit_msg=$(cat "$commit_msg_file")

min_length=10

if [ ${#commit_msg} -lt $min_length ]; then
    echo "❌ Commit message too short!"
    echo "Minimum length: $min_length characters"
    echo "Current length: ${#commit_msg} characters"
    exit 1
fi

echo "✅ Commit message length valid!"
"""
            },
            "no-wip": {
                "name": "Block WIP Commits",
                "description": "Prevent commits with WIP in message",
                "script": """#!/bin/sh
# GitCLI: Block WIP Commits Hook

commit_msg_file=$1
commit_msg=$(cat "$commit_msg_file")

if echo "$commit_msg" | grep -qiE "^(wip|work in progress)"; then
    echo "❌ WIP commits are not allowed!"
    echo "Please complete your work before committing."
    exit 1
fi

echo "✅ Commit message valid!"
"""
            }
        }
    },
    "post-commit": {
        "name": "Post-commit Hook",
        "description": "Runs after each commit",
        "templates": {
            "notify": {
                "name": "Commit Notification",
                "description": "Send notification after commit",
                "script": """#!/bin/sh
# GitCLI: Post-commit Notification Hook

commit_msg=$(git log -1 --pretty=%B)
commit_hash=$(git log -1 --pretty=%h)

echo "✅ Commit $commit_hash created successfully!"

# macOS notification
if command -v osascript >/dev/null 2>&1; then
    osascript -e "display notification \\"$commit_msg\\" with title \\"Commit Successful\\""
fi

# Linux notification
if command -v notify-send >/dev/null 2>&1; then
    notify-send "Commit Successful" "$commit_msg"
fi
"""
            },
            "backup": {
                "name": "Auto Backup",
                "description": "Create backup after commit",
                "script": """#!/bin/sh
# GitCLI: Auto Backup Post-commit Hook

backup_dir="../.git-backups"
timestamp=$(date +%Y%m%d_%H%M%S)
repo_name=$(basename $(git rev-parse --show-toplevel))

mkdir -p "$backup_dir"

echo "💾 Creating backup..."
git bundle create "$backup_dir/${repo_name}_${timestamp}.bundle" --all

echo "✅ Backup created: ${repo_name}_${timestamp}.bundle"
"""
            }
        }
    }
}
