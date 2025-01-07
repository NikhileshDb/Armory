

from datetime import datetime
import logging

from services.db_service import get_category_attribute_data_by_name, insert_category, insert_category_attributes, get_all_categories
import json
attr = {
    "material_code": "M002",
    "nomenclature": "ABC02",
    "section": "Z2",
    "main_equipment": "ME02"
}


# insert the categories if the category is not in the table  and then get all the categories, add the attributes to the
# which takes  categoryId: Any, data: Any
# categories takes arg
# name: Any,
# description: Any,
# added_date: Any,
# is_active: bool = False


def add_categoris_to_table():

    predefined_categories = [
        {
            "name": "car",
            "description": "Four wheeler",
            "is_active": True
        },
        {
            "name": "bicycle",
            "description": "Two wheeler",
            "is_active": True
        },
        {
            "name": "bottle",
            "description": "",
            "is_active": True
        },
        {
            "name": "pencil",
            "description": "",
            "is_active": True
        },
        {
            "name": "phone",
            "description": "",
            "is_active": True
        }
    ]
    categories = get_all_categories()

    # If no categories exist, insert predefined ones
    if len(categories) == 0:

        # Insert the predefined categories
        for category in predefined_categories:
            timing = datetime.now().timestamp()
            insert_category(category["name"],
                            category["description"], timing, True)

    # If there are less than 5 categories, insert missing ones
    elif len(categories) < 5:
        all_cat = get_all_categories()  # Fetch all categories from DB
        # Get the names of existing categories
        existing_names = [cat['name'] for cat in all_cat]

        for category in predefined_categories:
            if category["name"] not in existing_names:
                timing = datetime.now().timestamp()
                insert_category(category["name"],
                                category["description"], timing, True)


def add_attr_to_categories():
    all_cat = get_all_categories()
    for cat in all_cat:
        res_attr = get_category_attribute_data_by_name(cat["name"])

        if res_attr is None:
            # Use single quotes for the f-string
            attr = {
                "material_code": f"M00{cat['id']}",
                "nomenclature": f"ABC0{cat['id']}",
                "section": f"Z{cat['id']}",
                "main_equipment": f"ME0{cat['id']}"
            }

            # Convert attributes to JSON format
            # attj = json.dumps(attr)

            # Assuming `id` is defined somewhere, otherwise it will raise an error
            insert_category_attributes(cat['id'], attr)


def populate_database():
    logging.info(
        "****************8Populating Categoies and Attriutes**************")
    add_categoris_to_table()
    add_attr_to_categories()
