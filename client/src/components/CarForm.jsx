import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api';

const CarForm = () => {
    const [formData, setFormData] = useState({
        plate: '',
        make: '',
        model: '',
        model_year: new Date().getFullYear(),
        current_odometer: 0,
        vin: '',
        engine_model: '',
        engine_volume: '',
        transmission: 'MANUAL',
        drive_type: 'FWD',
        tire_size: '',
    });
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData({ ...formData, [name]: value });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        try {
            const payload = {
                ...formData,
                engine_volume: formData.engine_volume ? parseFloat(formData.engine_volume) : null,
                model_year: formData.model_year ? parseInt(formData.model_year) : null,
                current_odometer: parseInt(formData.current_odometer)
            };
            await api.post('/cars', payload);
            navigate('/home');
        } catch (err) {
            setError("Failed to add car. Please check inputs.");
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="max-w-4xl mx-auto bg-white p-8 md:p-12 rounded-3xl shadow-xl border border-gray-100">
            <div className="text-center mb-10">
                <h2 className="text-4xl font-black text-gray-900 mb-2 tracking-tight">Add New Vehicle</h2>
                <p className="text-gray-500">Provide detailed specifications for better tracking</p>
            </div>

            {error && <div className="bg-red-50 text-red-600 p-4 rounded-xl mb-6 text-sm font-medium border border-red-100 italic">{error}</div>}

            <form onSubmit={handleSubmit}>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-10">
                    {/* Basic Info */}
                    <section className="space-y-5">
                        <h3 className="text-lg font-bold text-blue-600 border-b border-blue-100 pb-2">Identity</h3>
                        <div>
                            <label className="block text-xs font-bold text-gray-400 uppercase tracking-widest mb-2">Plate Number</label>
                            <input type="text" name="plate" value={formData.plate} onChange={handleChange} className="w-full px-5 py-3 bg-gray-50 border-0 rounded-2xl focus:ring-2 focus:ring-blue-500 focus:bg-white outline-none transition uppercase font-mono tracking-widest text-lg" required data-testid="input-plate" placeholder="CA 1234 KA" />
                        </div>
                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <label className="block text-xs font-bold text-gray-400 uppercase tracking-widest mb-2">Make</label>
                                <input type="text" name="make" value={formData.make} onChange={handleChange} className="w-full px-5 py-3 bg-gray-50 border-0 rounded-2xl focus:ring-2 focus:ring-blue-500 focus:bg-white outline-none transition" required data-testid="input-make" placeholder="Toyota" />
                            </div>
                            <div>
                                <label className="block text-xs font-bold text-gray-400 uppercase tracking-widest mb-2">Model</label>
                                <input type="text" name="model" value={formData.model} onChange={handleChange} className="w-full px-5 py-3 bg-gray-50 border-0 rounded-2xl focus:ring-2 focus:ring-blue-500 focus:bg-white outline-none transition" required data-testid="input-model" placeholder="Camry" />
                            </div>
                        </div>
                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <label className="block text-xs font-bold text-gray-400 uppercase tracking-widest mb-2">Year</label>
                                <input type="number" name="model_year" value={formData.model_year} onChange={handleChange} className="w-full px-5 py-3 bg-gray-50 border-0 rounded-2xl focus:ring-2 focus:ring-blue-500 focus:bg-white outline-none transition" />
                            </div>
                            <div>
                                <label className="block text-xs font-bold text-gray-400 uppercase tracking-widest mb-2">Odometer (km)</label>
                                <input type="number" name="current_odometer" value={formData.current_odometer} onChange={handleChange} className="w-full px-5 py-3 bg-gray-50 border-0 rounded-2xl focus:ring-2 focus:ring-blue-500 focus:bg-white outline-none transition text-right font-bold" />
                            </div>
                        </div>
                    </section>

                    {/* Technical Info */}
                    <section className="space-y-5">
                        <h3 className="text-lg font-bold text-blue-600 border-b border-blue-100 pb-2">Technical Specs</h3>
                        <div>
                            <label className="block text-xs font-bold text-gray-400 uppercase tracking-widest mb-2">VIN</label>
                            <input type="text" name="vin" value={formData.vin} onChange={handleChange} className="w-full px-5 py-3 bg-gray-50 border-0 rounded-2xl focus:ring-2 focus:ring-blue-500 focus:bg-white outline-none transition font-mono" placeholder="17-Digit Vehicle ID" />
                        </div>
                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <label className="block text-xs font-bold text-gray-400 uppercase tracking-widest mb-2">Engine Volume</label>
                                <input type="number" step="0.1" name="engine_volume" value={formData.engine_volume} onChange={handleChange} className="w-full px-5 py-3 bg-gray-50 border-0 rounded-2xl focus:ring-2 focus:ring-blue-500 focus:bg-white outline-none transition" placeholder="e.g. 2.0" />
                            </div>
                            <div>
                                <label className="block text-xs font-bold text-gray-400 uppercase tracking-widest mb-2">Engine Code</label>
                                <input type="text" name="engine_model" value={formData.engine_model} onChange={handleChange} className="w-full px-5 py-3 bg-gray-50 border-0 rounded-2xl focus:ring-2 focus:ring-blue-500 focus:bg-white outline-none transition" placeholder="e.g. 1KD-FTV" />
                            </div>
                        </div>
                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <label className="block text-xs font-bold text-gray-400 uppercase tracking-widest mb-2">Transmission</label>
                                <select name="transmission" value={formData.transmission} onChange={handleChange} className="w-full px-5 py-3 bg-gray-50 border-0 rounded-2xl focus:ring-2 focus:ring-blue-500 focus:bg-white outline-none transition font-bold text-sm">
                                    <option value="MANUAL">Manual</option>
                                    <option value="AUTOMATIC">Automatic</option>
                                    <option value="CVT">CVT</option>
                                    <option value="DCT">DCT</option>
                                </select>
                            </div>
                            <div>
                                <label className="block text-xs font-bold text-gray-400 uppercase tracking-widest mb-2">Drive Type</label>
                                <select name="drive_type" value={formData.drive_type} onChange={handleChange} className="w-full px-5 py-3 bg-gray-50 border-0 rounded-2xl focus:ring-2 focus:ring-blue-500 focus:bg-white outline-none transition font-bold text-sm">
                                    <option value="FWD">Front Wheel (FWD)</option>
                                    <option value="RWD">Rear Wheel (RWD)</option>
                                    <option value="AWD">All Wheel (AWD)</option>
                                </select>
                            </div>
                        </div>
                        <div>
                            <label className="block text-xs font-bold text-gray-400 uppercase tracking-widest mb-2">Tire Size</label>
                            <input type="text" name="tire_size" value={formData.tire_size} onChange={handleChange} className="w-full px-5 py-3 bg-gray-50 border-0 rounded-2xl focus:ring-2 focus:ring-blue-500 focus:bg-white outline-none transition" placeholder="e.g. 225/45 R17" />
                        </div>
                    </section>
                </div>

                <button
                    type="submit"
                    disabled={loading}
                    className="w-full bg-blue-600 text-white font-black py-4 rounded-3xl hover:bg-blue-700 transition shadow-2xl disabled:opacity-50 text-xl tracking-wide uppercase"
                    data-testid="btn-submit-car"
                >
                    {loading ? 'Adding to Garage...' : 'Register Vehicle'}
                </button>
            </form>
        </div>
    );
};

export default CarForm;
