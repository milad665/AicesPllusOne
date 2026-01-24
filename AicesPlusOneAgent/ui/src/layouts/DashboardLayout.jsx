import React from 'react';
import { Outlet, Link, useLocation } from 'react-router-dom';
import { UserButton, OrganizationSwitcher } from "@clerk/clerk-react";
import { LayoutDashboard, Settings, CreditCard, Shield } from 'lucide-react';

export default function DashboardLayout() {
    const location = useLocation();

    const navItems = [
        { label: 'Dashboard', icon: LayoutDashboard, path: '/' },
        { label: 'Settings', icon: Settings, path: '/settings' },
        { label: 'Billing', icon: CreditCard, path: '/billing' },
        { label: 'Admin', icon: Shield, path: '/admin' },
    ];

    return (
        <div className="flex h-screen bg-gray-900 text-white">
            {/* Sidebar */}
            <aside className="w-64 border-r border-gray-800 bg-gray-900 flex flex-col">
                <div className="h-16 flex items-center px-6 border-b border-gray-800">
                    <span className="text-lg font-bold bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">
                        Aices+1
                    </span>
                </div>

                <div className="p-4 border-b border-gray-800">
                    {/* Tenant Switcher */}
                    <OrganizationSwitcher
                        appearance={{
                            elements: {
                                rootBox: "w-full",
                                organizationSwitcherTrigger: "w-full bg-gray-800 border border-gray-700 hover:bg-gray-750 text-white p-2 rounded-md",
                                organizationSwitcherTriggerIcon: "text-gray-400",
                                userPreviewTextContainer: "hidden"
                            }
                        }}
                    />
                </div>

                <nav className="flex-1 p-4 space-y-1">
                    {navItems.map((item) => {
                        const Icon = item.icon;
                        const isActive = location.pathname === item.path;
                        return (
                            <Link
                                key={item.path}
                                to={item.path}
                                className={`flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium transition-colors ${isActive
                                    ? 'bg-blue-600/10 text-blue-400'
                                    : 'text-gray-400 hover:text-white hover:bg-gray-800'
                                    }`}
                            >
                                <Icon size={18} />
                                {item.label}
                            </Link>
                        )
                    })}
                </nav>

                <div className="p-4 border-t border-gray-800">
                    <div className="flex items-center gap-3">
                        <UserButton />
                        <div className="text-xs text-gray-400">
                            <p>User Account</p>
                        </div>
                    </div>
                </div>
            </aside>

            {/* Main Content Area */}
            <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
                <Outlet />
            </div>
        </div>
    );
}
