import React from 'react';
import { SignInButton } from "@clerk/clerk-react";
import { Shield, Code, Globe, Activity, Layers, Zap } from 'lucide-react';

export default function LandingPage() {
    return (
        <div className="min-h-screen bg-[#0a0a0a] text-white selection:bg-blue-500/30">

            {/* Navigation */}
            <nav className="fixed w-full z-50 bg-[#0a0a0a]/80 backdrop-blur-md border-b border-white/5">
                <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
                    <div className="flex items-center gap-2">
                        <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                            <Layers className="text-white w-5 h-5" />
                        </div>
                        <span className="text-xl font-bold tracking-tight">Aices+1</span>
                    </div>
                    <div className="flex items-center gap-6">
                        <a href="#features" className="text-sm text-gray-400 hover:text-white transition-colors">Features</a>
                        <a href="#security" className="text-sm text-gray-400 hover:text-white transition-colors">Security</a>
                        <SignInButton mode="modal">
                            <button className="px-4 py-2 bg-white text-black text-sm font-semibold rounded-full hover:bg-gray-200 transition-colors">
                                Sign In
                            </button>
                        </SignInButton>
                    </div>
                </div>
            </nav>

            {/* Hero Section */}
            <section className="relative pt-32 pb-20 px-6 overflow-hidden">
                {/* Background Gradients */}
                <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[1000px] h-[500px] bg-blue-500/20 rounded-full blur-[120px] -z-10" />
                <div className="absolute bottom-0 right-0 w-[800px] h-[600px] bg-purple-500/10 rounded-full blur-[100px] -z-10" />

                <div className="max-w-5xl mx-auto text-center">
                    <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-xs font-medium mb-8">
                        <span className="relative flex h-2 w-2">
                            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75"></span>
                            <span className="relative inline-flex rounded-full h-2 w-2 bg-blue-500"></span>
                        </span>
                        v1.0 Enterprise Release Now Available
                    </div>

                    <h1 className="text-5xl md:text-7xl font-bold tracking-tight mb-8 bg-gradient-to-b from-white to-gray-400 bg-clip-text text-transparent">
                        Your Codebase, <br />
                        <span className="text-white">Fully Understood.</span>
                    </h1>

                    <p className="text-xl text-gray-400 mb-10 max-w-2xl mx-auto leading-relaxed">
                        Automatic C4 Architecture diagrams, enterprise-grade security, and deep code analysis for modern engineering teams.
                    </p>

                    <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
                        <SignInButton mode="modal">
                            <button className="px-8 py-4 bg-blue-600 hover:bg-blue-500 rounded-lg text-lg font-semibold shadow-lg shadow-blue-500/25 transition-all w-full sm:w-auto">
                                Get Started
                            </button>
                        </SignInButton>
                        <button className="px-8 py-4 bg-white/5 hover:bg-white/10 border border-white/10 rounded-lg text-lg font-medium backdrop-blur-sm transition-all w-full sm:w-auto">
                            View Documentation
                        </button>
                    </div>
                </div>

                {/* Hero Visual */}
                <div className="mt-20 max-w-6xl mx-auto rounded-xl border border-white/10 bg-white/5 backdrop-blur-sm shadow-2xl overflow-hidden p-2">
                    <div className="aspect-[16/9] bg-gray-900 rounded-lg overflow-hidden relative">
                        <div className="absolute inset-0 flex items-center justify-center text-gray-600">
                            <img src="/api/placeholder/1200/675" alt="Dashboard Preview" className="opacity-50" />
                            {/* Placeholder for actual screenshot */}
                            <span className="absolute">Interactive Architecture Dashboard Preview</span>
                        </div>
                    </div>
                </div>
            </section>

            {/* Stats/Logos */}
            <section className="py-10 border-y border-white/5 bg-white/[0.02]">
                <div className="max-w-7xl mx-auto px-6">
                    <p className="text-center text-sm text-gray-500 mb-8">TRUSTED BY ENGINEERING TEAMS WORKING WITH</p>
                    <div className="flex flex-wrap justify-center gap-8 md:gap-16 opacity-50 grayscale hover:grayscale-0 transition-all duration-500">
                        {['Python', 'TypeScript', 'C# .NET', 'Java', 'Go', 'Rust'].map(lang => (
                            <span key={lang} className="text-xl font-semibold text-white">{lang}</span>
                        ))}
                    </div>
                </div>
            </section>

            {/* Feature Grid */}
            <section id="features" className="py-24 px-6 max-w-7xl mx-auto">
                <div className="text-center mb-16">
                    <h2 className="text-3xl font-bold mb-4">Enterprise-Ready Architecture</h2>
                    <p className="text-gray-400">Built for scale, security, and complex dependency graphs.</p>
                </div>

                <div className="grid md:grid-cols-3 gap-8">
                    <FeatureCard
                        icon={Code}
                        title="Deep Code Analysis"
                        desc="Supports C#, Java, Python, and more. Auto-detects frameworks like ASP.NET Core, Spring Boot, and FastAPI."
                    />
                    <FeatureCard
                        icon={Shield}
                        title="Zero-Trust Security"
                        desc="Hybrid deployment model keeps your source code on-premise. Use mTLS for secure agent communication."
                    />
                    <FeatureCard
                        icon={Activity}
                        title="Live Observability"
                        desc="Real-time syncing with your repositories. Detect architectural drift before it hits production."
                    />
                    <FeatureCard
                        icon={Globe}
                        title="Multi-Tenancy"
                        desc="Strict data isolation per tenant. Ideal for large organizations with multiple independent teams."
                    />
                    <FeatureCard
                        icon={Zap}
                        title="AI-Powered Context"
                        desc="Gemini 2.5 integration creates meaningful summaries and architectural insights automatically."
                    />
                    <FeatureCard
                        icon={Layers}
                        title="C4 Model Native"
                        desc="Generates industry-standard C4 diagrams (Context, Container, Component) out of the box."
                    />
                </div>
            </section>

            {/* Footer */}
            <footer className="py-12 px-6 border-t border-white/10 bg-black text-center text-gray-500 text-sm">
                <p>&copy; 2026 Aices+1. All rights reserved.</p>
            </footer>
        </div>
    );
}

function FeatureCard({ icon: Icon, title, desc }) {
    return (
        <div className="p-6 rounded-2xl bg-white/5 border border-white/5 hover:border-blue-500/30 hover:bg-white/[0.07] transition-all group">
            <div className="w-12 h-12 bg-blue-500/10 rounded-lg flex items-center justify-center mb-4 group-hover:bg-blue-500/20 transition-colors">
                <Icon className="text-blue-400 w-6 h-6" />
            </div>
            <h3 className="text-xl font-semibold mb-2 text-white">{title}</h3>
            <p className="text-gray-400 leading-relaxed">{desc}</p>
        </div>
    );
}
