/// Path: src/pages/LoginPage.tsx
import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import ThemedInput from '../components/common/ThemedInput'; 
import ThemedButton from '../components/common/ThemedButton'; 
// Remove direct authService import if login is handled by context
// import { authService } from '../services/authService'; 
import { useAuth } from '../contexts/AuthContext'; // <--- IMPORT useAuth hook

const LoginPage: React.FC = () => {
  const [identifier, setIdentifier] = useState(''); 
  const [password, setPassword] = useState('');
  
  const auth = useAuth(); // <--- USE THE AUTH CONTEXT
  const navigate = useNavigate();

  // Use error and isLoading from context if desired, or keep local ones for form-specific feedback
  const [formError, setFormError] = useState<string | null>(null);
  const [formIsLoading, setFormIsLoading] = useState(false);


  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setFormIsLoading(true);
    setFormError(null);

    if (!auth) return; // Should not happen if wrapped in provider

    try {
      await auth.login({ username: identifier, password });
      // Login success is now handled within AuthContext (sets user, token, isAuthenticated)
      // AuthContext will also try to fetch current user.
      console.log('Login initiated through AuthContext');
      navigate('/dashboard'); // Redirect on successful login initiation
    } catch (err: any) {
      console.error('Login failed from LoginPage:', err);
      setFormError(err.message || 'An unknown error occurred during login.');
    } finally {
      setFormIsLoading(false);
    }
  };

  const pageStyle: React.CSSProperties = { /* ... (same as before) ... */
    display: 'flex', flexDirection: 'column', alignItems: 'center',
    justifyContent: 'center', minHeight: 'calc(100vh - 100px)',
    padding: '20px',
  };
  const formContainerStyle: React.CSSProperties = { /* ... (same as before) ... */
    backgroundColor: 'var(--parchment-highlight)', padding: '30px 40px',
    borderRadius: '8px', boxShadow: '0px 6px 18px rgba(0,0,0,0.15), 0px 0px 0px 1px var(--ink-color-light)',
    maxWidth: '450px', width: '100%', textAlign: 'center', border: '1px solid rgba(120, 90, 70, 0.3)',
  };
  const titleStyle: React.CSSProperties = { /* ... (same as before) ... */
    fontFamily: 'var(--font-heading-ornate)', color: 'var(--ink-color-dark)',
    fontSize: '2.8em', marginBottom: '1.5em',
  };
  const errorStyle: React.CSSProperties = { /* ... (same as before) ... */
    fontFamily: 'var(--font-body-primary)', color: '#a02c2c', 
    marginTop: '1em', minHeight: '1.2em',
  };

  // Display global loading or error state from context, or form-specific ones
  if (auth?.isLoading && !formIsLoading) { // If global auth is loading (e.g. on initial app load)
      return <div style={pageStyle}><p>Loading Scriptorium...</p></div>;
  }

  return (
    <div style={pageStyle}>
      <div style={formContainerStyle}>
        <h1 style={titleStyle}>
          Access the Scriptorium
        </h1>
        <form onSubmit={handleSubmit}>
          <ThemedInput
            label="Scribe's Name or Email:"
            id="identifier" // Changed from "username" to "identifier" to match state
            name="identifier"
            type="text"
            value={identifier}
            onChange={(e) => setIdentifier(e.target.value)}
            placeholder="Enter your registered name or email"
            disabled={formIsLoading || auth?.isLoading} // Disable if form or global auth is loading
            required
            style={{ marginBottom: '1.5em' }}
          />
          <ThemedInput
            label="Secret Word (Password):"
            id="password"
            name="password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Your pass-phrase to the archives"
            disabled={formIsLoading || auth?.isLoading}
            required
            style={{ marginBottom: '1.5em' }}
          />
          {formError && <p style={errorStyle}>{formError}</p>}
          {auth?.error && !formError && <p style={errorStyle}>{auth.error}</p>} {/* Display global auth error if no form error */}
          <div style={{ marginTop: '2.5em' }}>
            <ThemedButton 
              type="submit" 
              runeSymbol="🗝️" 
              variant="green" 
              tooltipText={formIsLoading || auth?.isLoading ? "Unlocking..." : "Unlock the Archives"}
              aria-label="Login"
              disabled={formIsLoading || auth?.isLoading}
            >
              {(formIsLoading || auth?.isLoading) ? "Loading..." : ""} 
            </ThemedButton>
          </div>
        </form>
        <div style={{ marginTop: '2em', fontFamily: 'var(--font-body-primary)' }}>
          <p>
            New to the Scriptorium?{' '}
            <Link to="/register" style={{ color: 'var(--ink-color-medium)', textDecoration: 'underline' }}>
              Inscribe your name here.
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;