"""Item name lists and mappings for autocompletion and grail logic"""
from functools import lru_cache
import csv
from init import media_path


# ============================================================================
# Constants
# ============================================================================

# Special non-equipment items that are NOT in the CSV
SPECIAL_VANILLA_ITEMS = [
    "Key of Destruction", "Key of Hate", "Key of Terror"
]

SPECIAL_PD2_ITEMS = [
    "Worldstone Shard", "Larzuk's Puzzlebox", "Larzuk's Puzzlepiece",
    "Demonic Cube", "Horadrim Navigator", "Horadrim Almanac", "Skeleton Key",
    "Vial of Lightsong", "Lilith's Mirror", "Sigil of Madawc", "Sigil of Talic",
    "Sigil of Korlic", "Prime Evil Soul", "Pure Demonic Essence",
    "Splinter of the Void", "Trang-Oul's Jawbone", "Demonic Insignia",
    "Talisman of Transgression", "Flesh of Malic", "Horadrim Scarab",
    "Catalyst Shard", "Fallen Garden's Map", "Zhar's Sanctum Map",
    "Stygian Caverns Map", "Imperial Palace Map", "Outer Void Map"
]

# Hardcoded UNID items that need special handling (Magic/Rare versions of items without unique/set)
UNID_SPECIAL_ITEMS = [
    # Selected tc81
    "Spired Helm (Magic)", "Spired Helm (Rare)", "Cryptic Axe (Magic)", "Cryptic Axe (Rare)",
    
    # Magic version of tc84/87 with unique/set counterparts
    "Archon Staff (Magic)", "Berserker Axe (Magic)", "Bloodlord Skull (Magic)", "Bone Visage (Magic)",
    "Caduceus (Magic)", "Champion Axe (Magic)", "Colossus Blade (Magic)", "Corona (Magic)", "Cryptic Sword (Magic)",
    "Demon Crossbow (Magic)", "Diadem (Magic)", "Dimensional Shard (Magic)", "Fanged Knife (Magic)",
    "Giant Thresher (Magic)", "Glorious Axe (Magic)", "Hydra Bow (Magic)", "Lacquered Plate (Magic)",
    "Legend Spike (Magic)", "Legendary Mallet (Magic)", "Myrmidon Greaves (Magic)", "Mythical Sword (Magic)",
    "Ogre Gauntlets (Magic)", "Sacred Armor (Magic)", "Scissors Suwayyah (Magic)", "Shadow Plate (Magic)",
    "Sky Spirit (Magic)", "Thunder Maul (Magic)", "Troll Belt (Magic)", "Unearthed Wand (Magic)",
    "Vortex Shield (Magic)", "War Pike (Magic)", "Ward (Magic)", "Winged Harpoon (Magic)", "Zakarum Shield (Magic)",
    
    # Rare version of tc84/87 with unique/set counterparts
    "Archon Staff (Rare)", "Berserker Axe (Rare)", "Bloodlord Skull (Rare)", "Bone Visage (Rare)",
    "Caduceus (Rare)", "Champion Axe (Rare)", "Colossus Blade (Rare)", "Corona (Rare)", "Cryptic Sword (Rare)",
    "Demon Crossbow (Rare)", "Diadem (Rare)", "Dimensional Shard (Rare)", "Fanged Knife (Rare)",
    "Giant Thresher (Rare)", "Glorious Axe (Rare)", "Hydra Bow (Rare)", "Lacquered Plate (Rare)",
    "Legend Spike (Rare)", "Legendary Mallet (Rare)", "Myrmidon Greaves (Rare)", "Mythical Sword (Rare)",
    "Ogre Gauntlets (Rare)", "Sacred Armor (Rare)", "Scissors Suwayyah (Rare)", "Shadow Plate (Rare)",
    "Sky Spirit (Rare)", "Thunder Maul (Rare)", "Troll Belt (Rare)", "Unearthed Wand (Rare)",
    "Vortex Shield (Rare)", "War Pike (Rare)", "Ward (Rare)", "Winged Harpoon (Rare)", "Zakarum Shield (Rare)",
    
    # Charms and jewels
    "Grand Charm (Magic)", "Large Charm (Magic)", "Small Charm (Magic)", "Jewel (Magic)", "Jewel (Rare)",
    
    # TC84 with no set/unique
    "Archon Plate (Magic)", "Archon Plate (Rare)", "Ghost Spear (Magic)", "Ghost Spear (Rare)", "Shillelagh (Magic)",
    "Shillelagh (Rare)", "Vortex Orb (Magic)", "Vortex Orb (Rare)", "Great Poleaxe (Magic)", "Great Poleaxe (Rare)",
    
    # TC87 with no set/unique
    "Colossus Girdle (Magic)", "Colossus Girdle (Rare)", "Dream Spirit (Magic)", "Dream Spirit (Rare)",
    "Guardian Crown (Magic)", "Guardian Crown (Rare)",
    
    # Circlet types
    "Circlet (Magic)", "Tiara (Magic)", "Coronet (Magic)", "Diadem (Magic)",
    "Circlet (Rare)", "Tiara (Rare)", "Coronet (Rare)", "Diadem (Rare)",
    
    # Other items requested by the CHOSEN Juan
    "Sacred Rondache (Magic)", "Sacred Targe (Magic)", "Kurast Shield (Magic)", "Colossus Sword (Magic)", "Monarch (Magic)",
    "Sacred Rondache (Rare)", "Sacred Targe (Rare)", "Kurast Shield (Rare)", "Colossus Sword (Rare)", "Monarch (Rare)",
]

UNID_PD2_SPECIAL_ITEMS = [
    "Map (Unique)",
]

NO_UNIQUE_MAP = {
    'Coronet': {'TC': 54, 'Item Class': 'Circlet'},

    'Sacred Targe': {'TC': 63, 'Item Class': 'Shield'},
    'Kurast Shield': {'TC': 75, 'Item Class': 'Shield'},
    'Colossus Sword': {'TC': 81, 'Item Class': 'Sword 2H'},

    'Archon Plate': {'TC': 84, 'Item Class': 'Armor'},
    'Ghost Spear': {'TC': 84, 'Item Class': 'Spear'},
    'Shillelagh': {'TC': 84, 'Item Class': 'Staff'},
    'Vortex Orb': {'TC': 84, 'Item Class': 'Orb'},
    'Great Poleaxe': {'TC': 84, 'Item Class': 'Polearm'},

    'Colossus Girdle': {'TC': 87, 'Item Class': 'Belt'},
    'Dream Spirit': {'TC': 87, 'Item Class': 'Helm'},
    'Guardian Crown': {'TC': 87, 'Item Class': 'Helm'},
}

NO_UNIQUE_MAP_PD2 = {
    'Coronet': {'TC': 54, 'Item Class': 'Circlet'},

    'Sacred Targe': {'TC': 63, 'Item Class': 'Shield'},
    'Kurast Shield': {'TC': 75, 'Item Class': 'Shield'},

    'Great Poleaxe': {'TC': 84, 'Item Class': 'Polearm'},
}

ITEM_ALIASES = {
    "Aldur's Boots": "Aldur's Advance",
    "Aldur's Weapon": "Aldur's Rhythm",
    "Aldur's Armor": "Aldur's Deception",
    "Aldur's Helm": "Aldur's Stony Gaze",
    "Andy's Face": "Andariel's Visage",
    'Angelic Amu': 'Angelic Wings',
    'Angelic Ring': 'Angelic Halo',
    'Angelic Armor': 'Angelic Mantle',
    'Angelic Weapon': 'Angelic Sickle',
    'BK ring': "Bul-Kathos' Wedding Band",
    'CoA': 'Crown of Ages',
    'DF': "Death's Fathom",
    'Dkey': 'Key of Destruction',
    'Dweb': "Death's Web",
    'G Angel': 'Guardian Angel',
    'GAngel': 'Guardian Angel',
    'GF': 'The Grandfather',
    "Griswold's Armor": "Griswold's Heart",
    "Griswold's Helm": "Griswold's Valor",
    "Griswold's Shield": "Griswold's Honor",
    "Griswold's Weapon": "Griswold's Redemption",
    "Griswold's Caduceus": "Griswold's Redemption",
    "Gris Caduceus": "Griswold's Redemption",
    "Gris Armor": "Griswold's Heart",
    "Gris Helm": "Griswold's Valor",
    "Gris Shield": "Griswold's Honor",
    "Gris Weapon": "Griswold's Redemption",
    'Gull Dagger': 'Gull',
    'HoZ': 'Herald of Zakarum',
    'Hkey': 'Key of Hate',
    'IK Armor': "Immortal King's Soul Cage",
    'IK Weapon': "Immortal King's Stone Crusher",
    'IK Helm': "Immortal King's Will",
    'IK Belt': "Immortal King's Detail",
    'IK Boots': "Immortal King's Pillar",
    'IK Gloves': "Immortal King's Forge",
    "Immortal King's Armor": "Immortal King's Soul Cage",
    "Immortal King's Weapon": "Immortal King's Stone Crusher",
    "Immortal King's Helm": "Immortal King's Will",
    "Immortal King's Belt": "Immortal King's Detail",
    "Immortal King's Boots": "Immortal King's Pillar",
    "Immortal King's Gloves": "Immortal King's Forge",
    'KoD': 'Key of Destruction',
    'KoH': 'Key of Hate',
    'KoT': 'Key of Terror',
    'LoH': 'Laying of Hands',
    "M'avina's Bow": "M'avina's Caster",
    "M'avina's Armor": "M'avina's Embrace",
    "M'avina's Gloves": "M'avina's Icy Clutch",
    "M'avina's Belt": "M'avina's Tenet",
    "M'avina's Diadem": "M'avina's True Sight",
    "M'avina's Helm": "M'avina's True Sight",
    'Mahim Oak': 'The Mahim-Oak Curio',
    'Nagel Ring': 'Nagelring',
    'Occu': 'The Oculus',
    'Occy': 'The Oculus',
    "Que Hegan's Wisdom": "Que-Hegan's Wisdom",
    'RBF cold die': 'Rainbow Facet (Cold Die)',
    'RBF cold level up': 'Rainbow Facet (Cold Level Up)',
    'RBF fire die': 'Rainbow Facet (Fire Die)',
    'RBF fire level up': 'Rainbow Facet (Fire Level Up)',
    'RBF light die': 'Rainbow Facet (Light Die)',
    'RBF light level up': 'Rainbow Facet (Light Level Up)',
    'RBF poison die': 'Rainbow Facet (Poison Die)',
    'RBF poison level up': 'Rainbow Facet (Poison Level Up)',
    'Rainbow Facet cold die': 'Rainbow Facet (Cold Die)',
    'Rainbow Facet cold level up': 'Rainbow Facet (Cold Level Up)',
    'Rainbow Facet fire die': 'Rainbow Facet (Fire Die)',
    'Rainbow Facet fire level up': 'Rainbow Facet (Fire Level Up)',
    'Rainbow Facet light die': 'Rainbow Facet (Light Die)',
    'Rainbow Facet light level up': 'Rainbow Facet (Light Level Up)',
    'Rainbow Facet poison die': 'Rainbow Facet (Poison Die)',
    'Rainbow Facet poison level up': 'Rainbow Facet (Poison Level Up)',
    'Shako': 'Harlequin Crest',
    'SoE': 'String of Ears',
    'SoJ': 'Stone of Jordan',
    'SS': 'Stormshield',
    "Sigon's Armor": "Sigon's Shelter",
    "Sigon's Belt": "Sigon's Wrap",
    "Sigon's Boots": "Sigon's Sabot",
    "Sigon's Gloves": "Sigon's Gage",
    "Sigon's Helm": "Sigon's Visor",
    "Sigon's Shield": "Sigon's Guard",
    'Tkey': 'Key of Terror',
    'TGS': "Thundergod's Vigor",
    'TGods': "Thundergod's Vigor",
    'Tal Amu': "Tal Rasha's Adjudication",
    'Tal Armor': "Tal Rasha's Guardianship",
    'Tal Belt': "Tal Rasha's Fine Spun Cloth",
    'Tal Helm': "Tal Rasha's Horadric Crest",
    'Tal Orb': "Tal Rasha's Lidless Eye",
    'Tal Weapon': "Tal Rasha's Lidless Eye",
    "Tancred's Amu": "Tancred's Weird",
    'Trang Armor': "Trang-Oul's Scales",
    'Trang Belt': "Trang-Oul's Girth",
    'Trang Gloves': "Trang-Oul's Claws",
    'Trang Helm': "Trang-Oul's Guise",
    'Trang Shield': "Trang-Oul's Wing",
    'Vgaze': 'Vampire Gaze',
    'WForce': 'Windforce',
    'WTrav': 'War Traveler',
    'WWs': 'Waterwalk',
    'Wizzy': 'Wizardspike'
}

# PD2-only aliases (only active when PD2 mode is enabled)
ITEM_ALIASES_PD2 = {
    'BK death': "Bul-Kathos' Death Band",
    'wss': 'Worldstone Shard',
    'pbox': "Larzuk's Puzzlebox",
    'piece': "Larzuk's Puzzlepiece",
    'pes': 'Prime Evil Soul',
    'pde': 'Pure Demonic Essence'
}

# ============================================================================
# Functions
# ============================================================================

def get_base_item(row, pd2_mode=False):
    """Get the base item for a row, using PD2 Base item if PD2 mode is enabled
    
    Args:
        row: Dictionary row from CSV
        pd2_mode: If True and 'PD2 Base item' exists, use it; otherwise use 'Base Item'
    
    Returns:
        Base item string
    """
    if pd2_mode and row.get('PD2 Base item'):
        return row['PD2 Base item']
    return row.get('Base Item', '')


@lru_cache(maxsize=2)
def get_eth_item_set(pd2_mode=False):
    """Get the ethereal item set based on PD2 mode, dynamically generated from CSV
    
    Args:
        pd2_mode: If True, return items with eth_possible_pd2=True; otherwise return items with eth_possible=True
    
    Returns:
        Set of item names that can spawn as ethereal
    """
    items = set()
    
    # Read items from CSV
    with open(media_path + 'item_library.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Check appropriate column based on pd2_mode
            eth_column = 'eth_possible_pd2' if pd2_mode else 'eth_possible'
            if row.get(eth_column, '').upper() == 'TRUE':
                items.add(row['Item'])
    
    return items


@lru_cache(maxsize=2)
def get_no_unique_map(pd2_mode=False):
    """Get the NO_UNIQUE_MAP based on PD2 mode
    
    Args:
        pd2_mode: If True, return NO_UNIQUE_MAP_PD2; otherwise return NO_UNIQUE_MAP
    
    Returns:
        Dictionary mapping base item names to TC and Item Class
    """
    return NO_UNIQUE_MAP_PD2 if pd2_mode else NO_UNIQUE_MAP


@lru_cache(maxsize=2)
def get_item_aliases(pd2_mode=False):
    """Get item aliases based on PD2 mode
    
    Args:
        pd2_mode: If True, return merged ITEM_ALIASES and ITEM_ALIASES_PD2; otherwise return ITEM_ALIASES only
    
    Returns:
        Dictionary mapping alias names to item names
    """
    if pd2_mode:
        # Merge aliases with PD2 aliases (no overlap exists, but this is safe)
        return ITEM_ALIASES | ITEM_ALIASES_PD2
    return ITEM_ALIASES


@lru_cache(maxsize=2)
def get_full_item_list(pd2_mode=False):
    """Generate FULL_ITEM_LIST dynamically from CSV with lru_cache
    
    Args:
        pd2_mode: If True, include PD2 items
    
    Returns:
        Sorted list of item names
    """
    items = set()
    
    # Read items from CSV
    with open(media_path + 'item_library.csv', 'r', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            # Filter based on PD2 mode
            if not pd2_mode and row.get('PD2 item', '').upper() == 'TRUE':
                continue
            
            # Add item name
            items.add(row['Item'])
    
    # Add special vanilla items (keys)
    items.update(SPECIAL_VANILLA_ITEMS)
    
    # Add special PD2 items if PD2 mode
    if pd2_mode:
        items.update(SPECIAL_PD2_ITEMS)
    
    return sorted(list(items))


@lru_cache(maxsize=2)
def get_unid_item_list(pd2_mode=False):
    """Generate UNID_ITEM_LIST dynamically from CSV with lru_cache
    
    Args:
        pd2_mode: If True, include PD2 items and use PD2 base items where applicable
    
    Returns:
        Sorted list of unid item names (Base Item + (Rarity))
    """
    items = set()
    runes = set()
    
    # Read items from CSV and generate base item + rarity combinations
    with open(media_path + 'item_library.csv', 'r', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            # Filter based on PD2 mode
            if not pd2_mode and row.get('PD2 item', '').upper() == 'TRUE':
                continue
            
            item_group_0 = row.get('Item Group 0', '')
            rarity = row.get('Rarity', '').strip()
            
            # Extract runes directly from CSV
            if item_group_0 == 'Runes':
                runes.add(row['Item'])
            elif rarity in ('Unique', 'Set'):
                # Use get_base_item to handle PD2 mode correctly
                base_item = get_base_item(row, pd2_mode)
                if base_item:
                    items.add(f"{base_item} ({rarity})")
    
    # Add special hardcoded UNID items (Magic/Rare versions of selected items)
    items.update(UNID_SPECIAL_ITEMS)
    
    # Add runes
    items.update(runes)
    
    # Add keys (from SPECIAL_VANILLA_ITEMS)
    items.update(SPECIAL_VANILLA_ITEMS)
    
    # Add PD2-specific special items if PD2 mode
    if pd2_mode:
        items.update(UNID_PD2_SPECIAL_ITEMS)
        # Add special PD2 non-equipment items
        items.update(SPECIAL_PD2_ITEMS)
    
    return sorted(list(items))


@lru_cache(maxsize=1)
def _get_pd2_only_items():
    """Get set of PD2-only items (items in PD2 list but not in vanilla list)"""
    vanilla_items = set(get_full_item_list(pd2_mode=False))
    pd2_items = set(get_full_item_list(pd2_mode=True))
    return pd2_items - vanilla_items


def is_pd2_item(item_name):
    """Check if an item is PD2-only (not in vanilla item list)
    
    Args:
        item_name: Name of the item to check
    
    Returns:
        True if item is PD2-only, False otherwise
    """
    return item_name in _get_pd2_only_items()
