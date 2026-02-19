import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../api';

const Req = () => <span className="text-red-500 ml-1">*</span>;

const InsuranceForm = () => {
    const { id } = useParams();
    const navigate = useNavigate();
    const [formData, setFormData] = useState({
        type: 'Civil Liability',
        renewed_date: '',
        expiry_date: ''
    });
    const [error, setError] = useState(null);

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError(null);
        try {
            await api.post(`/cars/${id}/insurances`, formData);
            navigate(`/cars/${id}`);
        } catch (err) {
            setError(err.response?.data?.detail || 'Error adding insurance. Please try again.');
            console.error("Error adding insurance", err);
        }
    };

    return (
        <div className="max-w-md mx-auto bg-white p-8 rounded-xl shadow-lg border border-gray-100">
            <div className="flex justify-between items-center mb-6">
                <h2 className="text-2xl font-bold text-gray-800">Add Insurance</h2>
                <button type="button" onClick={() => navigate(`/cars/${id}`)}
                    className="text-gray-400 hover:text-gray-600 transition text-2xl leading-none" title="Close">
                    &times;
                </button>
            </div>

            {error && <div className="bg-red-50 text-red-600 p-3 rounded-lg mb-4 text-sm font-medium">{error}</div>}

            <form onSubmit={handleSubmit} className="space-y-5">
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Type<Req /></label>
                    <select name="type" value={formData.type} onChange={handleChange}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none transition"
                        data-testid="select-insurance-type">
                        <option value="Civil Liability">Civil Liability</option>
                        <option value="Casco">Casco</option>
                    </select>
                </div>
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Renewed Date<Req /></label>
                    <input type="date" name="renewed_date" value={formData.renewed_date} onChange={handleChange}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none transition"
                        required data-testid="input-renewed-date" />
                </div>
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Expiry Date<Req /></label>
                    <input type="date" name="expiry_date" value={formData.expiry_date} onChange={handleChange}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none transition"
                        required data-testid="input-expiry-date" />
                </div>
                <div className="flex gap-3 pt-1">
                    <button type="button" onClick={() => navigate(`/cars/${id}`)}
                        className="flex-1 py-3 rounded-lg border border-gray-300 text-gray-600 font-medium hover:bg-gray-50 transition">
                        Cancel
                    </button>
                    <button type="submit"
                        className="flex-[2] bg-blue-600 text-white font-semibold py-3 rounded-lg hover:bg-blue-700 transition shadow-md"
                        data-testid="btn-submit-insurance">
                        Save Insurance
                    </button>
                </div>
            </form>
        </div>
    );
};

export default InsuranceForm;
