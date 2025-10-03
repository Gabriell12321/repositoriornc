import { useState } from 'react'
import LoginForm from './components/LoginForm'
import Dashboard from './components/Dashboard'
import { useKV } from '@github/spark/hooks'

function App() {
  const [currentUser, setCurrentUser] = useKV<{name: string, role: string} | null>('current-user', null)

  const handleLogin = (userData: {name: string, role: string}) => {
    setCurrentUser(userData)
  }

  const handleLogout = () => {
    setCurrentUser(null)
  }

  if (!currentUser) {
    return <LoginForm onLogin={handleLogin} />
  }

  return <Dashboard user={currentUser} onLogout={handleLogout} />
}

export default App