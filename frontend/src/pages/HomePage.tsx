import React from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../components/ui/card";
import { Activity, ShieldCheck, FileText, Database } from "lucide-react";
import { useAuth } from "../contexts/AuthContext";
import { Link } from "react-router-dom";
import { Button } from "../components/ui/button";

export function HomePage() {
  const { user } = useAuth();
  
  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Welcome, {user?.email?.split('@')[0]}</h1>
        <p className="text-muted-foreground mt-2">
          MedVision AI is a research and educational clinical decision-support prototype.
        </p>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">New Analysis</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">Predict</div>
            <p className="text-xs text-muted-foreground mt-1">Upload CXR images</p>
            <Link to="/analyze" className="block mt-4">
              <Button className="w-full" variant="secondary">
                Analyze Image
              </Button>
            </Link>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">History</CardTitle>
            <Database className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">Results</div>
            <p className="text-xs text-muted-foreground mt-1">View past predictions</p>
            <Link to="/history" className="block mt-4">
              <Button className="w-full" variant="secondary">
                View History
              </Button>
            </Link>
          </CardContent>
        </Card>

        {(user?.role === "REVIEWER" || user?.role === "ADMIN") && (
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Review Queue</CardTitle>
              <ShieldCheck className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">Audit</div>
              <p className="text-xs text-muted-foreground mt-1">Review flagged cases</p>
              <Link to="/reviews" className="block mt-4">
                <Button className="w-full" variant="secondary">
                  Open Queue
                </Button>
              </Link>
            </CardContent>
          </Card>
        )}
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Documentation</CardTitle>
            <FileText className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">Guide</div>
            <p className="text-xs text-muted-foreground mt-1">System instructions</p>
            <a href="https://github.com/medvision-ai" target="_blank" rel="noreferrer" className="block mt-4">
              <Button className="w-full" variant="outline">
                View Docs
              </Button>
            </a>
          </CardContent>
        </Card>
      </div>
      
      <div className="rounded-lg border bg-blue-50/50 p-6 shadow-sm dark:bg-blue-950/20">
        <h3 className="font-semibold text-blue-900 dark:text-blue-200">System Notice</h3>
        <p className="mt-2 text-sm text-blue-800 dark:text-blue-300 leading-relaxed">
          This system is running <strong>Phase 6</strong> architecture. It includes deep learning inference for Chest X-Ray classification,
          Grad-CAM explainability, and Role-Based Access Control. All uploads are processed by the PyTorch backend API. 
          <br/><br/>
          <strong>Disclaimer:</strong> This application is NOT a certified medical device and must not be used for actual clinical diagnosis.
        </p>
      </div>
    </div>
  );
}
