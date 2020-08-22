import requests
import json
from copy import deepcopy

api_page = 'http://d2-holy-grail.herokuapp.com/api/grail/'
default_data = {
    'sets': {'Angelic Raiment': {'Angelic Halo': {}, 'Angelic Mantle': {}, 'Angelic Sickle': {}, 'Angelic Wings': {}},
             "Arcanna's Tricks": {"Arcanna's Deathwand": {}, "Arcanna's Flesh": {}, "Arcanna's Head": {}, "Arcanna's Sign": {}},
             'Arctic Gear': {'Arctic Binding': {}, 'Arctic Furs': {}, 'Arctic Horn': {}, 'Arctic Mitts': {}},
             "Berserker's Arsenal": {"Berserker's Hatchet": {}, "Berserker's Hauberk": {}, "Berserker's Headgear": {}},
             "Cathan's Traps": {"Cathan's Mesh": {}, "Cathan's Rule": {}, "Cathan's Seal": {}, "Cathan's Sigil": {}, "Cathan's Visage": {}},
             "Civerb's Vestments": {"Civerb's Cudgel": {}, "Civerb's Icon": {}, "Civerb's Ward": {}},
             "Cleglaw's Brace": {"Cleglaw's Claw": {}, "Cleglaw's Pincers": {}, "Cleglaw's Tooth": {}},
             "Death's Disguise": {"Death's Guard": {}, "Death's Hand": {}, "Death's Touch": {}},
             "Hsaru's Defense": {"Hsarus' Iron Fist": {}, "Hsarus' Iron Heel": {}, "Hsarus' Iron Stay": {}},
             'Infernal Tools': {'Infernal Cranium': {}, 'Infernal Sign': {}, 'Infernal Torch': {}},
             "Iratha's Finery": {"Iratha's Coil": {}, "Iratha's Collar": {}, "Iratha's Cord": {}, "Iratha's Cuff": {}},
             "Isenhart's Armory": {"Isenhart's Case": {}, "Isenhart's Horns": {}, "Isenhart's Lightbrand": {}, "Isenhart's Parry": {}},
             "Milabrega's Regalia": {"Milabrega's Diadem": {}, "Milabrega's Orb": {}, "Milabrega's Robe": {}, "Milabrega's Rod": {}},
             "Sigon's Complete Steel": {"Sigon's Gage": {}, "Sigon's Guard": {}, "Sigon's Sabot": {}, "Sigon's Shelter": {}, "Sigon's Visor": {}, "Sigon's Wrap": {}},
             "Tancred's Battlegear": {"Tancred's Crowbill": {}, "Tancred's Hobnails": {}, "Tancred's Skull": {}, "Tancred's Spine": {}, "Tancred's Weird": {}},
             "Vidala's Rig": {"Vidala's Ambush": {}, "Vidala's Barb": {}, "Vidala's Fetlock": {}, "Vidala's Snare": {}},

             "Aldur's Watchtower": {"Aldur's Advance": {}, "Aldur's Deception": {}, "Aldur's Rhythm": {},  "Aldur's Stony Gaze": {}},
             "Bul-Kathos' Children": {"Bul-Kathos' Sacred Charge": {}, "Bul-Kathos' Tribal Guardian": {}},
             "Cow King's Leathers": {"Cow King's Hide": {}, "Cow King's Hooves": {}, "Cow King's Horns": {}},
             "Griswold's Legacy": {"Griswold's Heart": {}, "Griswold's Honor": {}, "Griswold's Redemption": {}, "Griswold's Valor": {}},
             "Heaven's Brethren": {"Dangoon's Teaching": {}, "Haemosu's Adamant": {}, "Ondal's Almighty": {}, "Taebaek's Glory": {}},
             "Hwanin's Majesty": {"Hwanin's Blessing": {}, "Hwanin's Justice": {}, "Hwanin's Refuge": {}, "Hwanin's Splendor": {}},
             'Immortal King': {"Immortal King's Detail": {}, "Immortal King's Forge": {}, "Immortal King's Pillar": {}, "Immortal King's Soul Cage": {}, "Immortal King's Stone Crusher": {}, "Immortal King's Will": {}},
             "M'avina's Battle Hymn": {"M'avina's Caster": {}, "M'avina's Embrace": {}, "M'avina's Icy Clutch": {}, "M'avina's Tenet": {}, "M'avina's True Sight": {}},
             "Naj's Ancient Vestige": {"Naj's Circlet": {}, "Naj's Light Plate": {}, "Naj's Puzzler": {}},
             "Natalya's Odium": {"Natalya's Mark": {}, "Natalya's Shadow": {}, "Natalya's Soul": {}, "Natalya's Totem": {}},
             "Orphan's Call": {"Guillaume's Face": {}, "Magnus' Skin": {}, "Whitstan's Guard": {}, "Wilhelm's Pride": {}},
             "Sander's Folly": {"Sander's Paragon": {}, "Sander's Riprap": {}, "Sander's Superstition": {}, "Sander's Taboo": {}},
             "Sazabi's Grand Tribute": {"Sazabi's Cobalt Redeemer": {}, "Sazabi's Ghost Liberator": {}, "Sazabi's Mental Sheath": {}},
             "Tal Rasha's Wrappings": {"Tal Rasha's Adjudication": {}, "Tal Rasha's Fine Spun Cloth": {}, "Tal Rasha's Guardianship": {}, "Tal Rasha's Horadric Crest": {}, "Tal Rasha's Lidless Eye": {}},
             'The Disciple': {'Credendum': {}, 'Dark Adherent': {}, 'Laying of Hands': {}, 'Rite of Passage': {}, 'Telling of Beads': {}},
             "Trang-Oul's Avatar": {"Trang-Oul's Claws": {}, "Trang-Oul's Girth": {}, "Trang-Oul's Guise": {}, "Trang-Oul's Scales": {}, "Trang-Oul's Wing": {}}},
    'uniques':
        {'armor':
             {'belts': {'normal': {'Bladebuckle': {}, 'Goldwrap': {}, 'Lenymo': {}, 'Nightsmoke': {}, 'Snakecord': {}},
                        'exceptional': {"Gloom's Trap": {}, 'Razortail': {}, 'Snowclash': {}, 'String of Ears': {}, "Thundergod's Vigor": {}},
                        'elite': {'Arachnid Mesh': {}, "Nosferatu's Coil": {}, "Verdungo's Hearty Cord": {}}},
              'boots': {'normal': {'Goblin Toe': {}, 'Gorefoot': {}, 'Hotspur': {}, 'Tearhaunch': {}, 'Treads of Cthon': {}},
                        'exceptional': {'Gore Rider': {}, 'Infernostride': {}, 'Silkweave': {}, 'War Traveler': {}, 'Waterwalk': {}},
                        'elite': {'Marrowwalk': {}, 'Sandstorm Trek': {}, 'Shadow Dancer': {}}},
              'chest': {'normal': {"Blinkbat's Form": {}, 'Boneflesh': {}, 'Darkglow': {}, 'Goldskin': {}, 'Greyform': {}, 'Hawkmail': {}, 'Heavenly Garb': {}, 'Iceblink': {}, 'Rattlecage': {}, 'Rockfleece': {}, 'Silks of the Victor': {}, 'Sparking Mail': {}, 'The Centurion': {}, 'Twitchthroe': {}, 'Venom Ward': {}},
                        'exceptional': {"Atma's Wail": {}, 'Black Hades': {}, 'Corpsemourn': {}, 'Crow Caw': {}, "Duriel's Shell": {}, 'Guardian Angel': {}, 'Iron Pelt': {}, "Que-Hegan's Wisdom": {}, 'Shaftstop': {}, 'Skin of the Flayed One': {}, 'Skin of the Vipermagi': {}, "Skullder's Ire": {}, 'Spirit Forge': {}, 'The Spirit Shroud': {}, 'Toothrow': {}},
                        'elite': {"Arkaine's Valor": {}, 'Leviathan': {}, "Ormus' Robes": {}, 'Steel Carapace': {}, "Templar's Might": {}, "The Gladiator's Bane": {}, "Tyrael's Might": {}}},
              'circlet': {'elite': {"Griffon's Eye": {}, "Kira's Guardian": {}}},
              'gloves': {'normal': {'Bloodfist': {}, 'Chance Guards': {}, 'Frostburn': {}, 'Magefist': {}, 'The Hand of Broc': {}},
                         'exceptional': {'Ghoulhide': {}, 'Gravepalm': {}, 'Hellmouth': {}, 'Lava Gout': {}, 'Venom Grip': {}},
                         'elite': {"Dracul's Grasp": {}, 'Soul Drainer': {}, 'Steelrend': {}}},
              'helm': {'normal': {"Biggin's Bonnet": {}, 'Coif of Glory': {}, 'Duskdeep': {}, 'Howltusk': {}, 'Tarnhelm': {}, 'The Face of Horror': {}, 'Undead Crown': {}, 'Wormskull': {}},
                       'exceptional': {"Blackhorn's Face": {}, 'Crown of Thieves': {}, 'Darksight Helm': {}, 'Peasant Crown': {}, 'Rockstopper': {}, 'Stealskull': {}, 'Valkyrie Wing': {}, 'Vampire Gaze': {}},
                       'elite': {"Andariel's Visage": {}, 'Crown of Ages': {}, 'Giant Skull': {}, 'Harlequin Crest': {}, "Nightwing's Veil": {}, 'Steel Shade': {}, 'Veil of Steel': {}}},
              'shields': {'normal': {'Bverrit Keep': {}, 'Pelta Lunata': {}, 'Steelclash': {}, 'Stormguild': {}, 'Swordback Hold': {}, 'The Ward': {}, 'Umbral Disk': {}, 'Wall of the Eyeless': {}},
                          'exceptional': {"Gerke's Sanctuary": {}, 'Lance Guard': {}, 'Lidless Wall': {}, "Moser's Blessed Circle": {}, "Radament's Sphere": {}, 'Stormchaser': {}, "Tiamat's Rebuke": {}, 'Visceratuant': {}},
                          'elite': {'Blackoak Shield': {}, "Head Hunter's Glory": {}, "Medusa's Gaze": {}, 'Spike Thorn': {}, 'Spirit Ward': {}, 'Stormshield': {}}}},
         'other':
             {'charms': {'all': {'Annihilus': {}, "Gheed's Fortune": {}, 'Hellfire Torch': {}}},
              'classes': {'amazon': {"Blood Raven's Charge": {}, "Lycander's Aim": {}, "Lycander's Flank": {}, 'Stoneraven': {}, 'Thunderstroke': {}, "Titan's Revenge": {}},
                          'assasin': {"Bartuc's Cut-Throat": {}, "Firelizard's Talons": {}, 'Jade Talon': {}, 'Shadow Killer': {}},
                          'barbarian': {"Arreat's Face": {}, "Demonhorn's Edge": {}, "Halaberd's Reign": {}, 'Wolfhowl': {}},
                          'druid': {"Cerebus' Bite": {}, "Jalal's Mane": {}, 'Ravenlore': {}, 'Spirit Keeper': {}},
                          'necromancer': {'Boneflame': {}, 'Darkforce Spawn': {}, 'Homunculus': {}},
                          'paladin': {'Alma Negra': {}, 'Dragonscale': {}, 'Herald of Zakarum': {}},
                          'sorceress': {"Death's Fathom": {}, "Eschuta's Temper": {}, 'The Oculus': {}}},
              'jewelry': {'amulets': {"Atma's Scarab": {}, 'Crescent Moon': {}, "Highlord's Wrath": {}, "Mara's Kaleidoscope": {}, 'Metalgrid': {}, 'Nokozan Relic': {}, "Saracen's Chance": {}, "Seraph's Hymn": {}, "The Cat's Eye": {}, 'The Eye of Etlich': {}, 'The Mahim-Oak Curio': {}, 'The Rising Sun': {}},
                          'rings': {"Bul-Kathos' Wedding Band": {}, 'Carrion Wind': {}, 'Dwarf Star': {}, 'Manald Heal': {}, 'Nagelring': {}, "Nature's Peace": {}, 'Raven Frost': {}, 'Stone of Jordan': {}, 'Wisp Projector': {}}},
              'rainbow facet (jewel)': {'die': {'Cold': {}, 'Fire': {}, 'Light': {}, 'Poison': {}},
                                        'level up': {'Cold': {}, 'Fire': {}, 'Light': {}, 'Poison': {}}}},
         'weapons':
             {'axe (1-h)': {'normal': {'Bladebone': {}, 'Deathspade': {}, 'Rakescar': {}, 'Skull Splitter': {}, 'The Gnasher': {}},
                            'exceptional': {"Butcher's Pupil": {}, 'Coldkill': {}, 'Guardian Naga': {}, 'Islestrike': {}, "Pompeii's Wrath": {}},
                            'elite': {'Cranebeak': {}, 'Death Cleaver': {}, "Razor's Edge": {}, 'Rune Master': {}}},
              'axe (2-h)': {'normal': {'Axe of Fechmar': {}, 'Brainhew': {}, 'Goreshovel': {}, 'Humongous': {}, 'The Chieftain': {}},
                            'exceptional': {'Boneslayer Blade': {}, 'Spellsteel': {}, 'Stormrider': {}, 'The Minotaur': {}, "Warlord's Trust": {}},
                            'elite': {'Ethereal Edge': {}, "Executioner's Justice": {}, 'Hellslayer': {}, "Messerschmidt's Reaver": {}}},
              'bow': {'normal': {'Blastbark': {}, 'Hellclap': {}, 'Pluckeye': {}, 'Raven Claw': {}, "Rogue's Bow": {}, 'Stormstrike': {}, 'Witherstring': {}, 'Wizendraw': {}},
                      'exceptional': {'Cliffkiller': {}, 'Endlesshail': {}, 'Goldstrike Arch': {}, 'Kuko Shakaku': {}, 'Magewrath': {}, 'Riphook': {}, 'Skystrike': {}, 'Witchwild String': {}},
                      'elite': {'Eaglehorn': {}, 'Widowmaker': {}, 'Windforce': {}}},
              'clubs (1-h)': {'normal': {'Bloodrise': {}, 'Crushflange': {}, 'Felloak': {}, 'Ironstone': {}, 'Stoutnail': {}, "The General's Tan Do Li Ga": {}},
                              'exceptional': {"Baezil's Vortex": {}, 'Dark Clan Crusher': {}, 'Earthshaker': {}, 'Fleshrender': {}, 'Moonfall': {}, 'Sureshrill Frost': {}},
                              'elite': {"Baranar's Star": {}, 'Demon Limb': {}, "Horizon's Tornado": {}, "Nord's Tenderizer": {}, "Schaefer's Hammer": {}, 'Stone Crusher': {}, 'Stormlash': {}}},
              'clubs (2-h)': {'normal': {'Bonesnap': {}, 'Steeldriver': {}},
                              'exceptional': {'Bloodtree Stump': {}, 'The Gavel of Pain': {}},
                              'elite': {'Earth Shifter': {}, 'The Cranium Basher': {}, 'Windhammer': {}},},
              'crossbow': {'normal': {'Doomslinger': {}, 'Hellcast': {}, 'Ichorsting': {}, 'Leadcrow': {}},
                           'exceptional': {'Buriza-Do Kyanon': {}, 'Demon Machine': {}, 'Langer Briser': {}, 'Pus Spitter': {}},
                           'elite': {'Gut Siphon': {}, 'Hellrack': {}}},
              'dagger': {'normal': {'Gull': {}, 'Spectral Shard': {}, 'The Diggler': {}, 'The Jade Tan Do': {}},
                         'exceptional': {"Blackbog's Sharp": {}, 'Heart Carver': {}, 'Spineripper': {}, 'Stormspike': {}},
                         'elite': {'Fleshripper': {}, 'Ghostflame': {}, 'Wizardspike': {}}},
              'polearms': {'normal': {"Dimoak's Hew": {}, 'Soul Harvest': {}, 'Steelgoad': {}, 'The Battlebranch': {}, 'The Grim Reaper': {}, 'Woestave': {}},
                           'exceptional': {"Athena's Wrath": {}, 'Blackleach Blade': {}, "Grim's Burning Dead": {}, 'Husoldal Evo': {}, 'Pierre Tombale Couant': {}, 'The Meat Scraper': {}},
                           'elite': {'Bonehew': {}, 'Stormspire': {}, "The Reaper's Toll": {}, 'Tomb Reaver': {}}},
              'scepters': {'normal': {'Knell Striker': {}, 'Rusthandle': {}, 'Stormeye': {}},
                           'exceptional': {'Hand of Blessed Light': {}, 'The Fetid Sprinkler': {}, "Zakarum's Hand": {}},
                           'elite': {"Astreon's Iron Ward": {}, "Heaven's Light": {}, 'The Redeemer': {}}},
              'spears': {'normal': {'Bloodthief': {}, 'Lance of Yaggai': {}, 'Razortine': {}, 'The Dragon Chang': {}, 'The Tannr Gorerod': {}},
                         'exceptional': {'Hone Sundan': {}, 'Kelpie Snare': {}, 'Soulfeast Tine': {}, 'Spire of Honor': {}, 'The Impaler': {}},
                         'elite': {"Arioc's Needle": {}, 'Steel Pillar': {}, 'Viperfork': {}}},
              'staves': {'normal': {'Bane Ash': {}, 'Serpent Lord': {}, 'Spire of Lazarus': {}, 'The Iron Jang Bong': {}, 'The Salamander': {}},
                         'exceptional': {'Chromatic Ire': {}, 'Razorswitch': {}, 'Ribcracker': {}, 'Skull Collector': {}, 'Warpspear': {}},
                         'elite': {"Mang Song's Lesson": {}, "Ondal's Wisdom": {}}},
              'swords (1-h)': {'normal': {'Blood Crescent': {}, "Culwen's Point": {}, 'Gleamscythe': {}, "Griswold's Edge": {}, 'Hellplague': {}, "Rixot's Keen": {}, 'Skewer of Krintiz': {}},
                               'exceptional': {'Blade of Ali Baba': {}, 'Bloodletter': {}, 'Coldsteel Eye': {}, "Ginther's Rift": {}, 'Headstriker': {}, 'Hexfire': {}, 'Plague Bearer': {}, 'The Atlantean': {}},
                               'elite': {'Azurewrath': {}, 'Bloodmoon': {}, 'Djinn Slayer': {}, 'Frostwind': {}, 'Lightsabre': {}}},
              'swords (2-h)': {'normal': {'Blacktongue': {}, "Kinemil's Awl": {}, 'Ripsaw': {}, 'Shadowfang': {}, 'Soulflay': {}, 'The Patriarch': {}},
                               'exceptional': {'Bing Sz Wang': {}, 'Cloudcrack': {}, 'Crainte Vomir': {}, 'Swordguard': {}, 'The Vile Husk': {}, 'Todesfaelle Flamme': {}},
                               'elite': {'Doombringer': {}, 'Flamebellow': {}, 'The Grandfather': {}}},
              'throwing': {'exceptional': {'Deathbit': {}, 'The Scalper': {}},
                           'elite': {"Demon's Arch": {}, "Gargoyle's Bite": {}, 'Gimmershred': {}, 'Lacerator': {}, 'Warshrike': {}, 'Wraith Flight': {}}},
              'wands': {'normal': {'Gravenspine': {}, 'Maelstrom': {}, 'Torch of Iro': {}, "Ume's Lament": {}},
                        'exceptional': {'Arm of King Leoric': {}, 'Blackhand Key': {}, 'Carin Shard': {}, 'Suicide Branch': {}},
                        'elite': {'Boneshade': {}, "Death's Web": {}}}}}}


def get_grail(uid, proxies=None):
    try:
        req = requests.get(url=api_page + uid, proxies=proxies)
    except Exception as e:
        raise e
    req.raise_for_status()
    return req.json()


def update_grail_dict(dct, item_upg_dict):
    def update_items(dct, item_upg_dict):
        if not item_upg_dict:
            return dct
        for k, v in dct.items():
            if k in item_upg_dict:
                dct[k] = {'wasFound': item_upg_dict.pop(k)}
            elif isinstance(v, dict):
                dct[k] = update_items(v, item_upg_dict)
        return dct

    if 'data' not in dct:
        raise KeyError("This is a blank holy grail profile, and cannot be modified before you have checked at least one item through the webpage UI.")

    # Holy grail app handles rainbow facets in a non-standard way compared to all other items, need to align with API as
    # well
    for key in list(item_upg_dict.keys()):
        if key.startswith('Rainbow Facet'):
            rbf = key.replace('(', '').replace(')', '').split(' ')
            dmg_type = rbf[2]
            activate_type = rbf[3]
            dct['data']['uniques']['other']['rainbow facet (jewel)'][activate_type.lower()][dmg_type.lower()] = {'wasFound': item_upg_dict.pop(key)}

    dct['data'] = update_items(deepcopy(dct['data']), item_upg_dict)
    return dct


def put_grail(uid, pwd, data, proxies=None):
    data['password'] = pwd
    data['grail'] = data['data']
    del data['data']

    try:
        req = requests.put(url=api_page + uid, data=json.dumps(data), headers={"Content-Type": "application/json"}, proxies=proxies)
    except Exception as e:
        raise e
    req.raise_for_status()
    return req.status_code


if __name__ == '__main__':
    p_addresses = None
    username = input('username')
    password = input('password')
    grail = get_grail(uid=username, proxies=p_addresses)
    updated_grail = update_grail_dict(dct=grail, item_upg_dict={'Stormshield': False, 'Shadow Dancer': False})
    put_grail(uid=username, pwd=password, data=updated_grail, proxies=p_addresses)
