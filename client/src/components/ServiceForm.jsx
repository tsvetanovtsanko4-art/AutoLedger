import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../api';

const ServiceForm = () => {
    const { id } = useParams();
    const navigate = useNavigate();
    const [formData, setFormData] = useState({
        date: '',
        parts_list: '',
        part_numbers: '',
        next_service_interval: '10000'
    });

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            // Fetch current car to get current odometer for calculation
            const carRes = await api.get(`/cars/${id}`);
            const currentOdometer = carRes.data.current_odometer;

            const nextOdometer = currentOdometer + parseInt(formData.next_service_interval);

            const payload = {
                date: formData.date,
                parts_list: formData.parts_list.split(',').map(s => s.trim()),
                part_numbers: formData.part_numbers.split(',').map(s => s.trim()),
                next_service_odometer: nextOdometer
            };

            await api.post(`/cars/${id}/services`, payload);
            navigate(`/cars/${id}`);
        } catch (error) {
            console.error("Error adding service", error);
        }
    };

    return (
        <div className="max-w-md mx-auto bg-white p-8 rounded-xl shadow-lg border border-gray-100">
            <h2 className="text-2xl font-bold mb-6 text-gray-800">Log Service</h2>
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
                        data-testid="input-service-date"
                    />
                </div>
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Parts Used (comma separated)</label>
                    <input
                        type="text"
                        name="parts_list"
                        value={formData.parts_list}
                        onChange={handleChange}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition"
                        placeholder="Oil, Filter, Pads"
                        data-testid="input-parts"
                    />
                </div>
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Part Numbers (comma separated)</label>
                    <input
                        type="text"
                        name="part_numbers"
                        value={formData.part_numbers}
                        onChange={handleChange}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition"
                        placeholder="12345, 67890"
                        data-testid="input-part-numbers"
                    />
                </div>
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Next Service Interval</label>
                    <select
                        name="next_service_interval"
                        value={formData.next_service_interval}
                        onChange={handleChange}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition"
                        data-testid="select-interval"
                    >
                        <option value="10000">10,000 km</option>
                        <option value="15000">15,000 km</option>
                        <option value="20000">20,000 km</option>
                        <option value="25000">25,000 km</option>
                    </select>
                </div>
                <button
                    type="submit"
                    className="w-full bg-blue-600 text-white font-semibold py-3 rounded-lg hover:bg-blue-700 transition shadow-md"
                    data-testid="btn-submit-service"
                >
                    Save Service
                </button>
            </form>
        </div>
    );
};

export default ServiceForm;
