import React, { useEffect, useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, LineChart, Line, PieChart, Pie, Cell } from 'recharts';
import api from '../api';
import { Link } from 'react-router-dom';

const PublicDashboard = () => {
    const [stats, setStats] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        api.get('/public/stats')
            .then(res => setStats(res.data))
            .catch(err => console.error("Error fetching public stats:", err))
            .finally(() => setLoading(false));
    }, []);

    if (loading) return <div className="text-center p-20 text-gray-500">Loading aggregate stats...</div>;
    if (!stats) return <div className="text-center p-20 text-gray-500">Stats unavailable.</div>;

    const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8', '#82ca9d'];

    return (
        <div className="space-y-12">
            <section className="text-center py-16 bg-gradient-to-r from-blue-600 to-blue-800 text-white rounded-3xl shadow-xl px-4">
                <h1 className="text-5xl font-extrabold mb-4">Track Your Fleet. Optimize Your Spend.</h1>
                <p className="text-xl mb-8 opacity-90 max-w-2xl mx-auto">The ultimate companion for car owners. Managing fuel, service, and insurance has never been easier.</p>
                <div className="flex justify-center space-x-4">
                    <Link to="/register" className="bg-white text-blue-700 px-8 py-4 rounded-full font-bold text-lg hover:bg-gray-100 transition shadow-lg">Get Started Free</Link>
                    <Link to="/login" className="bg-blue-500 text-white border border-blue-400 px-8 py-4 rounded-full font-bold text-lg hover:bg-blue-400 transition">Sign In</Link>
                </div>
            </section>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {/* Cars by Make Chart */}
                <div className="bg-white p-8 rounded-2xl shadow-sm border border-gray-100 min-w-0">
                    <h2 className="text-2xl font-bold mb-6 text-gray-800">Popularity by Manufacturer</h2>
                    <div className="h-[400px] w-full" style={{ minHeight: '400px' }}>
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={stats.cars_by_make}>
                                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                                <XAxis dataKey="make" />
                                <YAxis />
                                <Tooltip />
                                <Bar dataKey="count" fill="#3B82F6" radius={[4, 4, 0, 0]} />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                {/* Spending by Year */}
                <div className="bg-white p-8 rounded-2xl shadow-sm border border-gray-100 min-w-0">
                    <h2 className="text-2xl font-bold mb-6 text-gray-800">Global Spending Trends</h2>
                    <div className="h-[400px] w-full" style={{ minHeight: '400px' }}>
                        <ResponsiveContainer width="100%" height="100%">
                            <LineChart data={stats.cost_by_year}>
                                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                                <XAxis dataKey="year" />
                                <YAxis />
                                <Tooltip />
                                <Line type="monotone" dataKey="total_eur" stroke="#10B981" strokeWidth={3} dot={{ r: 6 }} activeDot={{ r: 8 }} />
                            </LineChart>
                        </ResponsiveContainer>
                    </div>
                </div>
            </div>

            <div className="bg-white p-8 rounded-2xl shadow-sm border border-gray-100">
                <h2 className="text-2xl font-bold mb-6 text-gray-800">Efficiency Insights</h2>
                <p className="text-gray-500 mb-6 italic text-sm">*Average cost per km based on refueling logs across our community.</p>
                <div className="overflow-x-auto">
                    <table className="w-full text-left">
                        <thead>
                            <tr className="border-b border-gray-100 text-gray-400 uppercase text-xs font-bold tracking-wider">
                                <th className="px-4 py-3">Make & Model</th>
                                <th className="px-4 py-3">Year</th>
                                <th className="px-4 py-3 text-right">Avg Cost (€/km)</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-50">
                            {stats.consumption_by_car?.map((item, idx) => (
                                <tr key={idx} className="hover:bg-gray-50 transition">
                                    <td className="px-4 py-4 font-medium text-gray-800">{item.make} {item.model}</td>
                                    <td className="px-4 py-4 text-gray-500">{item.model_year || 'N/A'}</td>
                                    <td className="px-4 py-4 text-right font-bold text-emerald-600">€{item.avg_cost_per_km.toFixed(4)}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
};

export default PublicDashboard;
