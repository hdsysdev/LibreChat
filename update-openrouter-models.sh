#!/bin/bash

# Script to update OpenRouter models and sync with LibreChat configuration
# This script:
# 1. Executes the OpenRouter Python script to fetch latest models
# 2. Updates the LibreChat configuration with the latest models
# 3. Maintains existing model specifications while updating model lists

set -e  # Exit on any error

echo "🔄 Starting OpenRouter models update process..."

# Check if we're in the right directory
if [ ! -f "librechat.yaml" ]; then
    echo "❌ Error: librechat.yaml not found. Please run this script from the LibreChat root directory."
    exit 1
fi

# Check if the OpenRouter script exists
if [ ! -f "utils/openrouter.py" ]; then
    echo "❌ Error: utils/openrouter.py not found."
    exit 1
fi

# Check if the update script exists
if [ ! -f "utils/update_librechat_config.py" ]; then
    echo "❌ Error: utils/update_librechat_config.py not found."
    exit 1
fi

# Create backup of current configuration
echo "📋 Creating backup of current configuration..."
cp librechat.yaml librechat.yaml.backup.$(date +%Y%m%d_%H%M%S)

# Execute the OpenRouter Python script
echo "🔍 Fetching latest OpenRouter models..."
cd utils
python3 openrouter.py
cd ..

# Check if the models file was created
if [ ! -f "openrouter.txt" ]; then
    echo "❌ Error: openrouter.txt was not created. Check the OpenRouter script execution."
    exit 1
fi

echo "✅ OpenRouter models fetched successfully."

# Execute the configuration update script
echo "🔄 Updating LibreChat configuration with latest models..."
python3 utils/update_librechat_config.py

if [ $? -eq 0 ]; then
    echo "✅ LibreChat configuration updated successfully!"
    echo ""
    echo "📋 Summary:"
    echo "  - OpenRouter models fetched from API"
    echo "  - LibreChat configuration updated with latest model versions"
    echo "  - Backup created: librechat.yaml.backup.*"
    echo ""
    echo "🔄 You can now restart LibreChat to use the updated models."
else
    echo "❌ Error updating LibreChat configuration."
    echo "🔄 Restoring backup..."
    cp librechat.yaml.backup.* librechat.yaml 2>/dev/null || echo "⚠️  Could not restore backup automatically."
    exit 1
fi

echo "🎉 Update process completed!"
