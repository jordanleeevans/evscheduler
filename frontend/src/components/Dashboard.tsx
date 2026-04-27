import { useQuery } from '@apollo/client';
import { Link } from 'react-router-dom';
import { GET_CHARGING_SESSIONS } from '../graphql/queries';
import type { ChargingSession, SessionStatus } from '../types';

const STATUS_COLORS: Record<SessionStatus, string> = {
  PENDING: '#f59e0b',
  SCHEDULED: '#3b82f6',
  ACTIVE: '#10b981',
  COMPLETED: '#6b7280',
  CANCELLED: '#ef4444',
};

function StatusBadge({ status }: { status: SessionStatus }) {
  return (
    <span
      style={{
        backgroundColor: STATUS_COLORS[status],
        color: '#fff',
        padding: '2px 8px',
        borderRadius: '9999px',
        fontSize: '0.75rem',
        fontWeight: 600,
      }}
    >
      {status}
    </span>
  );
}

export default function Dashboard() {
  const { data, loading, error } = useQuery<{ chargingSessions: ChargingSession[] }>(
    GET_CHARGING_SESSIONS
  );

  if (loading) return <p>Loading sessions…</p>;
  if (error) return <p>Error loading sessions: {error.message}</p>;

  const sessions = data?.chargingSessions ?? [];

  return (
    <div style={{ padding: '1.5rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
        <h1 style={{ fontSize: '1.5rem', fontWeight: 700 }}>EV Charging Dashboard</h1>
        <Link
          to="/schedule"
          style={{
            backgroundColor: '#3b82f6',
            color: '#fff',
            padding: '0.5rem 1rem',
            borderRadius: '0.375rem',
            textDecoration: 'none',
            fontWeight: 600,
          }}
        >
          + New Session
        </Link>
      </div>

      {sessions.length === 0 ? (
        <p style={{ color: '#6b7280' }}>No charging sessions yet. Schedule one to get started.</p>
      ) : (
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ borderBottom: '2px solid #e5e7eb', textAlign: 'left' }}>
              <th style={{ padding: '0.5rem' }}>Vehicle</th>
              <th style={{ padding: '0.5rem' }}>Departure</th>
              <th style={{ padding: '0.5rem' }}>Target %</th>
              <th style={{ padding: '0.5rem' }}>Status</th>
            </tr>
          </thead>
          <tbody>
            {sessions.map((session) => (
              <tr key={session.id} style={{ borderBottom: '1px solid #e5e7eb' }}>
                <td style={{ padding: '0.75rem 0.5rem' }}>{session.vehicle.name}</td>
                <td style={{ padding: '0.75rem 0.5rem' }}>
                  {new Date(session.departureTime).toLocaleString()}
                </td>
                <td style={{ padding: '0.75rem 0.5rem' }}>{session.targetChargePct}%</td>
                <td style={{ padding: '0.75rem 0.5rem' }}>
                  <StatusBadge status={session.status} />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
