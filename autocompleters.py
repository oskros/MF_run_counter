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
                  "Hwanin's Refuge", "Hwanin's Splendor", "Iceblink", "Ichorstring", "Immortal King's Detail",
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
                  "Pompeii's Wrath", "Pul Rune", "Pus Spitter", "Que-Hegan's Wisdom", "Radamant's Sphere",
                  "Rainbow Facet", "Rakescar", "Ral Rune", "Rattlecage", "Raven Claw", "Raven Frost",
                  "Ravenlore", "Razor's Edge", "Razorswitch", "Razortail", "Razortine", "Ribcracker", "Riphook",
                  "Ripsaw", "Rite of Passage", "Rixot's Keen", "Rockfleece", "Rockstopper", "Rogue's Bow",
                  "Rune Master", "Rusthandle", "Sander's Paragon", "Sander's Riprap", "Sander's Superstition",
                  "Sander's Taboo", "Sandstorm Trek", "Saracen's Chance", "Sazabi's Cobalt Redeemer",
                  "Sazabi's Ghost Liberator", "Sazabi's Mental Sheath", "Schaefer's Hammer", "Seraph's Hymn",
                  "Serpent Lord", "Shadow Dancer", "Shadow Killer", "Shadowfang", "Shael Rune", "Shaftstop",
                  "Sigon's Gage", "Sigon's Guard", "Sigon's Sabot", "Sigon's Shelter", "Sigon's Visor",
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
                  "The Atlantean", "The Battlebranch", "The Cat's Eye", "The Centurion", "The Chieftan",
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
                  "Wolfhowl", "Wormskull", "Wraith Flight", "Zakarum's Hand", "Zod Rune"]

ITEM_ALIASES = {"Aldur's Boots": "Aldur's Advance",
                "Aldur's Weapon": "Aldur's Rhythm",
                "Aldur's Armor": "Aldur's Deception",
                "Aldur's Helm": "Aldur's Stony Gaze",
                "Andy's Face": "Andariel's Visage",
                'Angelic Amu': 'Angelic Wings',
                'Angelic Ring': 'Angelic Halo',
                'BK ring': "Bul-Kathos' Wedding Band",
                'COA': 'Crown Of Ages',
                'DF': "Death's Fathom",
                'G Angel': 'Guardian Angel',
                'Gangel': 'Guardian Angel',
                'GF': 'The Grandfather',
                "Griswold's Armor": "Griswold's Heart",
                "Griswold's Helm": "Griswold's Valor",
                "Griswold's Shield": "Griswold's Honor",
                "Griswold's Weapon": "Griswold's Redemption",
                'Gull Dagger': 'Gull',
                'HOZ': 'Herald of Zakarum',
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
                'LOH': 'Laying Of Hands',
                'Mahim Oak': 'The Mahim-Oak Curio',
                'Nagel Ring': 'Nagelring',
                'OOC': 'Orb Of Corruption',
                'Occu': 'The Oculus',
                'Occy': 'The Oculus',
                "Que Hegan's Wisdom": "Que-Hegan's Wisdom",
                'RBF': 'Rainbow Facet',
                'SOE': 'String Of Ears',
                'SOJ': 'Stone of Jordan',
                'SS': 'Stormshield',
                'Shako': 'Harlequin Crest',
                "Sigon's Armor": "Sigon's Shelter",
                "Sigon's Belt": "Sigon's Wrap",
                "Sigon's Boots": "Sigon's Sabot",
                "Sigon's Gloves": "Sigon's Gage",
                "Sigon's Helm": "Sigon's Visor",
                "Sigon's Shield": "Sigon's Guard",
                'TGS': "Thundergod's Vigor",
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
                'WF': 'Windforce',
                'WT': 'War Traveler',
                'WWS': 'Waterwalk',
                'Wizzy': 'Wizardspike'}


class AutocompleteEntry(tk.Entry):
    def __init__(self, *args, **kwargs):
        self.chosen = None
        tk.Entry.__init__(self, *args, **kwargs)
        self.focus()

        self.var = self["textvariable"]
        if self.var == '':
            self.var = self["textvariable"] = tk.StringVar()

        self.var.trace('w', self.changed)
        self.bind("<Tab>", self.selection)
        self.bind("<Up>", self.move_up)
        self.bind("<Down>", self.move_down)

        self.listboxUp = False

    def changed(self, name, index, mode):
        if self.var.get() == '':
            if self.listboxUp:
                self.listbox.destroy()
                self.listboxUp = False
        else:
            words = self.comparison()
            if words:
                if self.listboxUp:
                    self.listbox.destroy()
                self.listbox = tk.Listbox(width=self["width"], height=min(len(words), 6))
                self.listbox.bind("<Double-Button-1>", self.selection)
                self.listbox.place(x=self.winfo_x(), y=self.winfo_y() + self.winfo_height())
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
            self.icursor(tk.END)

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

    def comparison(self):
        out = []
        hyphen_escape = re.sub('([^a-zA-Z]*)', "\\1[']?", re.escape(self.var.get()))
        pattern = re.compile(r"\b" + hyphen_escape + r".*\b", flags=re.IGNORECASE)
        for w in FULL_ITEM_LIST + list(ITEM_ALIASES.keys()):
            if re.search(pattern, w):
                out.append(ITEM_ALIASES.get(w, w))
        return out


class ACMbox(object):
    def __init__(self, title):
        self.root = root = tk.Tk()
        self.root.focus_set()
        self.root.iconbitmap(os.path.join(getattr(sys, '_MEIPASS', os.path.abspath('.')), media_path + 'icon.ico'))
        self.root.title(title)
        self.root.wm_attributes("-topmost", True)
        self.root.geometry('200x145')
        self.root.resizable(False, False)

        frm_1 = tk.Frame(self.root)
        frm_1.pack(ipadx=4, ipady=2)

        tk.Label(frm_1, text='Input your drop...').pack()

        self.entry = AutocompleteEntry(frm_1, width=32)
        self.entry.pack()

        frm_2 = tk.Frame(frm_1)
        frm_2.pack(padx=4, pady=4)

        # buttons
        btn_1 = tk.Button(frm_2, width=8, text='OK')
        btn_1['command'] = self.b1_action
        btn_1.pack(side='left')

        btn_2 = tk.Button(frm_2, width=8, text='Cancel')
        btn_2['command'] = self.close_mod
        btn_2.pack(side='left')

        root.unbind_all('<<NextWindow>>')
        root.unbind_all('<<PrevWindow>>')
        root.bind('<KeyPress-Return>', func=self.b1_action)
        root.bind('<KeyPress-Escape>', func=lambda e: self.close_mod())

        root.update_idletasks()
        xp = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
        yp = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
        geom = (root.winfo_width(), root.winfo_height(), xp, yp)
        root.geometry('{0}x{1}+{2}+{3}'.format(*geom))

        # call self.close_mod when the close button is pressed
        root.protocol("WM_DELETE_WINDOW", self.close_mod)

        # a trick to activate the window (on windows 7)
        root.deiconify()

    def b1_action(self, event=None):
        if self.entry.listboxUp:
            self.entry.selection(event)
        else:
            arg1 = self.entry.chosen
            arg2 = self.entry.get().replace(arg1, '').strip() if arg1 else self.entry.get().strip()
            self.returning = arg1, arg2
            self.root.quit()

    def close_mod(self):
        self.returning = None
        self.root.quit()


def acbox(title='Drop'):
    msgbox = ACMbox(title)
    msgbox.root.mainloop()

    # the function pauses here until the mainloop is quit
    msgbox.root.destroy()
    return msgbox.returning


if __name__ == '__main__':
    print(acbox())

    # root = tk.Tk()
    # entry = AutocompleteEntry(root, width=32)
    # entry.grid()
    # tk.Button(text='Python').grid(column=0)
    # tk.Button(text='Tkinter').grid(column=0)
    # tk.Button(text='Regular Expressions').grid(column=0)
    # tk.Button(text='Fixed bugs').grid(column=0)
    # tk.Button(text='New features').grid(column=0)
    # tk.Button(text='Check code comments').grid(column=0)
    # root.mainloop()
