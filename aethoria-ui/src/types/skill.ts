// Path: src/types/skill.ts

// Corresponds to backend's schemas.skill.Skill
export interface SkillDefinition {
  id: number;
  name: string;
  ability_modifier_name: string;
  description?: string | null;
}

// Corresponds to backend's schemas.skill.CharacterSkill
export interface CharacterSkill {
  id: number; // ID of the CharacterSkill association
  skill_id: number;
  is_proficient: boolean;
  has_expertise: boolean;
  skill_definition: SkillDefinition; // Nested skill details
}