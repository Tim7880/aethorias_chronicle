from app.schemas.item import ItemCreate as ItemCreateSchema
from app.models.item import ItemTypeEnum

PREDEFINED_ITEMS = [
    ItemCreateSchema(name="Backpack", item_type=ItemTypeEnum.ADVENTURING_GEAR, weight=5.0, cost_gp=2.0, properties={"capacity_lbs": 30, "description": "Holds 1 cubic foot or 30 pounds of gear."}),
    ItemCreateSchema(name="Bedroll", item_type=ItemTypeEnum.ADVENTURING_GEAR, weight=7.0, cost_gp=1.0),
    ItemCreateSchema(name="Mess Kit", item_type=ItemTypeEnum.ADVENTURING_GEAR, weight=1.0, cost_gp=0.2),
    ItemCreateSchema(name="Tinderbox", item_type=ItemTypeEnum.ADVENTURING_GEAR, weight=1.0, cost_gp=0.5, properties={"description": "For lighting fires."}),
    ItemCreateSchema(name="Torch", item_type=ItemTypeEnum.ADVENTURING_GEAR, weight=1.0, cost_gp=0.01, properties={"duration_hours": 1, "light_radius_ft": "20 bright, 20 dim"}),
    ItemCreateSchema(name="Rations (1 day)", item_type=ItemTypeEnum.ADVENTURING_GEAR, weight=2.0, cost_gp=0.5),
    ItemCreateSchema(name="Waterskin", item_type=ItemTypeEnum.ADVENTURING_GEAR, weight=5.0, cost_gp=0.2, properties={"capacity_gallons": 0.5, "full_weight_lbs": 5}),
    ItemCreateSchema(name="Rope, Hempen (50 feet)", item_type=ItemTypeEnum.ADVENTURING_GEAR, weight=10.0, cost_gp=1.0),
    ItemCreateSchema(name="Thieves' Tools", item_type=ItemTypeEnum.TOOL, weight=1.0, cost_gp=25.0, properties={"use": "Disarm traps, open locks"}),
    ItemCreateSchema(name="Spellbook (Blank)", item_type=ItemTypeEnum.TOOL, weight=3.0, cost_gp=50.0, properties={"description": "A blank spellbook for wizards."}),
    ItemCreateSchema(name="Dagger", item_type=ItemTypeEnum.WEAPON, weight=1.0, cost_gp=2.0, properties={"damage": "1d4 piercing", "type": "simple melee", "properties": ["finesse", "light", "thrown (range 20/60)"]}),
    ItemCreateSchema(name="Shortsword", item_type=ItemTypeEnum.WEAPON, weight=2.0, cost_gp=10.0, properties={"damage": "1d6 piercing", "type": "martial melee", "properties": ["finesse", "light"]}),
    ItemCreateSchema(name="Longsword", item_type=ItemTypeEnum.WEAPON, weight=3.0, cost_gp=15.0, properties={"damage": "1d8 slashing", "type": "martial melee", "properties": ["versatile (1d10)"]}),
    ItemCreateSchema(name="Light Crossbow", item_type=ItemTypeEnum.WEAPON, weight=5.0, cost_gp=25.0, properties={"damage": "1d8 piercing", "type": "simple ranged", "properties": ["ammunition (range 80/320)", "loading", "two-handed"]}),
    ItemCreateSchema(name="Shortbow", item_type=ItemTypeEnum.WEAPON, weight=2.0, cost_gp=25.0, properties={"damage": "1d6 piercing", "type": "simple ranged", "properties": ["ammunition (range 80/320)", "two-handed"]}),
    ItemCreateSchema(name="Arrows (20)", item_type=ItemTypeEnum.ADVENTURING_GEAR, weight=1.0, cost_gp=1.0),
    ItemCreateSchema(name="Leather Armor", item_type=ItemTypeEnum.ARMOR, weight=10.0, cost_gp=10.0, properties={"ac_base": 11, "armor_type": "light", "dex_bonus": True, "stealth_disadvantage": False}),
    ItemCreateSchema(name="Shield", item_type=ItemTypeEnum.SHIELD, weight=6.0, cost_gp=10.0, properties={"ac_bonus": 2}),
    ItemCreateSchema(name="Potion of Healing", item_type=ItemTypeEnum.POTION, weight=0.5, cost_gp=50.0, properties={"effect": "Restores 2d4+2 hit points."}),
    ItemCreateSchema(name="Potion of Greater Healing", item_type=ItemTypeEnum.POTION, weight=0.5, cost_gp=250.0, properties={"effect": "Restores 4d4+4 hit points."}),
]

