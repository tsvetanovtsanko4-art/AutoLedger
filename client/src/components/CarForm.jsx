import React, { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import api, { apiErrorMessage } from '../api';

const REQUIRED = { plate: 'Plate Number', vin: 'VIN', make: 'Make', model: 'Model', model_year: 'Year', current_odometer: 'Odometer' };

const Req = () => <span className="text-red-500 ml-1">*</span>;
const FieldError = ({ msg }) => msg ? <p className="text-red-500 text-xs mt-1 font-medium flex items-center gap-1"><span>⚠</span>{msg}</p> : null;

const CarForm = () => {
    const [formData, setFormData] = useState({
        plate: '',
        make: '',
        model: '',
        model_year: new Date().getFullYear(),
        current_odometer: '',
        vin: '',
        engine_model: '',
        engine_volume: '',
        transmission: 'Manual',
        drive_type: 'FWD',
        tire_size: '',
    });
    const [fieldErrors, setFieldErrors] = useState({});
    const [checking, setChecking] = useState({ plate: false, vin: false });
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();

    const plateTimer = useRef(null);
    const vinTimer = useRef(null);

    const setFieldError = (field, msg) =>
        setFieldErrors(prev => ({ ...prev, [field]: msg }));

    const clearFieldError = (field) =>
        setFieldErrors(prev => ({ ...prev, [field]: '' }));

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
        clearFieldError(name);

        // Wait until the user stops typing before asking the server.
        if (name === 'plate') {
            clearTimeout(plateTimer.current);
            if (value.trim().length >= 3) {
                plateTimer.current = setTimeout(() => checkPlate(value.trim()), 600);
            }
        }
        if (name === 'vin') {
            clearTimeout(vinTimer.current);
            if (value.trim().length >= 5) {
                vinTimer.current = setTimeout(() => checkVin(value.trim()), 600);
            }
        }
    };

    const checkPlate = async (plate) => {
        if (!plate) return;
        setChecking(prev => ({ ...prev, plate: true }));
        try {
            const res = await api.get(`/check/plate/${encodeURIComponent(plate.toUpperCase())}`);
            if (!res.data.available) {
                setFieldError('plate', 'This plate number is already registered — please use a different one to continue.');
            }
        } catch {
            // The server re-checks on submit, so a failed lookup is not fatal.
        } finally {
            setChecking(prev => ({ ...prev, plate: false }));
        }
    };

    const checkVin = async (vin) => {
        if (!vin) return;
        setChecking(prev => ({ ...prev, vin: true }));
        try {
            const res = await api.get(`/check/vin/${encodeURIComponent(vin.toUpperCase())}`);
            if (!res.data.available) {
                setFieldError('vin', 'This VIN is already registered — please use a different one to continue.');
            }
        } catch {
            // The server re-checks on submit, so a failed lookup is not fatal.
        } finally {
            setChecking(prev => ({ ...prev, vin: false }));
        }
    };

    const validate = () => {
        const errors = {};
        Object.entries(REQUIRED).forEach(([field, label]) => {
            const val = formData[field];
            if (val === '' || val === null || val === undefined) {
                errors[field] = `${label} is required and cannot be empty`;
            }
        });
        return errors;
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        const errors = validate();
        if (Object.keys(errors).length > 0) {
            setFieldErrors(errors);
            return;
        }
        if (fieldErrors.plate || fieldErrors.vin) return;

        setLoading(true);
        setError(null);
        try {
            const payload = {
                ...formData,
                plate: formData.plate.toUpperCase(),
                vin: formData.vin.toUpperCase(),
                engine_volume: formData.engine_volume ? parseFloat(formData.engine_volume) : null,
                model_year: formData.model_year ? parseInt(formData.model_year) : null,
                current_odometer: parseInt(formData.current_odometer) || 0,
            };
            await api.post('/cars', payload);
            navigate('/home');
        } catch (err) {
            const detail = apiErrorMessage(err, '');
            const conflict = err.response?.status === 409;
            if (conflict && detail.toLowerCase().includes('plate')) {
                setFieldError('plate', 'This plate number is already registered — please use a different one to continue.');
            } else if (conflict && detail.toLowerCase().includes('vin')) {
                setFieldError('vin', 'This VIN is already registered — please use a different one to continue.');
            } else if (err.response?.status === 422) {
                setError(`Validation error: ${detail || 'please check all required fields.'}`);
            } else {
                setError('Failed to add car. Please check your inputs and try again.');
            }
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const inputBase = (hasError, checking = false) =>
        `w-full px-5 py-3 bg-gray-50 border rounded-2xl focus:ring-2 focus:ring-blue-500 focus:bg-white outline-none transition ${hasError ? 'border-red-400 bg-red-50 focus:ring-red-300' : checking ? 'border-blue-300 animate-pulse' : 'border-transparent'
        }`;

    return (
        <div className="max-w-4xl mx-auto bg-white p-8 md:p-12 rounded-3xl shadow-xl border border-gray-100">
            <div className="flex justify-between items-start mb-10">
                <div>
                    <h2 className="text-4xl font-black text-gray-900 mb-2 tracking-tight">Add New Vehicle</h2>
                    <p className="text-gray-500">
                        Provide detailed specifications for better tracking.&nbsp;
                        <span className="text-red-500 font-semibold">*</span> Required
                    </p>
                </div>
                <button type="button" onClick={() => navigate('/home')}
                    className="text-gray-400 hover:text-gray-600 transition text-3xl leading-none mt-1" title="Close">
                    &times;
                </button>
            </div>

            {error && (
                <div className="bg-red-50 text-red-600 p-4 rounded-xl mb-6 text-sm font-medium border border-red-100">
                    {error}
                </div>
            )}

            <form onSubmit={handleSubmit} noValidate>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-10">

                    {/* Identity */}
                    <section className="space-y-5">
                        <h3 className="text-lg font-bold text-blue-600 border-b border-blue-100 pb-2">Identity</h3>

                        {/* Plate */}
                        <div>
                            <label className="block text-xs font-bold text-gray-400 uppercase tracking-widest mb-2">
                                Plate Number<Req />
                                {checking.plate && <span className="ml-2 text-blue-400 font-normal normal-case tracking-normal text-xs">Checking...</span>}
                            </label>
                            <input type="text" name="plate" value={formData.plate} onChange={handleChange}
                                className={`${inputBase(!!fieldErrors.plate, checking.plate)} uppercase font-mono tracking-widest text-lg`}
                                data-testid="input-plate" placeholder="CA 1234 KA" />
                            <FieldError msg={fieldErrors.plate} />
                        </div>

                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <label className="block text-xs font-bold text-gray-400 uppercase tracking-widest mb-2">Make<Req /></label>
                                <input type="text" name="make" value={formData.make} onChange={handleChange}
                                    className={inputBase(!!fieldErrors.make)}
                                    data-testid="input-make" placeholder="Toyota" />
                                <FieldError msg={fieldErrors.make} />
                            </div>
                            <div>
                                <label className="block text-xs font-bold text-gray-400 uppercase tracking-widest mb-2">Model<Req /></label>
                                <input type="text" name="model" value={formData.model} onChange={handleChange}
                                    className={inputBase(!!fieldErrors.model)}
                                    data-testid="input-model" placeholder="Camry" />
                                <FieldError msg={fieldErrors.model} />
                            </div>
                        </div>

                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <label className="block text-xs font-bold text-gray-400 uppercase tracking-widest mb-2">Year<Req /></label>
                                <input type="number" name="model_year" value={formData.model_year} onChange={handleChange}
                                    className={inputBase(!!fieldErrors.model_year)}
                                    min="1960" max={new Date().getFullYear() + 1} />
                                <FieldError msg={fieldErrors.model_year} />
                            </div>
                            <div>
                                <label className="block text-xs font-bold text-gray-400 uppercase tracking-widest mb-2">Odometer (km)<Req /></label>
                                <input type="number" name="current_odometer" value={formData.current_odometer} onChange={handleChange}
                                    className={`${inputBase(!!fieldErrors.current_odometer)} text-right font-bold`}
                                    min="0" placeholder="0" />
                                <FieldError msg={fieldErrors.current_odometer} />
                            </div>
                        </div>
                    </section>

                    {/* Technical Specs */}
                    <section className="space-y-5">
                        <h3 className="text-lg font-bold text-blue-600 border-b border-blue-100 pb-2">Technical Specs</h3>

                        {/* VIN */}
                        <div>
                            <label className="block text-xs font-bold text-gray-400 uppercase tracking-widest mb-2">
                                VIN<Req />
                                {checking.vin && <span className="ml-2 text-blue-400 font-normal normal-case tracking-normal text-xs">Checking...</span>}
                            </label>
                            <input type="text" name="vin" value={formData.vin} onChange={handleChange}
                                className={`${inputBase(!!fieldErrors.vin, checking.vin)} font-mono`}
                                placeholder="17-Digit Vehicle ID" maxLength={17} />
                            <FieldError msg={fieldErrors.vin} />
                        </div>

                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <label className="block text-xs font-bold text-gray-400 uppercase tracking-widest mb-2">Engine Volume</label>
                                <input type="number" step="0.1" name="engine_volume" value={formData.engine_volume} onChange={handleChange}
                                    className={inputBase(false)} placeholder="e.g. 2.0" />
                            </div>
                            <div>
                                <label className="block text-xs font-bold text-gray-400 uppercase tracking-widest mb-2">Engine Code</label>
                                <input type="text" name="engine_model" value={formData.engine_model} onChange={handleChange}
                                    className={inputBase(false)} placeholder="e.g. 1KD-FTV" />
                            </div>
                        </div>

                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <label className="block text-xs font-bold text-gray-400 uppercase tracking-widest mb-2">Transmission</label>
                                <select name="transmission" value={formData.transmission} onChange={handleChange}
                                    className="w-full px-5 py-3 bg-gray-50 border border-transparent rounded-2xl focus:ring-2 focus:ring-blue-500 focus:bg-white outline-none transition font-bold text-sm">
                                    <option value="Manual">Manual</option>
                                    <option value="Automatic">Automatic</option>
                                    <option value="CVT">CVT</option>
                                    <option value="DCT">DCT</option>
                                </select>
                            </div>
                            <div>
                                <label className="block text-xs font-bold text-gray-400 uppercase tracking-widest mb-2">Drive Type</label>
                                <select name="drive_type" value={formData.drive_type} onChange={handleChange}
                                    className="w-full px-5 py-3 bg-gray-50 border border-transparent rounded-2xl focus:ring-2 focus:ring-blue-500 focus:bg-white outline-none transition font-bold text-sm">
                                    <option value="FWD">Front Wheel (FWD)</option>
                                    <option value="RWD">Rear Wheel (RWD)</option>
                                    <option value="AWD">All Wheel (AWD)</option>
                                </select>
                            </div>
                        </div>

                        <div>
                            <label className="block text-xs font-bold text-gray-400 uppercase tracking-widest mb-2">Tire Size</label>
                            <input type="text" name="tire_size" value={formData.tire_size} onChange={handleChange}
                                className={inputBase(false)} placeholder="e.g. 225/45 R17" />
                        </div>
                    </section>
                </div>

                <div className="flex gap-4">
                    <button type="button" onClick={() => navigate('/home')}
                        className="flex-1 py-4 rounded-3xl border border-gray-300 text-gray-600 font-bold hover:bg-gray-50 transition text-lg">
                        Cancel
                    </button>
                    <button type="submit" disabled={loading}
                        className="flex-[2] bg-blue-600 text-white font-black py-4 rounded-3xl hover:bg-blue-700 transition shadow-2xl disabled:opacity-50 text-xl tracking-wide uppercase"
                        data-testid="btn-submit-car">
                        {loading ? 'Adding to Garage...' : 'Register Vehicle'}
                    </button>
                </div>
            </form>
        </div>
    );
};

export default CarForm;
