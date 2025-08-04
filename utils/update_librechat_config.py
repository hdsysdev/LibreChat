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
    
    # If no exact match found, try to find newer versions of the same model family
    if not latest_model:
        latest_model = find_newer_model_family(current_model, categories)
    
    return latest_model

def find_newer_model_family(current_model, categories):
    """Find newer versions of the same model family (e.g., claude-3.7 -> claude-4)."""
    # Define model family mappings for major version upgrades
    model_families = {
        'anthropic/claude-3.7-sonnet': ['anthropic/claude-4-sonnet', 'anthropic/claude-4'],
        'anthropic/claude-3.7-sonnet:thinking': ['anthropic/claude-4-sonnet:thinking', 'anthropic/claude-4:thinking'],
        'anthropic/claude-3.5-sonnet': ['anthropic/claude-4-sonnet', 'anthropic/claude-4'],
        'anthropic/claude-3.5-sonnet:thinking': ['anthropic/claude-4-sonnet:thinking', 'anthropic/claude-4:thinking'],
        'anthropic/claude-3-opus': ['anthropic/claude-4-opus', 'anthropic/claude-4'],
        'anthropic/claude-3-opus:thinking': ['anthropic/claude-4-opus:thinking', 'anthropic/claude-4:thinking'],
        'anthropic/claude-3-haiku': ['anthropic/claude-4-haiku', 'anthropic/claude-4'],
        'anthropic/claude-3-haiku:thinking': ['anthropic/claude-4-haiku:thinking', 'anthropic/claude-4:thinking'],
        'openai/gpt-4': ['openai/gpt-4o', 'openai/gpt-4o-latest'],
        'openai/gpt-4-turbo': ['openai/gpt-4o', 'openai/gpt-4o-latest'],
        'openai/gpt-4-turbo-preview': ['openai/gpt-4o', 'openai/gpt-4o-latest'],
        'openai/gpt-4-1106-preview': ['openai/gpt-4o', 'openai/gpt-4o-latest'],
        'openai/gpt-4-0125-preview': ['openai/gpt-4o', 'openai/gpt-4o-latest'],
        'openai/gpt-4-0613': ['openai/gpt-4o', 'openai/gpt-4o-latest'],
        'openai/gpt-4-0314': ['openai/gpt-4o', 'openai/gpt-4o-latest'],
        'openai/gpt-3.5-turbo': ['openai/gpt-4o-mini', 'openai/o4-mini'],
        'openai/gpt-3.5-turbo-16k': ['openai/gpt-4o-mini', 'openai/o4-mini'],
        'google/gemini-2.0': ['google/gemini-2.5-pro', 'google/gemini-2.5-pro-exp-03-25'],
        'google/gemini-1.5': ['google/gemini-2.5-pro', 'google/gemini-2.5-pro-exp-03-25'],
        'google/gemini-1.0': ['google/gemini-2.5-pro', 'google/gemini-2.5-pro-exp-03-25'],
        'deepseek/deepseek-chat-v2': ['deepseek/deepseek-chat-v3', 'deepseek/deepseek-chat-v3-0324'],
        'deepseek/deepseek-chat-v1': ['deepseek/deepseek-chat-v3', 'deepseek/deepseek-chat-v3-0324'],
        'x-ai/grok-2': ['x-ai/grok-3', 'x-ai/grok-3-beta'],
        'x-ai/grok-1': ['x-ai/grok-3', 'x-ai/grok-3-beta'],
        'mistralai/mistral-7b': ['mistralai/mistral-8x7b', 'mistralai/mistral-large'],
        'mistralai/mistral-medium': ['mistralai/mistral-large', 'mistralai/mistral-large-latest'],
        'meta-llama/llama-2': ['meta-llama/llama-3', 'meta-llama/llama-3.1'],
        'meta-llama/llama-2-70b': ['meta-llama/llama-3.1-70b', 'meta-llama/llama-3.1-405b'],
        'meta-llama/llama-2-13b': ['meta-llama/llama-3.1-8b', 'meta-llama/llama-3.1-70b'],
        'meta-llama/llama-2-7b': ['meta-llama/llama-3.1-8b', 'meta-llama/llama-3.1-70b'],
    }
    
    # Check if current model has a newer family version
    if current_model in model_families:
        for newer_model in model_families[current_model]:
            # Check if the newer model exists in available models
            for category, models in categories.items():
                for model in models:
                    if model.endswith(':free'):
                        continue
                    if model == newer_model:
                        return newer_model
    
    return None

def validate_model_exists(model_name, categories):
    """Check if a model exists in the available models."""
    for category, models in categories.items():
        for model in models:
            if model == model_name:
                return True
    return False

def find_valid_replacement_model(invalid_model, categories):
    """Find a valid replacement for an invalid model."""
    # Define replacement mappings for common invalid models
    replacement_mappings = {
        'google/gemini-2.5-flash-preview': 'google/gemini-2.5-pro-exp-03-25',
        'google/gemini-2.5-flash-preview:thinking': 'google/gemini-2.5-pro-exp-03-25',
        'google/gemini-2.5-pro-preview-03-25': 'google/gemini-2.5-pro-exp-03-25',
        'google/gemini-2.5-pro-preview': 'google/gemini-2.5-pro-exp-03-25',
        'google/gemini-2.0-flash': 'google/gemini-2.5-pro-exp-03-25',
        'google/gemini-2.0-pro': 'google/gemini-2.5-pro-exp-03-25',
        'google/gemini-1.5-pro': 'google/gemini-2.5-pro-exp-03-25',
        'google/gemini-1.5-flash': 'google/gemini-2.5-pro-exp-03-25',
        'openai/gpt-4-turbo': 'openai/gpt-4o-latest',
        'openai/gpt-4-turbo-preview': 'openai/gpt-4o-latest',
        'openai/gpt-4-1106-preview': 'openai/gpt-4o-latest',
        'openai/gpt-4-0125-preview': 'openai/gpt-4o-latest',
        'openai/gpt-4-0613': 'openai/gpt-4o-latest',
        'openai/gpt-4-0314': 'openai/gpt-4o-latest',
        'openai/gpt-3.5-turbo': 'openai/o4-mini',
        'openai/gpt-3.5-turbo-16k': 'openai/o4-mini',
        'anthropic/claude-3.5-sonnet': 'anthropic/claude-3.7-sonnet',
        'anthropic/claude-3.5-sonnet:thinking': 'anthropic/claude-3.7-sonnet:thinking',
        'anthropic/claude-3-opus': 'anthropic/claude-3.7-sonnet',
        'anthropic/claude-3-opus:thinking': 'anthropic/claude-3.7-sonnet:thinking',
        'anthropic/claude-3-haiku': 'anthropic/claude-3.7-sonnet',
        'anthropic/claude-3-haiku:thinking': 'anthropic/claude-3.7-sonnet:thinking',
        'deepseek/deepseek-chat-v2': 'deepseek/deepseek-chat-v3-0324',
        'deepseek/deepseek-chat-v1': 'deepseek/deepseek-chat-v3-0324',
        'x-ai/grok-2': 'x-ai/grok-3-beta',
        'x-ai/grok-1': 'x-ai/grok-3-beta',
        'mistralai/mistral-7b': 'mistralai/mistral-large',
        'mistralai/mistral-medium': 'mistralai/mistral-large',
        'meta-llama/llama-2': 'meta-llama/llama-3.1-8b',
        'meta-llama/llama-2-70b': 'meta-llama/llama-3.1-70b',
        'meta-llama/llama-2-13b': 'meta-llama/llama-3.1-8b',
        'meta-llama/llama-2-7b': 'meta-llama/llama-3.1-8b',
    }
    
    # Check if we have a direct replacement mapping
    if invalid_model in replacement_mappings:
        replacement = replacement_mappings[invalid_model]
        if validate_model_exists(replacement, categories):
            return replacement
    
    # Try to find a similar model by extracting the provider and model family
    parts = invalid_model.split('/')
    if len(parts) == 2:
        provider, model_name = parts
        
        # Look for models from the same provider
        for category, models in categories.items():
            for model in models:
                if model.endswith(':free'):
                    continue
                    
                if model.startswith(f"{provider}/"):
                    # Check if it's a similar model family
                    model_parts = model.split('/')[1].split('-')
                    invalid_parts = model_name.split('-')
                    
                    # If they share common parts, it might be a good replacement
                    if any(part in model for part in invalid_parts[:2]):
                        return model
    
    # Fallback: return the first available model from the same provider
    for category, models in categories.items():
        for model in models:
            if model.endswith(':free'):
                continue
                
            if model.startswith(f"{parts[0]}/"):
                return model
    
    return None

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
    replacements_made = 0
    
    for spec in config['modelSpecs']['list']:
        if 'preset' in spec and 'model' in spec['preset']:
            current_model = spec['preset']['model']
            
            # Check if current model exists
            if not validate_model_exists(current_model, categories):
                print(f"❌ Invalid model: {current_model}")
                # Try to find a valid replacement
                replacement_model = find_valid_replacement_model(current_model, categories)
                if replacement_model:
                    print(f"🔄 Replacing {current_model} → {replacement_model}")
                    spec['preset']['model'] = replacement_model
                    if 'modelLabel' in spec:
                        spec['modelLabel'] = replacement_model
                    replacements_made += 1
                else:
                    print(f"❌ Could not find replacement for {current_model}, keeping as is")
                updated_specs.append(spec)
                continue
            
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
    
    print(f"\n📈 Summary: Updated {updates_made} model specifications, replaced {replacements_made} invalid models")
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
            replacements_made = 0
            
            for current_model in current_models:
                # Check if current model exists
                if not validate_model_exists(current_model, categories):
                    print(f"❌ Invalid model in endpoint: {current_model}")
                    # Try to find a valid replacement
                    replacement_model = find_valid_replacement_model(current_model, categories)
                    if replacement_model:
                        print(f"🔄 Replacing endpoint model {current_model} → {replacement_model}")
                        updated_models.append(replacement_model)
                        replacements_made += 1
                    else:
                        print(f"❌ Could not find replacement for {current_model}, keeping as is")
                        updated_models.append(current_model)
                    continue
                
                latest_model = find_latest_model_version(current_model, categories)
                
                if latest_model and latest_model != current_model:
                    print(f"🔄 Updating endpoint model {current_model} → {latest_model}")
                    updated_models.append(latest_model)
                    updates_made += 1
                else:
                    updated_models.append(current_model)
            
            endpoint['models']['default'] = updated_models
            
            if updates_made > 0 or replacements_made > 0:
                print(f"📊 Updated {updates_made} models, replaced {replacements_made} invalid models in endpoint '{endpoint.get('name', 'Unknown')}'")
    
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