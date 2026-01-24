import React from 'react';

export default function Billing() {
    return (
        <div className="p-8 text-white h-full overflow-y-auto">
            <h1 className="text-3xl font-bold mb-4">Subscription & Billing</h1>
            <p className="text-gray-400 mb-8">Manage your subscription plan and payment methods.</p>

            {/* Current Plan */}
            <div className="bg-gray-800 rounded-lg p-6 border border-gray-700 mb-8">
                <h2 className="text-xl font-semibold mb-2">Current Plan: Free Tier</h2>
                <p className="text-gray-400 mb-4">You are currently on the free tier. Upgrade to access premium features.</p>
                <button className="px-4 py-2 bg-blue-600 hover:bg-blue-500 rounded text-sm font-medium transition-colors">
                    Manage Subscription
                </button>
            </div>

            {/* Pricing Table Mockup */}
            <h2 className="text-2xl font-bold mb-6">Available Plans</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {/* Free */}
                <div className="bg-gray-800 border border-gray-700 rounded-lg p-6 flex flex-col">
                    <h3 className="text-lg font-bold">Starter</h3>
                    <p className="text-3xl font-bold mt-2">$0<span className="text-sm font-normal text-gray-400">/mo</span></p>
                    <ul className="mt-6 space-y-3 flex-1">
                        <li className="flex gap-2 text-sm"><span className="text-green-400">✓</span> Basic Analysis</li>
                        <li className="flex gap-2 text-sm"><span className="text-green-400">✓</span> 1 Tenant</li>
                    </ul>
                    <button className="mt-8 w-full py-2 border border-gray-600 rounded text-sm hover:bg-gray-700">Current Plan</button>
                </div>

                {/* Pro */}
                <div className="bg-gradient-to-br from-blue-900 to-gray-900 border border-blue-500 rounded-lg p-6 flex flex-col relative overflow-hidden">
                    <div className="absolute top-0 right-0 bg-blue-500 text-xs px-2 py-1 rounded-bl">POPULAR</div>
                    <h3 className="text-lg font-bold">Pro</h3>
                    <p className="text-3xl font-bold mt-2">$99<span className="text-sm font-normal text-gray-400">/mo</span></p>
                    <ul className="mt-6 space-y-3 flex-1">
                        <li className="flex gap-2 text-sm"><span className="text-green-400">✓</span> Advanced C# Analysis</li>
                        <li className="flex gap-2 text-sm"><span className="text-green-400">✓</span> Tenant Isolation</li>
                        <li className="flex gap-2 text-sm"><span className="text-green-400">✓</span> Priority Support</li>
                    </ul>
                    <button className="mt-8 w-full py-2 bg-blue-600 hover:bg-blue-500 rounded text-sm font-bold">Upgrade to Pro</button>
                </div>

                {/* Enterprise */}
                <div className="bg-gray-800 border border-gray-700 rounded-lg p-6 flex flex-col">
                    <h3 className="text-lg font-bold">Enterprise</h3>
                    <p className="text-3xl font-bold mt-2">Custom</p>
                    <ul className="mt-6 space-y-3 flex-1">
                        <li className="flex gap-2 text-sm"><span className="text-green-400">✓</span> On-Premise Agents</li>
                        <li className="flex gap-2 text-sm"><span className="text-green-400">✓</span> Dedicated Support</li>
                        <li className="flex gap-2 text-sm"><span className="text-green-400">✓</span> Custom Contracts</li>
                    </ul>
                    <button className="mt-8 w-full py-2 border border-gray-600 rounded text-sm hover:bg-gray-700">Contact Sales</button>
                </div>
            </div>
        </div>
    );
}
