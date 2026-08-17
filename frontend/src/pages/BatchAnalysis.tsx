import React, { useState, useCallback } from "react";
import { appConfig } from "../config/env";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { UploadCloud, CheckCircle, Loader2 } from "lucide-react";

export function BatchAnalysis() {
  const [files, setFiles] = useState<File[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [batchResult, setBatchResult] = useState<any>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setFiles(Array.from(e.target.files));
      setBatchResult(null);
    }
  };

  const handleUpload = async () => {
    if (files.length === 0) return;
    
    setIsUploading(true);
    try {
      const formData = new FormData();
      files.forEach((file) => formData.append("files", file));

      const res = await fetch(`${appConfig.apiBaseUrl}/api/v1/batch`, {
        method: "POST",
        headers: { Authorization: `Bearer ${localStorage.getItem("token")}` },
        body: formData,
      });
      
      if (!res.ok) throw new Error("Batch upload failed");
      
      const data = await res.json();
      setBatchResult(data);
    } catch (err) {
      console.error(err);
      alert("Failed to submit batch.");
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Batch Analysis</h1>
        <p className="text-muted-foreground mt-2">Submit multiple Chest X-Rays for asynchronous batch processing.</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Upload Batch</CardTitle>
          <CardDescription>Select up to 50 DICOM/JPEG/PNG files.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="border-2 border-dashed border-gray-300 rounded-lg p-10 flex flex-col items-center justify-center bg-gray-50/50">
            <UploadCloud className="mx-auto h-12 w-12 text-gray-400" />
            <div className="mt-4 flex text-sm leading-6 text-gray-600">
              <label className="relative cursor-pointer rounded-md bg-white font-semibold text-primary focus-within:outline-none focus-within:ring-2 focus-within:ring-primary focus-within:ring-offset-2 hover:text-primary/80">
                <span>Select multiple files</span>
                <input type="file" multiple className="sr-only" onChange={handleFileChange} />
              </label>
            </div>
            {files.length > 0 && (
              <p className="mt-2 text-sm font-medium text-emerald-600">
                {files.length} files selected ready for batch upload.
              </p>
            )}
          </div>

          <Button 
            className="w-full" 
            onClick={handleUpload} 
            disabled={files.length === 0 || isUploading}
          >
            {isUploading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            {isUploading ? "Submitting..." : "Submit Batch"}
          </Button>
          
          {batchResult && (
            <div className="mt-6 p-4 bg-emerald-50 rounded-lg border border-emerald-200">
              <div className="flex items-center gap-2 text-emerald-800 font-semibold mb-2">
                <CheckCircle className="w-5 h-5" />
                Batch Submitted Successfully
              </div>
              <p className="text-sm text-emerald-700">Batch ID: {batchResult.batch_id}</p>
              <p className="text-sm text-emerald-700">Total Images: {batchResult.total_images}</p>
              <p className="text-xs text-emerald-600 mt-2">{batchResult.message}</p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
