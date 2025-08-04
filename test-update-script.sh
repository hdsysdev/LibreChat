#!/bin/bash

# Test script to verify the update functionality
# This script runs the update process in a test mode

echo "🧪 Testing OpenRouter models update process..."

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

# Check if the test script exists
if [ ! -f "utils/test_update_config.py" ]; then
    echo "❌ Error: utils/test_update_config.py not found."
    exit 1
fi

# Create a test backup
echo "📋 Creating test backup..."
cp librechat.yaml librechat.yaml.test.backup

# Execute the OpenRouter Python script
echo "🔍 Fetching latest OpenRouter models..."
cd utils
python3 openrouter.py
cd ..

# Check if the models file was created
if [ ! -f "openrouter.txt" ]; then
    echo "❌ Error: openrouter.txt was not created."
    exit 1
fi

echo "✅ OpenRouter models fetched successfully."

# Execute the test script
echo "🧪 Running test to see what would be updated..."
python3 utils/test_update_config.py

# Clean up test files
echo "🧹 Cleaning up test files..."
rm -f openrouter.txt

# Restore original configuration
echo "🔄 Restoring original configuration..."
cp librechat.yaml.test.backup librechat.yaml
rm -f librechat.yaml.test.backup

echo "�� Test completed!" 