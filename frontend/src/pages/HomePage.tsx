import React from "react";
import { Card, CardContent } from "../components/ui/card";
import { Database, FileText, HeartPulse, Scan, ShieldCheck } from "lucide-react";
import { useAuth } from "../contexts/AuthContext";
import { Link } from "react-router-dom";
import { Button } from "../components/ui/button";

export function HomePage() {
  const { user } = useAuth();
  
  return (
    <div className="space-y-10 max-w-7xl mx-auto pb-10">
      
      {/* Hero Section */}
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-blue-900 via-blue-800 to-blue-900 p-8 sm:p-12 shadow-2xl">
        <div className="absolute top-0 right-0 p-8 opacity-10 pointer-events-none">
          <HeartPulse className="w-64 h-64 text-white" />
        </div>
        <div className="relative z-10 max-w-3xl">
          <h1 className="text-4xl sm:text-5xl font-black tracking-tight text-white mb-4">
            Welcome back, {user?.email?.split('@')[0]}
          </h1>
          <p className="text-lg text-blue-100/90 leading-relaxed max-w-2xl">
            This tool allows you to upload and analyze Chest X-Rays to detect abnormalities such as Pneumonia.
          </p>
          <div className="mt-8 flex flex-wrap gap-4">
            <Link to="/analyze">
              <Button size="lg" className="bg-white text-blue-900 hover:bg-slate-100 font-bold px-8 shadow-lg">
                Start New Analysis
              </Button>
            </Link>
            <Link to="/history">
              <Button size="lg" variant="outline" className="bg-transparent border-blue-300/30 text-blue-100 hover:bg-blue-800/50 hover:text-white backdrop-blur-sm">
                View Patient History
              </Button>
            </Link>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div>
        <h2 className="text-xl font-bold tracking-tight mb-6">Platform Tools</h2>
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          
          <Link to="/analyze" className="block group">
            <Card className="h-full border border-slate-200 hover:border-blue-500/50 hover:shadow-md transition-all">
              <CardContent className="p-6 flex items-start gap-4">
                <div className="p-2.5 bg-slate-100 rounded-lg group-hover:bg-blue-500/10 group-hover:text-blue-600 transition-colors">
                  <Scan className="h-5 w-5 text-slate-600 group-hover:text-blue-600" />
                </div>
                <div>
                  <h4 className="font-bold text-slate-800 mb-1">Analysis Workspace</h4>
                  <p className="text-sm text-slate-500 leading-relaxed">Upload Chest X-Ray images for automated analysis.</p>
                </div>
              </CardContent>
            </Card>
          </Link>

          <Link to="/history" className="block group">
            <Card className="h-full border border-slate-200 hover:border-blue-500/50 hover:shadow-md transition-all">
              <CardContent className="p-6 flex items-start gap-4">
                <div className="p-2.5 bg-slate-100 rounded-lg group-hover:bg-blue-500/10 group-hover:text-blue-600 transition-colors">
                  <Database className="h-5 w-5 text-slate-600 group-hover:text-blue-600" />
                </div>
                <div>
                  <h4 className="font-bold text-slate-800 mb-1">Patient History</h4>
                  <p className="text-sm text-slate-500 leading-relaxed">Review past clinical analyses, download reports, and manage records.</p>
                </div>
              </CardContent>
            </Card>
          </Link>

          {(user?.role === "REVIEWER" || user?.role === "ADMIN") && (
            <Link to="/reviews" className="block group">
              <Card className="h-full border border-slate-200 hover:border-blue-500/50 hover:shadow-md transition-all">
                <CardContent className="p-6 flex items-start gap-4">
                  <div className="p-2.5 bg-slate-100 rounded-lg group-hover:bg-blue-500/10 group-hover:text-blue-600 transition-colors">
                    <ShieldCheck className="h-5 w-5 text-slate-600 group-hover:text-blue-600" />
                  </div>
                  <div>
                    <h4 className="font-bold text-slate-800 mb-1">Audits</h4>
                    <p className="text-sm text-slate-500 leading-relaxed">Review flagged and uncertain cases.</p>
                  </div>
                </CardContent>
              </Card>
            </Link>
          )}

        </div>
      </div>
      
      {/* Notice */}
      <div className="rounded-2xl border border-blue-100 bg-blue-50/50 p-6 sm:p-8 shadow-sm">
        <div className="flex items-start gap-4">
          <div className="p-2 bg-blue-100 text-blue-700 rounded-full mt-1">
            <FileText className="h-5 w-5" />
          </div>
          <div>
            <h3 className="font-bold text-blue-900">Clinical Protocol Notice</h3>
            <p className="mt-2 text-sm text-blue-800/80 leading-relaxed max-w-4xl">
              This system is designed to analyze Chest X-Rays.
              <strong> Please remember: To reset your current working session and clear the screen, use the "Reset Workspace" button located directly on the Analysis Workspace page. </strong> 
              Permanent deletion of records must be done via the History tab. This system is a decision-support tool and must not override professional medical judgement.
            </p>
          </div>
        </div>
      </div>

    </div>
  );
}
