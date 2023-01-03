"""Handle the loading and initialization of game sessions."""
from __future__ import annotations

from typing import Optional

import tcod
import numpy as np
import lzma
import pickle
import traceback

import colour
from engine import Engine
import input_handlers
from entity import Actor
from level_generator import MessyBSPTree
from level_parameters import level_params
from components.inventory import Inventory
from components.ai import BaseAI
from components.npc_templates import Fighter
from components.bodyparts import Body, Arm, Leg, Head
from random import randint, choices, choice

from copy import deepcopy

from components.weapons.glock17 import glock_17

from components.weapons.glock17 import glock17_frame, glock17_barrel, glock17_slide, glock17_slide_optic, \
    glock_switch, glock_9mm_compensator, glock_stock, glock_pic_rail, suppressor_surefire_9mm

# for crafting testing
from pydantic.utils import deep_update
from components.weapons.glock17 import glock17dict

#from components.weapons.mosin import mosin_stock, mosin_archangel_stock, mosin_carbine_stock, mosin_obrez_stock, \
#    mosin_barrel, mosin_carbine_barrel, mosin_obrez_barrel, mosin_pic_scope_mount, \
#    mosin_magazine_conversion, mosin_suppressor, mosin_muzzlebreak, mosin_nagant


def new_game() -> Engine:
    """Return a brand new game session as an Engine instance."""
    current_level = 0

    # initialises player entity
    fighter_component = Fighter(unarmed_meat_damage=10, unarmed_armour_damage=5)

    #TODO: adjust to be correct
    Head_part = Head(hp=50, defence=50, depth=15, width=15, height=20)
    Body_part = Body(hp=100, defence=50, depth=20, width=15, height=20)
    R_Arm = Arm(hp=30, defence=50, name='right arm', depth=15, width=15, height=20)
    L_Arm = Arm(hp=30, defence=50, name='left arm', depth=15, width=15, height=20)
    R_Leg = Leg(hp=30, defence=50, name='right leg', depth=15, width=15, height=20)
    L_Leg = Leg(hp=30, defence=50, name='left leg', depth=15, width=15, height=20)

    body_parts = (Body_part, Head_part, R_Arm, L_Arm, R_Leg, L_Leg)

    player = Actor(0,
                   0,
                   '@',
                   colour.GREEN,
                   'Player',
                   ai=BaseAI,
                   fighter=fighter_component,
                   bodyparts=body_parts,
                   player=True,
                   inventory=Inventory(capacity=15),
                   item_drops={},
                   weapons={},
                   )

    engine = Engine(player=player, current_level=current_level, current_floor=0)

    #inventory_items = [mac1045,]

    #inventory_items = [glock_17, glock17_frame, glock17_barrel, glock17_slide, glock17_slide_optic,
    #                   glock_switch, glock_9mm_compensator, glock_stock, glock_pic_rail, suppressor_surefire_9mm]

    inventory_items = [glock_17, glock17_frame, glock17_barrel, glock17_slide_optic,
                       glock_switch, glock_9mm_compensator, glock_stock, glock_pic_rail, suppressor_surefire_9mm]

    engine.crafting_recipes = deep_update(engine.crafting_recipes, glock17dict)

    #inventory_items = [glock17_frame, glock17_barrel, glock17l_barrel,
    #                   glock17_barrel_ported, glock17l_barrel_ported, glock17_slide, glock17l_slide,
    #                   glock17_slide_custom, glock17l_slide_custom,
    #                   glock_switch, glock_9mm_compensator, glock_stock, glock_pic_rail, glock_pistol_brace]

    #inventory_items = [mosin_stock, mosin_archangel_stock, mosin_carbine_stock, mosin_obrez_stock,
    #                   mosin_barrel, mosin_carbine_barrel, mosin_obrez_barrel, mosin_pic_scope_mount,
    #                   mosin_magazine_conversion, mosin_suppressor, mosin_muzzlebreak]

    #inventory_items = [mac1045_lower, mac1045_upper, mac1045_upper_tactical, mac1045_upper_max,mac1045_barrel,
    #                   mac1045_extended_barrel, mac1045_carbine_barrel, mac10_full_stock, mac10_folding_stock,
    #                   mac1045_sionics_suppressor, mac109_max_barrel, mac1045_max_barrel, mac10_vertical_grip]

    for item in inventory_items:
        itemcopy = deepcopy(item)
        player.inventory.items.append(itemcopy)
        itemcopy.parent = player.inventory

    engine.game_map = MessyBSPTree(level_params[current_level][0],  # messy tunnels
                                   level_params[current_level][1],  # map width
                                   level_params[current_level][2],  # map height
                                   level_params[current_level][3],  # max leaf size
                                   level_params[current_level][4],  # max room size
                                   level_params[current_level][5],  # room min size
                                   level_params[current_level][6],  # max monsters per room
                                   level_params[current_level][7],  # max items per room
                                   engine,
                                   current_level,
                                   ).generateLevel()

    engine.game_map.camera_xy = (engine.player.x, engine.player.y)

    engine.update_fov()

    engine.message_log.add_message(
        "You lose your footing and fall deep into the caverns below... You can't see any way to get back to the surface"
        , colour.LIGHT_MAGENTA
    )

    return engine


def load_game(filename: str) -> Engine:
    """Load an Engine instance from a file."""
    with open(filename, "rb") as f:
        engine = pickle.loads(lzma.decompress(f.read()))
    assert isinstance(engine, Engine)
    return engine


def generate_subtext() -> str:
    verb_1 = choice(('Aquarian', 'New-Age', 'Postdiluvian', 'Cosmic', 'Mystical', 'Esoteric',
                     'Dialectical', 'Demiurgic', 'Sublime', 'Hyper-Realistic', 'Platonic', 'MK-Ultra', 'Illegal',
                     'Post-Apocalyptic', 'Morally Ambiguous', 'Atlantean', 'New World Order',
                     'Harmonic', 'Universal', 'Post-Structural', 'Archetypal',
                     'Philosophical', 'Angelic', 'Paranormal', 'Shamanic', 'Vampiric', 'Cryptic', 'Jungian',
                     'Reptilian', 'Lovecraftian', 'Biblical', 'Heretical', 'Heterodox', 'Theological', 'Religious',
                     'Cursed', 'Hegelian', 'Occult'))

    verb_2 = choice(('Deep Underground', 'Splatterpunk', 'Cyphercore', 'Advanced', 'Modern', 'Post-Modern',
                     'Extreme', 'Sinister', 'Gothic', 'Revolutionary', 'Reactionary', 'Officially Licensed',
                     'Subversive', 'Covert', 'Magik', 'Chaos Magic', 'Solar', 'Lunar', 'Ideological', 'Cyclic',
                     'Meditative', 'Divine', 'Tactical', 'Forbidden', 'Psychedelic', 'Oracular', 'Quantum',
                     'Post-Industrial', 'Post-Fall', 'Hollow Earth', 'Pre-Modern', 'Introductory', 'Ritual'))

    verb_3 = choice(('Combat', 'Gun Smithing', 'UFO-ology', 'Warfare', 'Conspiracy', 'CQC', 'Harm Prevention',
                     'Self Defense', 'Horror', 'Action', 'Time-War', 'Numerology', 'Sacred Geometry',
                     'Violence', 'Tulpamancy', 'Astral Projection', 'Psychic', 'Englightenment', 'Gun Fu', 'Gunplay',
                     'Firearms Safety', 'Gun Collection', 'Ballistics', 'Gun Customization', 'Gun Building',
                     'Demonology', 'Virtual Reality', 'Lucid Dreaming', 'Remote Viewing', 'Folklore', 'Exorcism',
                     'Manifestation', 'Alien Abduction', 'Shape Shifting', 'Witchcraft', 'Predictive Programming',
                     'Terrorism'))

    noun = choice(('Computer Role Playing Game', 'Simulation', 'Training Module', 'Course', 'Engine',
                   'RPG', 'Rogue Like', 'Rogue Lite', 'Program', 'Center', 'Game', 'Experience', 'Proof-of-Concept',
                   'Videogame Adaptation', 'Demonstration', 'Tutorial', 'Simulator', '(DO NOT RESEARCH)', 'LARP',
                   'Survival Game', 'Educational Game', 'Shooter', '-Hack Like'))

    subtext_str = f"{verb_1} {verb_2} {verb_3} {noun}"
    return subtext_str


class MainMenu(input_handlers.BaseEventHandler):
    """Handle the main menu rendering and input."""

    def __init__(self):
        self.option_selected = 0
        self.colour_mode_forward = [True, True, True]
        self.fg_colour = [randint(60, 255), randint(60, 255), randint(60, 255)]
        self.subtext = generate_subtext()

    def change_fg_colour(self):

        for i in range(3):
            reverse_direction = choices(population=(True, False), weights=(1, 600))[0]

            if self.colour_mode_forward[i - 1]:
                if reverse_direction:
                    self.colour_mode_forward[i - 1] = False
                else:
                    self.fg_colour[i - 1] += 1
                    if self.fg_colour[i - 1] >= 250:
                        self.colour_mode_forward[i - 1] = False

            else:
                if reverse_direction:
                    self.colour_mode_forward[i - 1] = True
                else:
                    self.fg_colour[i - 1] -= 1
                    if self.fg_colour[i - 1] <= 25:
                        self.colour_mode_forward[i - 1] = True

    def on_render(self, console: tcod.Console) -> None:
        """Render the main menu on a background image."""

        path = "newmenu1.xp"  # REXPaint file with one layer.
        # Load a REXPaint file with a single layer.
        # The comma after console is used to unpack a single item tuple.
        console2, = tcod.console.load_xp(path, order="F")

        # Convert tcod's Code Page 437 character mapping into a NumPy array.
        CP437_TO_UNICODE = np.asarray(tcod.tileset.CHARMAP_CP437)

        # Convert from REXPaint's CP437 encoding to Unicode in-place.
        console2.ch[:] = CP437_TO_UNICODE[console2.ch]

        # Apply REXPaint's alpha key color.
        KEY_COLOR = (255, 0, 255)
        is_transparent = (console2.rgb["bg"] == KEY_COLOR).all(axis=2)
        console2.rgba[is_transparent] = (ord(" "), (0,), (0,))

        self.change_fg_colour()
        console2.rgb["fg"] = self.fg_colour

        console2.blit(dest=console, dest_x=console.width//2-40, dest_y=console.height//2-25, src_x=0, src_y=0, width=80,
                      height=50)

        console.print(
            console.width // 2,
            console.height // 2 + 18,
            self.subtext,
            fg=self.fg_colour,
            alignment=tcod.CENTER,
        )

        menu_width = 8
        for i, text in enumerate(
            ["New Game", "Continue", "  Quit"]
        ):
            console.print(
                console.width // 2,
                console.height // 2 - 2 + i,
                text.ljust(menu_width),
                fg=self.fg_colour,
                alignment=tcod.CENTER,
                bg_blend=tcod.BKGND_ALPHA(64),
            )

        console.print(x=console.width // 2 - 6, y=console.height // 2 - 2 + self.option_selected, string='►',
                      fg=self.fg_colour)

        console.print(x=console.width // 2 + 5, y=console.height // 2 - 2 + self.option_selected, string='◄',
                      fg=self.fg_colour)

    def ev_keydown(
        self, event: tcod.event.KeyDown
    ) -> Optional[input_handlers.BaseEventHandler]:
        if event.sym == tcod.event.K_ESCAPE:
            raise SystemExit()

        elif event.sym == tcod.event.K_DOWN:
            if self.option_selected < 2:
                self.option_selected += 1
            else:
                self.option_selected = 0

        elif event.sym == tcod.event.K_UP:
            if self.option_selected > 0:
                self.option_selected -= 1
            else:
                self.option_selected = 2

        elif event.sym == tcod.event.K_F1:
            self.subtext = generate_subtext()

        elif event.sym == tcod.event.K_RETURN:
            if self.option_selected == 0:
                return input_handlers.MainGameEventHandler(new_game())
            elif self.option_selected == 1:
                try:
                    return input_handlers.MainGameEventHandler(load_game("savegame.sav"))
                except FileNotFoundError:
                    return input_handlers.PopupMessage(self, "No saved game to load.")
                except Exception as exc:
                    traceback.print_exc()  # Print to stderr.
                    return input_handlers.PopupMessage(self, f"Failed to load save:\n{exc}")
                pass
            elif self.option_selected == 2:
                raise SystemExit()

        return None
