# battle.py

import random
import logging
from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass, field
from enum import Enum

# Set up logging
logger = logging.getLogger(__name__)

# Assuming that the Character class and related classes have been imported
from character_sheet import Character, PersonalInfo, Weapon, Armor, Talent

# Define the DamageType enumeration
class DamageType(Enum):
    NORMAL = 'normal'             # Reduced by toughness and armor
    IGNORE_ARMOR = 'ignore_armor' # Reduced by toughness only
    PURE = 'pure'                 # Not reduced at all

# Define the Combatant class as a data class since it primarily holds data
@dataclass
class Combatant:
    character: 'Character'
    team: str
    initiative: int = 0
    position: Tuple[int, int] = (0, 0)
    status: Dict[str, Any] = field(default_factory=dict)
    is_active: bool = True  # Indicates if the combatant is still in the battle

    def roll_initiative(self):
        """
        Rolls for initiative at the start of the battle or when required.
        """
        base_initiative = self.character.characteristics.initiative
        roll = random.randint(1, 10)
        self.initiative = base_initiative + roll

        # Apply any talents or conditions that modify initiative
        if any(talent.name == 'Combat Reflexes' for talent in self.character.talents):
            self.initiative += 10

        logger.debug(f"{self.character.personal_info.name} rolls initiative: {self.initiative} (Base: {base_initiative}, Roll: {roll})")

    def is_conscious(self) -> bool:
        """
        Checks if the combatant is conscious and able to act.
        """
        return self.character.combat_stats.wounds > 0

    def decide_action(self, battle: 'Battle') -> 'Action':
        """
        Decides the next action for the combatant.
        For player characters, this might involve player input.
        For NPCs, AI logic is used.
        """
        if self.character.character_role.is_player_character:
            return self.get_player_action(battle)
        else:
            return self.get_ai_action(battle)

    def get_player_action(self, battle: 'Battle') -> 'Action':
        """
        Prompts the player to choose an action.
        """
        logger.info(f"{self.character.personal_info.name}'s turn.")
        logger.info("Choose an action:")
        logger.info("1. Attack")
        logger.info("2. Move")
        logger.info("3. Defend")
        choice = input("Enter the number of your action choice: ")
        if choice == '1':
            target = self.find_target(battle)
            if target:
                # Prompt for damage type
                logger.info("Choose damage type:")
                logger.info("1. Normal (reduced by toughness and armor)")
                logger.info("2. Ignore Armor (reduced by toughness only)")
                logger.info("3. Pure (not reduced at all)")
                damage_choice = input("Enter the number of the damage type: ")
                if damage_choice == '1':
                    damage_type = DamageType.NORMAL
                elif damage_choice == '2':
                    damage_type = DamageType.IGNORE_ARMOR
                elif damage_choice == '3':
                    damage_type = DamageType.PURE
                else:
                    logger.warning("Invalid choice. Defaulting to Normal damage.")
                    damage_type = DamageType.NORMAL
                return AttackAction(actor=self, target=target, damage_type=damage_type)
            else:
                logger.info("No targets available.")
                return DefendAction(actor=self)
        elif choice == '2':
            # For simplicity, moving to a default position
            destination = (0, 0)
            return MoveAction(actor=self, destination=destination)
        elif choice == '3':
            return DefendAction(actor=self)
        else:
            logger.warning("Invalid choice. Defaulting to Defend.")
            return DefendAction(actor=self)

    def get_ai_action(self, battle: 'Battle') -> 'Action':
        """
        AI logic for NPC actions.
        """
        target = self.find_target(battle)
        if target:
            # AI can select damage type based on logic; we'll default to NORMAL
            damage_type = DamageType.NORMAL
            return AttackAction(actor=self, target=target, damage_type=damage_type)
        else:
            return DefendAction(actor=self)

    def find_target(self, battle: 'Battle') -> Optional['Combatant']:
        """
        Finds the nearest enemy combatant.
        """
        enemies = [c for c in battle.combatants if c.team != self.team and c.is_conscious()]
        if enemies:
            # For simplicity, pick the first enemy
            return enemies[0]
        else:
            return None

    def decide_defense_method(self) -> str:
        """
        Allows the defender to choose a defense method: 'parry', 'dodge', or 'special'.
        """
        if self.character.character_role.is_player_character:
            return self.get_player_defense_choice()
        else:
            return self.get_ai_defense_choice()

    def get_player_defense_choice(self) -> str:
        """
        Prompts the player to choose a defense method.
        """
        logger.info(f"{self.character.personal_info.name}, how do you want to defend?")
        logger.info("1. Parry")
        logger.info("2. Dodge")
        logger.info("3. Use Special Skill")
        choice = input("Choose your defense method (1-3): ")
        if choice == '1':
            return 'parry'
        elif choice == '2':
            return 'dodge'
        elif choice == '3':
            return 'special'
        else:
            logger.warning("Invalid choice. Defaulting to Dodge.")
            return 'dodge'

    def get_ai_defense_choice(self) -> str:
        """
        AI logic for choosing a defense method.
        """
        # Simple logic: choose the method with the highest chance of success
        parry_skill = self.character.characteristics.weapon_skill
        dodge_skill = self.character.characteristics.agility

        if parry_skill >= dodge_skill:
            return 'parry'
        else:
            return 'dodge'

@dataclass
class Action:
    actor: Combatant

    def execute(self):
        """
        Executes the action.
        """
        raise NotImplementedError("Execute method must be implemented in subclasses.")

@dataclass
class MoveAction(Action):
    destination: Tuple[int, int]

    def execute(self):
        """
        Moves the actor to the destination, considering movement allowance.
        """
        logger.info(f"{self.actor.character.personal_info.name} moves from {self.actor.position} to {self.destination}.")
        self.actor.position = self.destination

@dataclass
class AttackAction(Action):
    target: Combatant
    damage_type: DamageType = DamageType.NORMAL  # Default to NORMAL damage type

    def execute(self):
        """
        Executes an attack action against the target, allowing the defender to attempt defense.
        """
        attacker = self.actor.character
        defender = self.target.character

        logger.info(f"{attacker.personal_info.name} attacks {defender.personal_info.name}!")

        # Attacker rolls to hit
        attack_roll = random.randint(1, 100)
        attacker_ws = attacker.characteristics.weapon_skill

        if attack_roll <= attacker_ws:
            logger.info(f"Hit! (Attacker Roll: {attack_roll}, WS: {attacker_ws})")

            # Defender decides how to defend
            defense_method = self.target.decide_defense_method()
            defense_success = False

            if defense_method == 'parry':
                defense_success = self.attempt_parry(defender, attacker_ws)
            elif defense_method == 'dodge':
                defense_success = self.attempt_dodge(defender)
            elif defense_method == 'special':
                defense_success = self.attempt_special_defense(defender)
            else:
                logger.warning(f"Unknown defense method chosen by {defender.personal_info.name}.")

            if defense_success:
                logger.info(f"{defender.personal_info.name} successfully defended against the attack!")
                return  # Attack is defended; no damage applied
            else:
                logger.info(f"{defender.personal_info.name} failed to defend.")
                # Proceed to damage calculation
                self.apply_damage(attacker, defender)
        else:
            logger.info(f"Missed! (Attacker Roll: {attack_roll}, WS: {attacker_ws})")

    def attempt_parry(self, defender: Character, attacker_ws: int) -> bool:
        """
        Defender attempts to parry using Weapon Skill.
        """
        defender_ws = defender.characteristics.weapon_skill
        parry_roll = random.randint(1, 100)
        logger.info(f"{defender.personal_info.name} attempts to parry (Roll: {parry_roll}, WS: {defender_ws})")
        return parry_roll <= defender_ws

    def attempt_dodge(self, defender: Character) -> bool:
        """
        Defender attempts to dodge using Dodge skill or Agility.
        """
        # For simplicity, we'll use Agility as the dodge skill
        defender_agility = defender.characteristics.agility
        dodge_roll = random.randint(1, 100)
        logger.info(f"{defender.personal_info.name} attempts to dodge (Roll: {dodge_roll}, Agility: {defender_agility})")
        return dodge_roll <= defender_agility

    def attempt_special_defense(self, defender: Character) -> bool:
        """
        Defender attempts to use a special skill to defend.
        """
        # Placeholder implementation; can be expanded based on specific skills
        logger.info(f"{defender.personal_info.name} attempts to use a special defense skill.")
        # For now, we'll assume the special defense always fails
        return False

    def apply_damage(self, attacker: Character, defender: Character):
        """
        Calculates and applies damage to the defender.
        """
        weapon = self.get_equipped_weapon(attacker)
        if weapon:
            base_damage = weapon.damage + (attacker.characteristics.strength // 10)
            # Apply talents (e.g., 'Strike Mighty Blow')
            if any(talent.name == 'Strike Mighty Blow' for talent in attacker.talents):
                base_damage += 1
            # Apply damage with specified damage type
            net_damage = self.calculate_net_damage(defender, base_damage, self.damage_type)
            defender.combat_stats.wounds = max(defender.combat_stats.wounds - net_damage, 0)
            logger.info(f"{defender.personal_info.name} takes {net_damage} damage, now at {defender.combat_stats.wounds} wounds.")
        else:
            logger.warning(f"{attacker.personal_info.name} has no weapon equipped!")

    def get_equipped_weapon(self, character: Character) -> Optional[Weapon]:
        weapons = [item for item in character.equipment if isinstance(item, Weapon)]
        return weapons[0] if weapons else None

    @staticmethod
    def calculate_net_damage_static(defender: Character, base_damage: int, damage_type: DamageType) -> int:
        toughness_bonus = defender.characteristics.toughness // 10
        armor_points = defender.combat_stats.armor_points

        if damage_type == DamageType.NORMAL:
            damage_reduction = toughness_bonus + armor_points
        elif damage_type == DamageType.IGNORE_ARMOR:
            damage_reduction = toughness_bonus
        elif damage_type == DamageType.PURE:
            damage_reduction = 0
        else:
            damage_reduction = toughness_bonus + armor_points  # Default to normal

        net_damage = max(base_damage - damage_reduction, 0)
        return net_damage

@dataclass
class DefendAction(Action):
    def execute(self):
        """
        Executes a defend action, possibly increasing defensive stats.
        """
        logger.info(f"{self.actor.character.personal_info.name} takes a defensive stance.")

@dataclass
class UseSkillAction(Action):
    skill_name: str

    def execute(self):
        """
        Uses a skill.
        """
        logger.info(f"{self.actor.character.personal_info.name} uses skill: {self.skill_name}.")

class Battle:
    def __init__(self, combatants: List[Combatant]):
        self.combatants = combatants
        self.round_number = 0
        self.turn_order: List[Combatant] = []

    def start_battle(self):
        """
        Initiates the battle sequence.
        """
        logger.info("Battle begins!")
        self.determine_initiative()
        self.round_number = 1
        while not self.is_battle_over():
            logger.info(f"--- Round {self.round_number} ---")
            self.execute_round()
            self.round_number += 1
        logger.info("Battle has ended.")

    def determine_initiative(self):
        """
        Determines the initiative order for all combatants.
        """
        logger.debug("Determining initiative order...")
        for combatant in self.combatants:
            combatant.roll_initiative()
        # Sort combatants by initiative
        self.turn_order = sorted(self.combatants, key=lambda c: c.initiative, reverse=True)
        logger.info("Initiative order:")
        for idx, combatant in enumerate(self.turn_order, start=1):
            logger.info(f"{idx}. {combatant.character.personal_info.name} (Initiative: {combatant.initiative})")

    def execute_round(self):
        """
        Executes a single round of combat, iterating through the turn order.
        """
        for combatant in self.turn_order:
            if combatant.is_active and combatant.is_conscious():
                self.execute_turn(combatant)
            elif not combatant.is_conscious():
                logger.info(f"{combatant.character.personal_info.name} is unconscious and cannot act.")

    def execute_turn(self, combatant: Combatant):
        """
        Executes a single turn for the given combatant.
        """
        logger.debug(f"Executing turn for {combatant.character.personal_info.name}.")
        action = combatant.decide_action(self)
        action.execute()

    def is_battle_over(self) -> bool:
        """
        Checks if the battle has ended based on remaining teams.
        """
        active_teams = set()
        for combatant in self.combatants:
            if combatant.is_active and combatant.is_conscious():
                active_teams.add(combatant.team)
        if len(active_teams) <= 1:
            logger.info(f"Battle over. Remaining team: {active_teams}")
            return True
        return False
