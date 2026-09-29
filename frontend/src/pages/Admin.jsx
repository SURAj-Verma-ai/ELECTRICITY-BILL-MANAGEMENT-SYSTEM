import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import Nav from '../components/Nav'
import { apiGet, apiPost } from '../api'

const TABS = [
  { id: 'tab-add', label: 'Add Consumer' },
  { id: 'tab-bill', label: 'Generate Bill' },
  { id: 'tab-data', label: 'Records' },
]

export default function Admin({ isAdmin, onLogout }) {
  const navigate = useNavigate()
  const [consumers, setConsumers] = useState([])
  const [bills, setBills] = useState([])
  const [complaints, setComplaints] = useState([])
  const [activeTab, setActiveTab] = useState('tab-add')
  const [collapsed, setCollapsed] = useState(false)

  const [name, setName] = useState('')
  const [meterNo, setMeterNo] = useState('')
  const [address, setAddress] = useState('')
  const [consumerError, setConsumerError] = useState('')

  const [billConsumerId, setBillConsumerId] = useState('')
  const [month, setMonth] = useState('')
  const [units, setUnits] = useState('')
  const [billError, setBillError] = useState('')

  async function loadDashboard() {
    const data = await apiGet('/api/admin/dashboard')
    if (data.error) {
      navigate('/login')
      return
    }
    setConsumers(data.consumers || [])
    setBills(data.bills || [])
    setComplaints(data.complaints || [])
    setActiveTab(data.active_tab || 'tab-add')
  }

  useEffect(() => {
    if (!isAdmin) {
      navigate('/login')
      return
    }
    loadDashboard()
    try {
      const saved = localStorage.getItem('admin_sidebar_collapsed')
      setCollapsed(saved === '1' || (saved === null && window.innerWidth <= 800))
    } catch (e) {}
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isAdmin])

  function toggleSidebar() {
    setCollapsed(prev => {
      const next = !prev
      try { localStorage.setItem('admin_sidebar_collapsed', next ? '1' : '0') } catch (e) {}
      return next
    })
  }

  async function switchTab(tabId) {
    setActiveTab(tabId)
    try { await apiPost('/api/admin/tab', { tab_id: tabId }) } catch (e) {}
  }

  async function handleAddConsumer(e) {
    e.preventDefault()
    setConsumerError('')
    try {
      await apiPost('/api/admin/consumers', { name, meter_no: meterNo, address })
      setName(''); setMeterNo(''); setAddress('')
      loadDashboard()
    } catch (err) {
      setConsumerError(err.message)
    }
  }

  async function handleGenerateBill(e) {
    e.preventDefault()
    setBillError('')
    try {
      await apiPost('/api/admin/bills', { consumer_id: billConsumerId, month, units: Number(units) })
      setBillConsumerId(''); setMonth(''); setUnits('')
      loadDashboard()
    } catch (err) {
      setBillError(err.message)
    }
  }

  async function updateComplaintStatus(id, status) {
    await apiPost(`/api/admin/complaints/${id}/status`, { status })
    loadDashboard()
  }

  async function handleLogout() {
    await onLogout()
    navigate('/')
  }

  const unpaidCount = bills.filter(b => b.status === 'Unpaid').length
  const openComplaints = complaints.filter(c => c.status !== 'Resolved').length

  return (
    <div className="admin">
      <Nav active="/admin" isAdmin={isAdmin} onLogout={handleLogout} />

      <button className="side-toggle" onClick={toggleSidebar} title="Toggle sidebar">
        <span></span><span></span><span></span>
      </button>

      <div className="app">
        <aside className={`side-rail ${collapsed ? 'collapsed' : ''}`}>
          <div className="side-label">Admin Panel</div>
          {TABS.map(t => (
            <button key={t.id} className={`side-link ${activeTab === t.id ? 'active' : ''}`} onClick={() => switchTab(t.id)}>
              {t.label}
            </button>
          ))}
        </aside>

        <div className="backdrop" onClick={toggleSidebar}></div>

        <div className="main">
          <div className="topbar"><h2 className="title">Admin Control Dashboard</h2></div>

          <div className="container">
            <div className="stats">
              <div className="stat"><strong>{consumers.length}</strong><span>Consumers</span></div>
              <div className="stat"><strong>{bills.length}</strong><span>Bills Generated</span></div>
              <div className="stat"><strong>{unpaidCount}</strong><span>Unpaid Bills</span></div>
              <div className="stat"><strong>{openComplaints}</strong><span>Open Complaints</span></div>
            </div>

            <div className={`tab-panel ${activeTab === 'tab-add' ? 'active' : ''}`}>
              <div className="form-box">
                <h3>Register Consumer</h3>
                {consumerError && <div className="error-msg">{consumerError}</div>}
                <form onSubmit={handleAddConsumer}>
                  <div className="form-group">
                    <label>Consumer Full Name</label>
                    <input type="text" value={name} onChange={e => setName(e.target.value)} placeholder="e.g. Ramesh Sharma" required />
                  </div>
                  <div className="form-group">
                    <label>Meter Number</label>
                    <input type="text" value={meterNo} onChange={e => setMeterNo(e.target.value)} placeholder="e.g. MTR-1001" required />
                  </div>
                  <div className="form-group">
                    <label>Address</label>
                    <input type="text" value={address} onChange={e => setAddress(e.target.value)} placeholder="e.g. Flat 204, Green Park" required />
                  </div>
                  <button type="submit" className="btn-submit">Add Consumer</button>
                </form>
              </div>
            </div>

            <div className={`tab-panel ${activeTab === 'tab-bill' ? 'active' : ''}`}>
              <div className="form-box">
                <h3>Generate Monthly Bill</h3>
                {billError && <div className="error-msg">{billError}</div>}
                <form onSubmit={handleGenerateBill}>
                  <div className="form-group">
                    <label>Select Consumer</label>
                    <select value={billConsumerId} onChange={e => setBillConsumerId(e.target.value)} required>
                      <option value="">-- Choose Consumer --</option>
                      {consumers.map(c => (
                        <option key={c.id} value={c.id}>{c.name} (Meter: {c.meter_no})</option>
                      ))}
                    </select>
                  </div>
                  <div className="form-group">
                    <label>Billing Month</label>
                    <input type="month" value={month} onChange={e => setMonth(e.target.value)} required />
                  </div>
                  <div className="form-group">
                    <label>Units Consumed (kWh)</label>
                    <input type="number" min="0" value={units} onChange={e => setUnits(e.target.value)} placeholder="e.g. 150" required />
                  </div>
                  <button type="submit" className="btn-submit">Generate Bill</button>
                </form>
              </div>
            </div>

            <div className={`tab-panel ${activeTab === 'tab-data' ? 'active' : ''}`}>
              <div className="table-section">
                <h3>Registered Consumers ({consumers.length})</h3>
                {consumers.length ? (
                  <table>
                    <thead><tr><th>ID</th><th>Name</th><th>Meter No</th><th>Address</th></tr></thead>
                    <tbody>
                      {consumers.map(c => (
                        <tr key={c.id}><td>{c.id}</td><td>{c.name}</td><td>{c.meter_no}</td><td>{c.address}</td></tr>
                      ))}
                    </tbody>
                  </table>
                ) : <p style={{ color: '#666', fontSize: '14px' }}>No consumers added yet.</p>}
              </div>

              <div className="table-section">
                <h3>Generated Bills ({bills.length})</h3>
                {bills.length ? (
                  <table>
                    <thead><tr><th>Bill ID</th><th>Name</th><th>Meter No</th><th>Month</th><th>Units</th><th>Amount (₹)</th><th>Status</th></tr></thead>
                    <tbody>
                      {bills.map(b => (
                        <tr key={b.id}>
                          <td>#{b.id}</td><td>{b.name}</td><td>{b.meter_no}</td><td>{b.month}</td><td>{b.units}</td>
                          <td>₹{b.amount.toFixed(2)}</td>
                          <td><span className={`badge ${b.status === 'Paid' ? 'badge-paid' : 'badge-unpaid'}`}>{b.status}</span></td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                ) : <p style={{ color: '#666', fontSize: '14px' }}>No bills generated yet.</p>}
              </div>

              <div className="table-section">
                <h3>Consumer Complaints ({complaints.length})</h3>
                {complaints.length ? (
                  <table>
                    <thead><tr><th>ID</th><th>Consumer</th><th>Category</th><th>Description</th><th>Status</th><th>Update Status</th></tr></thead>
                    <tbody>
                      {complaints.map(cmp => (
                        <tr key={cmp.id}>
                          <td>#{cmp.id}</td><td>{cmp.name}</td><td>{cmp.category}</td><td>{cmp.description}</td>
                          <td>
                            <span className={`badge ${cmp.status === 'Resolved' ? 'badge-resolved' : cmp.status === 'In Progress' ? 'badge-progress' : 'badge-pending'}`}>
                              {cmp.status}
                            </span>
                          </td>
                          <td>
                            <div className="actions-cell">
                              {cmp.status !== 'In Progress' && cmp.status !== 'Resolved' && (
                                <button className="btn-status btn-progress" onClick={() => updateComplaintStatus(cmp.id, 'In Progress')}>In Progress</button>
                              )}
                              {cmp.status !== 'Resolved' ? (
                                <button className="btn-status btn-resolve" onClick={() => updateComplaintStatus(cmp.id, 'Resolved')}>Resolve</button>
                              ) : (
                                <span style={{ color: '#666', fontSize: '13px' }}>Completed</span>
                              )}
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                ) : <p style={{ color: '#666', fontSize: '14px' }}>No complaints filed yet.</p>}
              </div>
            </div>
          </div>
        </div>
      </div>

      <footer>PowerPay Admin &copy; 2026</footer>
    </div>
  )
}
