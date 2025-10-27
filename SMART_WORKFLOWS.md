# GitCLI Smart Workflows

## The Problem We Solved

Traditional Git has 100+ commands. Even simplified Git tools still require users to remember dozens of commands and their combinations. GitCLI Smart Workflows reduces your daily Git operations to **just 6 commands** that intelligently handle everything.

## Philosophy

**Instead of exposing Git commands, we automate Git workflows.**

- ❌ **Old way:** Remember 30+ commands and when to use each
- ✅ **New way:** Tell GitCLI what you want to do, it figures out how

## The 6 Core Commands

### 1. `save` - Smart Save Your Work

**What it does:** Intelligently saves your work based on current state.

**Scenarios it handles:**

**Scenario A: You have uncommitted changes**
```bash
gitcli save
> You have uncommitted changes on 'feature-login'
> What would you like to do?
>   1. Commit and push (save permanently)
>   2. Stash (save temporarily)
>   3. Show changes first
>   4. Cancel
```

**Scenario B: You have unpushed commits**
```bash
gitcli save
> You have 2 unpushed commit(s) on 'feature-login'
> Push to remote? (Y/n):
```

**Scenario C: Everything is saved**
```bash
gitcli save
> ✅ Everything is saved and up to date!
```

**Replaces these commands:**
- `git add .`
- `git commit -m "message"`
- `git push`
- `git stash`
- Checking status before each action

---

### 2. `work <branch>` - Start Working on a Feature

**What it does:** Prepares you to work on a feature branch, handling all edge cases.

**Example:**
```bash
gitcli work feature-login
```

**What happens automatically:**

1. **If you have uncommitted changes:**
   - Asks: Stash or commit them first?
   - Handles it for you

2. **If branch exists:**
   - Switches to it
   - Offers to pull latest changes

3. **If branch doesn't exist:**
   - Asks which branch to base it on (current/main/master)
   - Creates and switches to new branch
   - Pulls latest from base branch

**Replaces these commands:**
- `git stash`
- `git checkout -b feature-login`
- `git checkout feature-login`
- `git pull`
- Checking if branch exists
- Handling uncommitted changes

---

### 3. `done` - Finish Your Work

**What it does:** Completes your current work and optionally returns to main.

**Example:**
```bash
gitcli done
```

**What happens automatically:**

1. **If you have uncommitted changes:**
   - Stages all changes
   - Asks for commit message
   - Commits
   - Pushes to remote

2. **If everything is committed:**
   - Pushes unpushed commits
   - Asks if you want to switch back to main

3. **Switches back to main (optional):**
   - Switches to main/master
   - Pulls latest changes

**Replaces these commands:**
- `git add .`
- `git commit -m "message"`
- `git push`
- `git checkout main`
- `git pull`

---

### 4. `sync` - Sync with Remote

**What it does:** Intelligently syncs your branch with remote, handling conflicts automatically.

**Example:**
```bash
gitcli sync
```

**What happens automatically:**

1. **If you have uncommitted changes:**
   - Stashes them temporarily
   - Pulls latest
   - Restores your changes
   - Handles conflicts if they occur

2. **If you have no changes:**
   - Pulls latest
   - Auto-opens conflict resolution if conflicts occur
   - Pushes if you're ahead

3. **Conflict handling:**
   - Automatically detects conflicts
   - Opens interactive conflict resolution helper
   - Guides you through resolution

**Replaces these commands:**
- `git stash`
- `git pull`
- `git stash pop`
- `git push`
- Manual conflict detection
- Figuring out what to do when conflicts occur

---

### 5. `undo` - Smart Undo Last Action

**What it does:** Intelligently undoes your last action based on context.

**Example:**
```bash
gitcli undo
```

**Scenarios it handles:**

**Scenario A: Uncommitted changes**
```bash
> You have uncommitted changes.
> What would you like to undo?
>   1. Discard all uncommitted changes
>   2. Discard specific files
>   3. Undo last commit (keep changes)
>   4. Cancel
```

**Scenario B: Last commit not pushed**
```bash
> Last commit: feat: add login form
> Undo last commit? (y/N):
> ✅ Last commit undone! Changes are still staged.
```

**Scenario C: Last commit already pushed**
```bash
> ⚠️  This commit has been pushed to remote!
> Safer option: Create a revert commit instead?
>   1. Revert (safe, creates new commit)
>   2. Undo anyway (requires force push)
>   3. Cancel
```

**Replaces these commands:**
- `git reset --hard HEAD`
- `git reset --soft HEAD~1`
- `git revert HEAD`
- `git checkout -- <file>`
- Figuring out which reset to use
- Knowing when it's safe to undo

---

### 6. `status` - Enhanced Status

**What it does:** Shows everything you need to know in one view.

**Example:**
```bash
gitcli status
```

**Shows:**
- Current branch
- Uncommitted changes (if any)
- Unpushed commits (if any)
- Commits behind remote (if any)
- Merge conflicts (if any)
- Saved stashes (if any)
- Recent commit history

**Replaces these commands:**
- `git status`
- `git log`
- `git stash list`
- `git diff --name-only`
- Checking if ahead/behind remote
- Multiple commands to get full picture

---

## Real-World Workflows

### Daily Feature Development

**Old way (10+ commands):**
```bash
git status
git stash
git checkout main
git pull
git checkout -b feature-login
# ... make changes ...
git status
git add .
git commit -m "Add login form"
git push -u origin feature-login
git checkout main
git pull
```

**New way (3 commands):**
```bash
gitcli work feature-login
# ... make changes ...
gitcli done
```

---

### Quick Fix While Working

**Old way:**
```bash
git status
git stash
git checkout main
git pull
git checkout -b hotfix-typo
# ... fix typo ...
git add .
git commit -m "Fix typo"
git push -u origin hotfix-typo
git checkout feature-login
git stash pop
```

**New way:**
```bash
gitcli work hotfix-typo
# ... fix typo ...
gitcli done
gitcli work feature-login
```

---

### Syncing with Team Changes

**Old way:**
```bash
git status
# Oh, I have changes...
git stash
git pull
# Conflicts!
git status
# Figure out which files...
vim conflicted-file.js
git add conflicted-file.js
git commit
git stash pop
# More conflicts!
# Repeat...
```

**New way:**
```bash
gitcli sync
# Automatically stashes, pulls, handles conflicts interactively, restores changes
```

---

## Advanced Commands Still Available

All the original GitCLI commands are still available for advanced users:

- Branch management: `switch-branch`, `add-branch`, `delete-branch`, etc.
- Stash operations: `stash`, `stash-pop`, `stash-list`, etc.
- Conflict resolution: `resolve-conflicts`, `check-conflicts`
- Git hooks: `hooks`, `list-hooks`
- And more...

Type `gitcli help` to see all commands organized by category.

---

## Command Comparison

| Task | Traditional Git | Old GitCLI | Smart GitCLI |
|------|----------------|------------|--------------|
| Save work | 3-5 commands | 3 commands | 1 command: `save` |
| Start feature | 4-6 commands | 4 commands | 1 command: `work` |
| Finish feature | 4-5 commands | 3 commands | 1 command: `done` |
| Sync with team | 2-10 commands | 2-5 commands | 1 command: `sync` |
| Undo mistake | 1-3 commands | 1-2 commands | 1 command: `undo` |
| Check status | 3-5 commands | 1-3 commands | 1 command: `status` |

---

## Design Principles

### 1. Context-Aware
Commands adapt to your current situation. `save` does different things based on what state your repository is in.

### 2. Conversational
Instead of flags and options, we ask questions. More intuitive, less to remember.

### 3. Safe by Default
Destructive operations require confirmation. Pushed commits suggest revert instead of reset.

### 4. Intelligent Automation
Automatically handles common scenarios (stashing before pull, conflict detection, etc.)

### 5. Progressive Disclosure
Start with 6 simple commands. Advanced commands available when needed.

---

## Getting Started

### Interactive Mode
```bash
gitcli
> save              # Smart save
> work feature-x    # Start feature
> done              # Finish feature
> sync              # Sync with remote
> undo              # Undo last action
> status            # Check status
```

### Direct Commands
```bash
gitcli save
gitcli work feature-login
gitcli done
gitcli sync
```

### First Time Setup
```bash
gitcli hooks        # Optional: Set up automated hooks
```

---

## Tips

1. **Use `status` frequently** - It shows everything you need to know
2. **Let `sync` handle conflicts** - It guides you through resolution
3. **Trust `save`** - It knows whether to commit, stash, or push
4. **Use `work` for all branches** - It handles all the edge cases
5. **`undo` is safe** - It warns before destructive operations

---

## Philosophy: Automate Workflows, Not Commands

GitCLI Smart Workflows doesn't just wrap Git commands with prettier output. It understands **what you're trying to accomplish** and handles all the steps automatically.

**You think in workflows:**
- "I want to save my work"
- "I want to work on a feature"
- "I'm done with this feature"

**GitCLI handles the implementation:**
- Checking state
- Running correct commands
- Handling edge cases
- Dealing with conflicts
- Cleaning up after

This is true automation.

---

## Backward Compatibility

All existing GitCLI commands still work. Smart Workflows are additions, not replacements. Use what works for you:

- **Beginners:** Use the 6 smart commands
- **Intermediate:** Mix smart and advanced commands
- **Advanced:** Use all commands for fine-grained control

---

## Summary

**6 commands to rule them all:**

1. `save` - Save your work (commit/stash/push)
2. `work` - Start working on a branch
3. `done` - Finish your work
4. `sync` - Sync with remote
5. `undo` - Undo last action
6. `status` - See everything

**That's it.** Everything else is automated.
