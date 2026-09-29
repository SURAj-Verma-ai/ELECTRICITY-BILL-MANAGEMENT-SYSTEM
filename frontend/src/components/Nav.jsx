import { Link } from 'react-router-dom'

export default function Nav({ active, isAdmin, onLogout }) {
  const link = (to, label) => (
    <li><Link to={to} className={active === to ? 'active' : ''}>{label}</Link></li>
  )
  return (
    <div className="nav">
      <Link className="brand" to="/">
        <img src="/static/images/logo/ebms-logo.png" alt="" />
        <span>PowerPay</span>
      </Link>
      <ul>
        {link('/', 'Home')}
        {link('/consumer', 'Pay Bill')}
        {link('/complaints', 'Complaints')}
        {link('/admin', 'Admin')}
      </ul>
      {isAdmin
        ? <button className="loginbtn logoutbtn" onClick={onLogout}>Logout</button>
        : <Link className="loginbtn" to="/login">Log in</Link>}
    </div>
  )
}
