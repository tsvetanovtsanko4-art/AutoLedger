import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../api';

const RefuelingForm = () => {
    const { id } = useParams();
    const navigate = useNavigate();
    const [formData, setFormData] = useState({
        date: '',
        fuel_type: 'Petrol',
        cost_eur: '',
        odometer: ''
    });
    const [error, setError] = useState(null);

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            await api.post(`/cars/${id}/refuelings`, formData);
            navigate(`/cars/${id}`);
        } catch (err) {
            setError(err.response?.data?.detail || "Error adding refueling");
        }
    };

    return (
        <div className="max-w-md mx-auto bg-white p-8 rounded-xl shadow-lg border border-gray-100">
            <h2 className="text-2xl font-bold mb-6 text-gray-800">Log Refueling</h2>
            {error && <div className="bg-red-50 text-red-600 p-3 rounded mb-4 text-sm">{error}</div>}
            <form onSubmit={handleSubmit} className="space-y-5">
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Date</label>
                    <input
                        type="date"
                        name="date"
                        value={formData.date}
                        onChange={handleChange}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition"
                        required
                        data-testid="input-fuel-date"
                    />
                </div>
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Fuel Type</label>
                    <select
                        name="fuel_type"
                        value={formData.fuel_type}
                        onChange={handleChange}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition"
                        data-testid="select-fuel-type"
                    >
                        <option value="Petrol">Petrol</option>
                        <option value="LPG">LPG</option>
                        <option value="CNG">CNG</option>
                        <option value="Diesel">Diesel</option>
                        <option value="Electricity">Electricity</option>
                    </select>
                </div>
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Cost (€)</label>
                    <input
                        type="number"
                        step="0.01"
                        name="cost_eur"
                        value={formData.cost_eur}
                        onChange={handleChange}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition"
                        required
                        data-testid="input-cost"
                    />
                </div>
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Odometer (km)</label>
                    <input
                        type="number"
                        name="odometer"
                        value={formData.odometer}
                        onChange={handleChange}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition"
                        required
                        data-testid="input-odometer"
                    />
                </div>
                <button
                    type="submit"
                    className="w-full bg-blue-600 text-white font-semibold py-3 rounded-lg hover:bg-blue-700 transition shadow-md"
                    data-testid="btn-submit-refuel"
                >
                    Save Refueling
                </button>
            </form>
        </div>
    );
};

export default RefuelingForm;
