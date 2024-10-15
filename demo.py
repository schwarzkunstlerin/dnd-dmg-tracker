# demo.py

import logging
from battle import Battle, Combatant, AttackAction, DefendAction, MoveAction
from character_sheet import (
    Character,
    PersonalInfo,
    CharacterRole,
    Characteristics,
    Points,
    Experience,
    Skills,
    Talent,
    Weapon,
    Armor,
    CombatStats,
)

# Set up logging to display INFO level messages
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_character(name: str, team: str, is_player: bool = False) -> Combatant:
    # Create personal information
    personal_info = PersonalInfo(
        name=name,
        race='Human',
    )

    # Create character role
    character_role = CharacterRole(
        is_player_character=is_player,
    )

    # Create characteristics
    characteristics = Characteristics(
        weapon_skill=50,
        strength=40,
        toughness=30,
        agility=30,
        initiative=30,
    )

    # Create combat stats
    combat_stats = CombatStats(
        wounds=12,
        armor_points=2,
    )

    # Create equipment
    weapon = Weapon(
        name='Sword',
        damage=5,
        weapon_type='melee',
        weight=3.0,
    )

    # Create talents
    talents = [Talent(name='Strike Mighty Blow')]

    # Create the character
    character = Character(
        identifier=name.lower().replace(' ', '_'),
        personal_info=personal_info,
        character_role=character_role,
        characteristics=characteristics,
        points=Points(),
        experience=Experience(),
        skills=Skills(),
        talents=talents,
        equipment=[weapon],
        combat_stats=combat_stats,
    )

    # Wrap character in a Combatant
    combatant = Combatant(character=character, team=team)
    return combatant


def main():
    # Create combatants
    hero = create_character(name='Aldric', team='Heroes', is_player=True)
    goblin = create_character(name='Goblin', team='Monsters')

    # Initialize battle
    battle = Battle(combatants=[hero, goblin])

    # Start battle
    battle.start_battle()


if __name__ == '__main__':
    main()
