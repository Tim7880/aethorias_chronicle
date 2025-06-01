// Path: src/types/user.ts

// This should match the Pydantic User schema returned by your backend's /users/me
// (excluding sensitive info like hashed_password)
export interface User {
  id: number;
  username: string;
  email: string;
  preferred_timezone: string | null;
  is_active: boolean;
  is_superuser: boolean;
  created_at: string; // Typically string in ISO format from JSON
  updated_at: string; // Typically string in ISO format from JSON
  // Add other fields that /users/me returns, e.g., from CharacterBase if it's nested
  // For now, let's keep it to the User model's direct fields from UserSchema
}