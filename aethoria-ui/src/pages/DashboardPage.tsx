// Path: src/pages/DashboardPage.tsx
import React, { useEffect, useState } from 'react';
import { useAuth } from '../contexts/AuthContext'; // To get user and token
import { characterService } from '../services/characterService'; // Our new service
import type { Character } from '../types/character'; // Our Character interface
import { Link } from 'react-router-dom'; // For linking to character sheets later
import ThemedButton from '../components/common/ThemedButton'; // Assuming PascalCase import

const DashboardPage: React.FC = () => {
  const auth = useAuth();
  const [characters, setCharacters] = useState<Character[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchCharacters = async () => {
      if (auth?.token) { // Check if token is available
        setIsLoading(true);
        setError(null);
        try {
          const userCharacters = await characterService.getCharacters(auth.token);
          setCharacters(userCharacters);
        } catch (err: any) {
          console.error("Failed to fetch characters:", err);
          setError(err.message || "Could not load your characters.");
          // If 401, auth.logout() might be called by authService or a global error handler
        } finally {
          setIsLoading(false);
        }
      } else {
        // No token, user might not be fully authenticated yet or token cleared
        // This case should ideally be handled by ProtectedRoute redirecting to login
        // Or if AuthContext indicates loading, wait.
        if (!auth?.isLoading) { // Only set error if auth isn't already loading
            setError("You are not authenticated. Please log in.");
            setIsLoading(false);
        }
      }
    };

    if (auth?.isAuthenticated) { // Only fetch if authenticated
        fetchCharacters();
    } else if (!auth?.isLoading) { // If not loading and not authenticated
        setIsLoading(false); 
        // setError("Please log in to see your dashboard."); // Or rely on ProtectedRoute
    }
    // Dependency array: re-fetch if auth.token changes (e.g., after login)
    // or if auth.isAuthenticated changes.
  }, [auth?.token, auth?.isAuthenticated, auth?.isLoading]); 

  const pageStyle: React.CSSProperties = {
    padding: '20px',
    fontFamily: 'var(--font-body-primary)',
  };

  const sectionTitleStyle: React.CSSProperties = {
    fontFamily: 'var(--font-heading-ornate)',
    color: 'var(--ink-color-dark)',
    fontSize: '2.5em',
    borderBottom: '1px solid var(--ink-color-light)',
    paddingBottom: '0.3em',
    marginBottom: '1em',
  };

  const characterListStyle: React.CSSProperties = {
    listStyle: 'none',
    padding: 0,
  };

  const characterItemStyle: React.CSSProperties = {
    backgroundColor: 'var(--parchment-highlight)',
    border: '1px solid var(--ink-color-light)',
    borderRadius: '5px',
    padding: '15px',
    marginBottom: '10px',
    boxShadow: '0px 3px 10px rgba(0,0,0,0.08)',
  };


  if (auth?.isLoading) {
    return <div style={pageStyle}><p>Loading dashboard...</p></div>;
  }

  // If not authenticated (and not loading), ProtectedRoute should have redirected.
  // But as a fallback or if directly landed here and token check failed:
  if (!auth?.isAuthenticated) {
      return (
          <div style={{...pageStyle, textAlign: 'center'}}>
              <p>Please <Link to="/login">log in</Link> to view your dashboard.</p>
          </div>
      );
  }

  return (
    <div style={pageStyle}>
      <h1 style={sectionTitleStyle}>
        Welcome, {auth?.user?.username || 'Scribe'}!
      </h1>

      <div style={{ marginBottom: '30px' }}>
        <h2 style={{...sectionTitleStyle, fontSize: '2em' }}>Your Characters</h2>
        {isLoading && <p>Loading characters...</p>}
        {error && <p style={{ color: 'red' }}>Error: {error}</p>}
        {!isLoading && !error && characters.length === 0 && (
          <p>You have not yet chronicled any adventurers. Why not create one?</p>
        )}
        {!isLoading && !error && characters.length > 0 && (
          <ul style={characterListStyle}>
            {characters.map((char) => (
              <li key={char.id} style={characterItemStyle}>
                <h3 style={{fontFamily: 'var(--font-heading-ornate)', fontSize: '1.8em', margin: '0 0 10px 0'}}>
                  {/* Later, this Link will go to /characters/{char.id} */}
                  <Link to={`/characters/${char.id}`} style={{color: 'var(--ink-color-dark)', textDecoration: 'none'}}>
                    {char.name}
                  </Link>
                </h3>
                <p style={{margin: '5px 0'}}>Level {char.level} {char.race} {char.character_class}</p>
                {/* Add more details or a "View Sheet" button later */}
              </li>
            ))}
          </ul>
        )}
        <div style={{marginTop: '20px'}}>
            {/* Use your actual ThemedButton import name */}
            <Link to="/create-character"> {/* We'll need to create this route */}
                <ThemedButton variant="green" runeSymbol="+">Create New Character</ThemedButton>
            </Link>
        </div>
      </div>

      {/* Placeholder for Campaigns Section */}
      <div style={{ marginBottom: '30px' }}>
        <h2 style={{...sectionTitleStyle, fontSize: '2em' }}>Your Campaigns</h2>
        <p>(Campaigns will be listed here soon!)</p>
      </div>

    </div>
  );
};

export default DashboardPage;