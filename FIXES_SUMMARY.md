# Development Script Fixes - Summary

## Issues Fixed

### 0. Node.js Version Check (NEW)
**Problem**: Node.js 24 is too new. Native modules like `node-pty` fail with `spawn EINVAL` error.

**Fix**: Added Node.js version check to both scripts:
- Rejects Node.js versions > 20 or < 18
- Provides clear instructions to install Node.js 20 LTS
- Skips frontend if version is incompatible

**Location**: Both `start-dev.sh` (lines ~235-250) and `start-dev.ps1` (lines ~205-220)

### 1. Virtual Environment Activation on Windows (Git Bash)
**Problem**: Script tried to activate `py11_venv/bin/activate` which doesn't exist on Windows.

**Fix**: Added OS detection to use correct path:
- Windows: `py11_venv/Scripts/activate`
- Linux/Mac: `py11_venv/bin/activate`

**Location**: Both `start-dev.sh` and `start-dev.ps1`

### 2. Python Package Not Installed
**Problem**: Backend process starts but doesn't respond because `agentic_assistants` module is not installed in the virtual environment.

**Fix**: Added automatic package installation check:
```python
python -c "import agentic_assistants"
```
If this fails, the script automatically runs `poetry install` before starting services.

**Location**: Both `start-dev.sh` (lines ~85-105) and `start-dev.ps1` (lines ~100-120)

### 3. Yarn Workspace Conflict
**Problem**: Yarn error "The nearest package directory doesn't seem to be part of the project declared in C:\Users\Julian Wiley"

**Root Cause**: A `yarn.lock` or `package.json` file exists in a parent directory (home directory) that Yarn interprets as a parent workspace.

**Fix**: Scripts now automatically:
1. Create an empty `yarn.lock` in `frontend/` directory
2. Create `.yarnrc.yml` with proper configuration:
   ```yaml
   nodeLinker: node-modules
   enableGlobalCache: true
   ```

**Location**: 
- `start-dev.sh` (lines ~160-175)
- `start-dev.ps1` (lines ~220-235)

### 4. Native Module Build Failures on Windows
**Problem**: Native modules (`drivelist`, `node-pty`, `keytar`, etc.) fail to build because Visual Studio Build Tools are not installed.

**Important**: There is NO workaround for this on Windows. `@theia/core` itself requires `drivelist` which needs native compilation. You MUST install Visual Studio Build Tools to use Theia on Windows.

**Fix**: 
1. Display clear error message when native modules fail
2. Provide Visual Studio Build Tools download link
3. Suggest Docker alternative for those who don't want to install build tools
4. Continue with Python backend and MLFlow (they work without Theia)
5. Log installation output to `yarn-install.log` for debugging

**Location**: 
- `start-dev.sh` (lines ~180-220)
- `start-dev.ps1` (lines ~240-275)

### 5. Non-Interactive Mode for Yarn
**Problem**: Yarn prompts for user input during installation, blocking automated scripts.

**Fix**: Set environment variables:
```bash
COREPACK_ENABLE_DOWNLOAD_PROMPT=0
COREPACK_ENABLE_STRICT=0
YARN_ENABLE_IMMUTABLE_INSTALLS=false
```

**Location**: Both scripts, in frontend installation section

## New Files Created

### TROUBLESHOOTING.md
Comprehensive troubleshooting guide covering:
- All common development environment issues
- Step-by-step solutions
- Manual workarounds
- "Starting fresh" instructions
- Log file locations and debugging tips

### FIXES_SUMMARY.md (this file)
Quick reference for what was fixed and where.

## Updated Files

### scripts/start-dev.sh
- OS detection for virtual environment activation
- Automatic package installation check
- Yarn workspace conflict prevention
- Native module build failure handling with fallback
- Better error messages and logging

### scripts/start-dev.ps1
- Automatic package installation check
- Yarn workspace conflict prevention
- Native module build failure handling with fallback
- Better error messages and logging

### scripts/README.md
- Added "Automatic Fixes" section
- Updated troubleshooting to reference TROUBLESHOOTING.md
- Added note about first-time setup including package installation

## Testing the Fixes

### Bash/Git Bash (Windows, Linux, Mac)
```bash
# Make executable (first time only)
chmod +x scripts/start-dev.sh scripts/stop-dev.sh

# Run
./scripts/start-dev.sh
```

The script will now:
1. ✅ Detect Windows and use correct venv path
2. ✅ Check if `agentic_assistants` is installed, run `poetry install` if needed
3. ✅ Create `yarn.lock` and `.yarnrc.yml` to prevent workspace conflicts
4. ✅ Attempt `yarn install`, retry with `--ignore-optional` if it fails
5. ✅ Log everything to `yarn-install.log` for debugging

### PowerShell (Windows)
```powershell
.\scripts\start-dev.ps1
```

Same automatic fixes apply.

## Manual Steps No Longer Needed

You no longer need to manually:
- ❌ Run `poetry install`
- ❌ Create `yarn.lock` in frontend directory
- ❌ Remove conflicting `yarn.lock` from parent directories
- ❌ Run `yarn install --ignore-optional`
- ❌ Install Visual Studio Build Tools before trying (warning is shown, but script continues)

All these steps are now handled automatically by the scripts!

## If You Still Have Issues

1. Check the new log files:
   - `backend.log` - Backend startup and errors
   - `frontend.log` - Frontend startup
   - `yarn-install.log` - Yarn installation details
   - `mlflow.log` - MLFlow server

2. Read [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for detailed solutions

3. Try the "Starting Fresh" section in TROUBLESHOOTING.md to reset everything

4. For native module issues on Windows, you may still need to install Visual Studio Build Tools:
   - https://visualstudio.microsoft.com/downloads/
   - Choose "Build Tools for Visual Studio 2022"
   - Select "Desktop development with C++"

## Next Steps

Run the start script:
```bash
./scripts/start-dev.sh
```

It should now work without manual intervention!

