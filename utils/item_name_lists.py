"""Item name lists and mappings for autocompletion and grail logic"""
from functools import lru_cache
import csv
from init import assets_path


# ============================================================================
# Constants
# ============================================================================

# Special items are now in the CSV (Item Group 0='Misc', Item Group 1='Special')

# Base items for UNID mode that could be interesting to include (Magic/Rare versions generated dynamically)
INTESTING_MAGIC_RARE_BASES = [
    # Selected tc81
    "Spired Helm", "Cryptic Axe",
    
    # TC84/87 with unique/set counterparts
    "Archon Staff", "Berserker Axe", "Bloodlord Skull", "Bone Visage",
    "Caduceus", "Champion Axe", "Colossus Blade", "Corona", "Cryptic Sword",
    "Demon Crossbow", "Diadem", "Dimensional Shard", "Fanged Knife",
    "Giant Thresher", "Glorious Axe", "Hydra Bow", "Lacquered Plate",
    "Legend Spike", "Legendary Mallet", "Myrmidon Greaves", "Mythical Sword",
    "Ogre Gauntlets", "Sacred Armor", "Scissors Suwayyah", "Shadow Plate",
    "Sky Spirit", "Thunder Maul", "Troll Belt", "Unearthed Wand",
    "Vortex Shield", "War Pike", "Ward", "Winged Harpoon", "Zakarum Shield",
    
    # Misc
    "Grand Charm", "Large Charm", "Small Charm", "Jewel",
    
    # TC84 with no set/unique
    "Archon Plate", "Ghost Spear", "Shillelagh", "Vortex Orb", "Great Poleaxe",
    
    # TC87 with no set/unique
    "Colossus Girdle", "Dream Spirit", "Guardian Crown",
    
    # Circlet types
    "Circlet", "Tiara", "Coronet", "Diadem",
    
    # Other items requested by the CHOSEN Juan
    "Sacred Rondache", "Sacred Targe", "Kurast Shield", "Colossus Sword", "Monarch",
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


# Fixed item names when copying from clipboard in PD2
FIX_ITEM_NAMES = {
    "Aidans Scar": "Aidan's Scar",
    "Akarats Devotion": "Akarat's Devotion",
    "Aldur's Gauntlet": "Aldur's Rhythm",
    "Armageddon Blade": "Armageddon's Blade",
    "Asylum Staff": "Asylum",
    "Blinkbats Form": "Blinkbat's Form",
    "Bloodraven's Charge": "Blood Raven's Charge",
    "Bonesob": "Bonesnap",
    "Bul Katho's Wedding Band": "Bul-Kathos' Wedding Band",
    "Cerebus": "Cerebus' Bite",
    "Class Specific": "Class-specific",
    "Constricting Ring": "Constricting Loop",
    "Cow King's Hoofs": "Cow King's Hooves",
    "Culwens Point": "Culwen's Point",
    "Cutthroat1": "Bartuc's Cut-Throat",
    "Darkforge Spawn": "Darkforce Spawn",
    "Dclone Trophy": "Diablo Clone Trophy Season 4 Enlightenment",
    "Deathcleaver": "Death Cleaver",
    "Deaths's Web": "Death's Web",
    "Demonlimb": "Demon Limb",
    "Dev Charm": "Developers Bag Of Tricks",
    "Dimoaks Hew": "Dimoak's Hew",
    "Djinnslayer": "Djinn Slayer",
    "Doomspittle": "Doomslinger",
    "Earthshifter": "Earth Shifter",
    "Echo Quiver": "Echo",
    "Echo Weapon": "Echo",
    "Eschuta's temper": "Eschuta's Temper",
    "Fallen Gardens Map": "Fallen Gardens",
    "Fathom": "Death's Fathom",
    "Fechmars Axe": "Axe of Fechmar",
    "Giantskull": "Giant Skull",
    "Gloomstrap": "Gloom's Trap",
    "Godstrike Arch": "Goldstrike Arch",
    "Gorerider": "Gore Rider",
    "Griswolds Edge": "Griswold's Edge",
    "Griswolds's Redemption": "Griswold's Redemption",
    "Gutsiphon": "Gut Siphon",
    "Hadriels Hand": "Hadriel's Hand",
    "Haemosu's Adament": "Haemosu's Adamant",
    "Headhunter's Glory": "Head Hunter's Glory",
    "Heaven's Taebaek": "Taebaek's Glory",
    "Hwanin's Seal": "Hwanin's Blessing",
    "Imperial Palace Map": "Imperial Palace",
    "Irices Shard": "Spectral Shard",
    "Ironpelt": "Iron Pelt",
    "Ironward": "Astreon's Iron Ward",
    "Iros Torch": "Torch of Iro",
    "Itheraels Path": "Itherael's Path",
    "Jadetalon": "Jade Talon",
    "Kalans Legacy": "Kalan's Legacy",
    "Kerke's Sanctuary": "Gerke's Sanctuary",
    "KhalimFlail": "Khalim's Flail",
    "Kinemils Awl": "Kinemil's Awl",
    "Krintizs Skewer": "Skewer of Krintiz",
    "Lavagout": "Lava Gout",
    "Lazarus Spire": "Spire of Lazarus",
    "Lenyms Cord": "Lenymo",
    "Leoric's Mithril Blade": "Leoric's Mithril Bane",
    "Loyalty Bow": "Loyalty",
    "Loyalty Spear": "Loyalty",
    "Maelstromwrath": "Maelstrom",
    "Martyr": "Martyrdom",
    "Maxlevel Trophy": "Level 99 Trophy Season 4 Enlightenment",
    "McAuley's Paragon": "Sander's Paragon",
    "McAuley's Riprap": "Sander's Riprap",
    "McAuley's Superstition": "Sander's Superstition",
    "McAuley's Taboo": "Sander's Taboo",
    "Merman's Speed": "Merman's Sprocket",
    "Mindrend": "Skull Splitter",
    "Mirror Shield": "Twilight's Reflection",
    "Mosers Blessed Circle": "Moser's Blessed Circle",
    "Neophyte2": "Neophyte",
    "Nethercrow": "Kadala's Heirloom",
    "Nightmares Feast": "Ursa's Nightmare",
    "Outer Void Map": "Outer Void",
    "Overlords Helm": "Overlord's Helm",
    "Peasent Crown": "Peasant Crown",
    "Phoenix Staff": "Phoenix",
    "Piercerib": "Rogue's Bow",
    "Pompe's Wrath": "Pompeii's Wrath",
    "Pullspite": "Stormstrike",
    "Pus Spiter": "Pus Spitter",
    "Que-Hegan's Wisdon": "Que-Hegan's Wisdom",
    "Radimant's Sphere": "Radament's Sphere",
    "Raekors Virtue": "Raekor's Virtue",
    "Rathma Trophy": "Rathma Trophy Season 4 Enlightenment",
    "Razoredge": "Razor's Edge",
    "Rimeraven": "Raven Claw",
    "Rixots Keen": "Rixot's Keen",
    "Runemaster": "Rune Master",
    "Runeword1": "Ancients' Pledge",
    "Runeword10": "Brand",
    "Runeword100": "Penitence",
    "Runeword101": "Peril",
    "Runeword102": "Pestilence",
    "Runeword103": "Phoenix",
    "Runeword104": "Piety",
    "Runeword105": "Pillar of Faith",
    "Runeword106": "Plague",
    "Runeword107": "Praise",
    "Runeword108": "Prayer",
    "Runeword109": "Pride",
    "Runeword11": "Breath of the Dying",
    "Runeword110": "Principle",
    "Runeword111": "Prowess in Battle",
    "Runeword112": "Prudence",
    "Runeword113": "Punishment",
    "Runeword114": "Purity",
    "Runeword115": "Question",
    "Runeword116": "Radiance",
    "Runeword117": "Rain",
    "Runeword118": "Reason",
    "Runeword119": "Red",
    "Runeword12": "Broken Promise",
    "Runeword120": "Rhyme",
    "Runeword121": "Rift",
    "Runeword122": "Sanctuary",
    "Runeword123": "Serendipity",
    "Runeword124": "Shadow",
    "Runeword125": "Shadow of Doubt",
    "Runeword126": "Silence",
    "Runeword127": "Siren's Song",
    "Runeword128": "Smoke",
    "Runeword129": "Sorrow",
    "Runeword13": "Call to Arms",
    "Runeword130": "Spirit",
    "Runeword131": "Splendor",
    "Runeword132": "Starlight",
    "Runeword133": "Stealth",
    "Runeword134": "Steel",
    "Runeword135": "Still Water",
    "Runeword136": "Sting",
    "Runeword137": "Stone",
    "Runeword138": "Storm",
    "Runeword139": "Strength",
    "Runeword14": "Chains of Honor",
    "Runeword140": "Tempest",
    "Runeword141": "Temptation",
    "Runeword142": "Terror",
    "Runeword143": "Thirst",
    "Runeword144": "Thought",
    "Runeword145": "Thunder",
    "Runeword146": "Time",
    "Runeword147": "Tradition",
    "Runeword148": "Treachery",
    "Runeword149": "Trust",
    "Runeword15": "Chance",
    "Runeword150": "Truth",
    "Runeword151": "Unbending Will",
    "Runeword152": "Valor",
    "Runeword153": "Vengeance",
    "Runeword154": "Venom",
    "Runeword155": "Victory",
    "Runeword156": "Voice",
    "Runeword157": "Void",
    "Runeword158": "War",
    "Runeword159": "Water",
    "Runeword16": "Chaos",
    "Runeword160": "Wealth",
    "Runeword161": "Whisper",
    "Runeword162": "White",
    "Runeword163": "Wind",
    "Runeword164": "Wings of Hope",
    "Runeword165": "Wisdom",
    "Runeword166": "Woe",
    "Runeword167": "Wonder",
    "Runeword168": "Wrath",
    "Runeword169": "Youth",
    "Runeword17": "Crescent Moon",
    "Runeword170": "Zephyr",
    "Runeword171": "Dominion",
    "Runeword18": "Darkness",
    "Runeword19": "Daylight",
    "Runeword2": "Armageddon",
    "Runeword20": "Death",
    "Runeword21": "Deception",
    "Runeword22": "Delirium",
    "Runeword23": "Desire",
    "Runeword24": "Despair",
    "Runeword25": "Destruction",
    "Runeword26": "Doom",
    "Runeword27": "Dragon",
    "Runeword28": "Dread",
    "Runeword29": "Dream",
    "Runeword3": "Authority",
    "Runeword30": "Duress",
    "Runeword31": "Edge",
    "Runeword32": "Elation",
    "Runeword33": "Enigma",
    "Runeword34": "Enlightenment",
    "Runeword35": "Envy",
    "Runeword36": "Eternity",
    "Runeword37": "Exile",
    "Runeword38": "Faith",
    "Runeword39": "Famine",
    "Runeword4": "Beast",
    "Runeword40": "Flickering Flame",
    "Runeword41": "Fortitude",
    "Runeword42": "Fortune",
    "Runeword43": "Friendship",
    "Runeword44": "Fury",
    "Runeword45": "Gloom",
    "Runeword46": "Glory",
    "Runeword47": "Grief",
    "Runeword48": "Hand of Justice",
    "Runeword49": "Harmony",
    "Runeword5": "Beauty",
    "Runeword50": "Hatred",
    "Runeword51": "Heart of the Oak",
    "Runeword52": "Heaven's Will",
    "Runeword53": "Holy Tears",
    "Runeword54": "Holy Thunder",
    "Runeword55": "Honor",
    "Runeword56": "Revenge",
    "Runeword57": "Humility",
    "Runeword58": "Hunger",
    "Runeword59": "Ice",
    "Runeword6": "Black",
    "Runeword60": "Infinity",
    "Runeword61": "Innocence",
    "Runeword62": "Insight",
    "Runeword63": "Jealousy",
    "Runeword64": "Judgement",
    "Runeword65": "King's Grace",
    "Runeword66": "Kingslayer",
    "Runeword67": "Knight's Vigil",
    "Runeword68": "Knowledge",
    "Runeword69": "Last Wish",
    "Runeword7": "Blood",
    "Runeword70": "Law",
    "Runeword71": "Lawbringer",
    "Runeword72": "Leaf",
    "Runeword73": "Lightning",
    "Runeword74": "Lionheart",
    "Runeword75": "Lore",
    "Runeword76": "Love",
    "Runeword78": "Lust",
    "Runeword79": "Madness",
    "Runeword8": "Bone",
    "Runeword81": "Malice",
    "Runeword82": "Melody",
    "Runeword83": "Memory",
    "Runeword84": "Mist",
    "Runeword85": "Morning",
    "Runeword86": "Mystery",
    "Runeword87": "Myth",
    "Runeword88": "Nadir",
    "Runeword89": "Nature's Kingdom",
    "Runeword9": "Bramble",
    "Runeword90": "Night",
    "Runeword91": "Oath",
    "Runeword92": "Obedience",
    "Runeword93": "Oblivion",
    "Runeword94": "Obsession",
    "Runeword95": "Passion",
    "Runeword97": "Pattern",
    "Runeword98": "Peace",
    "Runeword99": "Voice of Reason",
    "Shadowdancer": "Shadow Dancer",
    "Shadowkiller": "Shadow Killer",
    "Sigurd's Staunch": "Siggard's Staunch",
    "Skin of the Flayerd One": "Skin of the Flayed One",
    "Skullcollector": "Skull Collector",
    "Souldrain": "Soul Drainer",
    "Spiritforge": "Spirit Forge",
    "Spiritkeeper": "Spirit Keeper",
    "Spiritual Custodian": "Dark Adherent",
    "Stalkers Cull": "Stalker's Cull",
    "Steel Carapice": "Steel Carapace",
    "Steelpillar": "Steel Pillar",
    "Steelshade": "Steel Shade",
    "SuperKhalimFlail": "Khalim's Will",
    "Tal Rasha's Fire-Spun Cloth": "Tal Rasha's Fine-Spun Cloth",
    "Tal Rasha's Howling Wind": "Tal Rasha's Guardianship",
    "The Atlantian": "The Atlantean",
    "The Chieftan": "The Chieftain",
    "The Generals Tan Do Li Ga": "The General's Tan Do Li Ga",
    "The Humongous": "Humongous",
    "The Minataur": "The Minotaur",
    "The Reedeemer": "The Redeemer",
    "Thudergod's Vigor": "Thundergod's Vigor",
    "Titangrip": "Titan's Grip",
    "Umes Lament": "Ume's Lament",
    "Ureh City Map": "City of Ureh",
    "Valkiry Wing": "Valkyrie Wing",
    "Vampiregaze": "Vampire Gaze",
    "Venomsward": "Venom Ward",
    "Verdugo's Hearty Cord": "Verdungo's Hearty Cord",
    "Victors Silk": "Silks of the Victor",
    "War Bonnet": "Biggin's Bonnet",
    "Warlord of Blood Map": "Warlord of Blood",
    "Wartraveler": "War Traveler",
    "Whichwild String": "Witchwild String",
    "Wihtstan's Guard": "Whitstan's Guard",
    "Wind Staff": "Wind",
    "Wind Throwable": "Wind",
    "Wisp": "Wisp Projector",
    "Wraithflight": "Wraith Flight",
    "Zeraes Resolve": "Zerae's Resolve",
    "Zhar the Mad Map": "Zhar's Sanctum",
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
    with open(assets_path + 'item_library.csv', 'r', encoding='utf-8') as f:
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
    with open(assets_path + 'item_library.csv', 'r', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            # Filter based on PD2 mode
            if not pd2_mode and row.get('PD2 item', '').upper() == 'TRUE':
                continue
            
            # Add item name
            items.add(row['Item'])
    
    
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
    with open(assets_path + 'item_library.csv', 'r', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            # Filter based on PD2 mode
            if not pd2_mode and row.get('PD2 item', '').upper() == 'TRUE':
                continue
            
            item_group_0 = row.get('Item Group 0', '')
            item_group_1 = row.get('Item Group 1', '')
            rarity = row.get('Rarity', '').strip()
            
            # Extract runes directly from CSV (Item Group 0='Misc', Item Group 1='Low Runes'/'Middle Runes'/'High Runes')
            if item_group_0 == 'Misc' and item_group_1 in ('Low Runes', 'Middle Runes', 'High Runes'):
                runes.add(row['Item'])
            elif rarity in ('Unique', 'Set'):
                # Use get_base_item to handle PD2 mode correctly
                base_item = get_base_item(row, pd2_mode)
                if base_item:
                    items.add(f"{base_item} ({rarity})")
    
    # Generate Magic/Rare versions of special UNID items
    for base_item in INTESTING_MAGIC_RARE_BASES:
        items.add(f"{base_item} (Magic)")
        # Charms cannot be Rare, only Magic
        if base_item not in {"Grand Charm", "Large Charm", "Small Charm"}:
            items.add(f"{base_item} (Rare)")
    
    # Add runes
    items.update(runes)
    
    # Add PD2-specific special items if PD2 mode
    if pd2_mode:
        items.update(UNID_PD2_SPECIAL_ITEMS)
    
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


def get_fixed_item_name(item_name):
    """Get the fixed item name for a given item name"""
    return FIX_ITEM_NAMES.get(item_name, item_name)