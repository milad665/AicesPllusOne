import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useAuth, useUser } from "@clerk/clerk-react";
import { Users, DollarSign, Activity, Server } from 'lucide-react';

export default function AdminDashboard() {
    const { getToken } = useAuth();
    const { user } = useUser();
    const [stats, setStats] = useState(null);
    const [loading, setLoading] = useState(true);

    // Configure Auth Interceptor if not global
    useEffect(() => {
        const interceptor = axios.interceptors.request.use(async (config) => {
            const token = await getToken();
            if (token) {
                config.headers.Authorization = `Bearer ${token}`;
            }
            return config;
        });
        return () => axios.interceptors.request.eject(interceptor);
    }, [getToken]);

    useEffect(() => {
        fetchStats();
    }, []);

    const fetchStats = async () => {
        try {
            const res = await axios.get('/api/admin/stats');
            setStats(res.data);
        } catch (err) {
            console.error("Failed to fetch admin stats", err);
        } finally {
            setLoading(false);
        }
    };

    if (loading) return <div className="p-8 text-white">Loading Admin Stats...</div>;
    if (!stats) return <div className="p-8 text-red-400">Access Denied or API Error</div>;

    const cards = [
        { title: 'Total Tenants', value: stats.total_tenants, icon: Users, color: 'bg-blue-600' },
        { title: 'Monthly Revenue', value: `$${stats.total_revenue}`, icon: DollarSign, color: 'bg-green-600' },
        { title: 'Active Instances', value: stats.active_tenants, icon: Server, color: 'bg-purple-600' },
        { title: 'System Status', value: stats.system_status, icon: Activity, color: 'bg-teal-600' },
    ];

    return (
        <div className="p-8 text-white overflow-y-auto h-full">
            <h1 className="text-3xl font-bold mb-2">Super Admin Dashboard</h1>
            <p className="text-gray-400 mb-8">Welcome back, {user?.firstName}</p>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                {cards.map((card, idx) => {
                    const Icon = card.icon;
                    return (
                        <div key={idx} className="bg-gray-800 rounded-lg p-6 border border-gray-700 flex items-center justify-between">
                            <div>
                                <p className="text-gray-400 text-sm font-medium">{card.title}</p>
                                <p className="text-2xl font-bold mt-1">{card.value}</p>
                            </div>
                            <div className={`p-3 rounded-full ${card.color} bg-opacity-20 text-white`}>
                                <Icon size={24} />
                            </div>
                        </div>
                    )
                })}
            </div>

            <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
                <h2 className="text-xl font-bold mb-4">Recent Activity</h2>
                <div className="text-gray-500 text-sm text-center py-8">
                    No recent system events logged.
                </div>
            </div>
        </div>
    );
}
