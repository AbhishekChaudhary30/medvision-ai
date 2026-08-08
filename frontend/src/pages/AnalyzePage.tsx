import React, { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { uploadAnalysis, explainAnalysis, AnalysisResponse } from "../services/api";
import { Button } from "../components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../components/ui/card";
import { UploadCloud, AlertCircle, FileText, Loader2 } from "lucide-react";
import { cn } from "../lib/utils";

export function AnalyzePage() {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [result, setResult] = useState<AnalysisResponse | null>(null);
  const queryClient = useQueryClient();

  const uploadMutation = useMutation({
    mutationFn: uploadAnalysis,
    onSuccess: (data) => {
      setResult(data);
      queryClient.invalidateQueries({ queryKey: ["analyses"] });
    },
  });

  const explainMutation = useMutation({
    mutationFn: (id: string) => explainAnalysis(id),
    onSuccess: (data) => {
      setResult(data);
    },
  });

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selected = e.target.files[0];
      setFile(selected);
      setPreview(URL.createObjectURL(selected));
      setResult(null);
    }
  };

  const handleUpload = () => {
    if (file) {
      uploadMutation.mutate(file);
    }
  };

  const handleExplain = () => {
    if (result) {
      explainMutation.mutate(result.id);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "HIGH_CONFIDENCE": return "text-emerald-600 bg-emerald-50 border-emerald-200";
      case "LOW_CONFIDENCE": return "text-amber-600 bg-amber-50 border-amber-200";
      case "UNCERTAIN": return "text-rose-600 bg-rose-50 border-rose-200";
      default: return "text-slate-600 bg-slate-50 border-slate-200";
    }
  };

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Analysis Workspace</h1>
        <p className="text-muted-foreground mt-2">Upload Chest X-Ray images for deep learning inference.</p>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Image Upload</CardTitle>
            <CardDescription>Select a JPEG or PNG file (Max 10MB)</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-10 flex flex-col items-center justify-center bg-gray-50/50">
              {preview ? (
                <div className="relative w-full aspect-square max-h-[300px] rounded overflow-hidden">
                  <img src={preview} alt="Preview" className="object-cover w-full h-full" />
                </div>
              ) : (
                <div className="text-center">
                  <UploadCloud className="mx-auto h-12 w-12 text-gray-400" />
                  <div className="mt-4 flex text-sm leading-6 text-gray-600">
                    <label
                      htmlFor="file-upload"
                      className="relative cursor-pointer rounded-md bg-white font-semibold text-primary focus-within:outline-none focus-within:ring-2 focus-within:ring-primary focus-within:ring-offset-2 hover:text-primary/80"
                    >
                      <span>Upload a file</span>
                      <input id="file-upload" name="file-upload" type="file" className="sr-only" accept="image/jpeg, image/png" onChange={handleFileChange} />
                    </label>
                    <p className="pl-1">or drag and drop</p>
                  </div>
                </div>
              )}
            </div>

            <Button 
              className="w-full" 
              onClick={handleUpload} 
              disabled={!file || uploadMutation.isPending}
            >
              {uploadMutation.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              {uploadMutation.isPending ? "Analyzing..." : "Run Prediction"}
            </Button>
            
            {uploadMutation.isError && (
              <div className="p-3 text-sm text-destructive bg-destructive/10 rounded-md flex items-center gap-2">
                <AlertCircle className="h-4 w-4" />
                <span>Failed to process image.</span>
              </div>
            )}
          </CardContent>
        </Card>

        {result && (
          <Card>
            <CardHeader className="pb-4">
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>Analysis Results</CardTitle>
                  <CardDescription className="mt-1">ID: {result.id}</CardDescription>
                </div>
                <div className={cn("px-3 py-1 rounded-full text-xs font-semibold border", getStatusColor(result.uncertainty_status))}>
                  {result.uncertainty_status.replace("_", " ")}
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-6">
              
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-secondary/50 p-4 rounded-lg">
                  <p className="text-sm font-medium text-muted-foreground uppercase tracking-wider mb-1">Prediction</p>
                  <p className="text-3xl font-bold text-primary">{result.predicted_class}</p>
                </div>
                <div className="bg-secondary/50 p-4 rounded-lg">
                  <p className="text-sm font-medium text-muted-foreground uppercase tracking-wider mb-1">Confidence</p>
                  <p className="text-3xl font-bold text-primary">{(result.confidence * 100).toFixed(1)}%</p>
                </div>
              </div>

              <div className="space-y-3">
                <h4 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground">Class Probabilities</h4>
                
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span>NORMAL</span>
                    <span className="font-medium">{(result.probability_normal * 100).toFixed(1)}%</span>
                  </div>
                  <div className="w-full bg-secondary rounded-full h-2">
                    <div className="bg-blue-500 h-2 rounded-full" style={{ width: `${result.probability_normal * 100}%` }}></div>
                  </div>
                </div>
                
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span>PNEUMONIA</span>
                    <span className="font-medium">{(result.probability_pneumonia * 100).toFixed(1)}%</span>
                  </div>
                  <div className="w-full bg-secondary rounded-full h-2">
                    <div className="bg-red-500 h-2 rounded-full" style={{ width: `${result.probability_pneumonia * 100}%` }}></div>
                  </div>
                </div>
              </div>

              <div className="pt-4 border-t space-y-4">
                <h4 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground">Explainability</h4>
                
                {result.explanation_method ? (
                  <div className="p-3 bg-emerald-50 text-emerald-700 rounded border border-emerald-200 text-sm flex items-start gap-2">
                    <FileText className="h-4 w-4 mt-0.5" />
                    <div>
                      <p className="font-medium">Grad-CAM Generated</p>
                      <p className="text-emerald-600 mt-1 opacity-90">View the heatmap in the History tab to see localized regions.</p>
                    </div>
                  </div>
                ) : (
                  <Button 
                    variant="outline" 
                    className="w-full"
                    onClick={handleExplain}
                    disabled={explainMutation.isPending}
                  >
                    {explainMutation.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                    Generate Grad-CAM Heatmap
                  </Button>
                )}
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}
