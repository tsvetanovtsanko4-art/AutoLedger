import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../api';

const Req = () => <span className="text-red-500 ml-1">*</span>;

const RefuelingForm = () => {
    const { id } = useParams();
    const navigate = useNavigate();
    const [formData, setFormData] = useState({
        date: '',
        fuel_type: 'Petrol',
        cost_eur: '',
        quantity_liters: '',
        odometer: ''
    });
    const [error, setError] = useState(null);

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError(null);
        try {
            await api.post(`/cars/${id}/refuelings`, {
                ...formData,
                quantity_liters: formData.quantity_liters ? parseFloat(formData.quantity_liters) : null,
            });
            navigate(`/cars/${id}`);
        } catch (err) {
            setError(err.response?.data?.detail || 'Error adding refueling. Please try again.');
        }
    };

    return (
        <div className="max-w-md mx-auto bg-white p-8 rounded-xl shadow-lg border border-gray-100">
            <div className="flex justify-between items-center mb-6">
                <h2 className="text-2xl font-bold text-gray-800">Log Refueling</h2>
                <button type="button" onClick={() => navigate(`/cars/${id}`)}
                    className="text-gray-400 hover:text-gray-600 transition text-2xl leading-none" title="Close">
                    &times;
                </button>
            </div>

            {error && <div className="bg-red-50 text-red-600 p-3 rounded-lg mb-4 text-sm font-medium">{error}</div>}

            <form onSubmit={handleSubmit} className="space-y-5">
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Date<Req /></label>
                    <input type="date" name="date" value={formData.date} onChange={handleChange}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none transition"
                        required data-testid="input-fuel-date" />
                </div>
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Fuel Type<Req /></label>
                    <select name="fuel_type" value={formData.fuel_type} onChange={handleChange}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none transition"
                        data-testid="select-fuel-type">
                        <option value="Petrol">Petrol</option>
                        <option value="LPG">LPG</option>
                        <option value="CNG">CNG</option>
                        <option value="Diesel">Diesel</option>
                        <option value="Electricity">Electricity</option>
                    </select>
                </div>
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Cost (€)<Req /></label>
                    <input type="number" step="0.01" name="cost_eur" value={formData.cost_eur} onChange={handleChange}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none transition"
                        required data-testid="input-cost" />
                </div>
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Quantity (L) <span className="text-gray-400 text-xs">(optional)</span></label>
                    <input type="number" step="0.01" name="quantity_liters" value={formData.quantity_liters} onChange={handleChange}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none transition"
                        placeholder="Optional" data-testid="input-quantity" />
                </div>
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Odometer (km)<Req /></label>
                    <input type="number" name="odometer" value={formData.odometer} onChange={handleChange}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none transition"
                        required data-testid="input-odometer" />
                </div>
                <div className="flex gap-3 pt-1">
                    <button type="button" onClick={() => navigate(`/cars/${id}`)}
                        className="flex-1 py-3 rounded-lg border border-gray-300 text-gray-600 font-medium hover:bg-gray-50 transition">
                        Cancel
                    </button>
                    <button type="submit"
                        className="flex-[2] bg-blue-600 text-white font-semibold py-3 rounded-lg hover:bg-blue-700 transition shadow-md"
                        data-testid="btn-submit-refuel">
                        Save Refueling
                    </button>
                </div>
            </form>
        </div>
    );
};

export default RefuelingForm;
