"""Generate default grail data structure from item_library"""
import csv
import re
from functools import lru_cache
from init import media_path
from utils.item_name_lists import get_eth_item_set, get_base_item

# Mapping from CSV format to JSON format for Item Group 1
# Items not in this mapping will default to .lower()
ITEM_GROUP_1_MAPPING = {
    'Axe 1H': 'axe (1-h)',
    'Axe 2H': 'axe (2-h)',
    'Sword 1H': 'swords (1-h)',
    'Sword 2H': 'swords (2-h)',
    'Club 1H': 'clubs (1-h)',
    'Club 2H': 'clubs (2-h)',
    'Javelin': 'throwing',
    'Throwing': 'throwing',
    'Staff': 'staves',
    'Polearm': 'polearms',
    'Wand': 'wands',
    'Spear': 'spears',
    'Scepter': 'scepters',
    'Belt': 'belts',
    'Shield': 'shields',
    'Hsarus\' Defense': 'Hsaru\'s Defense',  # Add set name typo for API alignment
}

# Mapping from CSV Base Item to normalized subcategory
BASE_ITEM_MAPPING = {
    'Ring': 'rings',
    'Amulet': 'amulets',
}

# Mapping from Item Group 0 to unique category
UNIQUE_CATEGORY_MAPPING = {
    'Unique Armor': 'armor',
    'Unique Weapons': 'weapons',
    'Unique Other': 'other',
}

# Handler functions for special unique item categories
# Each handler builds the path and returns (path, key) tuple
def handle_jewelry(path, row, **kwargs):
    quality = kwargs.get('quality')
    pd2_mode = kwargs.get('pd2_mode', False)
    base_item = get_base_item(row, pd2_mode)
    subcategory = BASE_ITEM_MAPPING.get(base_item, 'jewelry')
    path = path.setdefault(subcategory, {})
    if quality:
        path = path.setdefault(quality.lower(), {})
    return path, row['Item']

def handle_rainbow_facet(path, row, **kwargs):
    activation_type = row['Item Group 2'].lower()
    # Extract damage type from "Rainbow Facet (Cold Die)" -> "Cold"
    match = re.search(r'Rainbow Facet \(([A-Za-z]+)', row['Item'])
    damage_type = match.group(1) if match else row['Item'].split(' ')[2][1:]  # Fallback to old method
    path = path.setdefault(activation_type, {})
    return path, damage_type

def handle_classes(path, row, **kwargs):
    class_name = row['Class restriction'].lower()
    path = path.setdefault(class_name, {})
    return path, row['Item']

def handle_charms(path, row, **kwargs):
    quality = kwargs.get('quality')
    path = path.setdefault('all', {})
    if quality:
        path = path.setdefault(quality.lower(), {})
    return path, row['Item']

def handle_default(path, row, **kwargs):
    quality = kwargs.get('quality')
    # Special case: Kira's Guardian is marked as Exceptional in CSV but incorrectly goes under elite in JSON (API requirement)
    item_name = row['Item']
    if item_name == "Kira's Guardian":
        quality = 'elite'
    if quality:
        path = path.setdefault(quality.lower(), {})
    return path, item_name

# Map normalized group names to their handlers
UNIQUE_HANDLERS = {
    'jewelry': handle_jewelry,
    'rainbow facet (jewel)': handle_rainbow_facet,
    'classes': handle_classes,
    'charms': handle_charms,
}


@lru_cache(maxsize=4)
def generate_default_grail_data(pd2_mode=False, eth=False):
    """Generate default grail data structure from item_library.csv
    
    Args:
        pd2_mode: If True, include PD2 items
        eth: If True, only include items that can spawn as ethereal (from ETH_ITEM_SET)
    """
    
    data = {
        'uniques': {'armor': {}, 'weapons': {}, 'other': {}}
    }
    
    if not eth:
        data['sets'] = {}
        data['runes'] = {'low runes': {}, 'middle runes': {}, 'high runes': {}}
    
    # Load items from CSV
    eth_item_set = get_eth_item_set(pd2_mode)
    with open(media_path + 'item_library.csv', 'r', encoding='utf-8') as fo:
        for row in csv.DictReader(fo):
            item_name = row['Item']
            
            # Filter eth items if needed (include PD2 items if pd2_mode is active)
            if eth and item_name not in eth_item_set:
                continue
            
            # Filter based on PD2 mode
            if not pd2_mode and row.get('PD2 item', '').upper() == 'TRUE':
                continue
            
            rarity = row['Rarity']
            quality = row['Quality'].strip()
            item_group_0 = row['Item Group 0']
            item_group_1 = row['Item Group 1']
            
            # Handle runes
            if item_group_0 == 'Runes':
                data['runes'][item_group_1.lower()][item_name] = {}
            elif rarity == 'Set':
                item_group_1 = ITEM_GROUP_1_MAPPING.get(item_group_1, item_group_1)
                data['sets'].setdefault(item_group_1, {})[item_name] = {}
            elif rarity == 'Unique':
                category = UNIQUE_CATEGORY_MAPPING[item_group_0]
                normalized_group_1 = ITEM_GROUP_1_MAPPING.get(item_group_1, item_group_1.lower())
                
                # Get handler for this item group, or use default
                handler = UNIQUE_HANDLERS.get(normalized_group_1, handle_default)
                
                # Build the path using the handler
                path = data['uniques'][category].setdefault(normalized_group_1, {})
                path, key = handler(path, row, quality=quality, pd2_mode=pd2_mode)
                
                path[key] = {}
    
    return data


def get_default_data(pd2_mode=False):
    """Get default grail data, generating it if needed"""
    return generate_default_grail_data(pd2_mode, eth=False)


def get_default_eth_data(pd2_mode=False):
    """Get default eth grail data, generating it if needed"""
    return generate_default_grail_data(pd2_mode, eth=True)
