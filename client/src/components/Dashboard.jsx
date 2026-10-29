import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import api from '../api';
import { averageConsumption } from '../consumption';

const Dashboard = () => {
    const [cars, setCars] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        api.get('/me/cars')
            .then(res => setCars(res.data))
            .catch(error => console.error("Error fetching cars:", error))
            .finally(() => setLoading(false));
    }, []);

    const toggleFavorite = async (e, carId) => {
        e.preventDefault();
        e.stopPropagation();
        try {
            const { data: updated } = await api.patch(`/cars/${carId}/favorite`);
            // Same order as the server: favourites first, then oldest first.
            setCars(prev => prev
                .map(c => (c.id === updated.id ? updated : c))
                .sort((a, b) => b.is_favorite - a.is_favorite || a.id - b.id));
        } catch (error) {
            console.error("Error toggling favorite:", error);
        }
    };

    if (loading) {
        return <div className="text-center p-10 py-40" data-testid="loading-dashboard">
            <div className="animate-spin text-4xl mb-4">⚙️</div>
            <p className="text-gray-500">Opening your garage doors...</p>
        </div>;
    }

    return (
        <div>
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 gap-4">
                <div>
                    <h1 className="text-4xl font-black text-gray-900 tracking-tight">Your Garage</h1>
                    <p className="text-gray-500">Manage {cars.length} vehicle(s)</p>
                </div>
                <Link to="/add-car" className="bg-blue-600 text-white px-6 py-3 rounded-xl hover:bg-blue-700 transition shadow-lg font-bold flex items-center" data-testid="btn-add-car">
                    <span className="mr-2 text-xl">+</span> Add Vehicle
                </Link>
            </div>

            {cars.length === 0 ? (
                <div className="text-center py-20 bg-white rounded-3xl shadow-sm border border-dashed border-gray-300">
                    <div className="text-6xl mb-6 opacity-30">🚙💨</div>
                    <p className="text-gray-500 mb-8 text-xl font-medium">Your garage is empty. Time to add your first car!</p>
                    <Link to="/add-car" className="bg-blue-100 text-blue-700 px-8 py-4 rounded-2xl hover:bg-blue-200 transition font-bold">
                        Add Your Car
                    </Link>
                </div>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                    {cars.map((car) => {
                        const avgFuel = averageConsumption(car.refuelings);
                        return (
                            <Link key={car.id} to={`/cars/${car.id}`} className="block group relative" data-testid={`car-card-${car.id}`}>
                                <div className={`h-full bg-white rounded-3xl shadow-sm transition-all duration-300 border-2 overflow-hidden ${car.is_favorite ? 'border-blue-500 ring-4 ring-blue-500/10' : 'border-gray-100 hover:border-blue-200 hover:shadow-xl'}`}>
                                    {car.is_favorite && (
                                        <div className="absolute top-4 left-4 bg-blue-500 text-white px-3 py-1 rounded-full text-xs font-bold shadow-md z-10 flex items-center">
                                            <span className="mr-1">⭐</span> FAVORITE
                                        </div>
                                    )}

                                    <button
                                        onClick={(e) => toggleFavorite(e, car.id)}
                                        className={`absolute top-4 right-4 p-2 rounded-full shadow-sm z-10 transition ${car.is_favorite ? 'bg-blue-50 text-blue-500' : 'bg-gray-50 text-gray-300 hover:text-blue-500'}`}
                                        title={car.is_favorite ? "Remove from favorites" : "Add to favorites"}
                                    >
                                        <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                                            <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                                        </svg>
                                    </button>

                                    <div className="p-8">
                                        <div className="mb-4">
                                            <div className="text-gray-400 text-xs font-bold tracking-widest uppercase mb-1">{car.make}</div>
                                            <h2 className="text-2xl font-black text-gray-800 tracking-tight group-hover:text-blue-600 transition-colors uppercase">{car.model}</h2>
                                        </div>

                                        <div className="flex items-center text-sm font-medium text-gray-600 mb-6 py-2 px-3 bg-gray-50 rounded-xl w-fit">
                                            <span className="opacity-50 mr-2">📍</span>
                                            <span className="tracking-widest uppercase">{car.plate}</span>
                                        </div>

                                        <div className="flex justify-between items-end">
                                            <div>
                                                <p className="text-gray-400 text-xs font-bold uppercase tracking-wider mb-1">Mileage</p>
                                                <p className="text-xl font-bold text-gray-800">{car.current_odometer.toLocaleString()} <span className="text-gray-400 font-medium text-sm">km</span></p>
                                            </div>
                                            <div className="text-right">
                                                {avgFuel !== null ? (
                                                    <>
                                                        <p className="text-gray-400 text-xs font-bold uppercase tracking-wider mb-1">Avg Fuel</p>
                                                        <p className="text-lg font-bold text-emerald-600">{avgFuel} <span className="text-gray-400 font-medium text-xs">L/100km</span></p>
                                                    </>
                                                ) : (
                                                    <p className="text-xs text-gray-300 italic">No fuel data</p>
                                                )}
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </Link>
                        );
                    })}
                </div>
            )}
        </div>
    );
};

export default Dashboard;
