import json
import os
import re

TOKENS_DIR = os.path.join('..', 'Images', 'Tokens')
IMAGE_BASE_URL = 'https://niebvelungen.github.io/TCG-Arena-FoW/Images/Tokens/'
OUTPUT_FILE = 'tokens.json'


def sanitize(filename, delimiter):
    """Replace any non-alphanumeric characters with the given delimiter."""
    name = os.path.splitext(filename)[0]
    # Replace any non-alphanumeric character with the delimiter
    result = re.sub(r'[^a-zA-Z0-9]+', delimiter, name)
    # Strip leading/trailing delimiters
    result = result.strip(delimiter)
    return result


def build_tokens():
    if not os.path.isdir(TOKENS_DIR):
        print(f"Directory not found: {TOKENS_DIR}")
        return

    files = sorted(os.listdir(TOKENS_DIR))
    output = {}

    for filename in files:
        filepath = os.path.join(TOKENS_DIR, filename)
        if not os.path.isfile(filepath):
            continue

        card_id = sanitize(filename, '-')
        name = sanitize(filename, ' ')
        # URL-encode the filename for the image URL
        encoded_filename = filename.replace(' ', '%20')
        image_url = IMAGE_BASE_URL + encoded_filename

        entry = {
            'id': card_id,
            'name': name,
            'type': 'Token',
            'face': {
                'front': {
                    'name': name,
                    'type': 'Token',
                    'cost': 0,
                    'isHorizontal': False,
                    'image': image_url
                }
            },
            'Card type': 'Token',
            'set': 'token',
            'isHorizontal': False,
            'cost': 0,
            'isToken': True
        }

        output[card_id] = entry

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"Generated {len(output)} token entries in {OUTPUT_FILE}")


if __name__ == '__main__':
    build_tokens()
