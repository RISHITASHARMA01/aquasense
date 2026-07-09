import { useEffect, useState, type FormEvent } from 'react';
import { useNavigate, useParams, Link } from 'react-router-dom';
import * as api from '../api/fields';
import { SOIL_TYPES, IRRIGATION_METHODS } from '../types';

export default function FieldForm() {
  const { fieldId } = useParams();
  const isEdit = !!fieldId;
  const navigate = useNavigate();

  const [name, setName] = useState('');
  const [latitude, setLatitude] = useState('');
  const [longitude, setLongitude] = useState('');
  const [soilType, setSoilType] = useState<string>(SOIL_TYPES[2]);
  const [areaHectares, setAreaHectares] = useState('');
  const [irrigationMethod, setIrrigationMethod] = useState<string>(IRRIGATION_METHODS[0]);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!isEdit) return;
    api.getField(Number(fieldId)).then((field) => {
      setName(field.name);
      setLatitude(String(field.latitude));
      setLongitude(String(field.longitude));
      setSoilType(field.soil_type);
      setAreaHectares(String(field.area_hectares));
      setIrrigationMethod(field.irrigation_method);
    });
  }, [fieldId, isEdit]);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      if (isEdit) {
        await api.updateField(Number(fieldId), {
          name,
          soil_type: soilType,
          area_hectares: Number(areaHectares),
          irrigation_method: irrigationMethod,
        });
        navigate(`/fields/${fieldId}`);
      } else {
        const field = await api.createField({
          name,
          latitude: Number(latitude),
          longitude: Number(longitude),
          soil_type: soilType,
          area_hectares: Number(areaHectares),
          irrigation_method: irrigationMethod,
        });
        navigate(`/fields/${field.id}`);
      }
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Something went wrong');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="max-w-lg mx-auto">
      <Link to="/" className="text-sm text-aqua-600 mb-4 inline-block">
        ← Back to dashboard
      </Link>
      <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
        <h1 className="text-xl font-bold text-slate-800 mb-4">{isEdit ? 'Edit Field' : 'Add a New Field'}</h1>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-600 mb-1">Field name</label>
            <input
              required
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full rounded-lg border border-slate-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-aqua-400"
              placeholder="North Plot"
            />
          </div>

          {!isEdit && (
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-sm font-medium text-slate-600 mb-1">Latitude</label>
                <input
                  required
                  type="number"
                  step="any"
                  value={latitude}
                  onChange={(e) => setLatitude(e.target.value)}
                  className="w-full rounded-lg border border-slate-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-aqua-400"
                  placeholder="28.6139"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-600 mb-1">Longitude</label>
                <input
                  required
                  type="number"
                  step="any"
                  value={longitude}
                  onChange={(e) => setLongitude(e.target.value)}
                  className="w-full rounded-lg border border-slate-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-aqua-400"
                  placeholder="77.2090"
                />
              </div>
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-slate-600 mb-1">Soil type</label>
            <select
              value={soilType}
              onChange={(e) => setSoilType(e.target.value)}
              className="w-full rounded-lg border border-slate-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-aqua-400 capitalize"
            >
              {SOIL_TYPES.map((s) => (
                <option key={s} value={s} className="capitalize">
                  {s.replace('_', ' ')}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-600 mb-1">Area (hectares)</label>
            <input
              required
              type="number"
              step="any"
              min="0"
              value={areaHectares}
              onChange={(e) => setAreaHectares(e.target.value)}
              className="w-full rounded-lg border border-slate-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-aqua-400"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-600 mb-1">Irrigation method</label>
            <select
              value={irrigationMethod}
              onChange={(e) => setIrrigationMethod(e.target.value)}
              className="w-full rounded-lg border border-slate-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-aqua-400 capitalize"
            >
              {IRRIGATION_METHODS.map((m) => (
                <option key={m} value={m}>
                  {m}
                </option>
              ))}
            </select>
          </div>

          {error && <p className="text-sm text-red-600">{error}</p>}

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-aqua-600 hover:bg-aqua-700 text-white font-medium py-2 rounded-lg transition disabled:opacity-50"
          >
            {loading ? 'Saving...' : isEdit ? 'Save Changes' : 'Create Field'}
          </button>
        </form>
      </div>
    </div>
  );
}
