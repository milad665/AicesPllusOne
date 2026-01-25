import React from 'react';
import { SignInButton } from "@clerk/clerk-react";
import { Shield, Code, Globe, Activity, Layers, Zap } from 'lucide-react';
import { Helmet } from 'react-helmet-async';

export default function LandingPage() {
    return (
        <div className="min-h-screen bg-[#F8FAFC] text-slate-900 selection:bg-sky-200">

            <Helmet>
                <title>Aices+1 - Intelligent Architecture Context for Coding AI Agents</title>
                <meta name="description" content="Automated architecture diagrams and deep code analysis. Aices+1 provides the missing architectural context that Coding AI Agents need to operate effectively." />
                <link rel="canonical" href="https://www.studioaices.com" />
            </Helmet>

            {/* Navigation */}
            <nav className="fixed w-full z-50 bg-white/80 backdrop-blur-md border-b border-slate-200 shadow-sm">
                <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
                    <div className="flex items-center gap-2">
                        <div className="w-8 h-8 bg-gradient-to-br from-sky-600 to-indigo-600 rounded-lg flex items-center justify-center shadow-md">
                            <Layers className="text-white w-5 h-5" />
                        </div>
                        <span className="text-xl font-bold tracking-tight text-slate-900">Aices+1</span>
                    </div>
                    <div className="flex items-center gap-6">
                        <a href="#features" className="text-sm font-medium text-slate-600 hover:text-sky-600 transition-colors">Features</a>
                        <a href="#security" className="text-sm font-medium text-slate-600 hover:text-sky-600 transition-colors">Security</a>
                        <SignInButton mode="modal">
                            <button className="px-5 py-2 bg-slate-900 text-white text-sm font-semibold rounded-full hover:bg-slate-800 transition-colors shadow-lg shadow-slate-900/10">
                                Sign In
                            </button>
                        </SignInButton>
                    </div>
                </div>
            </nav>

            {/* Hero Section */}
            <section className="relative pt-32 pb-20 px-6 overflow-hidden">
                {/* Background Gradients (Subtle Light Mode) */}
                <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[1000px] h-[800px] bg-sky-100/50 rounded-full blur-[100px] -z-10 mix-blend-multiply opacity-70" />
                <div className="absolute bottom-0 right-0 w-[800px] h-[600px] bg-indigo-100/50 rounded-full blur-[120px] -z-10 mix-blend-multiply opacity-70" />

                <div className="max-w-5xl mx-auto text-center">
                    <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white border border-slate-200 text-sky-600 text-xs font-semibold mb-8 shadow-sm">
                        <span className="relative flex h-2 w-2">
                            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-sky-400 opacity-75"></span>
                            <span className="relative inline-flex rounded-full h-2 w-2 bg-sky-500"></span>
                        </span>
                        v1.1 Enterprise Release Now Available
                    </div>

                    <h1 className="text-5xl md:text-7xl font-bold tracking-tight mb-8 text-slate-900 leading-tight">
                        Complete Architecture Context <br />
                        <span className="bg-gradient-to-r from-sky-600 to-indigo-600 bg-clip-text text-transparent">for Coding AI Agents</span>
                    </h1>

                    <p className="text-xl text-slate-600 mb-6 max-w-3xl mx-auto leading-relaxed">
                        An intelligent AI-powered service that automatically generates and provides detailed architectural context to empower your Coding AI Agents.
                    </p>

                    <p className="text-lg text-slate-500 mb-10 max-w-2xl mx-auto italic font-medium">
                        "Modern software is a choreographed symphony of services. AI coding agents are flying blind without architectural context. Aices+1 provides that context."
                    </p>

                    <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
                        <SignInButton mode="modal">
                            <button className="px-8 py-4 bg-sky-600 hover:bg-sky-500 rounded-lg text-lg font-semibold text-white shadow-xl shadow-sky-500/20 transition-all w-full sm:w-auto">
                                Get Started
                            </button>
                        </SignInButton>
                        <button className="px-8 py-4 bg-white hover:bg-slate-50 border border-slate-200 rounded-lg text-lg font-medium text-slate-700 shadow-sm transition-all w-full sm:w-auto">
                            View Documentation
                        </button>
                    </div>
                </div>

                {/* Hero Visual */}
                <div className="mt-24 max-w-6xl mx-auto rounded-xl border border-slate-200 bg-white/50 backdrop-blur-sm shadow-2xl shadow-slate-900/5 overflow-hidden p-2">
                    <div className="aspect-[16/9] bg-slate-50 rounded-lg overflow-hidden relative border border-slate-100">
                        <div className="absolute inset-0 flex items-center justify-center text-gray-400">
                            <img src="/dashboard-preview.png" alt="Aether Grid Dashboard Preview" className="w-full h-full object-cover" />
                        </div>
                    </div>
                </div>
            </section>

            {/* Stats/Logos */}
            <section className="py-12 border-y border-slate-200 bg-white">
                <div className="max-w-7xl mx-auto px-6">
                    <p className="text-center text-xs font-semibold tracking-wider text-slate-400 mb-8 uppercase">Trusted by engineering teams working with</p>
                    <div className="flex flex-wrap justify-center gap-8 md:gap-16 opacity-60 grayscale hover:grayscale-0 transition-all duration-500">
                        {['Python', 'TypeScript', 'C# .NET', 'Java', 'Go', 'Rust'].map(lang => (
                            <span key={lang} className="text-xl font-bold text-slate-800">{lang}</span>
                        ))}
                    </div>
                </div>
            </section>

            {/* Feature Grid */}
            <section id="features" className="py-24 px-6 max-w-7xl mx-auto">
                <div className="text-center mb-16">
                    <h2 className="text-3xl font-bold mb-4 text-slate-900">Enterprise-Ready Architecture</h2>
                    <p className="text-slate-500 max-w-2xl mx-auto">Built for scale, security, and complex dependency graphs. Aether Grid design ensures clarity in complex systems.</p>
                </div>

                <div className="grid md:grid-cols-3 gap-8">
                    <FeatureCard
                        icon={Code}
                        title="Deep Code Analysis"
                        desc="Supports C#, Java, Python, and more. Auto-detects frameworks like ASP.NET Core, Spring Boot, and FastAPI."
                    />
                    <div id="security" className="contents">
                        <FeatureCard
                            icon={Shield}
                            title="Zero-Trust Security"
                            desc="Hybrid deployment model keeps your source code on-premise. Use mTLS for secure agent communication."
                        />
                    </div>
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
                        title="Standard Models"
                        desc="Generates industry-standard architecture diagrams (Context, Container, Component) out of the box."
                    />
                </div>
            </section>

            {/* Footer */}
            <footer className="py-12 px-6 border-t border-slate-200 bg-slate-50 text-center text-slate-500 text-sm">
                <p>&copy; 2026 Aices+1. All rights reserved.</p>
            </footer>
        </div>
    );
}

function FeatureCard({ icon: Icon, title, desc }) {
    return (
        <div className="p-8 rounded-2xl bg-white border border-slate-100 hover:border-sky-200 hover:shadow-lg hover:shadow-sky-500/5 transition-all group">
            <div className="w-12 h-12 bg-sky-50 rounded-xl flex items-center justify-center mb-6 group-hover:bg-sky-100 transition-colors">
                <Icon className="text-sky-600 w-6 h-6" />
            </div>
            <h3 className="text-xl font-bold mb-3 text-slate-900">{title}</h3>
            <p className="text-slate-500 leading-relaxed">{desc}</p>
        </div>
    );
}
