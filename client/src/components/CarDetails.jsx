import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import api from '../api';

const CarDetails = () => {
    const { id } = useParams();
    const [car, setCar] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchCar = async () => {
            try {
                const response = await api.get(`/cars/${id}`);
                setCar(response.data);
            } catch (error) {
                console.error("Error fetching car details:", error);
            } finally {
                setLoading(false);
            }
        };
        fetchCar();
    }, [id]);

    if (loading) return <div className="text-center p-10">Loading...</div>;
    if (!car) return <div className="text-center p-10">Car not found</div>;

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center bg-white p-6 rounded-xl shadow-sm border border-gray-200">
                <div>
                    <h1 className="text-3xl font-bold text-gray-800">{car.make} {car.model}</h1>
                    <p className="text-gray-500 text-lg uppercase tracking-wide">{car.plate}</p>
                </div>
                <div className="flex items-center gap-4">
                    <div className="text-right">
                        <p className="text-sm text-gray-500">Current Odometer</p>
                        <p className="text-2xl font-bold text-blue-600">{car.current_odometer.toLocaleString()} km</p>
                    </div>
                    <Link
                        to={`/cars/${id}/edit`}
                        className="bg-slate-100 hover:bg-slate-200 text-slate-700 font-medium px-4 py-2 rounded-lg transition text-sm border border-slate-200"
                    >
                        ✏️ Edit Car
                    </Link>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <Link to={`/cars/${id}/add-refueling`} className="bg-emerald-50 text-emerald-700 p-4 rounded-lg text-center hover:bg-emerald-100 transition border border-emerald-100 font-medium">
                    + Log Fuel
                </Link>
                <Link to={`/cars/${id}/add-service`} className="bg-amber-50 text-amber-700 p-4 rounded-lg text-center hover:bg-amber-100 transition border border-amber-100 font-medium">
                    + Log Service
                </Link>
                <Link to={`/cars/${id}/add-insurance`} className="bg-purple-50 text-purple-700 p-4 rounded-lg text-center hover:bg-purple-100 transition border border-purple-100 font-medium">
                    + Add Insurance
                </Link>
                <Link to={`/cars/${id}/add-vignette`} className="bg-blue-50 text-blue-700 p-4 rounded-lg text-center hover:bg-blue-100 transition border border-blue-100 font-medium">
                    + Add Vignette
                </Link>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Refueling History */}
                <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
                    <h2 className="text-xl font-bold mb-4 text-gray-700">Refueling History</h2>
                    {car.refuelings && car.refuelings.length > 0 ? (
                        <ul className="space-y-3">
                            {[...car.refuelings].sort((a, b) => a.odometer - b.odometer).map((refuel, idx, arr) => {
                                const prev = idx > 0 ? arr[idx - 1] : null;
                                const kmDiff = prev ? refuel.odometer - prev.odometer : null;
                                const consumption = (prev && refuel.quantity_liters && kmDiff > 0)
                                    ? ((refuel.quantity_liters / kmDiff) * 100).toFixed(1)
                                    : null;
                                return (
                                    <li key={refuel.id} className="flex justify-between items-center bg-gray-50 p-3 rounded hover:bg-gray-100 transition">
                                        <div>
                                            <p className="font-semibold text-gray-800">{refuel.date}</p>
                                            <p className="text-xs text-gray-500">{refuel.fuel_type}{refuel.quantity_liters ? ` · ${refuel.quantity_liters}L` : ''}</p>
                                        </div>
                                        <div className="text-right">
                                            <p className="font-bold text-gray-800">€{refuel.cost_eur.toFixed(2)}</p>
                                            <p className="text-xs text-gray-500">{refuel.odometer} km{consumption ? ` · ${consumption} L/100km` : ''}</p>
                                        </div>
                                    </li>
                                );
                            })}
                        </ul>
                    ) : (
                        <p className="text-gray-400 italic">No refueling records.</p>
                    )}
                </div>

                {/* Service History */}
                <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
                    <h2 className="text-xl font-bold mb-4 text-gray-700">Service History</h2>
                    {car.services && car.services.length > 0 ? (
                        <ul className="space-y-4">
                            {car.services.map((service) => (
                                <li key={service.id} className="bg-gray-50 p-4 rounded border border-gray-100">
                                    <div className="flex justify-between mb-2">
                                        <span className="font-semibold text-gray-800">{service.date}</span>
                                        {service.next_service_odometer && (
                                            <span className="text-xs text-amber-600 font-medium bg-amber-50 px-2 py-1 rounded">Next: {service.next_service_odometer}km</span>
                                        )}
                                    </div>
                                    <div className="text-sm text-gray-600">
                                        <p><strong>Parts:</strong> {service.parts_list ? service.parts_list.join(', ') : 'None'}</p>
                                    </div>
                                </li>
                            ))}
                        </ul>
                    ) : (
                        <p className="text-gray-400 italic">No service records.</p>
                    )}
                </div>
            </div>

            {/* Vignette History */}
            <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
                <h2 className="text-xl font-bold mb-4 text-gray-700">Vignettes</h2>
                {car.vignettes && car.vignettes.length > 0 ? (
                    <div className="overflow-x-auto">
                        <table className="min-w-full text-sm text-left text-gray-500">
                            <thead className="text-xs text-gray-700 uppercase bg-gray-50">
                                <tr>
                                    <th className="px-4 py-3">Country</th>
                                    <th className="px-4 py-3">Valid From</th>
                                    <th className="px-4 py-3">Valid To</th>
                                    <th className="px-4 py-3">Price</th>
                                    <th className="px-4 py-3">Status</th>
                                </tr>
                            </thead>
                            <tbody>
                                {car.vignettes.map((v) => (
                                    <tr key={v.id} className="bg-white border-b hover:bg-gray-50">
                                        <td className="px-4 py-3 font-medium text-gray-900">{v.country_code}</td>
                                        <td className="px-4 py-3">{v.date_start}</td>
                                        <td className="px-4 py-3">{v.date_end}</td>
                                        <td className="px-4 py-3">{v.price ? `${v.price} ${v.currency}` : '-'}</td>
                                        <td className="px-4 py-3">
                                            <span className={`px-2 py-1 rounded text-xs font-medium ${v.status === 'Active' || (!v.status && new Date(v.date_end) >= new Date()) ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}`}>
                                                {v.status || (new Date(v.date_end) >= new Date() ? 'Active' : 'Expired')}
                                            </span>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                ) : (
                    <p className="text-gray-400 italic">No vignette records.</p>
                )}
            </div>
        </div>
    );
};

export default CarDetails;
