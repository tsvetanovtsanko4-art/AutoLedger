import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api, { apiErrorMessage } from '../api';

// Must match the TransmissionType / DriveType enums on the server.
const TRANSMISSIONS = ['Manual', 'Automatic', 'CVT', 'DCT'];
const DRIVE_TYPES = ['FWD', 'RWD', 'AWD'];

const CarEditForm = () => {
    const { id } = useParams();
    const navigate = useNavigate();
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [error, setError] = useState(null);
    const [formData, setFormData] = useState({
        plate: '',
        make: '',
        model: '',
        model_year: '',
        current_odometer: '',
        engine_model: '',
        engine_volume: '',
        transmission: '',
        drive_type: '',
        tire_size: '',
    });
    const [vin, setVin] = useState('');

    useEffect(() => {
        const fetchCar = async () => {
            try {
                const res = await api.get(`/cars/${id}`);
                const c = res.data;
                setVin(c.vin || '');
                setFormData({
                    plate: c.plate || '',
                    make: c.make || '',
                    model: c.model || '',
                    model_year: c.model_year || '',
                    current_odometer: c.current_odometer || '',
                    engine_model: c.engine_model || '',
                    engine_volume: c.engine_volume || '',
                    transmission: c.transmission || '',
                    drive_type: c.drive_type || '',
                    tire_size: c.tire_size || '',
                });
            } catch {
                setError('Failed to load car data.');
            } finally {
                setLoading(false);
            }
        };
        fetchCar();
    }, [id]);

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setSaving(true);
        setError(null);
        try {
            const payload = {
                ...formData,
                model_year: formData.model_year ? parseInt(formData.model_year) : null,
                current_odometer: formData.current_odometer ? parseInt(formData.current_odometer) : 0,
                engine_volume: formData.engine_volume ? parseFloat(formData.engine_volume) : null,
                transmission: formData.transmission || null,
                drive_type: formData.drive_type || null,
                tire_size: formData.tire_size || null,
            };
            await api.patch(`/cars/${id}`, payload);
            navigate(`/cars/${id}`);
        } catch (err) {
            setError(apiErrorMessage(err, 'Failed to save changes.'));
            setSaving(false);
        }
    };

    if (loading) return <div className="text-center p-20 text-blue-600">Loading...</div>;

    return (
        <div className="max-w-2xl mx-auto bg-white p-8 rounded-xl shadow-lg border border-gray-100">
            <div className="flex justify-between items-center mb-6">
                <h1 className="text-2xl font-bold text-gray-800">Edit Car</h1>
                <button
                    type="button"
                    onClick={() => navigate(`/cars/${id}`)}
                    className="text-gray-400 hover:text-gray-600 transition text-2xl leading-none"
                    title="Close"
                >
                    &times;
                </button>
            </div>

            {error && <div className="bg-red-50 text-red-600 p-3 rounded mb-4 text-sm">{error}</div>}

            <form onSubmit={handleSubmit} className="space-y-5">
                <div className="grid grid-cols-2 gap-5">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Plate</label>
                        <input type="text" name="plate" value={formData.plate} onChange={handleChange} required
                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none transition" />
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">VIN <span className="text-gray-400 text-xs">(read-only)</span></label>
                        <input type="text" value={vin} readOnly
                            className="w-full px-4 py-2 border border-gray-200 rounded-lg bg-gray-50 text-gray-500 cursor-not-allowed" />
                    </div>
                </div>

                <div className="grid grid-cols-2 gap-5">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Make</label>
                        <input type="text" name="make" value={formData.make} onChange={handleChange} required
                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none transition" />
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Model</label>
                        <input type="text" name="model" value={formData.model} onChange={handleChange} required
                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none transition" />
                    </div>
                </div>

                <div className="grid grid-cols-2 gap-5">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Year</label>
                        <input type="number" name="model_year" value={formData.model_year} onChange={handleChange}
                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none transition" />
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Odometer (km)</label>
                        <input type="number" name="current_odometer" value={formData.current_odometer} onChange={handleChange}
                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none transition" />
                    </div>
                </div>

                <div className="grid grid-cols-2 gap-5">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Engine Model</label>
                        <input type="text" name="engine_model" value={formData.engine_model} onChange={handleChange}
                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none transition" />
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Engine Volume (L)</label>
                        <input type="number" step="0.1" name="engine_volume" value={formData.engine_volume} onChange={handleChange}
                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none transition" />
                    </div>
                </div>

                <div className="grid grid-cols-2 gap-5">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Transmission</label>
                        <select name="transmission" value={formData.transmission} onChange={handleChange}
                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none transition">
                            <option value="">— Select —</option>
                            {TRANSMISSIONS.map(t => <option key={t} value={t}>{t}</option>)}
                        </select>
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Drive Type</label>
                        <select name="drive_type" value={formData.drive_type} onChange={handleChange}
                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none transition">
                            <option value="">— Select —</option>
                            {DRIVE_TYPES.map(d => <option key={d} value={d}>{d}</option>)}
                        </select>
                    </div>
                </div>

                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Tire Size</label>
                    <input type="text" name="tire_size" value={formData.tire_size} onChange={handleChange} placeholder="e.g. 205/55 R16"
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none transition" />
                </div>

                <div className="flex gap-3 pt-2">
                    <button type="button" onClick={() => navigate(`/cars/${id}`)}
                        className="flex-1 py-3 rounded-lg border border-gray-300 text-gray-700 font-medium hover:bg-gray-50 transition">
                        Cancel
                    </button>
                    <button type="submit" disabled={saving}
                        className="flex-1 bg-slate-900 text-white font-bold py-3 rounded-lg hover:bg-slate-800 transition shadow-lg disabled:opacity-50">
                        {saving ? 'Saving...' : 'Save Changes'}
                    </button>
                </div>
            </form>
        </div>
    );
};

export default CarEditForm;
