import React from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { getAnalyses, downloadReport, deleteAnalysis } from "../services/api";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Calendar, Loader2, Trash2, AlertCircle, ArrowRight } from "lucide-react";
import { cn } from "../lib/utils";

export function HistoryPage() {
  const queryClient = useQueryClient();
  const { data, isLoading } = useQuery({
    queryKey: ["analyses"],
    queryFn: () => getAnalyses(0, 50),
  });

  const deleteMutation = useMutation({
    mutationFn: deleteAnalysis,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["analyses"] });
    },
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

  // Triage Logic: Sort critical cases to the top
  const isCritical = (c: string) => {
    if (!c) return false;
    const criticalKeywords = ["HEMORRHAGE", "TUMOR", "MALIGNANT", "PNEUMONIA", "FRACTURE", "APPENDICITIS", "TEAR", "ANOMALY", "CARCINOMA", "POLYP", "BIRADS-4/5"];
    return criticalKeywords.some(k => c.toUpperCase().includes(k));
  };

  const sortedAnalyses = data?.items ? [...data.items].sort((a, b) => {
    const aCritical = isCritical(a.predicted_class);
    const bCritical = isCritical(b.predicted_class);
    if (aCritical && !bCritical) return -1;
    if (!aCritical && bCritical) return 1;
    return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
  }) : [];

  return (
    <div className="max-w-4xl mx-auto space-y-8 pb-12">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Radiologist Triage Worklist</h1>
          <p className="text-muted-foreground mt-2">
            AI-prioritized patient cases. <strong className="text-red-500">STAT / Critical</strong> findings are automatically moved to the top of the queue for immediate attention.
          </p>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Recent Analyses</CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          <div className="divide-y">
            {sortedAnalyses.length === 0 ? (
              <div className="p-8 text-center text-muted-foreground">
                No analyses found in your history.
              </div>
            ) : (
              sortedAnalyses.map((analysis) => {
                const critical = isCritical(analysis.predicted_class);
                return (
                <div key={analysis.id} className={cn("p-6 hover:bg-slate-50 transition-colors flex flex-col sm:flex-row gap-6", critical && "bg-red-50/50 hover:bg-red-50 border-l-4 border-l-red-500")}>
                  <div className="flex-1 space-y-3">
                    <div className="flex items-center gap-2">
                      <span className="px-2.5 py-1 bg-slate-100 text-slate-700 text-xs font-bold rounded-md uppercase tracking-wider">
                        {analysis.modality ? analysis.modality.replace("-", " ") : "chest xray"}
                      </span>
                      {critical && (
                        <span className="px-2.5 py-1 bg-red-100 text-red-700 border border-red-200 text-xs font-bold rounded-md uppercase tracking-wider animate-pulse flex items-center gap-1">
                          <AlertCircle className="w-3 h-3" /> STAT / CRITICAL
                        </span>
                      )}
                    </div>
                    <div>
                      <h3 className="text-xl font-bold text-slate-800">{analysis.predicted_class}</h3>
                      <div className="text-sm font-medium text-primary mt-0.5">
                        Confidence: {(analysis.confidence * 100).toFixed(1)}%
                      </div>
                    </div>
                    {analysis.review_status !== "NOT_REVIEWED" && (
                      <span className="inline-block px-2.5 py-0.5 rounded-full text-xs font-semibold bg-blue-100 text-blue-700">
                        {analysis.review_status}
                      </span>
                    )}
                    <div className="flex flex-wrap items-center text-sm text-muted-foreground gap-4">
                      <span className="flex items-center gap-1">
                        <Calendar className="h-3.5 w-3.5" />
                        {new Date(analysis.created_at).toLocaleDateString()}
                      </span>
                      {analysis.patient_age && analysis.patient_gender && (
                        <span className="font-semibold text-slate-600">
                          Pt: {analysis.patient_age}y/{analysis.patient_gender}
                        </span>
                      )}
                      <span className="hidden sm:inline">ID: {analysis.id.substring(0, 8)}...</span>
                      {analysis.explanation_method && (
                        <span className="text-emerald-600 font-medium">• Explained</span>
                      )}
                    </div>

                    {analysis.clinical_notes && (
                      <div className="mt-2 text-xs text-slate-500 italic line-clamp-1 max-w-xl">
                        Context: "{analysis.clinical_notes}"
                      </div>
                    )}

                    {analysis.clinical_suggestions && (
                      <div className="mt-2 text-sm text-indigo-800 bg-indigo-50/50 p-2 rounded-md border border-indigo-100 line-clamp-2 max-w-xl">
                        <span className="font-semibold">Action Plan: </span> {analysis.clinical_suggestions}
                      </div>
                    )}
                  </div>

                  <div className="flex flex-row sm:flex-col items-center sm:items-end justify-between gap-2 sm:w-48 shrink-0 border-t sm:border-t-0 sm:border-l pt-4 sm:pt-0 sm:pl-6 border-slate-100">
                    <Button
                      variant="destructive"
                      size="sm"
                      className="w-full sm:w-auto opacity-100 sm:opacity-0 sm:group-hover:opacity-100 transition-opacity"
                      onClick={() => {
                        if (confirm("Are you sure you want to delete this record? This action cannot be undone.")) {
                          deleteMutation.mutate(analysis.id);
                        }
                      }}
                      disabled={deleteMutation.isPending}
                    >
                      {deleteMutation.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Trash2 className="h-4 w-4" />}
                      <span className="sm:hidden ml-2">Delete</span>
                    </Button>
                    <Link to={`/analyze`} className="w-full sm:w-auto text-center sm:text-right">
                       <Button variant="outline" size="sm" className="w-full">View Details <ArrowRight className="ml-2 h-4 w-4" /></Button>
                    </Link>
                  </div>
                </div>
                );
              })
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
