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

def save_yaml_file(file_path, data):
    """Save YAML file safely."""
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            yaml.dump(data, file, default_flow_style=False, allow_unicode=True, sort_keys=False)
        return True
    except Exception as e:
        print(f"Error saving {file_path}: {e}")
        return False

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

def update_model_specs_with_latest_models(config, openrouter_models):
    """Update modelSpecs with the latest OpenRouter models."""
    if 'modelSpecs' not in config:
        config['modelSpecs'] = {}
    
    if 'list' not in config['modelSpecs']:
        config['modelSpecs']['list'] = []
    
    # Extract models by category
    categories = extract_models_by_category(openrouter_models)
    
    print(f"📊 Found {len(categories)} model categories:")
    for category, models in categories.items():
        print(f"  - {category}: {len(models)} models")
    
    # Update existing modelSpecs with latest models
    updated_specs = []
    updates_made = 0
    
    for spec in config['modelSpecs']['list']:
        if 'preset' in spec and 'model' in spec['preset']:
            current_model = spec['preset']['model']
            
            # Find the latest version of this model
            latest_model = find_latest_model_version(current_model, categories)
            
            if latest_model and latest_model != current_model:
                print(f"🔄 Updating {current_model} → {latest_model}")
                spec['preset']['model'] = latest_model
                if 'modelLabel' in spec:
                    spec['modelLabel'] = latest_model
                updates_made += 1
            else:
                print(f"✅ Keeping {current_model} (already latest)")
        
        updated_specs.append(spec)
    
    config['modelSpecs']['list'] = updated_specs
    
    print(f"\n📈 Summary: Updated {updates_made} model specifications")
    return config

def update_endpoints_with_latest_models(config, openrouter_models):
    """Update endpoints with the latest OpenRouter models."""
    if 'endpoints' not in config or 'custom' not in config['endpoints']:
        return config
    
    # Extract models by category
    categories = extract_models_by_category(openrouter_models)
    
    for endpoint in config['endpoints']['custom']:
        if 'models' in endpoint and 'default' in endpoint['models']:
            current_models = endpoint['models']['default']
            updated_models = []
            updates_made = 0
            
            for current_model in current_models:
                latest_model = find_latest_model_version(current_model, categories)
                
                if latest_model and latest_model != current_model:
                    print(f"🔄 Updating endpoint model {current_model} → {latest_model}")
                    updated_models.append(latest_model)
                    updates_made += 1
                else:
                    updated_models.append(current_model)
            
            endpoint['models']['default'] = updated_models
            
            if updates_made > 0:
                print(f"📊 Updated {updates_made} models in endpoint '{endpoint.get('name', 'Unknown')}'")
    
    return config

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
    
    print("\n🔄 Updating model specifications with latest models...")
    config = update_model_specs_with_latest_models(config, openrouter_models)
    
    print("\n🔄 Updating endpoints with latest models...")
    config = update_endpoints_with_latest_models(config, openrouter_models)
    
    print("\n💾 Saving updated configuration...")
    if save_yaml_file('librechat.yaml', config):
        print("✅ Configuration updated successfully!")
        return True
    else:
        print("❌ Failed to save updated configuration")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 