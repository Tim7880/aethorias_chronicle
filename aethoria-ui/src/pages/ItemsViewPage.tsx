// Path: src/pages/ItemsViewPage.tsx
import React, { useEffect, useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { gameDataService } from '../services/gameDataService';
import type { ItemDefinition } from '../types/item';
import styles from './ItemsViewPage.module.css';

const ItemsViewPage: React.FC = () => {
  const auth = useAuth();
  const [items, setItems] = useState<ItemDefinition[]>([]);
  const [selectedItem, setSelectedItem] = useState<ItemDefinition | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadItems = async () => {
      if (auth.token) {
        setIsLoading(true);
        try {
          const data = await gameDataService.getItems(auth.token);
          setItems(data.sort((a, b) => a.name.localeCompare(b.name)));
        } catch (err: any) {
          setError(err.message || "Failed to load item data.");
        } finally {
          setIsLoading(false);
        }
      }
    };
    loadItems();
  }, [auth.token]);

  const handleSelection = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const selectedName = e.target.value;
    const details = items.find(i => i.name === selectedName) || null;
    setSelectedItem(details);
  };

  const formatItemType = (type: string) => {
    return type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
  };

  if (isLoading) return <div className={styles.pageContainer}><p>Unpacking the Bag of Holding...</p></div>;
  if (error) return <div className={styles.pageContainer}><p className={styles.errorText}>{error}</p></div>;

  return (
    <div className={styles.pageContainer}>
      <div className={styles.selectorContainer}>
        <label htmlFor="item-selector" className={styles.selectorLabel}>Browse the Catalogue</label>
        <select id="item-selector" onChange={handleSelection} className={styles.itemSelector} defaultValue="">
          <option value="" disabled>-- Select an Item --</option>
          {items.map(item => (
            <option key={item.id} value={item.name}>{item.name}</option>
          ))}
        </select>
      </div>

      <div className={styles.itemDisplay}>
        {selectedItem ? (
          <div>
            <h2 className={styles.itemName}>{selectedItem.name}</h2>
            <p className={styles.itemMeta}>
              {formatItemType(selectedItem.item_type)}
            </p>
            <ul className={styles.itemProperties}>
              <li><strong>Cost:</strong> {selectedItem.cost_gp} gp</li>
              <li><strong>Weight:</strong> {selectedItem.weight} lb.</li>
              {selectedItem.properties && Object.entries(selectedItem.properties).map(([key, value]) => (
                <li key={key}>
                  <strong>{key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}:</strong> {String(value)}
                </li>
              ))}
            </ul>
          </div>
        ) : (
          <p className={styles.promptText}>Select an item from the dropdown to see its details.</p>
        )}
      </div>
    </div>
  );
};

export default ItemsViewPage;
