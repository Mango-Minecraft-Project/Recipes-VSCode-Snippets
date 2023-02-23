import json
import os
import tomllib

sort_keys = [
    "forge:conditions", "fabric:load_conditions",
    "type", "group",
    "ingredient", "ingredients", "pattern", "key", "transitionalItem", "sequence", "template", "base", "addition",
    "result", "results",
    "processingTime", "acceptMirrored", "loops", "headRequirement", "experience", "cookingtime", "count", "category"
    ]

with open('./data/namespace.toml', 'rb') as file:
    mod_id_data = tomllib.load(file)

def get_json_data(subpath: str, path_base: str = 'data') -> dict:
    with open(f'./{path_base}/{subpath}') as file:
        return json.load(file)

def generate_snippet(mod_id: str, base_blacklist: list[str] = [], base_whitelist: list[str] = []) -> dict:
    base = get_json_data(f'{mod_id}/base.json')
    _mod_id = mod_id_data[mod_id]
    
    conditions = {}
    for condition in os.listdir(f'./data/condition'):
        conditions |= get_json_data(f'condition/{condition}')
    
    snippets = {}
    for type in os.listdir(f'./data/{mod_id}/type'):
        data = get_json_data(f'{mod_id}/type/{type}')
        
        type = type.removesuffix('.json')
        check = (type in base_whitelist or not base_whitelist) and type not in base_blacklist
        if check:
            data = base | data
        data |= conditions
        
        data['type'] = f'{_mod_id}:{type}'
        data = dict(sorted(data.items(), key=lambda x: sort_keys.index(x[0])))
        lines = [*json.dumps(data, indent=2).splitlines()]

        snippet_base = {
            f"Minecraft Recipes - {mod_id}:{type}": {
                "prefix": f"mr.{mod_id}:{type}",
                "body": lines
                }
            }
        
        # snippet_base = {
        #     f"Minecraft Recipes - {_mod_id}:{type}": {
        #         "prefix": f"mr.{_mod_id}:{type}",
        #         "body": lines
        #         }
        #     }
        snippets |= snippet_base
    
    with open(f'./src/result/{mod_id}.code-snippets', 'w') as file:
        json.dump(snippets, file, indent=2)
    return snippets

def snippets_mix(names: list[str]):
    snippets = {}
    for name in names:
        snippets |= get_json_data(f'result/{name}.code-snippets', 'src')
    with open('./src/result/mix.code-snippets', 'w') as file:
        json.dump(snippets, file, indent=2)

process_data = {
    'minecraft_1.19': {
        'base_whitelist': ['blasting', 'campfire_cooking', 'smelting', 'smoking']
        },
    'minecraft_1.20': {
        'base_whitelist': ['blasting', 'campfire_cooking', 'smelting', 'smoking', 'crafting_decorated_pot']
        },
    'create': {
        'base_blacklist': ['mechanical_crafting', 'sequenced_assembly']
        }
    }
for mod_id, kwargs in process_data.items():
    generate_snippet(mod_id, **kwargs)
snippets_mix(process_data.keys())