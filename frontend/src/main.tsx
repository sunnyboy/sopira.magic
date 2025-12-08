//..............................................................
//   ~/sopira.magic/version_01/frontend/src/main.tsx
//   main - React bootstrap entrypoint
//   Attaches the root React tree to the DOM container
//..............................................................

/**
 * React bootstrap entrypoint.
 *
 * Creates the React root and renders the App component into the DOM.
 * This file should remain minimal and free of domain-specific logic.
 */
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import App from './App.tsx'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)

