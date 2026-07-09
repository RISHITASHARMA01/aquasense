import { Link } from 'react-router-dom';
import type { Field } from '../types';

interface Props {
  field: Field;
  needsWater?: boolean;
  moisturePercent?: number;
  loading?: boolean;
}

export default function FieldCard({ field, needsWater, moisturePercent, loading }: Props) {
  const activeCrop = field.crops.find((c) => c.is_active);

  return (
    <Link
      to={`/fields/${field.id}`}
      className="block bg-white rounded-xl shadow-sm border border-slate-200 p-5 hover:shadow-md hover:border-aqua-300 transition"
    >
      <div className="flex items-start justify-between mb-3">
        <div>
          <h3 className="font-semibold text-slate-800">{field.name}</h3>
          <p className="text-xs text-slate-500">
            {activeCrop ? activeCrop.crop.name : 'No crop planted'} · {field.area_hectares} ha
          </p>
        </div>
        {loading ? (
          <span className="text-xs text-slate-400">…</span>
        ) : needsWater === undefined ? null : needsWater ? (
          <span className="inline-flex items-center gap-1 bg-amber-100 text-amber-800 text-xs font-medium px-2 py-1 rounded-full">
            💧 Water today
          </span>
        ) : (
          <span className="inline-flex items-center gap-1 bg-emerald-100 text-emerald-800 text-xs font-medium px-2 py-1 rounded-full">
            ✓ OK
          </span>
        )}
      </div>

      {moisturePercent !== undefined && (
        <div>
          <div className="flex justify-between text-xs text-slate-500 mb-1">
            <span>Soil moisture</span>
            <span>{moisturePercent.toFixed(0)}%</span>
          </div>
          <div className="w-full bg-slate-100 rounded-full h-2">
            <div
              className={`h-2 rounded-full ${moisturePercent < 30 ? 'bg-red-400' : moisturePercent < 60 ? 'bg-amber-400' : 'bg-emerald-500'}`}
              style={{ width: `${Math.max(0, Math.min(100, moisturePercent))}%` }}
            />
          </div>
        </div>
      )}

      <p className="text-xs text-slate-400 mt-3 capitalize">
        {field.soil_type.replace('_', ' ')} soil · {field.irrigation_method} irrigation
      </p>
    </Link>
  );
}
