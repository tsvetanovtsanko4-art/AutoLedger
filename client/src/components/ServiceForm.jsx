import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../api';

const Req = () => <span className="text-red-500 ml-1">*</span>;

const ServiceForm = () => {
    const { id } = useParams();
    const navigate = useNavigate();
    const [formData, setFormData] = useState({
        date: '',
        parts_list: '',
        part_numbers: '',
        next_service_interval: '10000'
    });
    const [error, setError] = useState(null);

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError(null);
        try {
            const carRes = await api.get(`/cars/${id}`);
            const currentOdometer = carRes.data.current_odometer;
            const nextOdometer = currentOdometer + parseInt(formData.next_service_interval);

            const payload = {
                date: formData.date,
                parts_list: formData.parts_list.split(',').map(s => s.trim()).filter(Boolean),
                part_numbers: formData.part_numbers.split(',').map(s => s.trim()).filter(Boolean),
                next_service_odometer: nextOdometer
            };

            await api.post(`/cars/${id}/services`, payload);
            navigate(`/cars/${id}`);
        } catch (err) {
            setError(err.response?.data?.detail || 'Error logging service. Please try again.');
            console.error("Error adding service", err);
        }
    };

    return (
        <div className="max-w-md mx-auto bg-white p-8 rounded-xl shadow-lg border border-gray-100">
            <div className="flex justify-between items-center mb-6">
                <h2 className="text-2xl font-bold text-gray-800">Log Service</h2>
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
                        required data-testid="input-service-date" />
                </div>
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Parts Used <span className="text-gray-400 text-xs">(comma separated)</span></label>
                    <input type="text" name="parts_list" value={formData.parts_list} onChange={handleChange}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none transition"
                        placeholder="Oil, Filter, Pads" data-testid="input-parts" />
                </div>
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Part Numbers <span className="text-gray-400 text-xs">(comma separated)</span></label>
                    <input type="text" name="part_numbers" value={formData.part_numbers} onChange={handleChange}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none transition"
                        placeholder="12345, 67890" data-testid="input-part-numbers" />
                </div>
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Next Service Interval<Req /></label>
                    <select name="next_service_interval" value={formData.next_service_interval} onChange={handleChange}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none transition"
                        data-testid="select-interval">
                        <option value="10000">10,000 km</option>
                        <option value="15000">15,000 km</option>
                        <option value="20000">20,000 km</option>
                        <option value="25000">25,000 km</option>
                    </select>
                </div>
                <div className="flex gap-3 pt-1">
                    <button type="button" onClick={() => navigate(`/cars/${id}`)}
                        className="flex-1 py-3 rounded-lg border border-gray-300 text-gray-600 font-medium hover:bg-gray-50 transition">
                        Cancel
                    </button>
                    <button type="submit"
                        className="flex-[2] bg-blue-600 text-white font-semibold py-3 rounded-lg hover:bg-blue-700 transition shadow-md"
                        data-testid="btn-submit-service">
                        Save Service
                    </button>
                </div>
            </form>
        </div>
    );
};

export default ServiceForm;
