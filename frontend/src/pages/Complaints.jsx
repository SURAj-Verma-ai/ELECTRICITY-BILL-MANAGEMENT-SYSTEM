import { useState } from 'react'
import Nav from '../components/Nav'
import { apiPost } from '../api'

const CATEGORIES = ['Power Interruption', 'Meter Fault', 'Billing', 'Other']

export default function Complaints({ isAdmin, onLogout }) {
  const [meterNo, setMeterNo] = useState('')
  const [category, setCategory] = useState(CATEGORIES[0])
  const [description, setDescription] = useState('')
  const [message, setMessage] = useState(null)
  const [complaints, setComplaints] = useState([])

  async function handleSubmit(e) {
    e.preventDefault()
    const data = await apiPost('/api/complaints', { meter_no: meterNo, category, description })
    setMessage(data.message)
    setComplaints(data.complaints || [])
  }

  function badgeClass(status) {
    if (status === 'Resolved') return 'badge-resolved'
    if (status === 'In Progress') return 'badge-progress'
    return 'badge-pending'
  }

  return (
    <>
      <Nav active="/complaints" isAdmin={isAdmin} onLogout={onLogout} />

      <div className="container split">
        <div className="form-col">
          <h1>File a Complaint</h1>

          {message && (
            <div className={`message ${complaints.length ? 'message-success' : 'message-error'}`}>{message}</div>
          )}

          <div className="form-box">
            <p className="subtitle">Report power interruptions, meter faults, or billing issues using your meter number.</p>

            <form onSubmit={handleSubmit}>
              <div className="field">
                <label htmlFor="meter_no">Meter Number</label>
                <input type="text" id="meter_no" placeholder="e.g. MTR-1001" value={meterNo} onChange={e => setMeterNo(e.target.value)} required />
              </div>

              <div className="field">
                <label htmlFor="category">Category</label>
                <select id="category" value={category} onChange={e => setCategory(e.target.value)} required>
                  {CATEGORIES.map(c => <option key={c} value={c}>{c === 'Billing' ? 'Billing Issue' : c}</option>)}
                </select>
              </div>

              <div className="field">
                <label htmlFor="description">Description</label>
                <textarea id="description" placeholder="Describe the issue in detail..." value={description} onChange={e => setDescription(e.target.value)} required />
              </div>

              <button type="submit">Submit Complaint</button>
            </form>
          </div>

          {complaints.length > 0 && (
            <div>
              <h3>Your Complaint History</h3>
              <table>
                <thead><tr><th>ID</th><th>Category</th><th>Description</th><th>Status</th></tr></thead>
                <tbody>
                  {complaints.map(c => (
                    <tr key={c.id}>
                      <td>#{c.id}</td>
                      <td>{c.category}</td>
                      <td>{c.description}</td>
                      <td><span className={badgeClass(c.status)}>{c.status}</span></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        <div className="media-col">
          <img src="/static/images/consumer/comp-31-1_1745332949.gif" alt="" className="side-gif" />
        </div>
      </div>

      <footer>PowerPay Complaints &copy; 2026</footer>
    </>
  )
}
