import yaml
import os

class BTBLEConstants:
    
    SERVICE_UUID = "7284a451-38b8-4c69-a763-db3a8cb54ab8"
    CHARACTERISTIC_UUID = "31f4e826-9265-46fb-b1a9-f1b1134484ee"

class BTClassicConstants:
    
    SERVICE_UUID = "36b26241-4367-4cc3-94f4-d5a0bd52d9d1"


class AIConstants:

    def load_class_names():
        yaml_file = os.path.join(os.path.dirname(__file__), 'data', 'ai', 'data.yaml')  
        with open(yaml_file, 'r') as file:
            data = yaml.safe_load(file)
            return data['names']  # Return the list of class names

    CLASS_NAMES = load_class_names()
