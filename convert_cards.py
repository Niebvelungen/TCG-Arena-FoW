import json

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
    """Get the card type, prioritizing Magic Stone, then Rune, otherwise first entry"""
    if not types:
        return "Unknown"

    # Check if any type contains "Magic Stone"
    if any("Magic Stone" in t for t in types):
        return "Magic_Stones"
    
    # Check if any type contains "Magic Stone"
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

def convert_cards(input_file, output_file):
    """Convert cards.json to example.json format"""

    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    output = {}

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
                                'image': f"https://fowsim.s3.amazonaws.com/media/cards/{card_id}.jpg"
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
                        # Update main entry with split card naming (no back face)
                        if base_id in output:
                            card_name_1 = output[base_id]['name']
                            card_name_2 = card.get('name', '')
                            card_type_1 = output[base_id]['Card type']
                            card_type_2 = ' - '.join(card.get('type', [])) if card.get('type') else ''

                            output[base_id]['name'] = f"{card_name_1} // {card_name_2}"
                            output[base_id]['Card type'] = f"{card_type_1} // {card_type_2}"
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
                                    'image': f"https://fowsim.s3.amazonaws.com/media/cards/{card_id}.jpg"
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

    # Write output
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"Conversion complete! Processed {len(output)} cards.")
    print(f"Output written to: {output_file}")

if __name__ == "__main__":
    convert_cards('cards.json', 'cards_fow.json')
