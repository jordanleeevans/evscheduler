import { useMemo } from 'react';
import { useQuery } from '@apollo/client';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ReferenceLine,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { GET_TARIFF_PRICES } from '../graphql/queries';
import type { TariffPrice } from '../types';

interface TariffChartProps {
  selectedSlotStarts?: string[];
}

export default function TariffChart({ selectedSlotStarts = [] }: TariffChartProps) {
  const now = useMemo(() => new Date(), []);
  const tomorrow = useMemo(() => {
    const d = new Date(now);
    d.setDate(d.getDate() + 1);
    return d;
  }, [now]);

  const { data, loading, error } = useQuery<{ tariffPrices: TariffPrice[] }>(GET_TARIFF_PRICES, {
    variables: {
      from: now.toISOString(),
      to: tomorrow.toISOString(),
      region: 'C',
    },
  });

  if (loading) return <p>Loading tariff prices…</p>;
  if (error) return <p>Error loading tariff data: {error.message}</p>;

  const chartData = (data?.tariffPrices ?? []).map((p) => ({
    time: new Date(p.slotStart).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    price: p.pricePerKwh,
    isSelected: selectedSlotStarts.includes(p.slotStart),
  }));

  return (
    <div style={{ padding: '1rem' }}>
      <h2 style={{ fontSize: '1.125rem', fontWeight: 600, marginBottom: '0.75rem' }}>
        24h Agile Tariff Prices
      </h2>
      <ResponsiveContainer width="100%" height={280}>
        <AreaChart data={chartData} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
          <defs>
            <linearGradient id="priceGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
              <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis dataKey="time" tick={{ fontSize: 11 }} interval={3} />
          <YAxis
            tickFormatter={(v) => `${v}p`}
            tick={{ fontSize: 11 }}
            label={{ value: 'p/kWh', angle: -90, position: 'insideLeft', fontSize: 11 }}
          />
          <Tooltip formatter={(value: number) => [`${value}p/kWh`, 'Price']} />
          <Legend />
          <Area
            type="monotone"
            dataKey="price"
            stroke="#3b82f6"
            fill="url(#priceGradient)"
            strokeWidth={2}
            name="Tariff (p/kWh)"
          />
          {selectedSlotStarts.map((slotStart) => (
            <ReferenceLine
              key={slotStart}
              x={new Date(slotStart).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              stroke="#10b981"
              strokeWidth={2}
              label={{ value: '✓', fill: '#10b981', fontSize: 12 }}
            />
          ))}
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
