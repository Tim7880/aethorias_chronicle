// Path: src/main.tsx
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.tsx'
import './index.css'
import { AuthProvider } from './contexts/AuthContext' // <--- IMPORT AuthProvider

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <AuthProvider> {/* <--- WRAP App with AuthProvider --- */}
      <App />
    </AuthProvider>
  </React.StrictMode>,
)