import requests
import json
from copy import deepcopy

api_page = 'http://d2-holy-grail.herokuapp.com/api/grail/'
default_data = {
    'uniques': {
        'armor': {
            'chest': {'normal': {'Greyform': {}, "Blinkbat's Form": {}, 'The Centurion': {}, 'Twitchthroe': {}, 'Darkglow': {}, 'Hawkmail': {}, 'Venom Ward': {}, 'Sparking Mail': {}, 'Iceblink': {}, 'Heavenly Garb': {}, 'Rockfleece': {}, 'Boneflesh': {}, 'Rattlecage': {}, 'Goldskin': {}, 'Silks of the Victor': {}},
                      'exceptional': {'The Spirit Shroud': {}, 'Skin of the Vipermagi': {}, 'Skin of the Flayed One': {}, 'Iron Pelt': {}, 'Crow Caw': {}, 'Spirit Forge': {}, "Duriel's Shell": {}, 'Shaftstop': {}, "Skullder's Ire": {}, "Que-Hegan's Wisdom": {}, 'Toothrow': {}, 'Guardian Angel': {}, "Atma's Wail": {}, 'Black Hades': {}, 'Corpsemourn': {}},
                      'elite': {"Ormus' Robes": {}, "The Gladiator's Bane": {}, "Arkaine's Valor": {}, 'Leviathan': {}, 'Steel Carapace': {}, "Templar's Might": {}, "Tyrael's Might": {}}},
            'helm': {'normal': {"Biggin's Bonnet": {}, 'Tarnhelm': {}, 'Coif of Glory': {}, 'Duskdeep': {}, 'Wormskull': {}, 'Howltusk': {}, 'Undead Crown': {}, 'The Face of Horror': {}},
                     'exceptional': {'Peasant Crown': {}, 'Rockstopper': {}, 'Stealskull': {}, 'Darksight Helm': {}, 'Vampire Gaze': {}, 'Valkyrie Wing': {}, 'Crown of Thieves': {}, "Blackhorn's Face": {}},
                     'elite': {"Andariel's Visage": {}, 'Crown of Ages': {}, 'Giant Skull': {}, 'Harlequin Crest': {}, "Nightwing's Veil": {}, 'Steel Shade': {}, 'Veil of Steel': {}}},
            'circlet': {'elite': {"Kira's Guardian": {}, "Griffon's Eye": {}}},
            'gloves': {'normal': {'The Hand of Broc': {}, 'Bloodfist': {}, 'Chance Guards': {}, 'Magefist': {}, 'Frostburn': {}},
                       'exceptional': {'Venom Grip': {}, 'Gravepalm': {}, 'Ghoulhide': {}, 'Lava Gout': {}, 'Hellmouth': {}},
                       'elite': {"Dracul's Grasp": {}, 'Soul Drainer': {}, 'Steelrend': {}}},
            'belts': {'normal': {'Lenymo': {}, 'Snakecord': {}, 'Nightsmoke': {}, 'Goldwrap': {}, 'Bladebuckle': {}},
                      'exceptional': {'String of Ears': {}, 'Razortail': {}, "Gloom's Trap": {}, 'Snowclash': {}, "Thundergod's Vigor": {}},
                      'elite': {'Arachnid Mesh': {}, "Nosferatu's Coil": {}, "Verdungo's Hearty Cord": {}}},
            'boots': {'normal': {'Hotspur': {}, 'Gorefoot': {}, 'Treads of Cthon': {}, 'Goblin Toe': {}, 'Tearhaunch': {}},
                      'exceptional': {'Infernostride': {}, 'Waterwalk': {}, 'Silkweave': {}, 'War Traveler': {}, 'Gore Rider': {}},
                      'elite': {'Marrowwalk': {}, 'Sandstorm Trek': {}, 'Shadow Dancer': {}}},
            'shields': {'normal': {'Pelta Lunata': {}, 'Umbral Disk': {}, 'Stormguild': {}, 'Swordback Hold': {}, 'Steelclash': {}, 'Wall of the Eyeless': {}, 'Bverrit Keep': {}, 'The Ward': {}},
                        'exceptional': {'Visceratuant': {}, "Moser's Blessed Circle": {}, 'Stormchaser': {}, 'Lance Guard': {}, "Tiamat's Rebuke": {}, 'Lidless Wall': {}, "Gerke's Sanctuary": {}, "Radament's Sphere": {}},
                        'elite': {'Blackoak Shield': {}, 'Stormshield': {}, "Head Hunter's Glory": {}, "Medusa's Gaze": {}, 'Spike Thorn': {}, 'Spirit Ward': {}}}},
        'weapons': {'axe (1-h)': {'normal': {'The Gnasher': {}, 'Deathspade': {}, 'Bladebone': {}, 'Skull Splitter': {}, 'Rakescar': {}},
                                  'exceptional': {'Coldkill': {}, "Butcher's Pupil": {}, 'Islestrike': {}, "Pompeii's Wrath": {}, 'Guardian Naga': {}},
                                  'elite': {"Razor's Edge": {}, 'Rune Master': {}, 'Cranebeak': {}, 'Death Cleaver': {}}},
                    'axe (2-h)': {'normal': {'Axe of Fechmar': {}, 'Goreshovel': {}, 'The Chieftain': {}, 'Brainhew': {}, 'Humongous': {}},
                                  'exceptional': {"Warlord's Trust": {}, 'Spellsteel': {}, 'Stormrider': {}, 'Boneslayer Blade': {}, 'The Minotaur': {}},
                                  'elite': {'Ethereal Edge': {}, 'Hellslayer': {}, "Messerschmidt's Reaver": {}, "Executioner's Justice": {}}},
                    'bow': {'normal': {'Pluckeye': {}, 'Witherstring': {}, 'Raven Claw': {}, "Rogue's Bow": {}, 'Stormstrike': {}, 'Wizendraw': {}, 'Hellclap': {}, 'Blastbark': {}},
                            'exceptional': {'Skystrike': {}, 'Riphook': {}, 'Kuko Shakaku': {}, 'Endlesshail': {}, 'Witchwild String': {}, 'Cliffkiller': {}, 'Magewrath': {}, 'Goldstrike Arch': {}},
                            'elite': {'Widowmaker': {}, 'Eaglehorn': {}, 'Windforce': {}}},
                    'crossbow': {'normal': {'Leadcrow': {}, 'Ichorsting': {}, 'Hellcast': {}, 'Doomslinger': {}},
                                 'exceptional': {'Langer Briser': {}, 'Pus Spitter': {}, 'Buriza-Do Kyanon': {}, 'Demon Machine': {}},
                                 'elite': {'Gut Siphon': {}, 'Hellrack': {}}},
                    'dagger': {'normal': {'Gull': {}, 'The Diggler': {}, 'The Jade Tan Do': {}, 'Spectral Shard': {}},
                               'exceptional': {'Spineripper': {}, 'Heart Carver': {}, "Blackbog's Sharp": {}, 'Stormspike': {}},
                               'elite': {'Fleshripper': {}, 'Ghostflame': {}, 'Wizardspike': {}}},
                    'clubs (1-h)': {'normal': {'Felloak': {}, 'Stoutnail': {}, 'Crushflange': {}, 'Bloodrise': {}, "The General's Tan Do Li Ga": {}, 'Ironstone': {}},
                                    'exceptional': {'Dark Clan Crusher': {}, 'Fleshrender': {}, 'Sureshrill Frost': {}, 'Moonfall': {}, "Baezil's Vortex": {}, 'Earthshaker': {}},
                                    'elite': {"Nord's Tenderizer": {}, "Baranar's Star": {}, 'Demon Limb': {}, 'Stormlash': {}, "Horizon's Tornado": {}, 'Stone Crusher': {}, "Schaefer's Hammer": {}}},
                    'clubs (2-h)': {'normal': {'Bonesnap': {}, 'Steeldriver': {}},
                                    'exceptional': {'Bloodtree Stump': {}, 'The Gavel of Pain': {}},
                                    'elite': {'Windhammer': {}, 'Earth Shifter': {}, 'The Cranium Basher': {}}},
                    'polearms': {'normal': {"Dimoak's Hew": {}, 'Steelgoad': {}, 'Soul Harvest': {}, 'The Battlebranch': {}, 'Woestave': {}, 'The Grim Reaper': {}},
                                 'exceptional': {'The Meat Scraper': {}, 'Blackleach Blade': {}, "Athena's Wrath": {}, 'Pierre Tombale Couant': {}, 'Husoldal Evo': {}, "Grim's Burning Dead": {}},
                                 'elite': {'Bonehew': {}, "The Reaper's Toll": {}, 'Tomb Reaver': {}, 'Stormspire': {}}},
                    'scepters': {'normal': {'Knell Striker': {}, 'Rusthandle': {}, 'Stormeye': {}},
                                 'exceptional': {"Zakarum's Hand": {}, 'The Fetid Sprinkler': {}, 'Hand of Blessed Light': {}},
                                 'elite': {"Astreon's Iron Ward": {}, "Heaven's Light": {}, 'The Redeemer': {}}},
                    'spears': {'normal': {'The Dragon Chang': {}, 'Razortine': {}, 'Bloodthief': {}, 'Lance of Yaggai': {}, 'The Tannr Gorerod': {}},
                               'exceptional': {'The Impaler': {}, 'Kelpie Snare': {}, 'Soulfeast Tine': {}, 'Hone Sundan': {}, 'Spire of Honor': {}},
                               'elite': {"Arioc's Needle": {}, 'Steel Pillar': {}, 'Viperfork': {}}},
                    'staves': {'normal': {'Bane Ash': {}, 'Serpent Lord': {}, 'Spire of Lazarus': {}, 'The Salamander': {}, 'The Iron Jang Bong': {}},
                               'exceptional': {'Razorswitch': {}, 'Ribcracker': {}, 'Chromatic Ire': {}, 'Warpspear': {}, 'Skull Collector': {}},
                               'elite': {"Mang Song's Lesson": {}, "Ondal's Wisdom": {}}},
                    'swords (1-h)': {'normal': {"Rixot's Keen": {}, 'Blood Crescent': {}, 'Skewer of Krintiz': {}, 'Gleamscythe': {}, "Griswold's Edge": {}, 'Hellplague': {}, "Culwen's Point": {}},
                                     'exceptional': {'Bloodletter': {}, 'Coldsteel Eye': {}, 'Hexfire': {}, 'Blade of Ali Baba': {}, "Ginther's Rift": {}, 'Headstriker': {}, 'Plague Bearer': {}, 'The Atlantean': {}},
                                     'elite': {'Azurewrath': {}, 'Bloodmoon': {}, 'Djinn Slayer': {}, 'Frostwind': {}, 'Lightsabre': {}}},
                    'swords (2-h)': {'normal': {'Shadowfang': {}, 'Soulflay': {}, "Kinemil's Awl": {}, 'Blacktongue': {}, 'Ripsaw': {}, 'The Patriarch': {}},
                                     'exceptional': {'Crainte Vomir': {}, 'Bing Sz Wang': {}, 'The Vile Husk': {}, 'Cloudcrack': {}, 'Todesfaelle Flamme': {}, 'Swordguard': {}},
                                     'elite': {'Flamebellow': {}, 'Doombringer': {}, 'The Grandfather': {}}},
                    'wands': {'normal': {'Torch of Iro': {}, 'Maelstrom': {}, 'Gravenspine': {}, "Ume's Lament": {}},
                              'exceptional': {'Suicide Branch': {}, 'Carin Shard': {}, 'Arm of King Leoric': {}, 'Blackhand Key': {}},
                              'elite': {'Boneshade': {}, "Death's Web": {}}},
                    'throwing': {'exceptional': {'Deathbit': {}, 'The Scalper': {}},
                                 'elite': {'Gimmershred': {}, 'Lacerator': {}, 'Warshrike': {}, "Demon's Arch": {}, 'Wraith Flight': {}, "Gargoyle's Bite": {}}}},
        'other': {'jewelry': {'rings': {'Nagelring': {}, 'Manald Heal': {}, 'Stone of Jordan': {}, 'Dwarf Star': {}, 'Raven Frost': {}, "Bul-Kathos' Wedding Band": {}, 'Carrion Wind': {}, "Nature's Peace": {}, 'Wisp Projector': {}},
                              'amulets': {'Nokozan Relic': {}, 'The Eye of Etlich': {}, 'The Mahim-Oak Curio': {}, "Saracen's Chance": {}, "The Cat's Eye": {}, 'The Rising Sun': {}, 'Crescent Moon': {}, "Atma's Scarab": {}, "Highlord's Wrath": {}, "Mara's Kaleidoscope": {}, "Seraph's Hymn": {}, 'Metalgrid': {}}},
                  'charms': {'all': {'Annihilus': {}, "Gheed's Fortune": {}, 'Hellfire Torch': {}}},
                  'rainbow facet (jewel)': {'level up': {'Cold': {}, 'Light': {}, 'Fire': {}, 'Poison': {}},
                                            'die': {'Cold': {}, 'Light': {}, 'Fire': {}, 'Poison': {}}},
                  'classes': {'amazon': {"Lycander's Aim": {}, "Titan's Revenge": {}, "Lycander's Flank": {}, "Blood Raven's Charge": {}, 'Thunderstroke': {}, 'Stoneraven': {}},
                              'assasin': {"Bartuc's Cut-Throat": {}, "Firelizard's Talons": {}, 'Jade Talon': {}, 'Shadow Killer': {}},
                              'barbarian': {"Arreat's Face": {}, "Demonhorn's Edge": {}, "Halaberd's Reign": {}, 'Wolfhowl': {}},
                              'druid': {"Jalal's Mane": {}, "Cerebus' Bite": {}, 'Ravenlore': {}, 'Spirit Keeper': {}},
                              'necromancer': {'Homunculus': {}, 'Boneflame': {}, 'Darkforce Spawn': {}},
                              'paladin': {'Herald of Zakarum': {}, 'Alma Negra': {}, 'Dragonscale': {}},
                              'sorceress': {'The Oculus': {}, "Death's Fathom": {}, "Eschuta's Temper": {}}}}},
    'sets': {'Angelic Raiment': {'Angelic Wings': {}, 'Angelic Halo': {}, 'Angelic Mantle': {}, 'Angelic Sickle': {}},
             "Arcanna's Tricks": {"Arcanna's Sign": {}, "Arcanna's Head": {}, "Arcanna's Flesh": {}, "Arcanna's Deathwand": {}},
             'Arctic Gear': {'Arctic Mitts': {}, 'Arctic Binding': {}, 'Arctic Furs': {}, 'Arctic Horn': {}},
             "Berserker's Arsenal": {"Berserker's Hatchet": {}, "Berserker's Hauberk": {}, "Berserker's Headgear": {}},
             "Cathan's Traps": {"Cathan's Seal": {}, "Cathan's Sigil": {}, "Cathan's Visage": {}, "Cathan's Mesh": {}, "Cathan's Rule": {}},
             "Civerb's Vestments": {"Civerb's Cudgel": {}, "Civerb's Ward": {}, "Civerb's Icon": {}},
             "Cleglaw's Brace": {"Cleglaw's Tooth": {}, "Cleglaw's Claw": {}, "Cleglaw's Pincers": {}},
             "Death's Disguise": {"Death's Touch": {}, "Death's Guard": {}, "Death's Hand": {}},
             "Hsaru's Defense": {"Hsarus' Iron Stay": {}, "Hsarus' Iron Fist": {}, "Hsarus' Iron Heel": {}},
             'Infernal Tools': {'Infernal Sign': {}, 'Infernal Torch': {}, 'Infernal Cranium': {}},
             "Iratha's Finery": {"Iratha's Coil": {}, "Iratha's Cuff": {}, "Iratha's Cord": {}, "Iratha's Collar": {}},
             "Isenhart's Armory": {"Isenhart's Lightbrand": {}, "Isenhart's Case": {}, "Isenhart's Horns": {}, "Isenhart's Parry": {}},
             "Milabrega's Regalia": {"Milabrega's Rod": {}, "Milabrega's Robe": {}, "Milabrega's Diadem": {}, "Milabrega's Orb": {}},
             "Sigon's Complete Steel": {"Sigon's Shelter": {}, "Sigon's Visor": {}, "Sigon's Guard": {}, "Sigon's Gage": {}, "Sigon's Sabot": {}, "Sigon's Wrap": {}},
             "Tancred's Battlegear": {"Tancred's Skull": {}, "Tancred's Weird": {}, "Tancred's Hobnails": {}, "Tancred's Spine": {}, "Tancred's Crowbill": {}},
             "Vidala's Rig": {"Vidala's Snare": {}, "Vidala's Ambush": {}, "Vidala's Fetlock": {}, "Vidala's Barb": {}},

             "Aldur's Watchtower": {"Aldur's Rhythm": {}, "Aldur's Stony Gaze": {}, "Aldur's Deception": {}, "Aldur's Advance": {}},
             "Bul-Kathos' Children": {"Bul-Kathos' Sacred Charge": {}, "Bul-Kathos' Tribal Guardian": {}},
             "Cow King's Leathers": {"Cow King's Horns": {}, "Cow King's Hide": {}, "Cow King's Hooves": {}},
             "Griswold's Legacy": {"Griswold's Redemption": {}, "Griswold's Valor": {}, "Griswold's Heart": {}, "Griswold's Honor": {}},
             "Heaven's Brethren": {"Dangoon's Teaching": {}, "Haemosu's Adamant": {}, "Taebaek's Glory": {}, "Ondal's Almighty": {}},
             "Hwanin's Majesty": {"Hwanin's Justice": {}, "Hwanin's Refuge": {}, "Hwanin's Splendor": {}, "Hwanin's Blessing": {}},
             'Immortal King': {"Immortal King's Stone Crusher": {}, "Immortal King's Will": {}, "Immortal King's Soul Cage": {}, "Immortal King's Detail": {}, "Immortal King's Forge": {}, "Immortal King's Pillar": {}},
             "M'avina's Battle Hymn": {"M'avina's Caster": {}, "M'avina's Embrace": {}, "M'avina's True Sight": {}, "M'avina's Tenet": {}, "M'avina's Icy Clutch": {}},
             "Naj's Ancient Vestige": {"Naj's Circlet": {}, "Naj's Light Plate": {}, "Naj's Puzzler": {}},
             "Natalya's Odium": {"Natalya's Mark": {}, "Natalya's Shadow": {}, "Natalya's Totem": {}, "Natalya's Soul": {}},
             "Orphan's Call": {"Whitstan's Guard": {}, "Guillaume's Face": {}, "Wilhelm's Pride": {}, "Magnus' Skin": {}},
             "Sander's Folly": {"Sander's Superstition": {}, "Sander's Paragon": {}, "Sander's Taboo": {}, "Sander's Riprap": {}},
             "Sazabi's Grand Tribute": {"Sazabi's Cobalt Redeemer": {}, "Sazabi's Ghost Liberator": {}, "Sazabi's Mental Sheath": {}},
             "Tal Rasha's Wrappings": {"Tal Rasha's Adjudication": {}, "Tal Rasha's Lidless Eye": {}, "Tal Rasha's Guardianship": {}, "Tal Rasha's Horadric Crest": {}, "Tal Rasha's Fine Spun Cloth": {}},
             'The Disciple': {'Dark Adherent': {}, 'Credendum': {}, 'Laying of Hands': {}, 'Rite of Passage': {}, 'Telling of Beads': {}},
             "Trang-Oul's Avatar": {"Trang-Oul's Guise": {}, "Trang-Oul's Scales": {}, "Trang-Oul's Girth": {}, "Trang-Oul's Claws": {}, "Trang-Oul's Wing": {}}},
    'runes': {'low runes': {'El Rune': {}, 'Eld Rune': {}, 'Tir Rune': {}, 'Nef Rune': {}, 'Eth Rune': {}, 'Ith Rune': {}, 'Tal Rune': {}, 'Ral Rune': {}, 'Ort Rune': {}, 'Thul Rune': {}, 'Amn Rune': {}, 'Sol Rune': {}, 'Shael Rune': {}, 'Dol Rune': {}},
              'middle runes': {'Hel Rune': {}, 'Io Rune': {}, 'Lum Rune': {}, 'Ko Rune': {}, 'Fal Rune': {}, 'Lem Rune': {}, 'Pul Rune': {}, 'Um Rune': {}, 'Mal Rune': {}},
              'high runes': {'Ist Rune': {}, 'Gul Rune': {}, 'Vex Rune': {}, 'Ohm Rune': {}, 'Lo Rune': {}, 'Sur Rune': {}, 'Ber Rune': {}, 'Jah Rune': {}, 'Cham Rune': {}, 'Zod Rune': {}}}}


def get_grail(uid, proxies=None):
    try:
        req = requests.get(url=api_page + uid, proxies=proxies)
    except Exception as e:
        raise e
    req.raise_for_status()
    out = req.json()
    if out.get('data', None) is None:
        dd = deepcopy(default_data)
        del dd['runes']
        out['data'] = default_data
    return out


def update_grail_dict(dct, item_upg_dict):
    def update_items(dct, item_upg_dict):
        if not item_upg_dict:
            return dct
        for k, v in dct.items():
            if k in item_upg_dict:
                dct[k].update({'wasFound': item_upg_dict.pop(k)})
            elif isinstance(v, dict):
                dct[k] = update_items(v, item_upg_dict)
        return dct

    # Deepcopy input nested dict to ensure original input is not changed
    dct = deepcopy(dct)

    # Holy grail app handles rainbow facets in a non-standard way compared to all other items, need to align with API
    for key in list(item_upg_dict):  # call "list" to make a copy of keys, since we pop them below
        if key.startswith('Rainbow Facet'):
            rbf = key.replace('(', '').replace(')', '').split(' ')
            dmg_type = rbf[2]
            activate_type = ' '.join(rbf[3:]).lower()
            dct['uniques']['other']['rainbow facet (jewel)'][activate_type][dmg_type] = {'wasFound': item_upg_dict.pop(key)}

    return update_items(dct, item_upg_dict)


# def owned_items(grail_dict):
#     def add_items(dct):
#         for k in dct:
#             if k in ['Cold', 'Fire', 'Light', 'Poison']:
#                 continue
#             if isinstance(dct[k], dict) and dct[k] and 'wasFound' not in dct[k]:
#                 add_items(dct[k])
#             elif dct[k].get('wasFound', False):
#                 my_items.append(k)
#     my_items = []
#     add_items(grail_dict)
#
#     for activate_type in ['die', 'level up']:
#         for dmg_type in ['Cold', 'Fire', 'Light', 'Poison']:
#             if grail_dict['uniques']['other']['rainbow facet (jewel)'][activate_type][dmg_type].get('wasFound', False):
#                 my_items.append('Rainbow Facet (%s %s)' % (dmg_type, activate_type.title()))
#     return my_items


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


# def count_items(dct):
#     tot, owned = 0, 0
#     for k in dct.keys():
#         if isinstance(dct[k], dict) and dct[k] and 'wasFound' not in dct[k]:
#             tmp = count_items(dct[k])
#             tot += tmp[0]
#             owned += tmp[1]
#         else:
#             tot += 1
#             if dct[k].get('wasFound', False):
#                 owned += 1
#     return tot, owned


def build_update_lst(dct):
    def recursive_update_list(dct):
        out = []
        for k, v in dct.items():
            if k in ['Cold', 'Fire', 'Light', 'Poison']:
                continue
            if isinstance(v, dict):
                if v.get('wasFound', False):
                    out.append(k)
                else:
                    out += recursive_update_list(v)

        return out

    lst = recursive_update_list(dct)
    for activate_type in ['die', 'level up']:
        for dmg_type in ['Cold', 'Fire', 'Light', 'Poison']:
            if dct['uniques']['other']['rainbow facet (jewel)'][activate_type][dmg_type].get('wasFound', False):
                lst.append('Rainbow Facet (%s %s)' % (dmg_type, activate_type.title()))

    return lst


if __name__ == '__main__':
    p_addresses = None
    username = input('username')
    password = input('password')
    grail = get_grail(uid=username, proxies=p_addresses)
    grail['data'] = update_grail_dict(dct=grail['data'], item_upg_dict={'Rainbow Facet (Cold Level Up)': True, 'Rainbow Facet (Light Die)': True})
    put_grail(uid=username, pwd=password, data=grail, proxies=p_addresses)
