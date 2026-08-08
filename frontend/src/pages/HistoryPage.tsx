import React from "react";
import { useQuery } from "@tanstack/react-query";
import { getAnalyses, downloadReport } from "../services/api";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { FileDown, Calendar, Loader2 } from "lucide-react";
import { cn } from "../lib/utils";

export function HistoryPage() {
  const { data, isLoading } = useQuery({
    queryKey: ["analyses"],
    queryFn: () => getAnalyses(0, 50),
  });

  const getStatusColor = (status: string) => {
    switch (status) {
      case "HIGH_CONFIDENCE": return "text-emerald-700 bg-emerald-100";
      case "LOW_CONFIDENCE": return "text-amber-700 bg-amber-100";
      case "UNCERTAIN": return "text-rose-700 bg-rose-100";
      default: return "text-slate-700 bg-slate-100";
    }
  };

  if (isLoading) {
    return <div className="flex h-64 items-center justify-center"><Loader2 className="h-8 w-8 animate-spin text-primary" /></div>;
  }

  const items = data?.items || [];

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Analysis History</h1>
        <p className="text-muted-foreground mt-2">View your past predictions and download PDF reports.</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Recent Analyses</CardTitle>
        </CardHeader>
        <CardContent>
          {items.length === 0 ? (
            <div className="py-8 text-center text-muted-foreground">
              No analysis history found. Upload an image to get started.
            </div>
          ) : (
            <div className="divide-y border rounded-md overflow-hidden">
              {items.map((analysis) => (
                <div key={analysis.id} className="p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white hover:bg-slate-50 transition-colors">
                  <div className="space-y-1">
                    <div className="flex items-center gap-3">
                      <span className="font-semibold text-lg">{analysis.predicted_class}</span>
                      <span className={cn("px-2.5 py-0.5 rounded-full text-xs font-semibold", getStatusColor(analysis.uncertainty_status))}>
                        {(analysis.confidence * 100).toFixed(1)}% Conf
                      </span>
                      {analysis.review_status !== "NOT_REVIEWED" && (
                        <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-blue-100 text-blue-700">
                          {analysis.review_status}
                        </span>
                      )}
                    </div>
                    
                    <div className="flex items-center text-sm text-muted-foreground gap-4">
                      <span className="flex items-center gap-1">
                        <Calendar className="h-3.5 w-3.5" />
                        {new Date(analysis.created_at).toLocaleDateString()}
                      </span>
                      <span>ID: {analysis.id.substring(0, 8)}...</span>
                      {analysis.explanation_method && (
                        <span>• Explained</span>
                      )}
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-2">
                    <Button 
                      variant="outline" 
                      size="sm"
                      onClick={() => downloadReport(analysis.id)}
                      className="whitespace-nowrap"
                    >
                      <FileDown className="mr-2 h-4 w-4" />
                      Report
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
