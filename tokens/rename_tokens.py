import os
import re

TOKENS_DIR = os.path.join('..', 'Images', 'Tokens')

renamed = 0
for f in os.listdir(TOKENS_DIR):
    filepath = os.path.join(TOKENS_DIR, f)
    if not os.path.isfile(filepath):
        continue
    name, ext = os.path.splitext(f)
    # Replace any non-alphanumeric/underscore character with underscore
    new_name = re.sub(r'[^a-zA-Z0-9_]', '_', name)
    # Collapse multiple underscores
    new_name = re.sub(r'_+', '_', new_name)
    # Strip leading/trailing underscores
    new_name = new_name.strip('_')
    new_filename = new_name + ext
    if new_filename != f:
        new_filepath = os.path.join(TOKENS_DIR, new_filename)
        if os.path.exists(new_filepath):
            print(f'COLLISION: {f}  ->  {new_filename} (already exists)')
        else:
            os.rename(filepath, new_filepath)
            print(f'{f}  ->  {new_filename}')
            renamed += 1

print(f'\nRenamed {renamed} files')