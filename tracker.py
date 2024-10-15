# tracker.py

import sys
import os
import json  # For serialization
from PyQt5.QtWidgets import (
    QApplication, QWidget, QMainWindow, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QComboBox, QTableWidget,
    QTableWidgetItem, QMessageBox, QInputDialog, QFileDialog, QAction
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt

# Import your existing classes
from character_sheet import Character, PersonalInfo, CharacterRole, Characteristics, Points, Experience, Skills, Talent, \
    Weapon, Armor, CombatStats, Condition, EquipmentItem
from battle import Combatant, DamageType, AttackAction


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Warhammer Fantasy Battle Tracker")
        # Set up the icon
        script_dir = os.path.dirname(os.path.realpath(__file__))
        icon_path = os.path.join(script_dir, 'img/whfrp-tracker.ico')
        self.setWindowIcon(QIcon(icon_path))
        self.combatants = []  # List of Combatant objects
        self.init_ui()

    def init_ui(self):
        # Set up the menu bar
        self.create_menu()

        # Main widget and layout
        main_widget = QWidget()
        main_layout = QVBoxLayout()

        # Character table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Name", "Team", "Initiative", "Wounds", "Status", "Conditions"])
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        main_layout.addWidget(self.table)

        # Controls layout
        controls_layout = QHBoxLayout()

        # Add Character Button
        self.add_character_button = QPushButton("Add Character")
        self.add_character_button.clicked.connect(self.add_character)
        controls_layout.addWidget(self.add_character_button)

        # Damage Input
        self.damage_input = QLineEdit()
        self.damage_input.setPlaceholderText("Damage Amount")
        controls_layout.addWidget(self.damage_input)

        # Damage Type ComboBox
        self.damage_type_combo = QComboBox()
        self.damage_type_combo.addItems(["Normal", "Ignore Armor", "Pure"])
        controls_layout.addWidget(self.damage_type_combo)

        # Condition Input
        self.condition_input = QLineEdit()
        self.condition_input.setPlaceholderText("Condition (Optional)")
        controls_layout.addWidget(self.condition_input)

        # Apply Damage Button
        self.apply_damage_button = QPushButton("Apply Damage/Condition")
        self.apply_damage_button.clicked.connect(self.apply_damage)
        controls_layout.addWidget(self.apply_damage_button)

        main_layout.addLayout(controls_layout)
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

    def create_menu(self):
        # Create a menu bar
        menu_bar = self.menuBar()

        # Create Options menu
        options_menu = menu_bar.addMenu("Opcje")  # "Opcje" means "Options" in Polish

        # Create Import Battle action
        import_action = QAction("Zaimportuj Walkę", self)  # "Import Battle"
        import_action.triggered.connect(self.import_battle)
        options_menu.addAction(import_action)

        # Create Export Battle action
        export_action = QAction("Wyeksportuj Walkę", self)  # "Export Battle"
        export_action.triggered.connect(self.export_battle)
        options_menu.addAction(export_action)

    def add_character(self):
        name, ok = QInputDialog.getText(self, "Add Character", "Character Name:")
        if not ok or not name:
            return

        team, ok = QInputDialog.getText(self, "Add Character", "Team Name:")
        if not ok or not team:
            return

        # For simplicity, we'll generate random characteristics
        import random
        personal_info = PersonalInfo(name=name)
        character_role = CharacterRole()
        characteristics = Characteristics(
            weapon_skill=random.randint(30, 60),
            strength=random.randint(30, 60),
            toughness=random.randint(30, 60),
            agility=random.randint(30, 60),
            initiative=random.randint(30, 60)
        )
        combat_stats = CombatStats(
            wounds=random.randint(10, 20),
            armor_points=random.randint(0, 5)
        )
        talents = [Talent(name='Strike Mighty Blow')]
        weapon = Weapon(
            name='Sword',
            damage=5,
            weapon_type='melee',
            weight=3.0,
        )
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
        combatant = Combatant(character=character, team=team)
        combatant.roll_initiative()
        self.combatants.append(combatant)
        self.update_table()

    def update_table(self):
        # Sort combatants by initiative
        self.combatants.sort(key=lambda c: c.initiative, reverse=True)

        self.table.setRowCount(len(self.combatants))
        for row, combatant in enumerate(self.combatants):
            character = combatant.character
            # Name
            name_item = QTableWidgetItem(character.personal_info.name)
            self.table.setItem(row, 0, name_item)
            # Team
            team_item = QTableWidgetItem(combatant.team)
            self.table.setItem(row, 1, team_item)
            # Initiative
            initiative_item = QTableWidgetItem(str(combatant.initiative))
            self.table.setItem(row, 2, initiative_item)
            # Wounds
            wounds_item = QTableWidgetItem(str(character.combat_stats.wounds))
            self.table.setItem(row, 3, wounds_item)
            # Status
            status = "Active" if combatant.is_active and combatant.is_conscious() else "Unconscious"
            status_item = QTableWidgetItem(status)
            self.table.setItem(row, 4, status_item)
            # Conditions
            conditions = ", ".join([cond.name for cond in character.conditions]) if character.conditions else "None"
            conditions_item = QTableWidgetItem(conditions)
            self.table.setItem(row, 5, conditions_item)

    def apply_damage(self):
        # Ensure a character is selected
        selected_items = self.table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Please select a character from the table.")
            return
        row = selected_items[0].row()
        combatant = self.combatants[row]
        character = combatant.character

        # Get damage amount
        try:
            damage_amount = int(self.damage_input.text())
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Please enter a valid damage amount.")
            return

        # Get damage type
        damage_type_str = self.damage_type_combo.currentText()
        if damage_type_str == "Normal":
            damage_type = DamageType.NORMAL
        elif damage_type_str == "Ignore Armor":
            damage_type = DamageType.IGNORE_ARMOR
        elif damage_type_str == "Pure":
            damage_type = DamageType.PURE
        else:
            damage_type = DamageType.NORMAL  # Default

        # Apply damage
        # We'll reuse the calculate_net_damage_static method from AttackAction
        base_damage = damage_amount
        net_damage = AttackAction.calculate_net_damage_static(character, base_damage, damage_type)
        character.combat_stats.wounds = max(character.combat_stats.wounds - net_damage, 0)

        # Apply condition if any
        condition_name = self.condition_input.text()
        if condition_name:
            condition = Condition(name=condition_name)
            character.add_condition(condition)

        # Update status if character is unconscious
        if character.combat_stats.wounds <= 0:
            combatant.is_active = False

        # Clear inputs
        self.damage_input.clear()
        self.condition_input.clear()

        # Update table
        self.update_table()

    def export_battle(self):
        """
        Exports the current battle state to a JSON file.
        """
        options = QFileDialog.Options()
        filename, _ = QFileDialog.getSaveFileName(self, "Wyeksportuj Walkę", "", "JSON Files (*.json)", options=options)
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as file:
                    data = [self.combatant_to_dict(combatant) for combatant in self.combatants]
                    json.dump(data, file, ensure_ascii=False, indent=4)
                QMessageBox.information(self, "Success", "Battle exported successfully.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export battle: {e}")

    def import_battle(self):
        """
        Imports a battle state from a JSON file.
        """
        options = QFileDialog.Options()
        filename, _ = QFileDialog.getOpenFileName(self, "Zaimportuj Walkę", "", "JSON Files (*.json)", options=options)
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                    self.combatants = [self.dict_to_combatant(c_data) for c_data in data]
                self.update_table()
                QMessageBox.information(self, "Success", "Battle imported successfully.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to import battle: {e}")

    def combatant_to_dict(self, combatant: Combatant) -> dict:
        """
        Serializes a Combatant object to a dictionary.
        """
        character = combatant.character
        return {
            'team': combatant.team,
            'initiative': combatant.initiative,
            'is_active': combatant.is_active,
            'personal_info': character.personal_info.__dict__,
            'characteristics': character.characteristics.__dict__,
            'combat_stats': character.combat_stats.__dict__,
            'conditions': [cond.__dict__ for cond in character.conditions],
            'talents': [talent.__dict__ for talent in character.talents],
            'equipment': [item.__dict__ for item in character.equipment],
            'status': combatant.status
        }

    def dict_to_combatant(self, data: dict) -> Combatant:
        """
        Deserializes a dictionary to a Combatant object.
        """
        personal_info = PersonalInfo(**data['personal_info'])
        characteristics = Characteristics(**data['characteristics'])
        combat_stats = CombatStats(**data['combat_stats'])
        conditions = [Condition(**cond_data) for cond_data in data.get('conditions', [])]
        talents = [Talent(**talent_data) for talent_data in data.get('talents', [])]
        equipment = []
        for item_data in data.get('equipment', []):
            if 'damage' in item_data:
                equipment.append(Weapon(**item_data))
            elif 'armor_points' in item_data:
                equipment.append(Armor(**item_data))
            else:
                equipment.append(EquipmentItem(**item_data))
        character = Character(
            identifier=personal_info.name.lower().replace(' ', '_'),
            personal_info=personal_info,
            character_role=CharacterRole(),
            characteristics=characteristics,
            points=Points(),
            experience=Experience(),
            skills=Skills(),
            talents=talents,
            equipment=equipment,
            combat_stats=combat_stats,
            conditions=conditions,
        )
        combatant = Combatant(
            character=character,
            team=data['team'],
            initiative=data['initiative'],
            is_active=data['is_active'],
            status=data.get('status', {})
        )
        return combatant


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
