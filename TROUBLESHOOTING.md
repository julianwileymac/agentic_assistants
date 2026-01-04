# Troubleshooting Guide

## Development Environment Issues

### Node.js Version Incompatibility

**Issue**: `node-pty` or other native modules fail with `spawn EINVAL` or similar errors

**Root Cause**: Node.js 22+ (including v24) is too new for many native modules. Theia requires **Node.js 18 or 20 LTS**.

**Solution**:
1. Install Node.js 20 LTS from https://nodejs.org/en/download/
2. Or use nvm (Node Version Manager):
   ```bash
   # Install nvm-windows (on Windows) or nvm (on Linux/Mac)
   nvm install 20
   nvm use 20
   node --version  # Should show v20.x.x
   ```

**The scripts now automatically check Node.js version and will warn you if it's incompatible.**

### Virtual Environment on Windows (Git Bash)

**Issue**: Script can't find `py11_venv/bin/activate`

**Solution**: On Windows, Python virtual environments use `Scripts/activate` instead of `bin/activate`. The start scripts now automatically detect the OS and use the correct path.

### Yarn Workspace Conflicts

**Issue**: Error like "The nearest package directory doesn't seem to be part of the project declared in C:\Users\Julian Wiley"

**Root Cause**: There's a `yarn.lock` or `package.json` file in a parent directory (like your home directory) that Yarn interprets as a parent workspace.

**Automatic Fix**: The start scripts now automatically create an empty `yarn.lock` in the `frontend/` directory to prevent this issue.

**Manual Fix** (if needed):
1. Check for unwanted `yarn.lock` files:
   ```bash
   find ~ -name "yarn.lock" -maxdepth 2
   ```
2. Remove any `yarn.lock` files that shouldn't be there:
   ```bash
   rm ~/yarn.lock  # if found in home directory
   ```
3. Create an empty `yarn.lock` in the frontend directory:
   ```bash
   cd frontend
   touch yarn.lock
   ```

### Native Module Build Failures (Windows)

**Issue**: `node-pty`, `drivelist`, `keytar`, or other native modules fail to build

**Root Cause**: Theia requires native Node.js modules that need C++ build tools to compile on Windows.

**Required Modules**:
- `drivelist` - Required by `@theia/core` for drive enumeration (cannot be skipped)
- `node-pty` - Required by `@theia/terminal` for terminal
- `keytar` - Required for credential storage
- `nsfw` - Required for file watching

**Solution - Install Visual Studio Build Tools**:

1. Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/
2. Run the installer
3. Select **"Desktop development with C++"** workload
4. Click Install and wait for completion
5. **Restart your terminal/IDE**
6. Clean and reinstall:
   ```bash
   cd frontend
   rm -rf node_modules .yarn yarn.lock
   yarn install
   ```

**Alternative - Use Docker**:
If you don't want to install build tools, use the Docker-based development environment:
```bash
# Build and start the IDE container (Linux-based, no Windows build tools needed)
docker-compose up -d agentic-ide

# Or build from scratch if you have issues
docker-compose build --no-cache agentic-ide
docker-compose up -d agentic-ide
```
Then access Theia at http://localhost:3000

**Note**: There is no "lite" version workaround because `@theia/core` itself requires native modules like `drivelist`.

### Docker Build Issues

**Issue**: Docker build fails with native module errors

**Solution**:
1. Make sure you have Docker Desktop running
2. Clean Docker build cache and retry:
   ```bash
   docker-compose down
   docker-compose build --no-cache agentic-ide
   docker-compose up -d agentic-ide
   ```

3. If still failing, check Docker has enough resources:
   - Docker Desktop → Settings → Resources
   - Recommended: 4GB+ RAM, 2+ CPUs

### Backend Not Responding

**Issue**: Backend process starts but health check times out

**Root Cause**: The `agentic_assistants` package may not be installed in the virtual environment.

**Automatic Fix**: The start scripts now check if the package is installed and run `poetry install` if needed.

**Manual Fix**:
```bash
# Activate your virtual environment first
poetry install
# or
pip install -e .
```

### Backend Import Errors

**Issue**: Backend crashes with `ModuleNotFoundError`

**Check the logs**:
```bash
tail -20 backend.log
```

**Common Solutions**:
1. Reinstall dependencies:
   ```bash
   poetry install --sync
   ```
2. Clear and reinstall:
   ```bash
   poetry env remove python
   poetry install
   ```
3. Check Python version:
   ```bash
   python --version  # Should be 3.10 or 3.11
   ```

## Port Already in Use

**Issue**: Service won't start because port is already in use

**Solution**:
1. Run the stop script:
   ```bash
   ./scripts/stop-dev.sh  # or stop-dev.ps1 on Windows
   ```
2. If that doesn't work, manually kill processes:
   ```bash
   # Find process on port
   lsof -ti:8080 | xargs kill  # Linux/Mac
   netstat -ano | findstr :8080  # Windows (then use Task Manager)
   ```

## Corepack/Yarn Prompts

**Issue**: Yarn asks for confirmation during `yarn install`

**Solution**: The scripts now set:
```bash
export YARN_ENABLE_IMMUTABLE_INSTALLS=false
export COREPACK_ENABLE_STRICT=0
export COREPACK_ENABLE_DOWNLOAD_PROMPT=0
```

This forces non-interactive mode.

## Dependency Installation Timeout

**Issue**: Yarn or Poetry installation hangs or takes too long

**For Yarn**:
```bash
cd frontend
# Clear cache and retry
yarn cache clean
yarn install
```

**For Poetry**:
```bash
# Clear Poetry cache
poetry cache clear pypi --all
poetry install
```

## MLFlow Won't Start

**Issue**: MLFlow fails to start

**Check**:
1. Port 5000 is not in use
2. `mlruns` directory has write permissions
3. Check logs:
   ```bash
   tail -20 mlflow.log
   ```

## General Tips

### Starting Fresh

If all else fails, start completely fresh:

```bash
# Stop everything
./scripts/stop-dev.sh

# Clean Python environment
rm -rf py11_venv
poetry env remove python

# Clean frontend
cd frontend
rm -rf node_modules .yarn yarn.lock
cd ..

# Clean logs and PIDs
rm -f backend.log frontend.log mlflow.log yarn-install.log
rm -f .backend.pid .frontend.pid .mlflow.pid

# Reinstall
poetry install
./scripts/start-dev.sh
```

### Checking Logs

All services log to files in the project root:
- `backend.log` - FastAPI backend
- `frontend.log` - Theia IDE
- `mlflow.log` - MLFlow server
- `yarn-install.log` - Yarn dependency installation

### Manual Service Control

If the scripts aren't working:

**Start Backend**:
```bash
poetry run uvicorn agentic_assistants.server.rest:create_rest_app --factory --host 127.0.0.1 --port 8080
```

**Start MLFlow**:
```bash
poetry run mlflow server --host 127.0.0.1 --port 5000 --backend-store-uri ./mlruns
```

**Start Frontend**:
```bash
cd frontend
yarn workspace agentic-theia-app start
```

## Getting Help

If you continue to experience issues:

1. Check the logs in the project root directory
2. Ensure all prerequisites are installed:
   - Python 3.10 or 3.11
   - Poetry
   - Node.js 18+
   - (Windows) Visual Studio Build Tools
3. Try the "Starting Fresh" steps above
4. Create an issue with:
   - Your OS and version
   - Python version (`python --version`)
   - Node version (`node --version`)
   - Relevant log files

