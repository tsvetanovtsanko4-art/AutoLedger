import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../api';

const COUNTRIES = [
    { code: "BG", name: "Bulgaria" },
    { code: "RO", name: "Romania" },
    { code: "GR", name: "Greece" },
    { code: "TR", name: "Turkey" },
    { code: "RS", name: "Serbia" },
    { code: "MK", name: "North Macedonia" },
    { code: "HU", name: "Hungary" },
    { code: "AT", name: "Austria" },
    { code: "DE", name: "Germany" },
    { code: "CZ", name: "Czech Republic" },
    { code: "SK", name: "Slovakia" },
    { code: "SI", name: "Slovenia" },
    { code: "HR", name: "Croatia" },
    { code: "CH", name: "Switzerland" },
    { code: "IT", name: "Italy" },
    { code: "FR", name: "France" },
    { code: "ES", name: "Spain" },
    { code: "PL", name: "Poland" },
    { code: "UA", name: "Ukraine" },
    { code: "MD", name: "Moldova" },
    { code: "AL", name: "Albania" },
    { code: "XK", name: "Kosovo" },
    { code: "ME", name: "Montenegro" },
    { code: "BA", name: "Bosnia and Herzegovina" },
];

const AddVignette = () => {
    const { id } = useParams();
    const navigate = useNavigate();
    const [loading, setLoading] = useState(false);
    const [checking, setChecking] = useState(false);
    const [error, setError] = useState(null);
    const [msg, setMsg] = useState(null);

    const [formData, setFormData] = useState({
        country_code: 'BG',
        date_start: '',
        date_end: '',
        price: '',
        currency: 'EUR',
        status: '',
        vehicle_type: '',
        vehicle_class: ''
    });

    const [plate, setPlate] = useState('');

    // The BG Toll lookup needs the car's plate.
    React.useEffect(() => {
        const fetchCar = async () => {
            try {
                const res = await api.get(`/cars/${id}`);
                setPlate(res.data.plate);
            } catch (err) {
                console.error("Failed to load car", err);
            }
        };
        fetchCar();
    }, [id]);

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData({ ...formData, [name]: value });
    };

    const handleCheckBGToll = async () => {
        if (!plate) return;
        setChecking(true);
        setError(null);
        setMsg(null);

        setFormData(prev => ({
            ...prev,
            date_start: '',
            date_end: '',
            price: '',
            currency: 'BGN',
            status: '',
            vehicle_type: '',
            vehicle_class: ''
        }));

        try {
            const res = await api.get(`/proxy/bgtoll/${plate}`);
            const data = res.data;

            if (data.ok && data.vignette && data.vignette.statusBoolean) {
                const v = data.vignette;
                setFormData(prev => ({
                    ...prev,
                    country_code: v.country || 'BG',
                    date_start: v.validityDateFrom ? v.validityDateFrom.split('T')[0] : '',
                    date_end: v.validityDateTo ? v.validityDateTo.split('T')[0] : '',
                    price: v.price,
                    currency: v.currency,
                    status: v.status === 'Активна' ? 'Active' : (v.status || ''),
                    vehicle_type: v.vehicleType,
                    vehicle_class: v.vehicleClassCode
                }));
                setMsg("Vignette found and loaded!");
            } else {
                setMsg("The car don't have a valid vignette");
            }
        } catch (err) {
            console.error(err);
            setError("Failed to check BG Toll.");
        } finally {
            setChecking(false);
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        try {
            await api.put(`/cars/${id}/vignettes`, {
                ...formData,
                price: formData.price ? parseFloat(formData.price) : null
            });
            navigate(`/cars/${id}`);
        } catch (err) {
            setError("Failed to save vignette.");
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="max-w-2xl mx-auto bg-white p-8 rounded-xl shadow-lg border border-gray-100">
            <div className="flex justify-between items-center mb-6">
                <h1 className="text-2xl font-bold text-gray-800">Add Vignette</h1>
                <button
                    type="button"
                    onClick={() => navigate(`/cars/${id}`)}
                    className="text-gray-400 hover:text-gray-600 transition text-2xl leading-none"
                    title="Close"
                >
                    &times;
                </button>
            </div>

            {error && <div className="bg-red-50 text-red-600 p-3 rounded mb-4">{error}</div>}
            {msg && <div className={`p-3 rounded mb-4 ${msg.includes("don't") ? 'bg-yellow-50 text-yellow-700' : 'bg-green-50 text-green-700'}`}>{msg}</div>}

            <div className="mb-8 p-4 bg-blue-50 rounded-lg border border-blue-100">
                <div className="flex justify-between items-center">
                    <div>
                        <p className="text-sm font-bold text-blue-800 uppercase tracking-wide">BG Toll Check</p>
                        <p className="text-xs text-blue-600">Check for valid vignette by plate: <strong>{plate}</strong></p>
                    </div>
                    <button
                        type="button"
                        onClick={handleCheckBGToll}
                        disabled={checking || !plate}
                        className="bg-blue-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-blue-700 transition disabled:opacity-50"
                    >
                        {checking ? 'Checking...' : 'Check BG Toll'}
                    </button>
                </div>
            </div>

            <form onSubmit={handleSubmit} className="space-y-6">
                <div className="grid grid-cols-2 gap-6">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Country</label>
                        <select
                            name="country_code"
                            value={formData.country_code}
                            onChange={handleChange}
                            className="w-full border-gray-300 rounded-lg shadow-sm focus:ring-blue-500 focus:border-blue-500 p-2 border"
                        >
                            {COUNTRIES.map(c => (
                                <option key={c.code} value={c.code}>{c.name} ({c.code})</option>
                            ))}
                        </select>
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Currency</label>
                        <select
                            name="currency"
                            value={formData.currency}
                            onChange={handleChange}
                            className="w-full border-gray-300 rounded-lg shadow-sm focus:ring-blue-500 focus:border-blue-500 p-2 border"
                        >
                            <option value="EUR">EUR</option>
                            <option value="BGN">BGN</option>
                            <option value="USD">USD</option>
                            <option value="RON">RON</option>
                            <option value="TRY">TRY</option>
                        </select>
                    </div>
                </div>

                <div className="grid grid-cols-2 gap-6">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Start Date</label>
                        <input
                            type="date"
                            name="date_start"
                            value={formData.date_start}
                            onChange={handleChange}
                            required
                            className="w-full border-gray-300 rounded-lg shadow-sm focus:ring-blue-500 focus:border-blue-500 p-2 border"
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">End Date</label>
                        <input
                            type="date"
                            name="date_end"
                            value={formData.date_end}
                            onChange={handleChange}
                            required
                            className="w-full border-gray-300 rounded-lg shadow-sm focus:ring-blue-500 focus:border-blue-500 p-2 border"
                        />
                    </div>
                </div>

                <div className="grid grid-cols-2 gap-6">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Price</label>
                        <input
                            type="number"
                            step="0.01"
                            name="price"
                            value={formData.price}
                            onChange={handleChange}
                            className="w-full border-gray-300 rounded-lg shadow-sm focus:ring-blue-500 focus:border-blue-500 p-2 border"
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Status (Optional)</label>
                        <input
                            type="text"
                            name="status"
                            value={formData.status}
                            onChange={handleChange}
                            className="w-full border-gray-300 rounded-lg shadow-sm focus:ring-blue-500 focus:border-blue-500 p-2 border bg-gray-50"
                            placeholder="Auto-filled or Manual"
                        />
                    </div>
                </div>

                <div className="grid grid-cols-2 gap-6">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Vehicle Type</label>
                        <input
                            type="text"
                            name="vehicle_type"
                            value={formData.vehicle_type}
                            onChange={handleChange}
                            className="w-full border-gray-300 rounded-lg shadow-sm focus:ring-blue-500 focus:border-blue-500 p-2 border bg-gray-50"
                            readOnly
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Class</label>
                        <input
                            type="text"
                            name="vehicle_class"
                            value={formData.vehicle_class}
                            onChange={handleChange}
                            className="w-full border-gray-300 rounded-lg shadow-sm focus:ring-blue-500 focus:border-blue-500 p-2 border bg-gray-50"
                            readOnly
                        />
                    </div>
                </div>


                <button
                    type="submit"
                    disabled={loading}
                    className="w-full bg-slate-900 text-white font-bold py-3 rounded-xl hover:bg-slate-800 transition shadow-lg"
                >
                    {loading ? 'Saving...' : 'Save Vignette'}
                </button>
            </form>
        </div>
    );
};

export default AddVignette;
