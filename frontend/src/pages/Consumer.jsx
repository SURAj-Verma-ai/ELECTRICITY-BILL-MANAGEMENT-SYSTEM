import { useState } from 'react'
import Nav from '../components/Nav'
import { apiPost } from '../api'

export default function Consumer({ isAdmin, onLogout }) {
  const [meterNo, setMeterNo] = useState('')
  const [searched, setSearched] = useState(false)
  const [consumer, setConsumer] = useState(null)
  const [bills, setBills] = useState([])

  async function handleSearch(e) {
    e.preventDefault()
    const data = await apiPost('/api/consumer/search', { meter_no: meterNo })
    setConsumer(data.consumer)
    setBills(data.bills || [])
    setSearched(true)
  }

  async function handlePay(billId) {
    await apiPost(`/api/consumer/pay/${billId}`, {})
    const data = await apiPost('/api/consumer/search', { meter_no: meterNo })
    setConsumer(data.consumer)
    setBills(data.bills || [])
  }

  return (
    <>
      <Nav active="/consumer" isAdmin={isAdmin} onLogout={onLogout} />

      <div className={`container ${!searched ? 'hero-mode' : ''}`}>
        {!searched && <img src="/static/images/consumer/pay-illustration.webp" alt="" className="hero-img" />}
        <h1>Find Electricity Bills</h1>

        <div className="search-box">
          <p>Enter your meter number to check pending dues and bill payment receipts.</p>
          <form className="input-row" onSubmit={handleSearch}>
            <input type="text" placeholder="e.g. MTR-1001" value={meterNo} onChange={e => setMeterNo(e.target.value)} required />
            <button type="submit">Search</button>
          </form>
        </div>

        {searched && (
          <div>
            {consumer ? (
              <>
                <div className="user-info">
                  <h3>{consumer.name}</h3>
                  <p>Meter Number: <strong>{consumer.meter_no}</strong> | Address: {consumer.address}</p>
                </div>

                {bills.length > 0 ? (
                  <table>
                    <thead>
                      <tr><th>Bill No</th><th>Month</th><th>Units (kWh)</th><th>Amount</th><th>Status</th><th>Action</th></tr>
                    </thead>
                    <tbody>
                      {bills.map(b => (
                        <tr key={b.id}>
                          <td>#{b.id}</td>
                          <td>{b.month}</td>
                          <td>{b.units}</td>
                          <td><strong>₹{b.amount.toFixed(2)}</strong></td>
                          <td><span className={b.status === 'Paid' ? 'badge-paid' : 'badge-unpaid'}>{b.status}</span></td>
                          <td>
                            {b.status === 'Unpaid'
                              ? <button className="btn-pay" onClick={() => handlePay(b.id)}>Pay ₹{b.amount.toFixed(2)}</button>
                              : <span style={{ color: '#166534', fontWeight: 'bold', fontSize: '13px' }}>Paid</span>}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                ) : (
                  <p style={{ color: '#666', fontSize: '14px' }}>No bills generated for this meter yet.</p>
                )}
              </>
            ) : (
              <p style={{ color: '#b91c1c', fontSize: '14px' }}>No consumer found with meter number "{meterNo}". Please check and try again.</p>
            )}
          </div>
        )}
      </div>

      <footer>PowerPay Consumer Portal &copy; 2026</footer>
    </>
  )
}
