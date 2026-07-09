import {
  ResponsiveContainer,
  ComposedChart,
  Area,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend,
} from 'recharts';
import type { HistoryPoint } from '../types';

export default function MoistureChart({ points, tawMm }: { points: HistoryPoint[]; tawMm: number }) {
  const data = points.map((p) => ({
    date: p.date.slice(5),
    'Soil moisture (%)': Math.max(0, Math.min(100, 100 * (1 - p.depletion_mm / tawMm))),
    'Rain (mm)': p.precipitation_mm,
    'ETc (mm)': p.etc_mm,
  }));

  return (
    <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm">
      <h3 className="font-semibold text-slate-800 mb-4">Moisture & ET Trend (last {points.length} days)</h3>
      <ResponsiveContainer width="100%" height={280}>
        <ComposedChart data={data} margin={{ top: 5, right: 10, left: -10, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
          <XAxis dataKey="date" tick={{ fontSize: 12 }} />
          <YAxis yAxisId="left" tick={{ fontSize: 12 }} unit="%" domain={[0, 100]} />
          <YAxis yAxisId="right" orientation="right" tick={{ fontSize: 12 }} unit="mm" />
          <Tooltip />
          <Legend wrapperStyle={{ fontSize: 12 }} />
          <Area
            yAxisId="left"
            type="monotone"
            dataKey="Soil moisture (%)"
            stroke="#0f8cd1"
            fill="#b8eaff"
            strokeWidth={2}
          />
          <Bar yAxisId="right" dataKey="Rain (mm)" fill="#60a5fa" barSize={8} />
          <Bar yAxisId="right" dataKey="ETc (mm)" fill="#f59e0b" barSize={8} />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
}
