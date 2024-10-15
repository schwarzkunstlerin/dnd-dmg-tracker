# character_io.py

import json
import logging
from dataclasses import is_dataclass, fields
from typing import Any, Type, TypeVar, List, Dict, get_type_hints

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import the Character class and related classes
from character_sheet import Character  # Replace 'your_module' with the actual module name

T = TypeVar('T')

def dataclass_to_dict(obj: Any) -> Any:
    """
    Recursively converts a dataclass object to a dictionary, handling nested dataclasses.
    """
    if is_dataclass(obj):
        return {
            field.name: dataclass_to_dict(getattr(obj, field.name))
            for field in fields(obj)
        }
    elif isinstance(obj, (list, tuple)):
        return [dataclass_to_dict(item) for item in obj]
    elif isinstance(obj, dict):
        return {
            key: dataclass_to_dict(value)
            for key, value in obj.items()
        }
    else:
        return obj

def dict_to_dataclass(data: Any, cls: Type[T]) -> T:
    """
    Recursively converts a dictionary to a dataclass object, handling nested dataclasses.
    """
    if not isinstance(data, dict):
        return data

    try:
        field_types = {field.name: field.type for field in fields(cls)}
        init_kwargs = {}
        for field_name, field_type in field_types.items():
            if field_name not in data:
                continue  # Field missing in data; you may set a default value if necessary

            field_value = data[field_name]

            if is_dataclass(field_type):
                # Nested dataclass
                init_kwargs[field_name] = dict_to_dataclass(field_value, field_type)
            elif hasattr(field_type, '__origin__'):
                origin = field_type.__origin__
                if origin is list:
                    item_type = field_type.__args__[0]
                    init_kwargs[field_name] = [
                        dict_to_dataclass(item, item_type) for item in field_value
                    ]
                elif origin is dict:
                    key_type, value_type = field_type.__args__
                    init_kwargs[field_name] = {
                        dict_to_dataclass(k, key_type): dict_to_dataclass(v, value_type)
                        for k, v in field_value.items()
                    }
                else:
                    # Other generic types
                    init_kwargs[field_name] = field_value
            else:
                # Basic type
                init_kwargs[field_name] = field_value

        return cls(**init_kwargs)
    except Exception as e:
        logger.error(f"Error deserializing {cls.__name__}: {e}")
        raise

def save_character_to_json(character: Character, filename: str):
    """
    Saves a Character object to a JSON file.
    """
    character_dict = dataclass_to_dict(character)
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(character_dict, f, ensure_ascii=False, indent=4)
        logger.info(f"Character saved to {filename}")
    except Exception as e:
        logger.error(f"Error saving character to {filename}: {e}")
        raise

def load_character_from_json(filename: str) -> Character:
    """
    Loads a Character object from a JSON file.
    """
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        character = dict_to_dataclass(data, Character)
        logger.info(f"Character loaded from {filename}")
        return character
    except Exception as e:
        logger.error(f"Error loading character from {filename}: {e}")
        raise
