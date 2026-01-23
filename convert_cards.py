import json
import requests
import re
import os
import argparse

CACHE_FILE = "image_cache.json"
S3_BASE_URL = "https://fowsim.s3.amazonaws.com/media/cards/"
FALLBACK_BASE_URL = "https://www.forceofwind.online/card/"
PLACEHOLDER_IMAGE = "https://fowsim.s3.amazonaws.com/static/img/none.000fb66afe5c.png"

def load_image_cache(cache_file):
    """Load image cache from file"""
    if os.path.exists(cache_file):
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    return {}

def save_image_cache(cache, cache_file):
    """Save image cache to file"""
    with open(cache_file, 'w', encoding='utf-8') as f:
        json.dump(cache, f, indent=2, ensure_ascii=False)

def find_uncached_cards(input_file, cache_file=CACHE_FILE):
    """Find all card IDs from input file that are not in the cache"""
    cache = load_image_cache(cache_file)

    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    uncached = []

    for game_data in data.values():
        if 'clusters' not in game_data:
            continue
        for cluster in game_data['clusters']:
            if 'sets' not in cluster:
                continue
            for card_set in cluster['sets']:
                if 'cards' not in card_set:
                    continue
                for card in card_set['cards']:
                    card_id = card.get('id', '')
                    if card_id and card_id not in cache:
                        uncached.append(card_id)

    return uncached

def get_image_url(card_id, cache):
    """
    Check if image exists at S3, if not scrape from forceofwind.online.
    Returns the valid image URL and updates cache.
    """
    # Check cache first
    if card_id in cache:
        return cache[card_id]

    s3_url = f"{S3_BASE_URL}{card_id}.jpg"

    # Try HEAD request to S3 URL
    try:
        response = requests.head(s3_url, timeout=5)
        if response.status_code == 200:
            cache[card_id] = s3_url
            return s3_url
    except requests.RequestException:
        pass

    # Fallback: scrape from forceofwind.online
    # Replace * with %5E for the URL (site encoding)
    url_card_id = card_id.replace('*', '%5E') if card_id.endswith('*') else card_id
    fallback_url = f"{FALLBACK_BASE_URL}{url_card_id}/"
    try:
        response = requests.get(fallback_url, timeout=10)
        if response.status_code == 200:
            # Find first img with class="card-img"
            match = re.search(r'<img[^>]*class="card-img"[^>]*src="([^"]+)"', response.text)
            if match:
                image_url = match.group(1)
                cache[card_id] = image_url
                return image_url
    except requests.RequestException:
        pass

    # Not found anywhere - cache empty string
    return ""

def parse_cost(cost_str):
    """Parse cost string and return numeric value"""
    if not cost_str or cost_str == "":
        return 0

    # Remove braces
    cost_str = cost_str.replace("{", "").replace("}", "")
    total = 0

    # Process each character
    i = 0
    while i < len(cost_str):
        char = cost_str[i]

        # Check if it's a digit - could be multi-digit number
        if char.isdigit():
            num_str = ""
            while i < len(cost_str) and cost_str[i].isdigit():
                num_str += cost_str[i]
                i += 1
            total += int(num_str)
        # Count each letter as 1 (W, U, B, R, G, etc.)
        elif char.isalpha():
            total += 1
            i += 1
        else:
            i += 1

    return total

def get_card_type(types):
    if not types:
        return "Unknown"

    if any("Sub-Ruler" in t for t in types):
        return "Sub_Ruler"
    
    if any("Magic Stone" in t for t in types):
        return "Magic_Stones"
    
    if any("Chant" in t for t in types):
        return "Chant"
    
    if any("Master Rune" in t for t in types):
        return "Master_Rune"

    if any("Addition" in t for t in types):
        return "Addition"
    
    if any("Extension Rule" in t for t in types):
        return "Extension_Rule"
    
    if "Rune" in types:
        return "Rune"

    return types[0]

def is_resonator(types):
    """Check if card is a Resonator"""
    return "Resonator" in types if types else False

def is_horizontal(types):
    """Check if card should be horizontal (Extension Rule cards)"""
    if not types:
        return False
    return "Extension Rule" in types or any("Extension" in t for t in types)

def convert_cards(input_file, output_file, check_images=True):
    """Convert cards.json to example.json format"""

    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    output = {}
    missing_images = []  # Track cards without images

    # Load image cache
    image_cache = load_image_cache(CACHE_FILE) if check_images else {}
    card_count = 0
    total_cards = 0

    # Count total cards for progress
    for game_data in data.values():
        if 'clusters' in game_data:
            for cluster in game_data['clusters']:
                if 'sets' in cluster:
                    for card_set in cluster['sets']:
                        if 'cards' in card_set:
                            total_cards += len(card_set['cards'])

    # Process each game
    for game_key, game_data in data.items():
        if 'clusters' not in game_data:
            continue

        # Process each cluster
        for cluster in game_data['clusters']:
            if 'sets' not in cluster:
                continue

            # Process each set
            for card_set in cluster['sets']:
                set_code = card_set.get('code', '').lower()

                if 'cards' not in card_set:
                    continue

                # Process each card
                for card in card_set['cards']:
                    card_id = card.get('id', '')

                    # Skip if no ID
                    if not card_id:
                        continue

                    # Progress indicator
                    card_count += 1
                    if card_count % 100 == 0:
                        print(f"Processing card {card_count}/{total_cards}...")

                    # Get image URL (with caching)
                    if check_images:
                        image_url = get_image_url(card_id, image_cache)
                        if not image_url or image_url == PLACEHOLDER_IMAGE:
                            missing_images.append(card_id)
                            continue  # Skip cards without images or with placeholder
                    else:
                        image_url = f"{S3_BASE_URL}{card_id}.jpg"

                    # Check if this is a J-card (backface) or *-card (split/double-faced)
                    is_j_card = card_id.endswith('J')
                    is_star_card = card_id.endswith('*')
                    base_id = card_id[:-1] if (is_j_card or is_star_card) else card_id

                    if is_j_card:
                        # Add as backface to existing card (J-Ruler back face)
                        if base_id in output:
                            card_types = card.get('type', [])
                            output[base_id]['face']['back'] = {
                                'name': card.get('name', ''),
                                'type': get_card_type(card_types),
                                'cost': parse_cost(card.get('cost', '')),
                                'isHorizontal': is_horizontal(card_types),
                                'image': image_url
                            }

                            # Add ATK/DEF if it's a Resonator
                            if is_resonator(card.get('type', [])):
                                atk = card.get('ATK', '')
                                def_val = card.get('DEF', '')
                                output[base_id]['face']['back']['ATK'] = atk if atk else ''
                                output[base_id]['face']['back']['DEF'] = def_val if def_val else ''
                                output[base_id]['ATK'] = atk if atk else ''
                                output[base_id]['DEF'] = def_val if def_val else ''
                    elif is_star_card:
                        # Update main entry with split card naming
                        if base_id in output:
                            card_types = card.get('type', [])
                            card_name_1 = output[base_id]['name']
                            card_name_2 = card.get('name', '')
                            card_type_1 = output[base_id]['Card type']
                            card_type_2 = ' - '.join(card_types) if card_types else ''

                            output[base_id]['name'] = f"{card_name_1} // {card_name_2}"
                            output[base_id]['Card type'] = f"{card_type_1} // {card_type_2}"

                            # Add back face if it's a Sub-Ruler
                            if any("Sub-Ruler" in t for t in card_types) or any("Resonator" in t for t in card_types) or any("Addition" in t for t in card_types) or any("Regalia" in t for t in card_types):
                                output[base_id]['face']['back'] = {
                                    'name': card.get('name', ''),
                                    'type': get_card_type(card_types),
                                    'cost': parse_cost(card.get('cost', '')),
                                    'isHorizontal': is_horizontal(card_types),
                                    'image': image_url
                                }
                    else:
                        # Create new card entry
                        card_types = card.get('type', [])
                        card_type = get_card_type(card_types)
                        colours = card.get('colour', [])
                        horizontal = is_horizontal(card_types)

                        card_entry = {
                            'id': card_id,
                            'name': card.get('name', ''),
                            'type': card_type,
                            'face': {
                                'front': {
                                    'name': card.get('name', ''),
                                    'type': card_type,
                                    'cost': parse_cost(card.get('cost', '')),
                                    'isHorizontal': horizontal,
                                    'image': image_url
                                }
                            },
                            'Colors': colours,
                            'Card type': ' - '.join(card_types) if card_types else '',
                            'Color identity': colours,
                            'set': set_code,
                            'isHorizontal': horizontal,
                            'cost': parse_cost(card.get('cost', ''))
                        }

                        # Add ATK/DEF if it's a Resonator
                        if is_resonator(card.get('type', [])):
                            atk = card.get('ATK', '')
                            def_val = card.get('DEF', '')
                            card_entry['ATK'] = atk if atk else ''
                            card_entry['DEF'] = def_val if def_val else ''
                            card_entry['face']['front']['ATK'] = atk if atk else ''
                            card_entry['face']['front']['DEF'] = def_val if def_val else ''

                        output[card_id] = card_entry

    # Save image cache
    if check_images:
        save_image_cache(image_cache, CACHE_FILE)
        print(f"Image cache saved to: {CACHE_FILE}")

        # Export missing images list
        if missing_images:
            missing_file = "missing_images.txt"
            with open(missing_file, 'w', encoding='utf-8') as f:
                for card_id in missing_images:
                    f.write(f"{card_id}\n")
            print(f"Cards without images ({len(missing_images)}): {missing_file}")

    # Write output
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"Conversion complete! Processed {len(output)} cards.")
    if check_images and missing_images:
        print(f"Excluded {len(missing_images)} cards without images.")
    print(f"Output written to: {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Convert FoW cards.json to output format')
    parser.add_argument('--uncached', action='store_true',
                        help='Output card IDs that are not in the image cache')
    parser.add_argument('--no-images', action='store_true',
                        help='Skip image checking (faster)')
    parser.add_argument('--input', default='cards.json',
                        help='Input file (default: cards.json)')
    parser.add_argument('--output', default='cards_fow.json',
                        help='Output file (default: cards_fow.json)')

    args = parser.parse_args()

    if args.uncached:
        uncached = find_uncached_cards(args.input)
        print(f"Found {len(uncached)} uncached card IDs:")
        for card_id in uncached:
            print(card_id)
    else:
        convert_cards(args.input, args.output, check_images=not args.no_images)
