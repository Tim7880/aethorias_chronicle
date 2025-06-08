// Path: src/pages/RegisterPage.tsx
import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { authService } from '../services/authService';
import type { RegisterPayload } from '../services/authService';
import ThemedInput from '../components/common/ThemedInput';
import ThemedButton from '../components/common/ThemedButton';
import styles from './RegisterPage.module.css'; // Using its own CSS module

const RegisterPage: React.FC = () => {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
  });
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();
  const auth = useAuth();

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const validateEmail = (email: string): boolean => {
    const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return regex.test(email);
  };

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setError(null);

    if (!formData.username || !formData.email || !formData.password) {
        setError("All fields are required.");
        return;
    }
    if (!validateEmail(formData.email)) {
        setError("Please enter a valid email address.");
        return;
    }
    if (formData.password !== formData.confirmPassword) {
      setError("Passwords do not match.");
      return;
    }
    if (formData.password.length < 8) {
        setError("Password must be at least 8 characters long.");
        return;
    }

    setIsLoading(true);
    try {
      const payload: RegisterPayload = {
        username: formData.username,
        email: formData.email,
        password: formData.password,
      };
      
      await authService.register(payload);

      alert("Registration successful! Please log in with your new account.");
      navigate('/login');

    } catch (err: any) {
      setError(err.message || "Registration failed. This username or email may already be in use.");
    } finally {
      setIsLoading(false);
    }
  };
  
  useEffect(() => {
    if (auth.isAuthenticated) {
      navigate('/dashboard');
    }
  }, [auth.isAuthenticated, navigate]);

  return (
    <div className={styles.pageContainer}>
      <div className={styles.formContainer}>
        <h1 className={styles.title}>Join the Chronicle</h1>
        <form onSubmit={handleSubmit} noValidate>
          <ThemedInput
            label="Username:"
            id="username"
            name="username"
            type="text"
            value={formData.username}
            onChange={handleChange}
            placeholder="e.g., ValiantScribe"
            disabled={isLoading}
            required
          />
          <ThemedInput
            label="Email Address:"
            id="email"
            name="email"
            type="email"
            value={formData.email}
            onChange={handleChange}
            placeholder="your.email@example.com"
            disabled={isLoading}
            required
          />
          <ThemedInput
            label="Password:"
            id="password"
            name="password"
            type="password"
            value={formData.password}
            onChange={handleChange}
            placeholder="8+ characters"
            disabled={isLoading}
            required
          />
          <ThemedInput
            label="Confirm Password:"
            id="confirmPassword"
            name="confirmPassword"
            type="password"
            value={formData.confirmPassword}
            onChange={handleChange}
            placeholder="Re-enter your password"
            disabled={isLoading}
            required
          />
          
          {error && <p className={styles.errorText}>{error}</p>}

          <div className={styles.buttonContainer}>
            <ThemedButton 
              type="submit" 
              runeSymbol="✍️" 
              variant="green" 
              tooltipText={isLoading ? "Registering..." : "Create Your Account"}
              disabled={isLoading}
            >
              {isLoading ? "Creating Account..." : "Register"}
            </ThemedButton>
          </div>
        </form>
        <div className={styles.linkContainer}>
          <span>Already have an account? </span>
          <Link to="/login" className={styles.link}>Log in</Link>
        </div>
      </div>
    </div>
  );
};

export default RegisterPage;
