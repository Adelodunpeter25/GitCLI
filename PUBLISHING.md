# Publishing to PyPI

## Prerequisites

1. **Update package info** in these files:
   - `setup.py` - Change author, email, GitHub URL
   - `pyproject.toml` - Change author, email, GitHub URL
   - `LICENSE` - Add your name
   - `gitcli/__init__.py` - Update author

2. **Create PyPI account**:
   - Register at https://pypi.org/account/register/
   - Register at https://test.pypi.org/account/register/ (for testing)

3. **Install build tools**:
   ```bash
   pip install build twine
   ```

## Steps to Publish

### 1. Test Locally
```bash
# Install in development mode
pip install -e .

# Test the command
gitcli help
gitcli status
```

### 2. Build the Package
```bash
# Clean old builds
rm -rf build/ dist/ *.egg-info

# Build
python -m build
```

This creates:
- `dist/gitcli-automation-1.0.0.tar.gz` (source distribution)
- `dist/gitcli_automation-1.0.0-py3-none-any.whl` (wheel)

### 3. Test on TestPyPI (Optional but Recommended)
```bash
# Upload to TestPyPI
twine upload --repository testpypi dist/*

# Test install from TestPyPI
pip install --index-url https://test.pypi.org/simple/ gitcli-automation
```

### 4. Upload to PyPI
```bash
# Upload to real PyPI
twine upload dist/*

# Enter your PyPI username and password when prompted
```

### 5. Verify Installation
```bash
# Install from PyPI
pip install gitcli-automation

# Test
gitcli help
```

## Updating the Package

1. Update version in:
   - `setup.py`
   - `pyproject.toml`
   - `gitcli/__init__.py`

2. Rebuild and upload:
   ```bash
   rm -rf build/ dist/ *.egg-info
   python -m build
   twine upload dist/*
   ```

## Important Notes

- **Package name**: `gitcli-automation` (check if available on PyPI first)
- **Command name**: `gitcli` (what users type in terminal)
- **Version**: Follow semantic versioning (MAJOR.MINOR.PATCH)
- **License**: MIT (already included)

## Troubleshooting

**Name already taken?**
- Try: `gitcli-tool`, `pygitcli`, `git-cli-automation`, etc.
- Update name in `setup.py` and `pyproject.toml`

**Upload fails?**
- Check credentials
- Ensure version number is unique (can't reupload same version)
- Check package name availability

**Import errors after install?**
- Verify package structure
- Check `entry_points` in setup.py
- Test with `pip install -e .` first
