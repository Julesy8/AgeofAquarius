from __future__ import annotations

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from entity import Entity, Actor
    from engine import Engine
    from game_map import GameMap


class BaseComponent:
    parent: Entity  # Owning entity instance.

    @property
    def gamemap(self) -> GameMap:
        return self.parent.gamemap

    @property
    def engine(self) -> Engine:
        return self.gamemap.engine


class Fighter(BaseComponent):
    parent: Actor

    # basic class for entities that fight
    def __init__(self,
                 unarmed_meat_damage,
                 unarmed_armour_damage,
                 unarmed_ap_cost: int = 100,
                 move_ap_cost: int = 100,
                 ap: int = 100,
                 ap_per_turn: int = 100,
                 melee_accuracy: float = 1.0,  # more = more accurate
                 ranged_accuracy: float = 1.0,  # less = more accurate
                 move_success_chance: float = 1.0,
                 ):

        self.max_ap = ap
        self._ap = ap
        self.ap_per_turn = ap_per_turn

        self.unarmed_ap_cost = unarmed_ap_cost
        self.move_ap_cost = move_ap_cost
        self.move_ap_original = move_ap_cost

        self.attack_ap_modifier = 1.0
        self.ap_per_turn_modifier = 1.0

        # unarmed melee attack damage
        self.unarmed_meat_damage = unarmed_meat_damage
        self.unarmed_armour_damage = unarmed_armour_damage

        # the base accuracy of the entity. 1 by defualt.
        self.melee_accuracy = melee_accuracy
        self.ranged_accuracy = ranged_accuracy

        # accuracy prior to any status effects being applied
        self.melee_accuracy_original = melee_accuracy
        self.ranged_accuracy_original = ranged_accuracy

        # move success chance changes when limb crippled - i.e. chance to fail moving when leg crippled
        self.move_success_original = move_success_chance
        self.move_success_chance = move_success_chance

    @property
    def ap(self) -> int:
        return self._ap

    @ap.setter
    def ap(self, value: int) -> None:
        self._ap = max(0, min(value, self.max_ap))
        #self._ap = min(value, self.max_ap)
