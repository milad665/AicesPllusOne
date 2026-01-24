import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { CreditCard, Zap, CheckCircle, AlertCircle, Clock } from 'lucide-react';
import { useAuth, useUser } from "@clerk/clerk-react";
import { format } from 'date-fns';

export default function Billing() {
    const { getToken, isLoaded } = useAuth();
    const [status, setStatus] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [processing, setProcessing] = useState(false);

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

    if (loading) return <div className="p-8 text-slate-500">Loading billing details...</div>;

    const isActive = status?.subscription_status === 'active_payg' || status?.subscription_status === 'trial';
    const isTrial = status?.subscription_status === 'trial';

    return (
        <div className="p-8 max-w-5xl mx-auto h-full overflow-y-auto">
            <header className="mb-8">
                <h1 className="text-3xl font-bold text-slate-900 mb-2">Subscription & Billing</h1>
                <p className="text-slate-500">Manage your plan, payment methods, and credits.</p>
            </header>

            <div className="grid md:grid-cols-3 gap-6 mb-12">
                {/* Balance Card */}
                <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
                    <h3 className="text-sm font-medium text-slate-500 uppercase tracking-wide mb-2">Credits Balance</h3>
                    <div className="flex items-baseline gap-2">
                        <span className="text-4xl font-bold text-slate-900">€{status?.credits_balance?.toFixed(2)}</span>
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

            {/* Offer Section */}
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
                                <p className="text-slate-500 mb-6">Perfect for evaluating the platform. No credit card required.</p>
                                <ul className="space-y-3 mb-8">
                                    <li className="flex items-center gap-2 text-sm text-slate-700"><CheckCircle size={16} className="text-emerald-500" /> Full Analyzer Access</li>
                                    <li className="flex items-center gap-2 text-sm text-slate-700"><CheckCircle size={16} className="text-emerald-500" /> 30 Days Duration</li>
                                    <li className="flex items-center gap-2 text-sm text-slate-400"><AlertCircle size={16} /> No Welcome Credits</li>
                                </ul>
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
                            <p className="text-slate-300 mb-6">Flexible pricing for scaling teams. Pay only for what you use.</p>
                            <ul className="space-y-3 mb-8">
                                <li className="flex items-center gap-2 text-sm text-slate-200"><CheckCircle size={16} className="text-emerald-400" /> Full Enterprise Access</li>
                                <li className="flex items-center gap-2 text-sm text-slate-200"><CheckCircle size={16} className="text-emerald-400" /> Priority Support</li>
                                {status?.is_eligible_for_welcome_credit && (
                                    <li className="flex items-center gap-2 text-sm text-yellow-300 font-medium"><CheckCircle size={16} /> Includes €200 Initial Credit</li>
                                )}
                            </ul>

                            {/* Simplified Stripe Placeholder */}
                            <div className="bg-white/5 p-4 rounded-lg border border-white/10 mb-4">
                                <p className="text-xs text-slate-400 mb-2 uppercase tracking-wide">Payment Method</p>
                                <div className="flex items-center gap-3 text-slate-300 text-sm">
                                    <div className="w-8 h-5 bg-slate-600 rounded"></div>
                                    <span>•••• •••• •••• 4242</span>
                                </div>
                            </div>

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

            {/* If Active, show management options */}
            {isActive && (
                <div className="bg-slate-50 border border-slate-200 rounded-xl p-8 mb-8">
                    <h3 className="text-lg font-bold text-slate-900 mb-4">Subscription Management</h3>
                    <p className="text-slate-500 mb-6 text-sm">
                        You can view your usage history and manage payment methods via the Stripe Customer Portal.
                    </p>
                    <button className="px-6 py-2 bg-white border border-slate-300 text-slate-700 font-medium rounded-lg hover:bg-slate-50 transition-colors">
                        Open Billing Portal
                    </button>
                </div>
            )}

        </div>
    );
}
