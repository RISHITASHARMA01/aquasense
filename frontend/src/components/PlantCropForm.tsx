import { useEffect, useState, type FormEvent } from 'react';
import * as api from '../api/fields';
import type { Crop } from '../types';

export default function PlantCropForm({ fieldId, onPlanted }: { fieldId: number; onPlanted: () => void }) {
  const [crops, setCrops] = useState<Crop[]>([]);
  const [cropId, setCropId] = useState<number | ''>('');
  const [plantingDate, setPlantingDate] = useState(new Date().toISOString().slice(0, 10));
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    api.listCrops().then((c) => {
      setCrops(c);
      if (c.length) setCropId(c[0].id);
    });
  }, []);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!cropId) return;
    setError('');
    setLoading(true);
    try {
      await api.plantCrop(fieldId, cropId, plantingDate);
      onPlanted();
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Could not plant crop');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="bg-white rounded-xl border border-dashed border-slate-300 p-6">
      <h3 className="font-semibold text-slate-800 mb-3">Plant a Crop</h3>
      <form onSubmit={handleSubmit} className="flex flex-col sm:flex-row gap-3 items-end">
        <div className="flex-1 w-full">
          <label className="block text-xs font-medium text-slate-500 mb-1">Crop</label>
          <select
            value={cropId}
            onChange={(e) => setCropId(Number(e.target.value))}
            className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
          >
            {crops.map((c) => (
              <option key={c.id} value={c.id}>
                {c.name}
              </option>
            ))}
          </select>
        </div>
        <div className="w-full sm:w-44">
          <label className="block text-xs font-medium text-slate-500 mb-1">Planting date</label>
          <input
            type="date"
            value={plantingDate}
            onChange={(e) => setPlantingDate(e.target.value)}
            className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
          />
        </div>
        <button
          type="submit"
          disabled={loading || !cropId}
          className="bg-aqua-600 hover:bg-aqua-700 text-white text-sm font-medium px-4 py-2 rounded-lg transition disabled:opacity-50 w-full sm:w-auto"
        >
          {loading ? 'Planting...' : 'Plant'}
        </button>
      </form>
      {error && <p className="text-sm text-red-600 mt-2">{error}</p>}
    </div>
  );
}
