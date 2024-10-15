# character_sheet.py

from dataclasses import dataclass, field
from typing import List, Optional

# Auxiliary Classes

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
    is_player_character: bool = True  # True for PC, False for NPC or 'Mob'

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
class Mutation:
    name: str
    description: Optional[str] = None

@dataclass
class EquipmentItem:
    name: str
    description: Optional[str] = None
    weight: float = 0.0

@dataclass
class Weapon(EquipmentItem):
    damage: int = 0
    weapon_type: str = 'melee'  # e.g., 'melee', 'ranged'

@dataclass
class Armor(EquipmentItem):
    armor_points: int = 0
    location: str = 'body'  # e.g., 'head', 'body', 'arms', 'legs'

@dataclass
class CombatStats:
    initiative: int = 0
    advantage: int = 0
    wounds: int = 0
    max_wounds = int = 0
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

# Main Character Class

@dataclass
class Character:
    identifier: str  # Internal technical name or identifier
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
        """
        Calculates the total encumbrance based on the weight of equipment carried.
        """
        total_weight = sum(item.weight for item in self.equipment)
        self.encumbrance = total_weight
        return self.encumbrance

    def add_equipment(self, item: EquipmentItem):
        """
        Adds an item to the character's equipment and recalculates encumbrance.
        """
        self.equipment.append(item)
        self.calculate_encumbrance()

    def add_condition(self, condition: Condition):
        """
        Adds a condition to the character.
        """
        self.conditions.append(condition)

    def remove_condition(self, condition_name: str):
        """
        Removes a condition from the character by name.
        """
        self.conditions = [cond for cond in self.conditions if cond.name != condition_name]

    # Additional methods for combat, skill checks, etc., can be added here
