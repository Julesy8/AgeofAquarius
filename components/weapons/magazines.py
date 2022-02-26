import colour
from entity import Item
from components.consumables import Magazine

glock_mag_9mm = Item(
    x=0, y=0,
    char="m",
    fg_colour=colour.LIGHT_GRAY,
    bg_colour=None,
    name="Glock Magazine 9mm",
    weight=0.2,
    stacking=None,
    description='glock magazine accepting 9mm bullets',
    usable_properties=Magazine(
        magazine_type='glock9mm',
        compatible_bullet_type='9mm',
        mag_capacity=17,
        turns_to_load=1,
        magazine_size='small',
    )
)

magazine_dict = {
    "glock9mm": {
        "mag_items": [glock_mag_9mm],
        "mag_weight": [1]
    }
}

magazine_crafting_dict = {
    "Glock Magazine 9mm - 17 rounds": {
        "required parts": ["material"],
        "compatible parts": [],
        "parts names": ["Material"],
        "item": glock_mag_9mm
    },
}
