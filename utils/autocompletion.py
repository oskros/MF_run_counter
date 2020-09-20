import tkinter as tk
import re
from init import *
import os, sys

FULL_ITEM_LIST = ["Aldur's Advance", "Aldur's Deception", "Aldur's Rhythm", "Aldur's Stony Gaze", "Alma Negra",
                  "Amn Rune", "Andariel's Visage", "Angelic Halo", "Angelic Mantle", "Angelic Sickle",
                  "Angelic Wings", "Annihilus", "Arachnid Mesh", "Arcanna's Deathwand", "Arcanna's Flesh",
                  "Arcanna's Head", "Arcanna's Sign", "Arctic Binding", "Arctic Furs", "Arctic Horn",
                  "Arctic Mitts", "Arioc's Needle", "Arkaine's Valor", "Arm of King Leoric", "Arreat's Face",
                  "Astreon's Iron Ward", "Athena's Wrath", "Atma's Scarab", "Atma's Wail", "Axe of Fechmar",
                  "Azurewrath", "Baezil's Vortex", "Bane Ash", "Baranar's Star", "Bartuc's Cut-Throat",
                  "Ber Rune", "Berserker's Hatchet", "Berserker's Hauberk", "Berserker's Headgear",
                  "Biggin's Bonnet", "Bing Sz Wang", "Black Hades", "Blackbog's Sharp", "Blackhand Key",
                  "Blackhorn's Face", "Blackleach Blade", "Blackoak Shield", "Blacktongue", "Blade of Ali Baba",
                  "Bladebone", "Bladebuckle", "Blastbark", "Blinkbat's Form", "Blood Crescent",
                  "Blood Raven's Charge", "Bloodfist", "Bloodletter", "Bloodmoon", "Bloodrise", "Bloodthief",
                  "Bloodtree Stump", "Boneflame", "Boneflesh", "Bonehew", "Boneshade", "Boneslayer Blade",
                  "Bonesnap", "Brainhew", "Bul-Kathos' Sacred Charge", "Bul-Kathos' Tribal Guardian",
                  "Bul-Kathos' Wedding Band", "Buriza-Do Kyanon", "Butcher's Pupil", "Bverrit Keep",
                  "Carin Shard", "Carrion Wind", "Cathan's Mesh", "Cathan's Rule", "Cathan's Seal",
                  "Cathan's Sigil", "Cathan's Visage", "Cerebus' Bite", "Cham Rune", "Chance Guards",
                  "Chromatic Ire", "Civerb's Cudgel", "Civerb's Icon", "Civerb's Ward", "Cleglaw's Claw",
                  "Cleglaw's Pincers", "Cleglaw's Tooth", "Cliffkiller", "Cloudcrack", "Coif of Glory",
                  "Coldkill", "Coldsteel Eye", "Corpsemourn", "Cow King's Hide", "Cow King's Hooves",
                  "Cow King's Horns", "Crainte Vomir", "Cranebeak", "Credendum", "Crescent Moon", "Crow Caw",
                  "Crown of Ages", "Crown of Thieves", "Crushflange", "Culwen's Point", "Dangoon's Teaching",
                  "Dark Adherent", "Dark Clan Crusher", "Darkforce Spawn", "Darkglow", "Darksight Helm",
                  "Death Cleaver", "Deathbit", "Death's Fathom", "Death's Guard", "Death's Hand", "Death's Touch",
                  "Death's Web", "Deathspade", "Demon Limb", "Demon Machine", "Demonhorn's Edge", "Demon's Arch",
                  "Dimoak's Hew", "Djinn Slayer", "Dol Rune", "Doombringer", "Doomslinger", "Dracul's Grasp",
                  "Dragonscale", "Duriel's Shell", "Duskdeep", "Dwarf Star", "Eaglehorn", "Earth Shifter",
                  "Earthshaker", "El Rune", "Eld Rune", "Endlesshail", "Eschuta's Temper", "Eth Rune",
                  "Ethereal Edge", "Executioner's Justice", "Fal Rune", "Felloak", "Firelizard's Talons",
                  "Flamebellow", "Fleshrender", "Fleshripper", "Frostburn", "Frostwind", "Gargoyle's Bite",
                  "Gerke's Sanctuary", "Gheed's Fortune", "Ghostflame", "Ghoulhide", "Giant Skull", "Gimmershred",
                  "Ginther's Rift", "Gleamscythe", "Gloom's Trap", "Goblin Toe", "Goldskin", "Goldstrike Arch",
                  "Goldwrap", "Gore Rider", "Gorefoot", "Goreshovel", "Gravenspine", "Gravepalm", "Greyform",
                  "Griffon's Eye", "Grim's Burning Dead", "Griswold's Edge", "Griswold's Heart",
                  "Griswold's Honor", "Griswold's Redemption", "Griswold's Valor", "Guardian Angel",
                  "Guardian Naga", "Guillaume's Face", "Gul Rune", "Gull", "Gut Siphon", "Haemosu's Adamant",
                  "Halaberd's Reign", "Hand of Blessed Light", "Harlequin Crest", "Hawkmail",
                  "Head Hunter's Glory", "Headstriker", "Heart Carver", "Heavenly Garb", "Heaven's Light",
                  "Hel Rune", "Hellcast", "Hellclap", "Hellfire Torch", "Hellmouth", "Hellplague", "Hellrack",
                  "Hellslayer", "Herald of Zakarum", "Hexfire", "Highlord's Wrath", "Homunculus", "Hone Sundan",
                  "Horizon's Tornado", "Hotspur", "Howltusk", "Hsarus' Iron Fist", "Hsarus' Iron Heel",
                  "Hsarus' Iron Stay", "Humongous", "Husoldal Evo", "Hwanin's Blessing", "Hwanin's Justice",
                  "Hwanin's Refuge", "Hwanin's Splendor", "Iceblink", "Ichorsting", "Immortal King's Detail",
                  "Immortal King's Forge", "Immortal King's Pillar", "Immortal King's Soul Cage",
                  "Immortal King's Stone Crusher", "Immortal King's Will", "Infernal Cranium", "Infernal Sign",
                  "Infernal Torch", "Infernostride", "Io Rune", "Iratha's Coil", "Iratha's Collar",
                  "Iratha's Cord", "Iratha's Cuff", "Iron Pelt", "Ironstone", "Isenhart's Case",
                  "Isenhart's Horns", "Isenhart's Lightbrand", "Isenhart's Parry", "Islestrike", "Ist Rune",
                  "Ith Rune", "Jade Talon", "Jah Rune", "Jalal's Mane", "Kelpie Snare", "Kinemil's Awl",
                  "Kira's Guardian", "Knell Striker", "Ko Rune", "Kuko Shakaku", "Lacerator", "Lance Guard",
                  "Lance of Yaggai", "Langer Briser", "Lava Gout", "Laying of Hands", "Leadcrow", "Lem Rune",
                  "Lenymo", "Leviathan", "Lidless Wall", "Lightsabre", "Lo Rune", "Lum Rune", "Lycander's Aim",
                  "Lycander's Flank", "Maelstrom", "Magefist", "Magewrath", "Magnus' Skin", "Mal Rune",
                  "Manald Heal", "Mang Song's Lesson", "Mara's Kaleidoscope", "Marrowwalk", "M'avina's Caster",
                  "M'avina's Embrace", "M'avina's Icy Clutch", "M'avina's Tenet", "M'avina's True Sight",
                  "Medusa's Gaze", "Messerschmidt's Reaver", "Metalgrid", "Milabrega's Diadem", "Milabrega's Orb",
                  "Milabrega's Robe", "Milabrega's Rod", "Moonfall", "Moser's Blessed Circle", "Nagelring",
                  "Naj's Circlet", "Naj's Light Plate", "Naj's Puzzler", "Natalya's Mark", "Natalya's Shadow",
                  "Natalya's Soul", "Natalya's Totem", "Nature's Peace", "Nef Rune", "Nightsmoke",
                  "Nightwing's Veil", "Nokozan Relic", "Nord's Tenderizer", "Nosferatu's Coil", "Ohm Rune",
                  "Ondal's Almighty", "Ondal's Wisdom", "Orb of Corruption", "Ormus' Robes", "Ort Rune",
                  "Peasant Crown", "Pelta Lunata", "Pierre Tombale Couant", "Plague Bearer", "Pluckeye",
                  "Pompeii's Wrath", "Pul Rune", "Pus Spitter", "Que-Hegan's Wisdom", "Radament's Sphere",
                  "Rainbow Facet (Cold Die)", "Rainbow Facet (Cold Level Up)", "Rainbow Facet (Fire Die)",
                  "Rainbow Facet (Fire Level Up)", "Rainbow Facet (Light Die)", "Rainbow Facet (Light Level Up)",
                  "Rainbow Facet (Poison Die)", "Rainbow Facet (Poison Level Up)", "Rakescar", "Ral Rune", "Rattlecage",
                  "Raven Claw", "Raven Frost", "Ravenlore", "Razor's Edge", "Razorswitch", "Razortail", "Razortine",
                  "Ribcracker", "Riphook", "Ripsaw", "Rite of Passage", "Rixot's Keen", "Rockfleece", "Rockstopper",
                  "Rogue's Bow", "Rune Master", "Rusthandle", "Sander's Paragon", "Sander's Riprap",
                  "Sander's Superstition", "Sander's Taboo", "Sandstorm Trek", "Saracen's Chance",
                  "Sazabi's Cobalt Redeemer", "Sazabi's Ghost Liberator", "Sazabi's Mental Sheath", "Schaefer's Hammer",
                  "Seraph's Hymn", "Serpent Lord", "Shadow Dancer", "Shadow Killer", "Shadowfang", "Shael Rune",
                  "Shaftstop", "Sigon's Gage", "Sigon's Guard", "Sigon's Sabot", "Sigon's Shelter", "Sigon's Visor",
                  "Sigon's Wrap", "Silks of the Victor", "Silkweave", "Skewer of Krintiz",
                  "Skin of the Flayed One", "Skin of the Vipermagi", "Skull Collector", "Skull Splitter",
                  "Skullder's Ire", "Skystrike", "Snakecord", "Snowclash", "Sol Rune", "Soul Drainer",
                  "Soul Harvest", "Soulfeast Tine", "Soulflay", "Sparking Mail", "Spectral Shard", "Spellsteel",
                  "Spike Thorn", "Spineripper", "Spire of Honor", "Spire of Lazarus", "Spirit Forge",
                  "Spirit Keeper", "Spirit Ward", "Stealskull", "Steel Carapace", "Steel Pillar", "Steel Shade",
                  "Steelclash", "Steeldriver", "Steelgoad", "Steelrend", "Stone Crusher", "Stone of Jordan",
                  "Stoneraven", "Stormchaser", "Stormeye", "Stormguild", "Stormlash", "Stormrider",
                  "Stormshield", "Stormspike", "Stormspire", "Stormstrike", "Stoutnail", "String of Ears",
                  "Suicide Branch", "Sur Rune", "Sureshrill Frost", "Swordback Hold", "Swordguard",
                  "Taebaek's Glory", "Tal Rasha's Adjudication", "Tal Rasha's Fine Spun Cloth",
                  "Tal Rasha's Guardianship", "Tal Rasha's Horadric Crest", "Tal Rasha's Lidless Eye", "Tal Rune",
                  "Tancred's Crowbill", "Tancred's Hobnails", "Tancred's Skull", "Tancred's Spine",
                  "Tancred's Weird", "Tarnhelm", "Tearhaunch", "Telling of Beads", "Templar's Might",
                  "The Atlantean", "The Battlebranch", "The Cat's Eye", "The Centurion", "The Chieftain",
                  "The Cranium Basher", "The Diggler", "The Dragon Chang", "The Eye of Etlich",
                  "The Face of Horror", "The Fetid Sprinkler", "The Gavel of Pain", "The General's Tan Do Li Ga",
                  "The Gladiator's Bane", "The Gnasher", "The Grandfather", "The Grim Reaper",
                  "The Hand of Broc", "The Impaler", "The Iron Jang Bong", "The Jade Tan Do",
                  "The Mahim-Oak Curio", "The Meat Scraper", "The Minotaur", "The Oculus", "The Patriarch",
                  "The Reaper's Toll", "The Redeemer", "The Rising Sun", "The Salamander", "The Scalper",
                  "The Spirit Shroud", "The Tannr Gorerod", "The Vile Husk", "The Ward", "Thul Rune",
                  "Thundergod's Vigor", "Thunderstroke", "Tiamat's Rebuke", "Tir Rune", "Titan's Revenge",
                  "Todesfaelle Flamme", "Tomb Reaver", "Toothrow", "Torch of Iro", "Trang-Oul's Claws",
                  "Trang-Oul's Girth", "Trang-Oul's Guise", "Trang-Oul's Scales", "Trang-Oul's Wing",
                  "Treads of Cthon", "Twitchthroe", "Tyrael's Might", "Um Rune", "Umbral Disk",
                  "Ume's Lament", "Undead Crown", "Valkyrie Wing", "Vampire Gaze", "Veil of Steel",
                  "Venom Grip", "Venom Ward", "Verdungo's Hearty Cord", "Vex Rune", "Vidala's Ambush",
                  "Vidala's Barb", "Vidala's Fetlock", "Vidala's Snare", "Viperfork", "Visceratuant",
                  "Wall of the Eyeless", "War Traveler", "Warlord's Trust", "Warpspear", "Warshrike", "Waterwalk",
                  "Whitstan's Guard", "Widowmaker", "Wilhelm's Pride", "Windforce", "Windhammer",
                  "Wisp Projector", "Witchwild String", "Witherstring", "Wizardspike", "Wizendraw", "Woestave",
                  "Wolfhowl", "Wormskull", "Wraith Flight", "Zakarum's Hand", "Zod Rune",
                  "Key of Destruction", "Key of Hate", "Key of Terror"]

ITEM_ALIASES = {"Aldur's Boots": "Aldur's Advance",
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
                'LoH': 'Laying of Hands',
                "M'avina's Bow": "M'avina's Caster",
                "M'avina's Armor": "M'avina's Embrace",
                "M'avina's Gloves": "M'avina's Icy Clutch",
                "M'avina's Belt": "M'avina's Tenet",
                "M'avina's Diadem": "M'avina's True Sight",
                "M'avina's Helm": "M'avina's True Sight",
                'Mahim Oak': 'The Mahim-Oak Curio',
                'Nagel Ring': 'Nagelring',
                'OOC': 'Orb of Corruption',
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
                'Wizzy': 'Wizardspike'}


class AutocompleteEntry:
    def __init__(self, master, width, textvariable, enable=True):
        self.chosen = None
        self.enable = enable
        self.master = master
        self.width = width
        self.var = textvariable
        self.entry = tk.Entry(master, textvariable=self.var)
        self.entry.pack(fill=tk.X, padx=4)
        self.entry.focus()

        self.var.trace_add('write', lambda name, index, mode: self.changed(name, index, mode))
        self.entry.bind("<Up>", self.move_up)
        self.entry.bind("<Down>", self.move_down)
        self.entry.bind("<Tab>", self.selection)

        self.listboxUp = False

    def changed(self, name=None, index=None, mode=None):
        var = self.var.get()
        if var == '':
            if self.listboxUp:
                self.listbox.destroy()
                self.listboxUp = False
        else:
            if self.enable:
                words = self.comparison(var)
                if var.lower().startswith('eth '):
                    words.extend(self.comparison(var[4:], eth=True))
            else:
                words = []

            if words:
                if self.listboxUp:
                    self.listbox.destroy()
                self.listbox = tk.Listbox(self.master, width=self.width, height=min(len(words), 6))
                self.listbox.bind("<Double-Button-1>", self.selection)
                self.listbox.bind("<Tab>", self.selection)
                self.listbox.place(relx=0, rely=0.3)
                self.listbox.tkraise()
                self.listboxUp = True

                self.listbox.delete(0, tk.END)
                for w in words:
                    self.listbox.insert(tk.END, w)
            else:
                if self.listboxUp:
                    self.listbox.destroy()
                    self.listboxUp = False

    def selection(self, event=None):
        if self.listboxUp:  # and self.listbox.curselection():
            self.chosen = self.listbox.get(tk.ACTIVE)
            self.var.set(self.chosen + ' ')
            self.listbox.destroy()
            self.listboxUp = False
            self.entry.icursor(tk.END)

    def move_up(self, event):
        if self.listboxUp:
            if self.listbox.curselection() == ():
                index = tk.END
                hl_idx = tk.END
            else:
                index = self.listbox.curselection()[0]
                hl_idx = str(int(index) - 1)

            if index != '0':
                self.listbox.selection_clear(first=index)

                self.listbox.see(hl_idx)  # Scroll!
                self.listbox.selection_set(first=hl_idx)
                self.listbox.activate(hl_idx)

    def move_down(self, event):
        if self.listboxUp:
            if self.listbox.curselection() == ():
                index = '0'
                hl_idx = '0'
            else:
                index = self.listbox.curselection()[0]
                hl_idx = str(int(index) + 1)

            if index != tk.END:
                self.listbox.selection_clear(first=index)

                self.listbox.see(hl_idx)  # Scroll!
                self.listbox.selection_set(first=hl_idx)
                self.listbox.activate(hl_idx)

    @staticmethod
    def comparison(var, eth=False):
        out = set()
        # regex to append a [']? after all letters, which is an optional argument for adding a hyphen
        # this means that for example typing in "mavinas" and "m'avina's" will yield the same results
        hyphen_escape = re.sub('([^a-zA-Z]*)', "\\1[']?", re.escape(var))
        # encapsulating with \b ensures that searches are done only at the start of each word
        # ".*" allows anything to follow after the already typed letters
        pattern = re.compile(r"\b" + hyphen_escape + r".*\b", flags=re.IGNORECASE)

        for w in FULL_ITEM_LIST + list(ITEM_ALIASES.keys()):
            if re.search(pattern, w):
                # Append true entry from the alias list - if none are found, add the match from original list
                i_name = ITEM_ALIASES.get(w, w)
                if eth:
                    if 'Rune' not in i_name and 'Orb of Corruption' not in i_name:
                        out.add('Eth ' + i_name)
                else:
                    out.add(i_name)
        return sorted(out)


class ACMbox(object):
    def __init__(self, title, enable=True):
        self.root = tk.Toplevel()
        self.root.geometry(
            '200x145+%s+%s' % (self.root.winfo_screenwidth() // 2 - 100, self.root.winfo_screenheight() // 2 - 72))
        self.root.update_idletasks()
        self.root.focus_set()
        self.root.iconbitmap(os.path.join(getattr(sys, '_MEIPASS', os.path.abspath('.')), media_path + 'icon.ico'))
        self.root.title(title)
        self.root.wm_attributes("-topmost", True)
        self.root.resizable(False, False)

        frm_1 = tk.Frame(self.root)
        frm_1.pack(ipadx=4, ipady=2, fill=tk.BOTH, expand=tk.Y)

        tk.Label(frm_1, text='Input your drop...').pack()

        tw = tk.StringVar()
        self.entry = AutocompleteEntry(frm_1, width=32, textvariable=tw, enable=enable)

        frm_2 = tk.Frame(frm_1)
        frm_2.pack(padx=4, pady=4)

        tk.Button(frm_2, width=8, text='OK', command=self.b1_action).pack(side=tk.LEFT)
        tk.Button(frm_2, width=8, text='Cancel', command=self.close_mod).pack(side=tk.LEFT)

        self.root.bind('<KeyPress-Return>', func=self.b1_action)
        self.root.bind('<KeyPress-Escape>', func=self.close_mod)

        # call self.close_mod when the close button is pressed
        self.root.protocol("WM_DELETE_WINDOW", self.close_mod)

        # a trick to activate the window (on windows 7)
        self.root.deiconify()

    def b1_action(self, event=None):
        if self.entry.listboxUp:
            self.entry.selection(event)
        else:
            item_name = self.entry.chosen
            if item_name is not None and item_name.startswith('Eth ') and item_name != 'Eth Rune':
                item_name = item_name[4:]
            user_input = self.entry.var.get().strip()
            extra_input = user_input.replace(item_name, '').strip().replace('  ', ' ') if item_name is not None else ''
            self.returning = {'item_name': item_name, 'input': user_input, 'extra': extra_input}
            self.root.quit()

    def close_mod(self, event=None):
        if self.entry.listboxUp:
            self.entry.listbox.destroy()
            self.entry.listboxUp = False
        else:
            self.returning = None
            self.root.quit()


def acbox(title='Drop', enable=True):
    msgbox = ACMbox(title, enable=enable)
    msgbox.root.mainloop()

    # the function pauses here until the mainloop is quit
    msgbox.root.destroy()
    return msgbox.returning


if __name__ == '__main__':
    print(acbox(enable=True))
