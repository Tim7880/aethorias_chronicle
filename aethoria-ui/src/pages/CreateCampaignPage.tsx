// Path: src/pages/CreateCampaignPage.tsx
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { campaignService } from '../services/campaignService';
import type { CampaignCreatePayload } from '../types/campaign';
import ThemedInput from '../components/common/ThemedInput';
import ThemedButton from '../components/common/ThemedButton';
import styles from './CreateCampaignPage.module.css';

const CreateCampaignPage: React.FC = () => {
  const auth = useAuth();
  const navigate = useNavigate();

  const [formData, setFormData] = useState<CampaignCreatePayload>({
    title: '',
    description: '',
    max_players: 8,
    house_rules: '',
    is_open_for_recruitment: true,
    banner_image_url: '',
    next_session_utc: '', // <--- ADDED
    session_notes: ''     // <--- ADDED
  });

  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value, type } = e.target;
    // Special handling for number input
    if (type === 'number') {
        const numValue = value === '' ? null : parseInt(value, 10);
        setFormData(prev => ({ ...prev, [name]: numValue }));
    } else {
        setFormData(prev => ({ ...prev, [name]: value }));
    }
  };

  const handleCheckboxChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, checked } = e.target;
    setFormData(prev => ({ ...prev, [name]: checked }));
  };

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setError(null);
    if (!formData.title) {
      setError("Campaign title is required.");
      return;
    }
    if (!auth?.token) {
      setError("Authentication error. Please log in again.");
      return;
    }

    setIsLoading(true);
    try {
      // Filter out empty string fields so backend defaults can apply if needed
      const payload: CampaignCreatePayload = {
        ...formData,
        description: formData.description || null,
        house_rules: formData.house_rules || null,
        banner_image_url: formData.banner_image_url || null,
        max_players: formData.max_players || null,
      };

      const newCampaign = await campaignService.createCampaign(auth.token, payload);
      alert(`Campaign "${newCampaign.title}" created successfully!`);
      // Navigate to the new campaign's management page
      navigate(`/campaigns/${newCampaign.id}/manage`);
    } catch (err: any) {
      setError(err.message || "Failed to create campaign. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className={styles.pageContainer}>
      <div className={styles.formContainer}>
        <h1 className={styles.title}>Forge a New Campaign</h1>
        <form onSubmit={handleSubmit} noValidate>
          <div className={styles.formGroup}>
            <ThemedInput
              label="Campaign Title"
              id="title"
              name="title"
              type="text"
              value={formData.title}
              onChange={handleChange}
              placeholder="e.g., The Sunless Citadel"
              disabled={isLoading}
              required
            />
          </div>

          <div className={styles.formGroup}>
            <label htmlFor="description" className={styles.label}>Description</label>
            <textarea
              id="description"
              name="description"
              value={formData.description || ''}
              onChange={handleChange}
              className={styles.textarea}
              placeholder="A brief summary of your campaign's theme, story, and what players can expect."
              disabled={isLoading}
              rows={4}
            />
          </div>

          <div className={styles.formGroup}>
            <ThemedInput
              label="Max Players"
              id="max_players"
              name="max_players"
              type="number"
              value={formData.max_players || ''}
              onChange={handleChange}
              placeholder="e.g., 8"
              min="1"
              disabled={isLoading}
            />
          </div>

          <div className={styles.formGroup}>
            <label htmlFor="house_rules" className={styles.label}>House Rules</label>
            <textarea
              id="house_rules"
              name="house_rules"
              value={formData.house_rules || ''}
              onChange={handleChange}
              className={styles.textarea}
              placeholder="Any custom rules or variations for your game (e.g., 'Critical hits do max damage + roll', 'Potions are a bonus action')."
              disabled={isLoading}
              rows={3}
            />
          </div>
          
          <div className={styles.formGroup}>
            <ThemedInput
              label="Schedule First Session (Optional)"
              id="next_session_utc"
              name="next_session_utc"
              type="datetime-local"
              value={formData.next_session_utc || ''}
              onChange={handleChange}
              disabled={isLoading}
            />
          </div>
          {/* --- END NEW --- */}

          {/* --- NEW: Session Notes Input --- */}
          <div className={styles.formGroup}>
            <label htmlFor="session_notes" className={styles.label}>Session Notes (Optional)</label>
            <textarea
              id="session_notes"
              name="session_notes"
              value={formData.session_notes || ''}
              onChange={handleChange}
              className={styles.textarea}
              placeholder="e.g., 'Session 0: Character Creation. Players will meet at the Yawning Portal tavern.'"
              disabled={isLoading}
              rows={4}
            />
          </div>

          <div className={styles.formGroup}>
            <div className={styles.checkboxContainer}>
              <input
                id="is_open_for_recruitment"
                name="is_open_for_recruitment"
                type="checkbox"
                checked={formData.is_open_for_recruitment}
                onChange={handleCheckboxChange}
                className={styles.checkboxInput}
                disabled={isLoading}
              />
              <label htmlFor="is_open_for_recruitment" className={styles.checkboxLabel}>
                Open for players to request to join?
              </label>
            </div>
          </div>

          {error && <p className={styles.errorText}>{error}</p>}

          <div className={styles.buttonContainer}>
            <ThemedButton 
              type="submit" 
              runeSymbol="📜" 
              variant="red" 
              tooltipText={isLoading ? "Forging..." : "Create Your Campaign"}
              disabled={isLoading}
            >
              {isLoading ? "Saving..." : "Forge Campaign"}
            </ThemedButton>
          </div>
        </form>
      </div>
    </div>
  );
};

export default CreateCampaignPage;
