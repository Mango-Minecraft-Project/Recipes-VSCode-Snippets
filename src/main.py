import json
import tomllib
import os


CONDITION_DATA: dict[str, dict] = {}
for filename in os.listdir('./data/condition'):
    with open(f'./data/condition/{filename}') as file:
        CONDITION_DATA |= json.load(file)
with open('./data/namespace.toml', 'rb') as file:
    NAMESPACE_DATA: dict[str, str] = tomllib.load(file)
with open('./data/sort_keys.toml', 'rb') as file:
    SORT_KEYS_DATA: dict[str, dict] = tomllib.load(file)
with open('./data/base_usage.toml', 'rb') as file:
    BASE_USAGE_DATA: dict[str, dict[str, list]] = tomllib.load(file)


class CodeSnippetsGenerator:
    def __init__(self, folder_name: str) -> None:
        self.folder_name = folder_name
        mod_id = NAMESPACE_DATA[folder_name]
        self.sort_keys = SORT_KEYS_DATA['general'] + SORT_KEYS_DATA[mod_id]
        
        with open(f'./data/mods/{folder_name}/base.json') as file:
            base_data = json.load(file)
        base_blacklist = BASE_USAGE_DATA[folder_name].setdefault('blacklist', [])
        
        self.code_snippets = {}
        for file_name in os.listdir(f'./data/mods/{folder_name}/type'):
            recipe_type = file_name.removesuffix('.json')
            
            with open(f'./data/mods/{self.folder_name}/type/{file_name}') as file:
                data = json.load(file)
            
            if recipe_type not in base_blacklist:
                data = base_data | data
            data |= CONDITION_DATA | {'type': f'{mod_id}:{recipe_type}'}
            
            data = self.dict_sort(object=data)
            self.code_snippets |= self.generate_code_snippet(recipe_type=file_name, content=data)

    
    def generate_code_snippet(self, recipe_type: str, content: dict) -> dict:
        recipe_type = recipe_type.removesuffix('.json')
        return {
            f'Minecraft Recipes - {self.folder_name}:{recipe_type}': {
                'prefix': f'mr.{self.folder_name}:{recipe_type}',
                'body': json.dumps(content, ensure_ascii=False, indent=2).splitlines()
            }
        }

    def dict_sort(self, object: dict) -> dict:
        return dict(sorted(object.items(), key=lambda x: self.sort_keys.index(x[0])))


if __name__ == '__main__':
    generator_blacklist = ['tconstruct']
    for folder_name in os.listdir('./data/mods'):
        if folder_name in generator_blacklist:
            continue
        generator = CodeSnippetsGenerator(folder_name)    
        with open(f'./src/result/{folder_name}.code-snippets', 'w') as file:
            json.dump(generator.code_snippets, file, indent=2)
