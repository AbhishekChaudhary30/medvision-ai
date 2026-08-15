import React from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../components/ui/card";
import { Activity, ShieldCheck, FileText, Database, HeartPulse, Brain, Zap, Stethoscope, Scan } from "lucide-react";
import { useAuth } from "../contexts/AuthContext";
import { Link } from "react-router-dom";
import { Button } from "../components/ui/button";

export function HomePage() {
  const { user } = useAuth();
  
  return (
    <div className="space-y-10 max-w-7xl mx-auto pb-10">
      
      {/* Hero Section */}
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-indigo-900 via-primary to-indigo-800 p-8 sm:p-12 shadow-2xl">
        <div className="absolute top-0 right-0 p-8 opacity-10 pointer-events-none">
          <HeartPulse className="w-64 h-64 text-white" />
        </div>
        <div className="relative z-10 max-w-3xl">
          <div className="inline-flex items-center rounded-full border border-indigo-400/30 bg-indigo-400/10 px-3 py-1 text-sm font-medium text-indigo-100 mb-6 backdrop-blur-sm">
            <Zap className="mr-1.5 h-4 w-4 text-amber-300" />
            MedVision Enterprise OS v2.0
          </div>
          <h1 className="text-4xl sm:text-5xl font-black tracking-tight text-white mb-4">
            Welcome back, {user?.email?.split('@')[0]}
          </h1>
          <p className="text-lg text-indigo-100/90 leading-relaxed max-w-2xl">
            Our multi-modal clinical AI platform empowers healthcare professionals with instantaneous, deep-learning powered diagnostics across Respiratory, Neurology, and Dermatology fields.
          </p>
          <div className="mt-8 flex flex-wrap gap-4">
            <Link to="/analyze">
              <Button size="lg" className="bg-white text-indigo-900 hover:bg-slate-100 font-bold px-8 shadow-lg">
                Start New Analysis
              </Button>
            </Link>
            <Link to="/history">
              <Button size="lg" variant="outline" className="bg-transparent border-indigo-300/30 text-indigo-100 hover:bg-indigo-800/50 hover:text-white backdrop-blur-sm">
                View Patient History
              </Button>
            </Link>
          </div>
        </div>
      </div>

      {/* Global Analytics / Status */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card className="border-0 shadow-md bg-white overflow-hidden group">
          <div className="h-2 w-full bg-blue-500"></div>
          <CardContent className="p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 bg-blue-50 text-blue-600 rounded-xl group-hover:bg-blue-600 group-hover:text-white transition-colors">
                <Scan className="h-6 w-6" />
              </div>
              <span className="text-xs font-bold uppercase tracking-widest text-slate-400">Radiography</span>
            </div>
            <h3 className="text-xl font-black text-slate-800 mb-1">X-Ray & CT</h3>
            <p className="text-sm text-muted-foreground">Chest, Bone, Dental, Head, Abdomen.</p>
          </CardContent>
        </Card>

        <Card className="border-0 shadow-md bg-white overflow-hidden group">
          <div className="h-2 w-full bg-purple-500"></div>
          <CardContent className="p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 bg-purple-50 text-purple-600 rounded-xl group-hover:bg-purple-600 group-hover:text-white transition-colors">
                <Brain className="h-6 w-6" />
              </div>
              <span className="text-xs font-bold uppercase tracking-widest text-slate-400">Neurology</span>
            </div>
            <h3 className="text-xl font-black text-slate-800 mb-1">MRI Suite</h3>
            <p className="text-sm text-muted-foreground">Brain, Spine, and Musculoskeletal MRIs.</p>
          </CardContent>
        </Card>

        <Card className="border-0 shadow-md bg-white overflow-hidden group">
          <div className="h-2 w-full bg-emerald-500"></div>
          <CardContent className="p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 bg-emerald-50 text-emerald-600 rounded-xl group-hover:bg-emerald-600 group-hover:text-white transition-colors">
                <Activity className="h-6 w-6" />
              </div>
              <span className="text-xs font-bold uppercase tracking-widest text-slate-400">Sonography</span>
            </div>
            <h3 className="text-xl font-black text-slate-800 mb-1">Ultrasound</h3>
            <p className="text-sm text-muted-foreground">Echocardiogram, Fetal, and Abdominal.</p>
          </CardContent>
        </Card>

        <Card className="border-0 shadow-md bg-white overflow-hidden group">
          <div className="h-2 w-full bg-rose-500"></div>
          <CardContent className="p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 bg-rose-50 text-rose-600 rounded-xl group-hover:bg-rose-600 group-hover:text-white transition-colors">
                <Stethoscope className="h-6 w-6" />
              </div>
              <span className="text-xs font-bold uppercase tracking-widest text-slate-400">Pathology</span>
            </div>
            <h3 className="text-xl font-black text-slate-800 mb-1">Derm & Tissue</h3>
            <p className="text-sm text-muted-foreground">Melanoma, Retinal Fundus, Histology.</p>
          </CardContent>
        </Card>
      </div>

      {/* Quick Actions */}
      <div>
        <h2 className="text-xl font-bold tracking-tight mb-6">Platform Tools</h2>
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          
          <Link to="/analyze" className="block group">
            <Card className="h-full border border-slate-200 hover:border-primary/50 hover:shadow-md transition-all">
              <CardContent className="p-6 flex items-start gap-4">
                <div className="p-2.5 bg-slate-100 rounded-lg group-hover:bg-primary/10 group-hover:text-primary transition-colors">
                  <Scan className="h-5 w-5 text-slate-600 group-hover:text-primary" />
                </div>
                <div>
                  <h4 className="font-bold text-slate-800 mb-1">Analysis Workspace</h4>
                  <p className="text-sm text-slate-500 leading-relaxed">Upload DICOM/JPEG scans for instantaneous multi-modal AI predictions.</p>
                </div>
              </CardContent>
            </Card>
          </Link>

          <Link to="/history" className="block group">
            <Card className="h-full border border-slate-200 hover:border-primary/50 hover:shadow-md transition-all">
              <CardContent className="p-6 flex items-start gap-4">
                <div className="p-2.5 bg-slate-100 rounded-lg group-hover:bg-primary/10 group-hover:text-primary transition-colors">
                  <Database className="h-5 w-5 text-slate-600 group-hover:text-primary" />
                </div>
                <div>
                  <h4 className="font-bold text-slate-800 mb-1">Patient History</h4>
                  <p className="text-sm text-slate-500 leading-relaxed">Review past clinical analyses, download PDF reports, and manage records.</p>
                </div>
              </CardContent>
            </Card>
          </Link>

          {(user?.role === "REVIEWER" || user?.role === "ADMIN") && (
            <Link to="/reviews" className="block group">
              <Card className="h-full border border-slate-200 hover:border-primary/50 hover:shadow-md transition-all">
                <CardContent className="p-6 flex items-start gap-4">
                  <div className="p-2.5 bg-slate-100 rounded-lg group-hover:bg-primary/10 group-hover:text-primary transition-colors">
                    <ShieldCheck className="h-5 w-5 text-slate-600 group-hover:text-primary" />
                  </div>
                  <div>
                    <h4 className="font-bold text-slate-800 mb-1">Human-in-Loop Audits</h4>
                    <p className="text-sm text-slate-500 leading-relaxed">Review flagged and uncertain cases to calibrate AI accuracy.</p>
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
              This system utilizes advanced PyTorch inference engines with integrated Grad-CAM explainability for transparent diagnostics. 
              <strong> Please remember: To reset your current working session and clear the screen, use the "Reset Workspace" button located directly on the Analysis Workspace page. </strong> 
              Permanent deletion of records must be done via the History tab. This system is a decision-support tool and must not override professional medical judgement.
            </p>
          </div>
        </div>
      </div>

    </div>
  );
}
