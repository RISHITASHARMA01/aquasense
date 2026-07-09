import { useEffect, useState } from 'react';
import * as api from '../api/fields';
import type { Field, WaterSavings as WaterSavingsType } from '../types';
import WaterSavingsChart from '../components/WaterSavingsChart';

interface FieldSavings {
  field: Field;
  savings: WaterSavingsType;
}

export default function WaterSavings() {
  const [results, setResults] = useState<FieldSavings[]>([]);
  const [loading, setLoading] = useState(true);
  const [hasFields, setHasFields] = useState(true);

  useEffect(() => {
    api.listFields().then(async (fields) => {
      setHasFields(fields.length > 0);
      const withCrops = fields.filter((f) => f.crops.some((c) => c.is_active));
      const settled = await Promise.allSettled(
        withCrops.map(async (field) => ({ field, savings: await api.getWaterSavings(field.id) }))
      );
      setResults(
        settled
          .filter((r): r is PromiseFulfilledResult<FieldSavings> => r.status === 'fulfilled')
          .map((r) => r.value)
      );
      setLoading(false);
    });
  }, []);

  const totalAqua = results.reduce((sum, r) => sum + r.savings.aquasense_total_mm, 0);
  const totalFixed = results.reduce((sum, r) => sum + r.savings.fixed_schedule_total_mm, 0);
  const overallPercent = totalFixed > 0 ? Math.round((100 * (totalFixed - totalAqua)) / totalFixed) : 0;

  const rows = results.map((r) => ({
    name: r.field.name,
    'AquaSense (mm)': r.savings.aquasense_total_mm,
    'Fixed Schedule (mm)': r.savings.fixed_schedule_total_mm,
  }));

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-800">Water Savings</h1>
        <p className="text-slate-500 text-sm">
          AquaSense's demand-based irrigation vs. a fixed calendar schedule, over each field's simulated history
        </p>
      </div>

      {loading ? (
        <p className="text-slate-500">Crunching the numbers...</p>
      ) : !hasFields ? (
        <p className="text-slate-500">Add a field and plant a crop to see water savings.</p>
      ) : results.length === 0 ? (
        <p className="text-slate-500">Plant a crop in at least one field to see water savings.</p>
      ) : (
        <>
          <div className="bg-gradient-to-br from-aqua-600 to-aqua-800 text-white rounded-2xl p-8 text-center shadow-lg">
            <p className="text-sm uppercase tracking-wide text-aqua-100 mb-1">Overall Water Saved</p>
            <p className="text-6xl font-extrabold">{overallPercent}%</p>
            <p className="text-aqua-100 mt-2 text-sm">
              {Math.round(totalAqua)}mm applied by AquaSense vs. {Math.round(totalFixed)}mm under a fixed schedule,
              across {results.length} field{results.length > 1 ? 's' : ''}
            </p>
          </div>

          <WaterSavingsChart rows={rows} />

          <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
            <table className="w-full text-sm">
              <thead className="bg-slate-50 text-slate-500 text-xs uppercase">
                <tr>
                  <th className="text-left px-4 py-2">Field</th>
                  <th className="text-right px-4 py-2">AquaSense (mm)</th>
                  <th className="text-right px-4 py-2">AquaSense events</th>
                  <th className="text-right px-4 py-2">Fixed (mm)</th>
                  <th className="text-right px-4 py-2">Fixed events</th>
                  <th className="text-right px-4 py-2">Saved</th>
                </tr>
              </thead>
              <tbody>
                {results.map((r) => (
                  <tr key={r.field.id} className="border-t border-slate-100">
                    <td className="px-4 py-2 font-medium text-slate-700">{r.field.name}</td>
                    <td className="px-4 py-2 text-right">{r.savings.aquasense_total_mm.toFixed(0)}</td>
                    <td className="px-4 py-2 text-right">{r.savings.aquasense_events}</td>
                    <td className="px-4 py-2 text-right">{r.savings.fixed_schedule_total_mm.toFixed(0)}</td>
                    <td className="px-4 py-2 text-right">{r.savings.fixed_schedule_events}</td>
                    <td className="px-4 py-2 text-right font-semibold text-aqua-700">
                      {r.savings.percent_water_saved.toFixed(0)}%
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <p className="text-xs text-slate-400">
            Fixed schedule baseline: irrigate every {results[0]?.savings.fixed_schedule_interval_days ?? 3} days back
            to the readily-available-water threshold, regardless of actual soil moisture — a common calendar-based
            practice this app is meant to replace.
          </p>
        </>
      )}
    </div>
  );
}
