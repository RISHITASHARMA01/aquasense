import type { ForecastPoint } from '../types';

function weatherEmoji(point: ForecastPoint): string {
  if (point.precipitation_mm >= 5) return '🌧️';
  if (point.precipitation_mm > 0) return '🌦️';
  if (point.t_max_c >= 35) return '☀️';
  return '⛅';
}

export default function WeatherStrip({ points }: { points: ForecastPoint[] }) {
  return (
    <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm">
      <h3 className="font-semibold text-slate-800 mb-4">7-Day Forecast</h3>
      <div className="grid grid-cols-4 sm:grid-cols-7 gap-2">
        {points.map((p) => (
          <div key={p.date} className="text-center bg-slate-50 rounded-lg py-3">
            <p className="text-xs text-slate-500">
              {new Date(p.date).toLocaleDateString(undefined, { weekday: 'short' })}
            </p>
            <p className="text-xl my-1">{weatherEmoji(p)}</p>
            <p className="text-xs font-medium text-slate-700">
              {Math.round(p.t_max_c)}° / {Math.round(p.t_min_c)}°
            </p>
            {p.precipitation_mm > 0 && <p className="text-[10px] text-aqua-600">{p.precipitation_mm.toFixed(0)}mm</p>}
          </div>
        ))}
      </div>
    </div>
  );
}
