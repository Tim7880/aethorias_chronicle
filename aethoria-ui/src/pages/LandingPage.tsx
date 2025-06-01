// Path: src/pages/LandingPage.tsx
import React from 'react';
import { Link } from 'react-router-dom'; // For the login button
import ThemedButton from '../components/common/ThemedButton'; // Our themed button

const LandingPage: React.FC = () => {
  const pageStyle: React.CSSProperties = {
    padding: '20px',
    textAlign: 'center',
    minHeight: 'calc(100vh - 60px)', // Assuming a small header/footer if any
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center'
  };

  return (
    <div style={pageStyle}>
      <h1 style={{ fontFamily: 'var(--font-heading-ornate)', fontSize: '3em', color: 'var(--ink-color-dark)', marginBottom: '0.5em' }}>
        Welcome to Aethoria's Chronicle!
      </h1>
      <p style={{ fontFamily: 'var(--font-body-primary)', fontSize: '1.2em', color: 'var(--ink-color-medium)', maxWidth: '600px', marginBottom: '2em' }}>
        Your ultimate companion for weaving epic tales and managing grand adventures in the realms of Tabletop Adventures. 
        Explore community creations, get the latest news, or log in to continue your saga.
      </p>

      <div style={{ display: 'flex', gap: '20px', marginTop: '20px' }}>
        <Link to="/login" style={{ textDecoration: 'none' }}>
          <ThemedButton 
            runeSymbol="🗝️" 
            variant="green" 
            tooltipText="Access Your Account"
            aria-label="Login"
          > 
            {/* If button supports children text alongside rune */}
            {/* Login */}
          </ThemedButton>
        </Link>
        {/* We'll add a Register button later */}
        {/* <Link to="/register" style={{ textDecoration: 'none' }}>
          <ThemedButton runeSymbol="+" variant="red" tooltipText="Create New Account">
            Register
          </ThemedButton>
        </Link> */}
      </div>

      <div style={{ marginTop: '40px', border: '1px dashed var(--ink-color-light)', padding: '20px', width: '80%', maxWidth: '800px' }}>
        Community Spotlights & News Placeholder
      </div>
    </div>
  );
};

export default LandingPage;