import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { CreditCard, Zap, CheckCircle, AlertCircle, Clock, Users, ToggleLeft, ToggleRight, Loader } from 'lucide-react';
import { useAuth } from "@clerk/clerk-react";
import { format } from 'date-fns';

export default function Billing() {
    const { getToken, isLoaded } = useAuth();
    const [status, setStatus] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [processing, setProcessing] = useState(false);
    const [togglingService, setTogglingService] = useState(null);
    const [updatingSeats, setUpdatingSeats] = useState(false);
    const [seatCountInput, setSeatCountInput] = useState(1);

    // Configure Axios Authorization
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

    const fetchStatus = async () => {
        try {
            const res = await axios.get('/api/billing/status');
            setStatus(res.data);
            setSeatCountInput(res.data.seat_count || 1);
        } catch (err) {
            console.error(err);
            setError("Failed to load billing status.");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        if (isLoaded) {
            fetchStatus();
        }
    }, [isLoaded]);

    const handleActivateTrial = async () => {
        setProcessing(true);
        try {
            await axios.post('/api/billing/activate-trial', {});
            await fetchStatus();
        } catch (err) {
            alert(err.response?.data?.detail || "Failed to activate trial");
        } finally {
            setProcessing(false);
        }
    };

    const handleActivatePAYG = async () => {
        // Mocking Stripe Element Token
        setProcessing(true);
        try {
            await axios.post('/api/billing/activate-payg', {
                stripe_setup_intent_id: "mock_setup_intent_id"
            });
            await fetchStatus();
            alert("Subscription Activated! Welcome to Aices+1.");
        } catch (err) {
            alert(err.response?.data?.detail || "Failed to activate subscription");
        } finally {
            setProcessing(false);
        }
    };

    const handleUpdateSeats = async () => {
        if (seatCountInput < 1) return;
        setUpdatingSeats(true);
        try {
            await axios.post('/api/billing/seats', { seat_count: parseInt(seatCountInput) });
            await fetchStatus();
            alert("Seat count updated.");
        } catch (err) {
            alert(err.response?.data?.detail || "Failed to update seats");
        } finally {
            setUpdatingSeats(false);
        }
    };

    const toggleService = async (serviceId, currentStatus) => {
        setTogglingService(serviceId);
        try {
            if (currentStatus === 'active') {
                if (!confirm(`Are you sure you want to deactivate ${serviceId}? It will remain available until the end of the billing period.`)) {
                    setTogglingService(null);
                    return;
                }
                await axios.post(`/api/billing/services/${serviceId}/deactivate`);
            } else {
                // Activate
                const price = serviceId === 'architecture_overview' ? 20 : 5;
                const cost = price * (status.seat_count || 1);
                if (!confirm(`Activate ${serviceId}? This will deduct €${cost} from your credits (` + (status.seat_count || 1) + ` seats).`)) {
                    setTogglingService(null);
                    return;
                }
                await axios.post(`/api/billing/services/${serviceId}/activate`);
            }
            await fetchStatus();
        } catch (err) {
            alert(err.response?.data?.detail || `Failed to toggle service.`);
        } finally {
            setTogglingService(null);
        }
    };

    if (loading) return <div className="p-8 text-slate-500">Loading billing details...</div>;

    const isActive = status?.subscription_status === 'active_payg' || status?.subscription_status === 'trial';
    const isTrial = status?.subscription_status === 'trial';

    const servicesList = [
        { id: 'architecture_overview', name: 'Architecture Overview', price: 20, desc: 'Detailed C4 diagrams, analysis, and MCP tools.' },
        { id: 'documentation', name: 'Documentation Service', price: 5, desc: 'Document storage, retrieval, and search tools.' }
    ];

    return (
        <div className="p-8 max-w-5xl mx-auto h-full overflow-y-auto">
            <header className="mb-8">
                <h1 className="text-3xl font-bold text-slate-900 mb-2">Subscription & Billing</h1>
                <p className="text-slate-500">Manage your plan, services, and credits.</p>
            </header>

            <div className="grid md:grid-cols-3 gap-6 mb-12">
                {/* Balance Card */}
                <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
                    <h3 className="text-sm font-medium text-slate-500 uppercase tracking-wide mb-2">Credits Balance</h3>
                    <div className="flex items-baseline gap-2">
                        <span className={`text-4xl font-bold ${status?.credits_balance < 20 ? 'text-red-600' : 'text-slate-900'}`}>
                            €{status?.credits_balance?.toFixed(2)}
                        </span>
                    </div>
                </div>

                {/* Status Card */}
                <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
                    <h3 className="text-sm font-medium text-slate-500 uppercase tracking-wide mb-2">Current Status</h3>
                    <div className="flex items-center gap-3">
                        <div className={`px-3 py-1 rounded-full text-sm font-bold uppercase tracking-wider ${isActive ? 'bg-emerald-100 text-emerald-700' : 'bg-slate-100 text-slate-600'
                            }`}>
                            {status?.subscription_status === 'active_payg' ? 'Pay As You Go' : status?.subscription_status}
                        </div>
                        {isTrial && (
                            <span className="text-xs text-orange-600 font-medium">
                                Expires {format(new Date(status.trial_expires_at), 'MMM d, yyyy')}
                            </span>
                        )}
                    </div>
                </div>
            </div>

            {/* PAYG / Trial Activation UI (Only if inactive) */}
            {!isActive && (
                <div className="mb-12">
                    <h2 className="text-xl font-bold text-slate-900 mb-6">Choose a Plan to Activate Services</h2>
                    <div className="grid md:grid-cols-2 gap-8">
                        {/* Free Trial Offer */}
                        {status?.is_eligible_for_trial && (
                            <div className="bg-white border border-slate-200 rounded-xl p-8 relative overflow-hidden group hover:border-sky-300 transition-all">
                                <div className="absolute top-0 right-0 bg-sky-100 text-sky-700 text-xs font-bold px-3 py-1 rounded-bl">NEW TENANT ONLY</div>
                                <div className="w-12 h-12 bg-sky-50 rounded-lg flex items-center justify-center mb-6 text-sky-600">
                                    <Clock size={24} />
                                </div>
                                <h3 className="text-xl font-bold text-slate-900 mb-2">30-Day Free Trial</h3>
                                <p className="text-slate-500 mb-6">Access all features (Architecture & Docs) free for 30 days.</p>
                                <button
                                    onClick={handleActivateTrial}
                                    disabled={processing}
                                    className="w-full py-3 bg-white border-2 border-slate-200 text-slate-700 font-bold rounded-lg hover:border-sky-500 hover:text-sky-600 transition-all disabled:opacity-50">
                                    {processing ? 'Processing...' : 'Start Free Trial'}
                                </button>
                            </div>
                        )}

                        {/* PAYG Offer */}
                        <div className="bg-gradient-to-br from-slate-900 to-slate-800 text-white rounded-xl p-8 relative overflow-hidden shadow-xl">
                            {status?.is_eligible_for_welcome_credit && (
                                <div className="absolute top-4 right-4 bg-yellow-400 text-yellow-900 text-xs font-bold px-3 py-1 rounded-full flex items-center gap-1 shadow-lg animate-pulse">
                                    <Zap size={12} fill="currentColor" />
                                    €200 WELCOME CREDIT
                                </div>
                            )}
                            <div className="w-12 h-12 bg-white/10 rounded-lg flex items-center justify-center mb-6 text-yellow-400">
                                <CreditCard size={24} />
                            </div>
                            <h3 className="text-xl font-bold text-white mb-2">Pay As You Go</h3>
                            <p className="text-slate-300 mb-6">Activate flexible service billing.</p>
                            <button
                                onClick={handleActivatePAYG}
                                disabled={processing}
                                className="w-full py-3 bg-emerald-500 text-emerald-950 font-bold rounded-lg hover:bg-emerald-400 transition-all shadow-lg shadow-emerald-500/20 disabled:opacity-50">
                                {processing ? 'Processing...' : 'Add Card & Activate'}
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* Active Service Management */}
            {isActive && !isTrial && (
                <div className="space-y-8">
                    {/* Seat Management */}
                    <section className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
                        <div className="flex items-center justify-between mb-4">
                            <h2 className="text-xl font-bold text-slate-900 flex items-center gap-2">
                                <Users className="text-slate-600" /> Seat Management
                            </h2>
                            <span className="text-sm text-slate-500">Billable Users</span>
                        </div>
                        <div className="flex items-end gap-4 max-w-sm">
                            <div className="flex-1">
                                <label className="block text-sm font-medium text-slate-700 mb-1">Total Seats</label>
                                <input
                                    type="number"
                                    min="1"
                                    value={seatCountInput}
                                    onChange={(e) => setSeatCountInput(e.target.value)}
                                    className="w-full bg-slate-50 border border-slate-200 rounded px-3 py-2 text-slate-900 focus:ring-2 focus:ring-sky-500 outline-none"
                                />
                            </div>
                            <button
                                onClick={handleUpdateSeats}
                                disabled={updatingSeats || seatCountInput == status.seat_count}
                                className="px-4 py-2 bg-slate-900 text-white font-medium rounded hover:bg-slate-800 disabled:opacity-50 transition-colors">
                                {updatingSeats ? 'Updating...' : 'Update Seats'}
                            </button>
                        </div>
                        <p className="text-xs text-slate-400 mt-2">
                            System charges are calculated based on total active seats × service price.
                        </p>
                    </section>

                    {/* Services List */}
                    <section className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
                        <div className="p-6 border-b border-slate-100">
                            <h2 className="text-xl font-bold text-slate-900 flex items-center gap-2">
                                <Zap className="text-sky-600" /> Active Services
                            </h2>
                        </div>
                        <div className="divide-y divide-slate-100">
                            {servicesList.map(svc => {
                                const svcState = status?.services?.[svc.id];
                                const isSvcActive = svcState?.status === 'active';
                                const activeUntil = svcState?.active_until ? new Date(svcState.active_until) : null;
                                const isCanceled = svcState?.status === 'canceled';

                                return (
                                    <div key={svc.id} className="p-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
                                        <div>
                                            <h3 className="font-bold text-slate-900">{svc.name}</h3>
                                            <p className="text-sm text-slate-500">{svc.desc}</p>
                                            <div className="flex items-center gap-3 mt-2">
                                                <span className="text-xs font-bold bg-slate-100 text-slate-600 px-2 py-1 rounded">
                                                    ${svc.price}/user/mo
                                                </span>
                                                {(isSvcActive || (isCanceled && activeUntil > new Date())) && (
                                                    <span className="text-xs font-bold text-emerald-600 flex items-center gap-1">
                                                        <CheckCircle size={12} /> Active
                                                    </span>
                                                )}
                                                {isCanceled && activeUntil > new Date() && (
                                                    <span className="text-xs text-orange-600">
                                                        (Cancels on {format(activeUntil, 'MMM d')})
                                                    </span>
                                                )}
                                            </div>
                                        </div>

                                        <div className="flex items-center gap-4">
                                            {togglingService === svc.id ? (
                                                <Loader className="animate-spin text-slate-400" />
                                            ) : (
                                                <button
                                                    onClick={() => toggleService(svc.id, isSvcActive ? 'active' : 'inactive')}
                                                    className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-all ${isSvcActive
                                                            ? 'bg-red-50 text-red-600 hover:bg-red-100'
                                                            : 'bg-emerald-50 text-emerald-600 hover:bg-emerald-100'
                                                        }`}
                                                >
                                                    {isSvcActive ? <ToggleRight className="fill-current" /> : <ToggleLeft />}
                                                    {isSvcActive ? 'Deactivate' : 'Activate'}
                                                </button>
                                            )}
                                        </div>
                                    </div>
                                );
                            })}
                        </div>
                    </section>
                </div>
            )}

            {/* Trial Info */}
            {isTrial && (
                <div className="mt-8 bg-indigo-50 border border-indigo-200 rounded-xl p-6">
                    <p className="text-indigo-900 font-medium">✨ You are in Free Trial Mode</p>
                    <p className="text-indigo-700 text-sm mt-1">
                        You have full access to all services (Architecture & Documentation) for unlimited seats until your trial expires.
                        Upgrade to PAYG to continue using services after the trial.
                    </p>
                </div>
            )}

        </div>
    );
}
