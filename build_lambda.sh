#!/bin/bash
# Build Lambda deployment package
# Creates build/lambda_package/ with source code and dependencies, then zips it

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUILD_DIR="${SCRIPT_DIR}/build"
PACKAGE_DIR="${BUILD_DIR}/lambda_package"
ZIP_FILE="${BUILD_DIR}/lambda_package.zip"
LAMBDA_DIR="${SCRIPT_DIR}/lambda"

echo "Building Lambda deployment package..."

# Check for Docker (required for Linux-compatible binaries)
if ! command -v docker &> /dev/null; then
    echo "ERROR: Docker is required to build Lambda-compatible packages."
    echo "Please install Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

# Clean previous build
echo "Cleaning previous build..."
rm -rf "${BUILD_DIR}"
mkdir -p "${PACKAGE_DIR}"

# Copy Lambda source code
echo "Copying Lambda source code..."
cp "${LAMBDA_DIR}"/*.py "${PACKAGE_DIR}/"

# Install Python dependencies using uv with lock file (Linux-compatible)
# Uses uv.lock for reproducible builds with exact dependency versions
if [ -f "${SCRIPT_DIR}/uv.lock" ]; then
    echo "Installing dependencies from uv.lock (reproducible build)..."
    docker run --rm --platform linux/amd64 \
        -v "${SCRIPT_DIR}:/workspace" \
        -w /workspace \
        python:3.11 \
        bash -c "curl -LsSf https://astral.sh/uv/install.sh | sh && \
                 /root/.local/bin/uv export --no-dev --format requirements.txt | \
                 grep -v '^-e \.' > /tmp/requirements.txt && \
                 /root/.local/bin/uv pip install --system --target build/lambda_package \
                 --no-cache-dir -r /tmp/requirements.txt"
else
    echo "Warning: uv.lock not found, installing from pyproject.toml..."
    docker run --rm --platform linux/amd64 \
        -v "${SCRIPT_DIR}:/workspace" \
        -w /workspace \
        python:3.11 \
        bash -c "curl -LsSf https://astral.sh/uv/install.sh | sh && \
                 /root/.local/bin/uv pip install --system --target build/lambda_package \
                 --no-cache-dir boto3 pydantic"
fi

# Clean up unnecessary files
echo "Cleaning up unnecessary files..."
find "${PACKAGE_DIR}" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find "${PACKAGE_DIR}" -type f -name "*.pyc" -delete 2>/dev/null || true
find "${PACKAGE_DIR}" -type f -name "*.pyo" -delete 2>/dev/null || true
find "${PACKAGE_DIR}" -type d -name "*.dist-info" -exec rm -rf {} + 2>/dev/null || true
find "${PACKAGE_DIR}" -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
rm -rf "${PACKAGE_DIR}/bin" 2>/dev/null || true

# Create ZIP archive (zip contents of PACKAGE_DIR, not the directory itself)
echo "Creating ZIP archive..."
cd "${PACKAGE_DIR}"
zip -r "${ZIP_FILE}" . -q
cd "${SCRIPT_DIR}"

echo "✓ Lambda package created: ${ZIP_FILE}"
echo "✓ Package size: $(du -h "${ZIP_FILE}" | cut -f1)"

