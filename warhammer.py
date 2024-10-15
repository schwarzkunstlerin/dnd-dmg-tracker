# warhammer.py

import random
import logging
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional, Any

# Set up logging
logger = logging.getLogger(__name__)

# Data Classes for Character Attributes


# Placeholder for Mutation class used in Character
@dataclass
class Mutation:
    name: str
    description: Optional[str] = None


@dataclass
class PersonalInfo:
    name: str
    nickname: Optional[str] = None
    surname: Optional[str] = None
    gender: Optional[str] = None
    race: Optional[str] = None
    origin_country: Optional[str] = None
    origin_region: Optional[str] = None
    age: Optional[int] = None
    height: Optional[int] = None
    hair_color: Optional[str] = None
    eye_color: Optional[str] = None
    distinctive_features: Optional[str] = None
    character_description: Optional[str] = None
    appearance_description: Optional[str] = None

@dataclass
class CharacterRole:
    character_class: Optional[str] = None
    profession: Optional[str] = None
    profession_level: Optional[int] = None
    profession_path: Optional[str] = None
    status: Optional[str] = None
    is_player_character: bool = True

@dataclass
class Characteristics:
    weapon_skill: int = 0
    ballistic_skill: int = 0
    strength: int = 0
    toughness: int = 0
    initiative: int = 0
    agility: int = 0
    dexterity: int = 0
    intelligence: int = 0
    willpower: int = 0
    fellowship: int = 0

@dataclass
class Points:
    hero_points: int = 0
    determination_points: int = 0
    fate_points: int = 0
    fortune_points: int = 0
    sin_points: int = 0
    warp_points: int = 0
    insanity_points: int = 0

@dataclass
class Experience:
    current: int = 0
    spent: int = 0
    total: int = 0

@dataclass
class Skills:
    basic_skills: List[str] = field(default_factory=list)
    advanced_skills: List[str] = field(default_factory=list)
    combat_skills: List[str] = field(default_factory=list)

@dataclass
class Talent:
    name: str
    description: Optional[str] = None
    effects: List[str] = field(default_factory=list)

@dataclass
class EquipmentItem:
    name: str
    description: Optional[str] = None
    weight: float = 0.0

@dataclass
class Weapon(EquipmentItem):
    damage: int = 0
    weapon_type: str = 'melee'

@dataclass
class Armor(EquipmentItem):
    armor_points: int = 0
    location: str = 'body'

@dataclass
class CombatStats:
    initiative: int = 0
    advantage: int = 0
    wounds: int = 0
    mana_points: int = 0
    speed: int = 0
    walk: int = 0
    run: int = 0
    armor_points: int = 0

@dataclass
class Condition:
    name: str
    description: Optional[str] = None

@dataclass
class SpecialEffect:
    name: str
    description: Optional[str] = None

@dataclass
class Character:
    identifier: str
    personal_info: PersonalInfo
    character_role: CharacterRole
    characteristics: Characteristics
    points: Points
    experience: Experience
    skills: Skills
    talents: List[Talent] = field(default_factory=list)
    physical_mutations: List[Mutation] = field(default_factory=list)
    mental_mutations: List[Mutation] = field(default_factory=list)
    equipment: List[EquipmentItem] = field(default_factory=list)
    combat_stats: CombatStats = field(default_factory=CombatStats)
    conditions: List[Condition] = field(default_factory=list)
    special_effects: List[SpecialEffect] = field(default_factory=list)
    wealth: int = 0
    encumbrance: float = 0.0
    spells: List[str] = field(default_factory=list)

    def calculate_encumbrance(self) -> float:
        total_weight = sum(item.weight for item in self.equipment)
        self.encumbrance = total_weight
        return self.encumbrance

    def add_equipment(self, item: EquipmentItem):
        self.equipment.append(item)
        self.calculate_encumbrance()

    def add_condition(self, condition: Condition):
        self.conditions.append(condition)

    def remove_condition(self, condition_name: str):
        self.conditions = [cond for cond in self.conditions if cond.name != condition_name]

# Combat Classes

@dataclass
class Combatant:
    character: Character
    team: str
    initiative: int = 0
    position: Tuple[int, int] = (0, 0)
    status: Dict[str, Any] = field(default_factory=dict)
    is_active: bool = True

    def roll_initiative(self):
        base_initiative = self.character.characteristics.initiative
        roll = random.randint(1, 10)
        self.initiative = base_initiative + roll

        if any(talent.name == 'Combat Reflexes' for talent in self.character.talents):
            self.initiative += 10

        logger.debug(f"{self.character.personal_info.name} rolls initiative: {self.initiative} (Base: {base_initiative}, Roll: {roll})")

    def is_conscious(self) -> bool:
        return self.character.combat_stats.wounds > 0

    def decide_action(self, battle: 'Battle') -> 'Action':
        if self.character.character_role.is_player_character:
            return self.get_player_action(battle)
        else:
            return self.get_ai_action(battle)

    def get_player_action(self, battle: 'Battle') -> 'Action':
        # For demo purposes, automatically choose to attack if possible
        logger.info(f"{self.character.personal_info.name}'s turn.")
        target = self.find_target(battle)
        if target:
            return AttackAction(actor=self, target=target)
        else:
            return DefendAction(actor=self)

    def get_ai_action(self, battle: 'Battle') -> 'Action':
        target = self.find_target(battle)
        if target:
            return AttackAction(actor=self, target=target)
        else:
            return DefendAction(actor=self)

    def find_target(self, battle: 'Battle') -> Optional['Combatant']:
        enemies = [c for c in battle.combatants if c.team != self.team and c.is_conscious()]
        if enemies:
            return enemies[0]
        else:
            return None

@dataclass
class Action:
    actor: Combatant

    def execute(self):
        raise NotImplementedError("Execute method must be implemented in subclasses.")

@dataclass
class MoveAction(Action):
    destination: Tuple[int, int]

    def execute(self):
        logger.info(f"{self.actor.character.personal_info.name} moves from {self.actor.position} to {self.destination}.")
        self.actor.position = self.destination

@dataclass
class AttackAction(Action):
    target: Combatant

    def execute(self):
        attacker = self.actor.character
        defender = self.target.character

        logger.info(f"{attacker.personal_info.name} attacks {defender.personal_info.name}!")

        # Roll to hit
        attack_roll = random.randint(1, 100)
        ws = attacker.characteristics.weapon_skill

        if attack_roll <= ws:
            logger.info(f"Hit! (Roll: {attack_roll}, WS: {ws})")
            # Calculate damage
            weapon = self.get_equipped_weapon(attacker)
            if weapon:
                base_damage = weapon.damage + (attacker.characteristics.strength // 10)
                # Apply talents
                if any(talent.name == 'Strike Mighty Blow' for talent in attacker.talents):
                    base_damage += 1
                # Apply damage
                net_damage = self.apply_damage(defender, base_damage)
                logger.info(f"{defender.personal_info.name} takes {net_damage} damage, now at {defender.combat_stats.wounds} wounds.")
            else:
                logger.warning(f"{attacker.personal_info.name} has no weapon equipped!")
        else:
            logger.info(f"Missed! (Roll: {attack_roll}, WS: {ws})")

    def get_equipped_weapon(self, character: Character) -> Optional[Weapon]:
        weapons = [item for item in character.equipment if isinstance(item, Weapon)]
        return weapons[0] if weapons else None

    def apply_damage(self, defender: Character, damage: int) -> int:
        toughness_bonus = defender.characteristics.toughness // 10
        armor_points = defender.combat_stats.armor_points
        damage_reduction = toughness_bonus + armor_points
        net_damage = max(damage - damage_reduction, 0)
        defender.combat_stats.wounds = max(defender.combat_stats.wounds - net_damage, 0)
        return net_damage

@dataclass
class DefendAction(Action):
    def execute(self):
        logger.info(f"{self.actor.character.personal_info.name} takes a defensive stance.")

class Battle:
    def __init__(self, combatants: List[Combatant]):
        self.combatants = combatants
        self.round_number = 0
        self.turn_order: List[Combatant] = []

    def start_battle(self):
        logger.info("Battle begins!")
        self.determine_initiative()
        self.round_number = 1
        while not self.is_battle_over():
            logger.info(f"--- Round {self.round_number} ---")
            self.execute_round()
            self.round_number += 1
        logger.info("Battle has ended.")

    def determine_initiative(self):
        logger.debug("Determining initiative order...")
        for combatant in self.combatants:
            combatant.roll_initiative()
        self.turn_order = sorted(self.combatants, key=lambda c: c.initiative, reverse=True)
        logger.info("Initiative order:")
        for idx, combatant in enumerate(self.turn_order, start=1):
            logger.info(f"{idx}. {combatant.character.personal_info.name} (Initiative: {combatant.initiative})")

    def execute_round(self):
        for combatant in self.turn_order:
            if combatant.is_active and combatant.is_conscious():
                self.execute_turn(combatant)
            elif not combatant.is_conscious():
                logger.info(f"{combatant.character.personal_info.name} is unconscious and cannot act.")

    def execute_turn(self, combatant: Combatant):
        logger.debug(f"Executing turn for {combatant.character.personal_info.name}.")
        action = combatant.decide_action(self)
        action.execute()

    def is_battle_over(self) -> bool:
        active_teams = set()
        for combatant in self.combatants:
            if combatant.is_active and combatant.is_conscious():
                active_teams.add(combatant.team)
        if len(active_teams) <= 1:
            logger.info(f"Battle over. Remaining team: {active_teams}")
            return True
        return False
