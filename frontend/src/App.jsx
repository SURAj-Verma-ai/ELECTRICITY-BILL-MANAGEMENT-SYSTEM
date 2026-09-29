import { useEffect, useState } from 'react'
import { Routes, Route } from 'react-router-dom'
import Home from './pages/Home'
import Login from './pages/Login'
import Consumer from './pages/Consumer'
import Complaints from './pages/Complaints'
import Admin from './pages/Admin'
import { apiGet, apiPost } from './api'

export default function App() {
  const [isAdmin, setIsAdmin] = useState(false)
  const [ready, setReady] = useState(false)

  useEffect(() => {
    apiGet('/api/session').then(data => {
      setIsAdmin(!!data.is_admin)
      setReady(true)
    })
  }, [])

  async function handleLogout() {
    await apiPost('/api/logout', {})
    setIsAdmin(false)
  }

  if (!ready) return null

  return (
    <Routes>
      <Route path="/" element={<Home isAdmin={isAdmin} onLogout={handleLogout} />} />
      <Route path="/login" element={<Login onLoggedIn={() => setIsAdmin(true)} />} />
      <Route path="/consumer" element={<Consumer isAdmin={isAdmin} onLogout={handleLogout} />} />
      <Route path="/complaints" element={<Complaints isAdmin={isAdmin} onLogout={handleLogout} />} />
      <Route path="/admin" element={<Admin isAdmin={isAdmin} onLogout={handleLogout} />} />
    </Routes>
  )
}
