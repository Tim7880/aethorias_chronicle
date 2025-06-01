// Path: src/types/item.ts

// Using a string literal union type for type safety
export type FrontendItemType = 
    | "weapon"
    | "armor"
    | "shield"
    | "adventuring_gear"
    | "tool"
    | "potion"
    | "scroll"
    | "wand"
    | "ring"
    | "wondrous_item"
    | "currency"
    | "other";

// Optional: If you need an object to iterate over values (e.g., for a dropdown)
export const FrontendItemTypeEnumObject = {
    WEAPON: "weapon",
    ARMOR: "armor",
    SHIELD: "shield",
    ADVENTURING_GEAR: "adventuring_gear",
    TOOL: "tool",
    POTION: "potion",
    SCROLL: "scroll",
    WAND: "wand",
    RING: "ring",
    WONDROUS_ITEM: "wondrous_item",
    CURRENCY: "currency",
    OTHER: "other"
} as const; // 'as const' makes keys readonly and values literal types

export interface ItemDefinition {
  id: number;
  name: string;
  description?: string | null;
  item_type: FrontendItemType; // Use the string literal union type
  weight?: number | null;
  cost_gp?: number | null;
  properties?: any | null; 
}

export interface CharacterItem {
  id: number; 
  item_id: number;
  quantity: number;
  is_equipped: boolean;
  item_definition: ItemDefinition; 
}