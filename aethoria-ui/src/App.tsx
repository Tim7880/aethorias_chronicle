// Path: src/App.tsx
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link, Outlet, useLocation, NavLink } from 'react-router-dom'; 
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import LandingPage from './pages/LandingPage';
import RegisterPage from './pages/RegisterPage';
import ProtectedRoute from './components/auth/ProtectedRoute';
import CreateCharacterPage from './pages/CreateCharacterPage';
import LevelUpHPPage from './pages/LevelUpHPPage'; 
import LevelUpExpertisePage from './pages/LevelUpExpertisePage';
import CharacterSheetPage from './pages/CharacterSheetPage';
import LevelUpArchetypePage from './pages/LevelUpArchetypePage';
import LevelUpASIPage from './pages/LevelUpASIPage';
import CreateCampaignPage from './pages/CreateCampaignPage';
import DiscoverCampaignsPage from './pages/DiscoverCampaignsPage';
import CampaignManagementPage from './pages/CampaignManagementPage';
import CampaignViewPage from './pages/CampaignViewPage';
import ClassesViewPage from './pages/ClassesViewPage';
import CompendiumPage from './pages/CompendiumPage';
import RacesViewPage from './pages/RacesViewPage';
// --- NEW IMPORTS ---
import MonstersViewPage from './pages/MonstersViewPage';
import SpellsViewPage from './pages/SpellsViewPage';
import ItemsViewPage from './pages/ItemsViewPage';
import BackgroundsViewPage from './pages/BackgroundsViewPage';
import ConditionsViewPage from './pages/ConditionsViewPage';
import SorcererSpellSelectionPage from './pages/SorcererSpellSelectionPage';
import CampaignRoomPage from './pages/CampaignRoomPage';
// --- END NEW IMPORTS ---
import { useAuth } from './contexts/AuthContext';
import './App.css'; 

// Shared style function for NavLinks
const navLinkStyle = ({ isActive }: { isActive: boolean }) => ({
  fontFamily: 'var(--font-body-primary)',
  color: isActive ? 'var(--ink-color-dark)' : 'var(--ink-color-medium)',
  textDecoration: 'none',
  fontWeight: isActive ? 'bold' : 'normal',
});

// Layout for Public Pages
const PublicLayout: React.FC = () => {
  const location = useLocation();
  return (
    <div>
      <nav className="main-nav">
        <ul className="nav-list">
          <div className="nav-section">
            {location.pathname !== '/' && (
              <li><NavLink to="/" style={navLinkStyle}>Community</NavLink></li>
            )}
          </div>
          <div className="nav-section">
            <li><NavLink to="/login" style={navLinkStyle}>Login</NavLink></li>
            <li><NavLink to="/register" style={navLinkStyle}>Register</NavLink></li>
          </div>
        </ul>
      </nav>
      <Outlet /> 
    </div>
  );
};

// Layout for Authenticated Pages
const AuthenticatedLayout: React.FC = () => {
  const auth = useAuth(); 
  const location = useLocation();
  const handleLogout = () => { auth.logout(); };
  // --- START MODIFICATION ---
  // Check if the current route is the campaign room
  const isCampaignRoom = location.pathname.includes('/play');

  // Conditionally apply the container class
  const mainContentClass = isCampaignRoom ? '' : 'page-content-container';
  // --- END MODIFICATION ---
  return (
    <div className={mainContentClass}>
      <nav className="main-nav">
        <ul className="nav-list">
          <div className="nav-section">
            {location.pathname === '/dashboard' ? (
                <li><NavLink to="/" style={navLinkStyle}>Community</NavLink></li>
            ) : (
                <li><NavLink to="/dashboard" style={navLinkStyle}>Dashboard</NavLink></li>
            )}
            <li><NavLink to="/discover-campaigns" style={navLinkStyle}>Discover</NavLink></li>
            <li><NavLink to="/compendium" style={navLinkStyle}>Compendium</NavLink></li>
          </div>
          <div className="nav-section">
            {auth.isAuthenticated && auth.user && (
              <li style={{fontFamily: 'var(--font-body-primary)', color: 'var(--ink-color-dark)'}}>
                Scribe: {auth.user.username}
              </li>
            )}
            <li>
              <button onClick={handleLogout} className="nav-logout" onKeyPress={(e) => { if (e.key === 'Enter') handleLogout(); }}>
                Logout
              </button>
            </li>
          </div>
        </ul>
      </nav>
      <Outlet /> 
    </div>
  );
};

function App() {
  return (
    <Router>
      <Routes>
        <Route element={<PublicLayout />}>
            <Route path="/" element={<LandingPage />} /> 
            <Route path="/login" element={<LoginPage />} /> 
            <Route path="/register" element={<RegisterPage />} />
        </Route>
        <Route element={<ProtectedRoute />}> 
          <Route element={<AuthenticatedLayout />}> 
            <Route path="/dashboard" element={<DashboardPage />} /> 
            <Route path="/create-character" element={<CreateCharacterPage />} />
            <Route path="/create-campaign" element={<CreateCampaignPage />} />
            
            <Route path="/compendium" element={<CompendiumPage />}>
              <Route path="classes" element={<ClassesViewPage />} />
              <Route path="races" element={<RacesViewPage />} />
              <Route path="monsters" element={<MonstersViewPage />} />
              <Route path="spells" element={<SpellsViewPage />} />
              <Route path="items" element={<ItemsViewPage />} />
              <Route path="backgrounds" element={<BackgroundsViewPage />} />
              <Route path="conditions" element={<ConditionsViewPage />} />
            </Route>

            <Route path="/character/:characterId/level-up/hp" element={<LevelUpHPPage />} />
            <Route path="/character/:characterId/level-up/asi" element={<LevelUpASIPage />} /> 
            <Route path="/character/:characterId/level-up/expertise" element={<LevelUpExpertisePage />} />
            <Route path="/character/:characterId/level-up/archetype" element={<LevelUpArchetypePage />} />
            <Route path="/character/:characterId/level-up/spells" element={<SorcererSpellSelectionPage />} />
            <Route path="/characters/:characterIdFromRoute/view" element={<CharacterSheetPage />} />
            <Route path="/discover-campaigns" element={<DiscoverCampaignsPage />} />
            <Route path="/campaigns/:campaignId/manage" element={<CampaignManagementPage />} />
            <Route path="/campaigns/:campaignId/play" element={<CampaignRoomPage />} />
            <Route path="/campaigns/:campaignId/view" element={<CampaignViewPage />} />
          </Route>
        </Route>
        <Route path="*" element={
          <div className="not-found-page">
            <h1 className="not-found-title">404 - Page Not Found</h1>
            <p className="not-found-text">The chronicle page you seek is lost to the mists of time.</p>
            <Link to="/" className="not-found-link">Return to the Community Page</Link>
          </div>
        } />
      </Routes>
    </Router>
  );
}

export default App;

