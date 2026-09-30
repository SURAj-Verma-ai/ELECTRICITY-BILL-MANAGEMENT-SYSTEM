import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { apiPost } from '../api'

export default function Login({ onLoggedIn }) {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const navigate = useNavigate()

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    try {
      await apiPost('/api/login', { username, password })
      onLoggedIn()
      navigate('/admin')
    } catch (err) {
      setError(err.message === 'Invalid username or password' ? err.message : 'Invalid username or password')
    }
  }

  return (
    <>
      <div className="nav">
        <Link className="brand" to="/">
          <img src="/static/images/logo/ebms-logo.png" alt="" />
          <span>PowerPay</span>
        </Link>
      </div>

      <div className="login-wrapper">
        <div className="login-box">
          <h1>Admin Login</h1>
          <p className="subtitle">Sign in to access the admin dashboard</p>

          {error && <div className="error-msg">{error}</div>}

          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label htmlFor="username">Username</label>
              <input type="text" id="username" value={username} onChange={e => setUsername(e.target.value)} required autoFocus />
            </div>
            <div className="form-group">
              <label htmlFor="password">Password</label>
              <input type="password" id="password" value={password} onChange={e => setPassword(e.target.value)} required />
            </div>
            <button type="submit" className="btn-submit">Login</button>
          </form>
          <div className ="SytemInfo">
            <p>System Information:</p>
            <ul>
              <li>THis is a simple system info for Electric Utility Management which generates bill and payment records.</li>
              <li>This helps the admin and users manage their power payments efficiently.</li>
            </ul>
          </div>

          <Link to="/" className="back-link">Back to Home</Link>
        </div>
      </div>
    </>
  )
}
