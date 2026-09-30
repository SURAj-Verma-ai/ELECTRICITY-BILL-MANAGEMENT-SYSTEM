import { Link } from 'react-router-dom'
import Nav from '../components/Nav'

export default function Home({ isAdmin, onLogout }) {
  return (
    <>
      <Nav active="/" isAdmin={isAdmin} onLogout={onLogout} />

      <div className="hero">
        <div>
          <h1>Pay your electricity bill without standing in a queue</h1>
          <p className="lead">
            Look up your bill with just a meter number, clear pending dues in a couple of clicks
            and raise a complaint if something looks off, No account required.
          </p>
          <Link className="cta" to="/consumer">Check My Bill</Link>
          <Link className="sub" to="/complaints">File a complaint</Link>
        </div>
        <img src="/static/images/home/tower.jpg" alt="" />
      </div>

      <div className="infobar">
        <div><strong>&#8377;7 / unit</strong><span>Flat domestic tariff, no hidden charges</span></div>
        <div><strong>1200-123456</strong><span>Toll-free customer care, all days</span></div>
        <div><strong>48 hrs</strong><span>Average complaint resolution time</span></div>
      </div>
    </>
  )
}
