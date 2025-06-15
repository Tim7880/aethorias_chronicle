// Path: src/pages/CompendiumPage.tsx
import React from 'react';
import { NavLink, Outlet } from 'react-router-dom';
import styles from './CompendiumPage.module.css';

const CompendiumPage: React.FC = () => {
  // Style for the active NavLink in the sidebar
  const activeLinkStyle = {
    backgroundColor: 'var(--ink-color-light)',
    color: 'var(--ink-color-dark)',
  };

  return (
    <div className={styles.pageContainer}>
      <header className={styles.header}>
        <h1 className={styles.title}>Compendium</h1>
      </header>
      
      <div className={styles.layout}>
        <aside className={styles.sidebar}>
          <h2 className={styles.sidebarTitle}>Categories</h2>
          <nav>
            <ul className={styles.sidebarNav}>
              <li>
                <NavLink 
                  to="/compendium/races" 
                  className={styles.sidebarLink}
                  style={({ isActive }) => isActive ? activeLinkStyle : {}}
                >
                  Races
                </NavLink>
              </li>
              <li>
                <NavLink 
                  to="/compendium/classes" 
                  className={styles.sidebarLink}
                  style={({ isActive }) => isActive ? activeLinkStyle : {}}
                >
                  Classes
                </NavLink>
              </li>
              <li><NavLink 
                    to="/compendium/backgrounds" 
                    className={styles.sidebarLink} 
                    style={({ isActive }) => isActive ? activeLinkStyle : {}}
                >
                  Backgrounds
                  </NavLink>
              </li>
               <li><NavLink 
                    to="/compendium/conditions" 
                    className={styles.sidebarLink} 
                    style={({ isActive }) => isActive ? activeLinkStyle : {}}
                >
                  Conditions
                  </NavLink>
              </li>
              <li>
                <NavLink 
                  to="/compendium/monsters" 
                  className={styles.sidebarLink}
                  style={({ isActive }) => isActive ? activeLinkStyle : {}}
                >
                  Monsters
                </NavLink>
              </li>
               <li>
                <NavLink 
                  to="/compendium/spells" 
                  className={styles.sidebarLink}
                  style={({ isActive }) => isActive ? activeLinkStyle : {}}
                >
                  Spells
                </NavLink>
              </li>
              <li>
                <NavLink 
                  to="/compendium/items" 
                  className={styles.sidebarLink}
                  style={({ isActive }) => isActive ? activeLinkStyle : {}}
                >
                  Items
                </NavLink>
              </li>
            </ul>
          </nav>
        </aside>

        <main className={styles.contentOutlet}>
          {/* Child routes like ClassesViewPage will be rendered here */}
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default CompendiumPage;
