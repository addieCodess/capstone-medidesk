import React, { useEffect, useState } from 'react';

const API = '/api/appointments';

export default function App() {
  const [items, setItems] = useState([]);
  const [stats, setStats] = useState(null);
  const [filter, setFilter] = useState('all');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [form, setForm] = useState({ patient_name: '', doctor_name: 'Dr. Rao', reason: '', priority: 'medium', status: 'scheduled', scheduled_for: '' });

  const load = async () => {
    setLoading(true); setError('');
    try {
      const [a, s] = await Promise.all([
        fetch(filter === 'all' ? API : `${API}?status=${filter}`).then(r => { if (!r.ok) throw new Error('backend unreachable'); return r.json(); }),
        fetch(`${API}/stats`).then(r => r.json())
      ]);
      setItems(a); setStats(s);
    } catch (e) { setError('Backend unreachable. Start with docker compose up --build'); }
    setLoading(false);
  };
  useEffect(() => { load(); }, [filter]);

  const create = async (e) => {
    e.preventDefault();
    const r = await fetch(API, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(form) });
    if (r.ok) { setShowModal(false); setForm({ patient_name: '', doctor_name: 'Dr. Rao', reason: '', priority: 'medium', status: 'scheduled', scheduled_for: '' }); load(); }
  };
  const remove = async (id) => { await fetch(`${API}/${id}`, { method: 'DELETE' }); load(); };
  const advance = async (it) => {
    const next = it.status === 'scheduled' ? 'checked-in' : it.status === 'checked-in' ? 'completed' : 'scheduled';
    await fetch(`${API}/${it.id}`, { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ status: next }) });
    load();
  };

  return (
    <div className="layout">
      <aside className="sidebar">
        <h2>🏥 MediDesk</h2>
        <nav><a className="active" href="#">Dashboard</a><a href="#">Appointments</a><a href="#">Doctors</a><a href="#">Pipeline ●</a></nav>
        <div className="side-foot">CI: GH Actions → GHCR<br />CD: Helm → EKS</div>
      </aside>
      <main>
        <header className="topbar"><div><h1>Clinic Appointments</h1><p>Schedule, check-in and track patient visits</p></div>
          <button className="primary" onClick={() => setShowModal(true)}>+ New appointment</button></header>
        <section className="kpis">
          <div className="card"><span>Total</span><b>{stats?.total ?? '—'}</b></div>
          <div className="card"><span>Scheduled</span><b>{stats?.by_status?.scheduled ?? 0}</b></div>
          <div className="card"><span>Checked-in</span><b>{stats?.by_status?.['checked-in'] ?? 0}</b></div>
          <div className="card alert"><span>Urgent</span><b>{stats?.urgent ?? 0}</b></div>
        </section>
        <section className="filters">
          {['all', 'scheduled', 'checked-in', 'completed', 'cancelled'].map(f => (
            <button key={f} className={filter === f ? 'chip active' : 'chip'} onClick={() => setFilter(f)}>{f}</button>
          ))}
        </section>
        {loading ? <p>Loading…</p> : error ? <p className="err">{error}</p> : (
          <table className="table">
            <thead><tr><th>#</th><th>Patient</th><th>Doctor</th><th>Reason</th><th>Status</th><th>Priority</th><th>Actions</th></tr></thead>
            <tbody>{items.map(it => (
              <tr key={it.id}><td>{it.id}</td><td>{it.patient_name}</td><td>{it.doctor_name}</td><td>{it.reason}</td>
                <td><span className={`badge ${it.status}`}>{it.status}</span></td>
                <td><span className={`badge ${it.priority}`}>{it.priority}</span></td>
                <td><button onClick={() => advance(it)}>Advance</button> <button onClick={() => remove(it.id)}>Delete</button></td></tr>
            ))}</tbody>
          </table>
        )}
        <section className="feed"><h3>Activity</h3><p>● Pipeline passing → images pushed to GHCR with commit SHA</p><p>● EKS + Helm + Prometheus/Grafana live</p></section>
        {showModal && (
          <div className="modal-bg" onClick={() => setShowModal(false)}>
            <form className="modal" onClick={e => e.stopPropagation()} onSubmit={create}>
              <h3>New appointment</h3>
              <input placeholder="Patient name" value={form.patient_name} onChange={e => setForm({ ...form, patient_name: e.target.value })} required />
              <input placeholder="Doctor" value={form.doctor_name} onChange={e => setForm({ ...form, doctor_name: e.target.value })} />
              <input placeholder="Reason" value={form.reason} onChange={e => setForm({ ...form, reason: e.target.value })} />
              <div className="row">
                <select value={form.priority} onChange={e => setForm({ ...form, priority: e.target.value })}><option>low</option><option>medium</option><option>high</option><option>urgent</option></select>
                <select value={form.status} onChange={e => setForm({ ...form, status: e.target.value })}><option>scheduled</option><option>checked-in</option><option>completed</option><option>cancelled</option></select>
              </div>
              <input type="datetime-local" value={form.scheduled_for} onChange={e => setForm({ ...form, scheduled_for: e.target.value })} />
              <div className="row"><button type="submit" className="primary">Create</button><button type="button" onClick={() => setShowModal(false)}>Cancel</button></div>
            </form>
          </div>
        )}
      </main>
    </div>
  );
}
