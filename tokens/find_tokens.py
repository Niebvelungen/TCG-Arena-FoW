import json
import re
import os

def parse_token_text(text):
    """
    Parse token creation text and extract token details.
    Pattern: put {quantity} {statline} {attribute} {race} {type} {with effect} into your/the field.
    """
    tokens = []

    # Pattern to find token creation
    # Matches: put a/number [stats] attribute race(s) type (with effects) into (your/the) field
    token_pattern = re.compile(
        r'put\s+'
        r'(a|\d+)\s+'                           # quantity
        r'(\[[^\]]+\])\s+'                       # statline in brackets
        r'([a-zA-Z/]+)\s+'                       # attribute (can have / for multi-color)
        r'(.+?)\s+'                              # race and type (greedy until we hit 'into' or 'with')
        r'(?:token\s+)?'                         # optional 'token' word
        r'(with\s+.+?\s+)?'                      # optional 'with effect'
        r'into\s+(?:your\s+|the\s+)?field',     # into your/the field
        re.IGNORECASE
    )

    # Find all matches
    matches = token_pattern.findall(text)

    for match in matches:
        quantity, statline, attribute, race_type, with_effect = match

        # Parse race and type from combined string
        race_type = race_type.strip()

        # Type is usually the last word(s) before 'token' or at the end
        # Common types: resonator, token, resonator token
        type_match = re.search(r'(resonator\s+token|resonator|token)$', race_type, re.IGNORECASE)
        if type_match:
            token_type = type_match.group(1)
            race = race_type[:type_match.start()].strip()
        else:
            # Check if 'token' is separate
            if 'token' in race_type.lower():
                parts = race_type.rsplit('token', 1)
                race = parts[0].strip()
                token_type = 'token'
            else:
                race = race_type
                token_type = 'resonator token'

        # Clean up race - remove trailing comma
        race = race.rstrip(',').strip()

        # Clean up with_effect
        with_effect = with_effect.strip() if with_effect else ''
        if with_effect.startswith('with '):
            with_effect = with_effect[5:].strip()

        tokens.append({
            'quantity': quantity,
            'statline': statline,
            'attribute': attribute,
            'race': race,
            'type': token_type,
            'effect': with_effect
        })

    return tokens


def parse_token_text_v2(text):
    """
    Alternative parser - more flexible approach
    """
    tokens = []

    # Find all "put ... into ... field" segments
    segments = re.finditer(
        r'put\s+(a|\d+)\s+(\[[^\]]+\])\s+(.+?)\s+into\s+(?:your\s+|the\s+)?field',
        text,
        re.IGNORECASE
    )

    for segment in segments:
        quantity = segment.group(1)
        statline = segment.group(2)
        remainder = segment.group(3).strip()

        # Check for "with" clause
        with_effect = ''
        with_match = re.search(r'\s+with\s+(.+)$', remainder, re.IGNORECASE)
        if with_match:
            with_effect = with_match.group(1).strip()
            remainder = remainder[:with_match.start()].strip()

        # Now parse: attribute race(s) type
        # Attribute is first word (can have / for multi-color like "water/darkness")
        parts = remainder.split(None, 1)
        if len(parts) >= 1:
            attribute = parts[0]
            rest = parts[1] if len(parts) > 1 else ''
        else:
            attribute = remainder
            rest = ''

        # Find type (resonator token, resonator, token)
        type_match = re.search(r'(resonator\s+token|resonator|token)\s*$', rest, re.IGNORECASE)
        if type_match:
            token_type = type_match.group(1)
            race = rest[:type_match.start()].strip()
        else:
            token_type = 'token'
            race = rest

        # Clean up race
        race = race.rstrip(',').strip()

        if statline and attribute:  # Valid token
            tokens.append({
                'quantity': quantity,
                'statline': statline,
                'attribute': attribute,
                'race': race,
                'type': token_type,
                'effect': with_effect
            })

    return tokens


def find_token_creators(input_file, output_file='token_creators.json'):
    """Find all cards that create tokens and extract token details."""

    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    results = []
    set_order = []  # Track order of sets as they appear

    # Process each game
    for game_key, game_data in data.items():
        if 'clusters' not in game_data:
            continue

        for cluster in game_data['clusters']:
            if 'sets' not in cluster:
                continue

            for card_set in cluster['sets']:
                set_code = card_set.get('code', '')

                # Track set order
                if set_code and set_code not in set_order:
                    set_order.append(set_code)

                if 'cards' not in card_set:
                    continue

                for card in card_set['cards']:
                    card_id = card.get('id', '')
                    card_name = card.get('name', '')
                    abilities = card.get('abilities', [])

                    if not abilities:
                        continue

                    # Check each ability for token creation
                    for ability in abilities:
                        # Skip counter-related "put" (counters use [+X/+X] or [-X/-X])
                        if re.search(r'put\s+a\s+\[\+|\[\-', ability):
                            continue

                        # Look for token creation patterns
                        if 'put' in ability.lower() and 'token' in ability.lower() and 'into' in ability.lower():
                            tokens = parse_token_text_v2(ability)

                            if tokens:
                                results.append({
                                    'card_id': card_id,
                                    'card_name': card_name,
                                    'set': set_code,
                                    'ability_text': ability,
                                    'tokens': tokens
                                })

    # Write results
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"Found {len(results)} cards that create tokens.")
    print(f"Output written to: {output_file}")

    # Also create a summary
    print("\n--- Token Summary ---")

    # Load existing token summary to preserve user data
    existing_tokens = {}
    existing_summary = []
    if os.path.exists('token_summary.json'):
        try:
            with open('token_summary.json', 'r', encoding='utf-8') as f:
                existing_summary = json.load(f)
                # Create lookup by unique key (stats|attribute|race|type|effect)
                for token in existing_summary:
                    effect = token.get('effect', 'none') if token.get('effect') else 'none'
                    key = f"{token['stats']}|{token['attribute']}|{token['race']}|{token['type']}|{effect}"
                    existing_tokens[key] = token
            print(f"Loaded {len(existing_summary)} existing tokens from token_summary.json")
        except (json.JSONDecodeError, IOError):
            pass

    # Each unique combination of properties is a separate token
    unique_tokens = {}
    for result in results:
        for token in result['tokens']:
            # Create a unique key for each distinct token (all properties matter)
            effect = token['effect'] if token['effect'] else 'none'
            key = f"{token['statline']}|{token['attribute']}|{token['race']}|{token['type']}|{effect}"

            if key not in unique_tokens:
                unique_tokens[key] = {
                    'statline': token['statline'],
                    'attribute': token['attribute'],
                    'race': token['race'],
                    'card_type': token['type'],
                    'effect': token['effect'],
                    'created_by': [],
                    'first_set': result['set'],
                    'first_set_index': set_order.index(result['set']) if result['set'] in set_order else 999
                }
            unique_tokens[key]['created_by'].append(result['card_name'])

    # Sort unique tokens by set order (first appearance)
    sorted_tokens = sorted(unique_tokens.items(), key=lambda x: x[1]['first_set_index'])

    # Build summary, preserving existing data
    summary = []
    new_tokens = 0

    # First, get the highest existing token number for new IDs
    max_token_num = 0
    for token in existing_summary:
        try:
            num = int(token['id'].replace('Token-', ''))
            max_token_num = max(max_token_num, num)
        except (ValueError, KeyError):
            pass

    token_counter = max_token_num + 1

    for token_key, token_data in sorted_tokens:
        # Check if this token already exists
        if token_key in existing_tokens:
            # Preserve existing token with its user data (image_url, created)
            existing = existing_tokens[token_key]

            # Update created_by list (might have new cards)
            seen = set()
            unique_created_by = []
            for card in token_data['created_by']:
                if card not in seen:
                    seen.add(card)
                    unique_created_by.append(card)

            existing['created_by_count'] = len(unique_created_by)
            existing['created_by'] = unique_created_by[:5]

            summary.append(existing)
        else:
            # New token - create entry
            token_id = f"Token-{token_counter:03d}"
            token_counter += 1
            new_tokens += 1

            # Build a human-readable name
            name_parts = []
            if token_data['statline']:
                name_parts.append(token_data['statline'])
            if token_data['attribute']:
                name_parts.append(token_data['attribute'].capitalize())
            if token_data['race']:
                name_parts.append(token_data['race'])
            name_parts.append(token_data['card_type'].replace('resonator token', 'Resonator Token').replace('token', 'Token'))

            token_name = ' '.join(name_parts)

            # Clean up created_by list (remove duplicates while preserving order)
            seen = set()
            unique_created_by = []
            for card in token_data['created_by']:
                if card not in seen:
                    seen.add(card)
                    unique_created_by.append(card)

            entry = {
                'id': token_id,
                'name': token_name,
                'stats': token_data['statline'],
                'attribute': token_data['attribute'],
                'race': token_data['race'],
                'type': token_data['card_type'],
                'first_set': token_data['first_set'],
                'created_by_count': len(unique_created_by),
                'created_by': unique_created_by[:5],  # First 5 examples
                'image_url': '',  # To be filled in manually
                'created': False  # Done state
            }

            # Only add effect if it exists
            if token_data['effect']:
                entry['effect'] = token_data['effect']

            summary.append(entry)

    # Sort summary by token ID to maintain order
    summary.sort(key=lambda x: int(x['id'].replace('Token-', '')))

    with open('token_summary.json', 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print(f"Total tokens: {len(summary)} ({new_tokens} new, {len(summary) - new_tokens} existing preserved)")
    print("Summary written to: token_summary.json")

    # Also create a simple human-readable list
    with open('token_list.txt', 'w', encoding='utf-8') as f:
        f.write("=== FORCE OF WILL TOKEN LIST ===\n\n")
        for entry in summary:
            f.write(f"{entry['id']}: {entry['name']}\n")
            f.write(f"   Stats: {entry['stats']}\n")
            f.write(f"   Color: {entry['attribute']}\n")
            f.write(f"   Race: {entry['race']}\n")
            if 'effect' in entry:
                f.write(f"   Effect: {entry['effect']}\n")
            f.write(f"   First appeared in: {entry['first_set']}\n")
            f.write(f"   Created by: {', '.join(entry['created_by'])}\n")
            f.write("\n")

    print("Human-readable list written to: token_list.txt")

    return results


if __name__ == "__main__":
    # cards.json is in parent directory
    find_token_creators('../cards.json')
