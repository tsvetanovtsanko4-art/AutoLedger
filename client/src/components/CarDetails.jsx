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
                <div className="text-right">
                    <p className="text-sm text-gray-500">Current Odometer</p>
                    <p className="text-2xl font-bold text-blue-600">{car.current_odometer.toLocaleString()} km</p>
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
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Refueling History */}
                <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
                    <h2 className="text-xl font-bold mb-4 text-gray-700">Refueling History</h2>
                    {car.refuelings && car.refuelings.length > 0 ? (
                        <ul className="space-y-3">
                            {car.refuelings.map((refuel) => (
                                <li key={refuel.id} className="flex justify-between items-center bg-gray-50 p-3 rounded hover:bg-gray-100 transition">
                                    <div>
                                        <p className="font-semibold text-gray-800">{refuel.date}</p>
                                        <p className="text-xs text-gray-500">{refuel.fuel_type}</p>
                                    </div>
                                    <div className="text-right">
                                        <p className="font-bold text-gray-800">€{refuel.cost_eur.toFixed(2)}</p>
                                        <p className="text-xs text-gray-500">{refuel.odometer} km</p>
                                    </div>
                                </li>
                            ))}
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
        </div>
    );
};

export default CarDetails;
