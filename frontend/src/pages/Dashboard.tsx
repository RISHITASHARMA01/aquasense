import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import * as api from '../api/fields';
import type { Field, Recommendation } from '../types';
import FieldCard from '../components/FieldCard';

export default function Dashboard() {
  const [fields, setFields] = useState<Field[]>([]);
  const [recommendations, setRecommendations] = useState<Record<number, Recommendation | null>>({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.listFields().then(async (fetchedFields) => {
      setFields(fetchedFields);
      setLoading(false);

      fetchedFields.forEach((field) => {
        if (!field.crops.some((c) => c.is_active)) return;
        api
          .getRecommendation(field.id)
          .then((rec) => setRecommendations((prev) => ({ ...prev, [field.id]: rec })))
          .catch(() => setRecommendations((prev) => ({ ...prev, [field.id]: null })));
      });
    });
  }, []);

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-slate-800">Your Fields</h1>
          <p className="text-slate-500 text-sm">At-a-glance irrigation status across all fields</p>
        </div>
        <Link
          to="/fields/new"
          className="bg-aqua-600 hover:bg-aqua-700 text-white text-sm font-medium px-4 py-2 rounded-lg transition"
        >
          + Add Field
        </Link>
      </div>

      {loading ? (
        <p className="text-slate-500">Loading fields...</p>
      ) : fields.length === 0 ? (
        <div className="bg-white rounded-xl border border-dashed border-slate-300 p-12 text-center">
          <p className="text-slate-500 mb-4">No fields yet. Add your first field to get started.</p>
          <Link
            to="/fields/new"
            className="inline-block bg-aqua-600 hover:bg-aqua-700 text-white text-sm font-medium px-4 py-2 rounded-lg transition"
          >
            + Add Field
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {fields.map((field) => {
            const rec = recommendations[field.id];
            const hasActiveCrop = field.crops.some((c) => c.is_active);
            const moisturePercent = rec ? 100 * (1 - rec.depletion_mm / rec.taw_mm) : undefined;
            return (
              <FieldCard
                key={field.id}
                field={field}
                needsWater={hasActiveCrop ? rec?.needs_irrigation : undefined}
                moisturePercent={moisturePercent}
                loading={hasActiveCrop && rec === undefined}
              />
            );
          })}
        </div>
      )}
    </div>
  );
}
