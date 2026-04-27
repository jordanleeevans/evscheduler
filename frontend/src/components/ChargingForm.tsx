import React, { useState } from 'react';
import { useQuery, useMutation } from '@apollo/client';
import { useNavigate } from 'react-router-dom';
import { GET_VEHICLES, GET_CHARGING_SESSIONS } from '../graphql/queries';
import { SCHEDULE_CHARGING_SESSION } from '../graphql/mutations';
import type { Vehicle } from '../types';

export default function ChargingForm() {
  const navigate = useNavigate();
  const { data: vehiclesData, loading: vehiclesLoading } = useQuery<{ vehicles: Vehicle[] }>(GET_VEHICLES);

  const [vehicleId, setVehicleId] = useState('');
  const [departureTime, setDepartureTime] = useState('');
  const [targetChargePct, setTargetChargePct] = useState(80);
  const [currentBatteryPct, setCurrentBatteryPct] = useState(20);

  const [scheduleSession, { loading, error }] = useMutation(SCHEDULE_CHARGING_SESSION, {
    refetchQueries: [{ query: GET_CHARGING_SESSIONS }],
    onCompleted: () => navigate('/'),
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!vehicleId || !departureTime) return;

    scheduleSession({
      variables: {
        vehicleId,
        departureTime: new Date(departureTime).toISOString(),
        targetChargePct,
      },
    });
  };

  const inputStyle: React.CSSProperties = {
    width: '100%',
    padding: '0.5rem',
    border: '1px solid #d1d5db',
    borderRadius: '0.375rem',
    fontSize: '1rem',
    boxSizing: 'border-box',
  };

  const labelStyle: React.CSSProperties = {
    display: 'block',
    marginBottom: '0.25rem',
    fontWeight: 600,
    fontSize: '0.875rem',
    color: '#374151',
  };

  return (
    <div style={{ padding: '1.5rem', maxWidth: '480px', margin: '0 auto' }}>
      <h1 style={{ fontSize: '1.5rem', fontWeight: 700, marginBottom: '1.5rem' }}>
        Schedule Charging Session
      </h1>

      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        <div>
          <label style={labelStyle}>Vehicle</label>
          <select
            value={vehicleId}
            onChange={(e) => setVehicleId(e.target.value)}
            required
            style={inputStyle}
          >
            <option value="">Select a vehicle…</option>
            {vehiclesLoading && <option disabled>Loading…</option>}
            {vehiclesData?.vehicles.map((v) => (
              <option key={v.id} value={v.id}>
                {v.name}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label style={labelStyle}>Departure Time</label>
          <input
            type="datetime-local"
            value={departureTime}
            onChange={(e) => setDepartureTime(e.target.value)}
            required
            style={inputStyle}
          />
        </div>

        <div>
          <label style={labelStyle}>Target Charge % (current: {currentBatteryPct}%)</label>
          <input
            type="number"
            min={0}
            max={100}
            value={targetChargePct}
            onChange={(e) => setTargetChargePct(Number(e.target.value))}
            required
            style={inputStyle}
          />
        </div>

        <div>
          <label style={labelStyle}>Current Battery %</label>
          <input
            type="number"
            min={0}
            max={100}
            value={currentBatteryPct}
            onChange={(e) => setCurrentBatteryPct(Number(e.target.value))}
            required
            style={inputStyle}
          />
        </div>

        {error && (
          <p style={{ color: '#ef4444', fontSize: '0.875rem' }}>
            Error: {error.message}
          </p>
        )}

        <div style={{ display: 'flex', gap: '0.75rem' }}>
          <button
            type="submit"
            disabled={loading}
            style={{
              flex: 1,
              backgroundColor: '#3b82f6',
              color: '#fff',
              padding: '0.625rem 1rem',
              border: 'none',
              borderRadius: '0.375rem',
              fontSize: '1rem',
              fontWeight: 600,
              cursor: loading ? 'not-allowed' : 'pointer',
              opacity: loading ? 0.7 : 1,
            }}
          >
            {loading ? 'Scheduling…' : 'Schedule Charging'}
          </button>
          <button
            type="button"
            onClick={() => navigate('/')}
            style={{
              backgroundColor: '#e5e7eb',
              color: '#374151',
              padding: '0.625rem 1rem',
              border: 'none',
              borderRadius: '0.375rem',
              fontSize: '1rem',
              cursor: 'pointer',
            }}
          >
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
}
