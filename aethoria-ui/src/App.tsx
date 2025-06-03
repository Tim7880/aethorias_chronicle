// Path: src/App.tsx
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link, Outlet, useLocation, NavLink } from 'react-router-dom'; 
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import LandingPage from './pages/LandingPage';
import ProtectedRoute from './components/auth/ProtectedRoute';
import CreateCharacterPage from './pages/CreateCharacterPage';
import LevelUpHPPage from './pages/LevelUpHPPage'; 
import LevelUpExpertisePage from './pages/LevelUpExpertisePage';
import CharacterSheetPage from './pages/CharacterSheetPage';
import LevelUpArchetypePage from './pages/LevelUpArchetypePage';
import LevelUpASIPage from './pages/LevelUpASIPage';
import './App.css'; 

const AuthenticatedLayout: React.FC = () => {
  const location = useLocation();
  const auth = useAuth(); // We'll use this for the Logout button

  const handleLogout = () => {
    if (auth) {
      auth.logout();
      // Navigate to home or login after logout.
      // The ProtectedRoute will handle redirecting from dashboard if logout occurs.
      // For now, AuthContext's logout just clears state. 
      // Navigation after logout can be handled in components or here.
      // Let's assume for now logout from AuthContext will also trigger a navigation if needed
      // or ProtectedRoute will pick up the isAuthenticated === false state.
    }
  };

  return (
    <div>
      <nav style={{ 
          padding: '10px 20px', 
          backgroundColor: 'rgb(224, 204, 165)', 
          marginBottom: '20px', 
          borderBottom: '1px solid rgba(192, 175, 162, 0.92)' 
        }}>
        <ul style={{ listStyle: 'none', display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: 0, margin: 0 }}>
          <div style={{ display: 'flex', gap: '20px' }}>
            <li>
              <NavLink 
                to="/" 
                style={({ isActive }) => ({
                  fontFamily: 'var(--font-body-primary)',
                  color: isActive && location.pathname === "/" ? 'var(--ink-color-dark)' : 'var(--ink-color-medium)', 
                  textDecoration: 'none',
                  fontWeight: isActive && location.pathname === "/" ? 'bold' : 'normal',
                  cursor: isActive && location.pathname === "/" ? 'default' : 'pointer'
                })}
              >
                Home
              </NavLink>
            </li>
            {location.pathname !== "/dashboard" && (
              <li>
                <NavLink 
                  to="/dashboard" 
                  style={({ isActive }) => ({
                    fontFamily: 'var(--font-body-primary)',
                    color: isActive ? 'var(--ink-color-dark)' : 'var(--ink-color-medium)',
                    textDecoration: 'none',
                    fontWeight: isActive ? 'bold' : 'normal',
                    cursor: isActive ? 'default' : 'pointer'
                  })}
                >
                  Dashboard
                </NavLink>
              </li>
            )}
            {/* Add other primary authenticated links here */}
          </div>
          <div style={{ display: 'flex', gap: '20px' }}>
            {auth.isAuthenticated && auth.user && ( // Show username if logged in
              <li style={{fontFamily: 'var(--font-body-primary)', color: 'var(--ink-color-dark)'}}>
                Scribe: {auth.user.username}
              </li>
            )}
            <li>
              <span 
                onClick={handleLogout} 
                style={{fontFamily: 'var(--font-body-primary)', color: 'var(--ink-color-medium)', cursor: 'pointer'}}
                tabIndex={0} // Make it focusable
                onKeyPress={(e) => { if (e.key === 'Enter') handleLogout(); }} // Keyboard accessible
              >
                Logout
              </span>
            </li>
          </div>
        </ul>
      </nav>
      <Outlet /> 
    </div>
  );
};

// Need to import useAuth for AuthenticatedLayout
import { useAuth } from './contexts/AuthContext';


function App() {
  return (
    <Router>
      <Routes>
        {/* Public Routes */}
        <Route path="/" element={<LandingPage />} /> 
        <Route path="/login" element={<LoginPage />} /> 
        {/* <Route path="/register" element={<RegisterPage />} /> */}

        {/* Protected Routes Group */}
        <Route element={<ProtectedRoute />}> 
          <Route element={<AuthenticatedLayout />}> 
            <Route path="/dashboard" element={<DashboardPage />} /> 
            <Route path="/create-character" element={<CreateCharacterPage />} />
            <Route path="/character/:characterId/level-up/hp" element={<LevelUpHPPage />} />
            <Route path="/character/:characterId/level-up/asi" element={<LevelUpASIPage />} /> 
            {/* <Route path="/character/:characterId/level-up/spells" element={<LevelUpSpellsPage />} /> */}
            <Route path="/character/:characterId/level-up/expertise" element={<LevelUpExpertisePage />} /> {/* <--- NEW ROUTE */}
            <Route path="/character/:characterId/level-up/archetype" element={<LevelUpArchetypePage />} />
            <Route path="/characters/:characterIdFromRoute/view" element={<CharacterSheetPage />} />
          </Route>
        </Route>

        {/* Catch-all for undefined routes */}
        <Route path="*" element={
          <div style={{textAlign: 'center', paddingTop: '50px'}}>
            <h1 style={{fontFamily: 'var(--font-heading-ornate)'}}>404 - Page Not Found</h1>
            <p style={{fontFamily: 'var(--font-body-primary)'}}>
              The chronicle page you seek is lost to the mists of time.
            </p>
            <Link to="/" style={{fontFamily: 'var(--font-body-primary)', color: 'var(--ink-color-dark)'}}>Return to the Landing Page</Link>
          </div>
        } />
      </Routes>
    </Router>
  );
}

export default App;

