#!/usr/bin/env python3

import yaml
import json
import re
from pathlib import Path

def load_yaml_file(file_path):
    """Load YAML file safely."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return yaml.safe_load(file)
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return None

def load_openrouter_models(file_path):
    """Load OpenRouter models from JSON file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return []

def extract_models_by_category(models_list):
    """Extract models organized by category from the OpenRouter output."""
    categories = {}
    current_category = None
    
    for item in models_list:
        if item.startswith('---') and item.endswith('---'):
            current_category = item.strip('-')
        elif current_category and not item.startswith('---'):
            if current_category not in categories:
                categories[current_category] = []
            categories[current_category].append(item)
    
    return categories

def find_latest_model_version(current_model, categories):
    """Find the latest version of a model based on the base model name."""
    # Extract base model name (remove version suffixes)
    base_model = current_model.split(':')[0] if ':' in current_model else current_model
    
    # Search through all categories for the latest version
    latest_model = None
    
    for category, models in categories.items():
        for model in models:
            # Skip free models (models with :free suffix)
            if model.endswith(':free'):
                continue
                
            model_base = model.split(':')[0] if ':' in model else model
            if model_base == base_model:
                # If this is a newer version, update
                if not latest_model or model > latest_model:
                    latest_model = model
    
    return latest_model

def test_model_specs_updates(config, openrouter_models):
    """Test what modelSpecs would be updated."""
    if 'modelSpecs' not in config or 'list' not in config['modelSpecs']:
        print("❌ No modelSpecs found in configuration")
        return
    
    # Extract models by category
    categories = extract_models_by_category(openrouter_models)
    
    print(f"📊 Found {len(categories)} model categories:")
    for category, models in categories.items():
        print(f"  - {category}: {len(models)} models")
    
    # Test existing modelSpecs
    updates_found = 0
    
    for spec in config['modelSpecs']['list']:
        if 'preset' in spec and 'model' in spec['preset']:
            current_model = spec['preset']['model']
            
            # Find the latest version of this model
            latest_model = find_latest_model_version(current_model, categories)
            
            if latest_model and latest_model != current_model:
                print(f"🔄 Would update {current_model} → {latest_model}")
                updates_found += 1
            else:
                print(f"✅ {current_model} (already latest)")
    
    print(f"\n📈 Test Summary: {updates_found} model specifications would be updated")

def test_endpoints_updates(config, openrouter_models):
    """Test what endpoints would be updated."""
    if 'endpoints' not in config or 'custom' not in config['endpoints']:
        print("❌ No custom endpoints found in configuration")
        return
    
    # Extract models by category
    categories = extract_models_by_category(openrouter_models)
    
    for endpoint in config['endpoints']['custom']:
        if 'models' in endpoint and 'default' in endpoint['models']:
            current_models = endpoint['models']['default']
            updates_found = 0
            
            print(f"\n🔍 Testing endpoint: {endpoint.get('name', 'Unknown')}")
            
            for current_model in current_models:
                latest_model = find_latest_model_version(current_model, categories)
                
                if latest_model and latest_model != current_model:
                    print(f"  🔄 Would update {current_model} → {latest_model}")
                    updates_found += 1
                else:
                    print(f"  ✅ {current_model} (already latest)")
            
            if updates_found > 0:
                print(f"  📊 {updates_found} models would be updated in this endpoint")

def main():
    print("🔄 Loading LibreChat configuration...")
    config = load_yaml_file('librechat.yaml')
    if not config:
        print("❌ Failed to load librechat.yaml")
        return False
    
    print("🔄 Loading OpenRouter models...")
    openrouter_models = load_openrouter_models('openrouter.txt')
    if not openrouter_models:
        print("❌ Failed to load openrouter.txt")
        return False
    
    print(f"📊 Loaded {len(openrouter_models)} models from OpenRouter")
    
    print("\n🧪 Testing model specifications updates...")
    test_model_specs_updates(config, openrouter_models)
    
    print("\n🧪 Testing endpoints updates...")
    test_endpoints_updates(config, openrouter_models)
    
    print("\n✅ Test completed! No changes were made to the configuration.")
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 