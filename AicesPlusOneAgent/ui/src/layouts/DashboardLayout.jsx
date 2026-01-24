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
        <div className="flex h-screen bg-[#F8FAFC] text-slate-900">
            {/* Sidebar */}
            <aside className="w-64 border-r border-slate-200 bg-white flex flex-col shadow-sm">
                <div className="h-16 flex items-center px-6 border-b border-slate-100">
                    <span className="text-lg font-bold bg-gradient-to-r from-sky-600 to-indigo-600 bg-clip-text text-transparent">
                        Aices+1
                    </span>
                </div>

                <div className="p-4 border-b border-slate-100">
                    {/* Tenant Switcher */}
                    <OrganizationSwitcher
                        appearance={{
                            elements: {
                                rootBox: "w-full",
                                organizationSwitcherTrigger: "w-full bg-slate-50 border border-slate-200 hover:bg-slate-100 text-slate-900 p-2 rounded-md transition-colors",
                                organizationSwitcherTriggerIcon: "text-slate-400",
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
                                    ? 'bg-sky-50 text-sky-700'
                                    : 'text-slate-500 hover:text-slate-900 hover:bg-slate-50'
                                    }`}
                            >
                                <Icon size={18} className={isActive ? 'text-sky-600' : 'text-slate-400'} />
                                {item.label}
                            </Link>
                        )
                    })}
                </nav>

                <div className="p-4 border-t border-slate-100 mt-auto">
                    <div className="flex items-center gap-3">
                        <UserButton />
                        <div className="text-xs text-slate-500">
                            <p className="font-medium text-slate-900">User Account</p>
                            <p>Manage Profile</p>
                        </div>
                    </div>
                </div>
            </aside>

            {/* Main Content Area */}
            <div className="flex-1 flex flex-col min-w-0 overflow-hidden bg-[#F8FAFC]">
                <Outlet />
            </div>
        </div>
    );
}
