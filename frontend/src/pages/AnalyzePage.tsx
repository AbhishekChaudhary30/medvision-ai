import React, { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { uploadAnalysis, explainAnalysis, AnalysisResponse } from "../services/api";
import { Button } from "../components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardFooter } from "../components/ui/card";
import { UploadCloud, AlertCircle, FileText, Loader2, Scan, User, ZoomIn, ZoomOut, Contrast, Sun, RotateCcw, Download, ArrowRight, Activity } from "lucide-react";
import { cn } from "../lib/utils";

export function AnalyzePage() {
  const [step, setStep] = useState(1);
  
  // Patient Context
  const [age, setAge] = useState<string>("");
  const [gender, setGender] = useState<string>("Male");
  const [notes, setNotes] = useState<string>("");

  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [result, setResult] = useState<AnalysisResponse | null>(null);
  
  // PACS Viewer State
  const [zoom, setZoom] = useState(1);
  const [contrast, setContrast] = useState(100);
  const [brightness, setBrightness] = useState(100);
  const [invert, setInvert] = useState(false);
  
  const queryClient = useQueryClient();

  const uploadMutation = useMutation({
    mutationFn: (f: File) => uploadAnalysis(
      f, 
      "chest-xray", 
      age ? parseInt(age) : undefined, 
      gender, 
      notes
    ),
    onSuccess: (data) => {
      setResult(data);
      setStep(3);
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

  const resetViewer = () => {
    setZoom(1);
    setContrast(100);
    setBrightness(100);
    setInvert(false);
  };

  const resetAll = () => {
    setStep(1);
    setAge("");
    setGender("Male");
    setNotes("");
    setFile(null);
    setPreview(null);
    setResult(null);
    resetViewer();
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "HIGH_CONFIDENCE": return "text-emerald-600 bg-emerald-50 border-emerald-200 ring-emerald-200";
      case "LOW_CONFIDENCE": return "text-amber-600 bg-amber-50 border-amber-200 ring-amber-200";
      case "UNCERTAIN": return "text-rose-600 bg-rose-50 border-rose-200 ring-rose-200";
      default: return "text-indigo-600 bg-indigo-50 border-indigo-200 ring-indigo-200";
    }
  };

  return (
    <div className="max-w-6xl mx-auto space-y-12 pb-16 relative">
      <div className="absolute top-0 right-0 -z-10 w-96 h-96 bg-blue-400/10 rounded-full blur-3xl"></div>

      <div className="flex flex-col md:flex-row justify-between md:items-end gap-6 animate-fade-in-up">
        <div className="space-y-3">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-100 text-blue-700 font-semibold text-xs tracking-wide">
            <Scan className="w-4 h-4" /> MEDICAL IMAGING
          </div>
          <h1 className="text-4xl md:text-5xl font-extrabold tracking-tight text-slate-900">
            Chest X-Ray <span className="text-blue-600">Analysis Tool</span>
          </h1>
          <p className="text-lg text-slate-600 max-w-2xl leading-relaxed">
            This tool analyzes Chest X-Rays to detect abnormalities such as Pneumonia. Provide patient details and upload a scan below for automated analysis.
          </p>
        </div>
        <Button variant="outline" onClick={resetAll} className="shadow-sm hover:shadow transition-shadow">Reset Workspace</Button>
      </div>

      <div className="relative px-4 py-8 mb-4 animate-fade-in-up" style={{ animationDelay: '0.1s' }}>
        <div className="absolute left-4 right-4 top-1/2 transform -translate-y-1/2 h-1.5 bg-slate-200/50 -z-10 rounded-full overflow-hidden">
          <div className="h-full bg-blue-500 transition-all duration-700 ease-out" style={{ width: `${((step - 1) / 2) * 100}%` }}></div>
        </div>
        
        <div className="flex items-center justify-between">
          {[1, 2, 3].map(s => (
            <div key={s} className={cn(
              "w-12 h-12 rounded-full flex items-center justify-center font-bold border-4 transition-all duration-500 z-10", 
              step >= s 
                ? "bg-blue-600 border-white text-white shadow-lg scale-110" 
                : "bg-white border-slate-100 text-slate-400"
            )}>
              {step > s ? <span className="text-xl">✓</span> : s}
            </div>
          ))}
        </div>
      </div>

      <div className="min-h-[400px]">
        {step === 1 && (
          <div className="space-y-6 animate-fade-in-up">
            <div className="text-center space-y-2 mb-8">
              <h2 className="text-2xl font-bold text-slate-800">Patient Details</h2>
              <p className="text-slate-500">Provide demographic and clinical information</p>
            </div>
            
            <Card className="glass overflow-hidden border-0">
              <CardContent className="p-8 space-y-8">
                <div className="grid md:grid-cols-2 gap-8">
                  <div className="space-y-3">
                    <label className="text-xs font-bold uppercase tracking-widest text-slate-500">Age (Years)</label>
                    <div className="relative">
                      <input 
                        type="number" 
                        value={age} 
                        onChange={e => setAge(e.target.value)} 
                        placeholder="e.g. 45"
                        className="flex h-14 w-full rounded-xl border-2 border-slate-100 bg-white/50 px-4 py-2 text-lg font-medium transition-colors placeholder:text-slate-300 focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 outline-none"
                      />
                    </div>
                  </div>
                  <div className="space-y-3">
                    <label className="text-xs font-bold uppercase tracking-widest text-slate-500">Gender</label>
                    <select 
                      value={gender} 
                      onChange={e => setGender(e.target.value)}
                      className="flex h-14 w-full rounded-xl border-2 border-slate-100 bg-white/50 px-4 py-2 text-lg font-medium transition-colors focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 outline-none appearance-none"
                    >
                      <option value="Male">Male</option>
                      <option value="Female">Female</option>
                      <option value="Other">Other</option>
                    </select>
                  </div>
                </div>
                <div className="space-y-3">
                  <label className="text-xs font-bold uppercase tracking-widest text-slate-500 flex items-center justify-between">
                    <span>Clinical Notes & History</span>
                    <span className="text-slate-400 font-normal normal-case">Optional</span>
                  </label>
                  <textarea 
                    value={notes} 
                    onChange={e => setNotes(e.target.value)} 
                    placeholder="Enter any presenting symptoms or medical history..."
                    className="flex min-h-[160px] w-full rounded-xl border-2 border-slate-100 bg-white/50 px-4 py-3 text-base transition-colors placeholder:text-slate-300 focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 outline-none resize-y"
                  />
                </div>
              </CardContent>
              <CardFooter className="flex justify-end bg-slate-50/80 p-6 border-t border-slate-100">
                <Button size="lg" className="h-12 px-8 bg-blue-600 hover:bg-blue-700 text-white transition-all hover:scale-105" onClick={() => setStep(2)}>
                  Next: Upload Media <ArrowRight className="ml-2 h-5 w-5" />
                </Button>
              </CardFooter>
            </Card>
          </div>
        )}

        {step === 2 && (
          <div className="space-y-6 animate-fade-in-up">
            <div className="text-center space-y-2 mb-8">
              <h2 className="text-2xl font-bold text-slate-800">Upload Clinical Image</h2>
              <p className="text-slate-500">Upload a Chest X-Ray image for analysis</p>
            </div>

            <Card className="glass overflow-hidden border-0">
              <CardContent className="p-10">
                <div className={cn(
                  "relative border-3 border-dashed rounded-3xl p-12 flex flex-col items-center justify-center transition-all duration-300 min-h-[400px]",
                  preview ? "border-transparent bg-slate-900/5" : "border-slate-300 bg-white/50 hover:bg-white hover:border-blue-400"
                )}>
                  {preview ? (
                    <div className="relative w-full h-full max-h-[500px] rounded-2xl overflow-hidden shadow-2xl ring-1 ring-black/5 flex items-center justify-center bg-black/5">
                      <img src={preview} alt="Preview" className="object-contain max-w-full max-h-[500px]" />
                      <div className="absolute inset-0 bg-gradient-to-t from-black/50 via-transparent to-transparent opacity-0 hover:opacity-100 transition-opacity flex items-end justify-center pb-6">
                        <label
                          htmlFor="file-upload-replace"
                          className="cursor-pointer bg-white/20 backdrop-blur-md hover:bg-white/30 text-white px-6 py-2 rounded-full font-medium transition-colors"
                        >
                          Replace Image
                          <input id="file-upload-replace" type="file" className="sr-only" accept="image/jpeg, image/png" onChange={handleFileChange} />
                        </label>
                      </div>
                    </div>
                  ) : (
                    <div className="text-center py-10 w-full">
                      <div className="mx-auto h-24 w-24 rounded-full bg-blue-50 flex items-center justify-center mb-8 shadow-inner">
                        <UploadCloud className="h-12 w-12 text-blue-500" />
                      </div>
                      <h3 className="text-xl font-bold text-slate-700 mb-2">Drag & drop your scan here</h3>
                      <p className="text-slate-500 mb-8">Supported formats: JPEG/PNG up to 10MB</p>
                      
                      <label
                        htmlFor="file-upload"
                        className="cursor-pointer inline-flex items-center justify-center h-14 px-8 rounded-full font-bold text-white bg-slate-900 hover:bg-slate-800 shadow-lg transition-all hover:scale-105"
                      >
                        <UploadCloud className="w-5 h-5 mr-2" /> Browse Files
                        <input id="file-upload" type="file" className="sr-only" accept="image/jpeg, image/png" onChange={handleFileChange} />
                      </label>
                    </div>
                  )}
                </div>

                <div className="flex justify-between items-center mt-10">
                  <Button variant="ghost" size="lg" onClick={() => setStep(1)} className="text-slate-500 hover:text-slate-800">Back</Button>
                  <Button 
                    size="lg"
                    className={cn("h-14 px-10 text-lg shadow-lg transition-all", file && !uploadMutation.isPending ? "bg-blue-600 hover:bg-blue-700 text-white hover:scale-105" : "bg-slate-200 text-slate-400")} 
                    onClick={handleUpload} 
                    disabled={!file || uploadMutation.isPending}
                  >
                    {uploadMutation.isPending ? (
                      <>
                        <Loader2 className="mr-3 h-6 w-6 animate-spin" />
                        Analyzing...
                      </>
                    ) : (
                      <>
                        <Scan className="mr-2 h-5 w-5" /> Analyze Image
                      </>
                    )}
                  </Button>
                </div>
                
                {uploadMutation.isError && (
                  <div className="mt-6 p-5 text-sm text-red-700 bg-red-50 border border-red-200 rounded-xl flex items-start gap-4 animate-fade-in-up">
                    <AlertCircle className="h-6 w-6 flex-shrink-0 text-red-500 mt-0.5" />
                    <div>
                      <h4 className="font-bold text-red-800 text-base">Processing Failed</h4>
                      <p className="mt-1 opacity-90">{uploadMutation.error instanceof Error ? uploadMutation.error.message : "Please check your network connection and ensure the image format is supported."}</p>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        )}

        {step === 3 && result && (
          <div className="space-y-8 animate-fade-in-up">
            <div className="glass rounded-2xl p-6 flex flex-col md:flex-row md:items-center justify-between gap-6 relative overflow-hidden">
              <div className="flex items-center gap-5 z-10">
                <div className="p-4 bg-blue-600 rounded-2xl shadow-md">
                  <User className="h-8 w-8 text-white" />
                </div>
                <div>
                  <h3 className="text-sm font-bold text-slate-400 uppercase tracking-widest mb-1">Patient Profile</h3>
                  <p className="text-xl font-bold text-slate-800">
                    {result.patient_age ? `${result.patient_age} Years` : "Age N/A"} <span className="text-slate-300 mx-2">|</span> {result.patient_gender || "Other"}
                  </p>
                </div>
              </div>
              
              <div className="flex items-center gap-4 z-10">
                <div className="text-right">
                  <p className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-1">Status</p>
                  <div className={cn("px-4 py-1.5 rounded-full text-xs font-black tracking-wide uppercase shadow-sm ring-1 ring-inset", getStatusColor(result.uncertainty_status || ""))}>
                    {(result.uncertainty_status || "ANALYZED").replace("_", " ")}
                  </div>
                </div>
                <div className="h-10 w-px bg-slate-200 hidden md:block"></div>
                <div className="text-right hidden md:block">
                  <p className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-1">Analysis ID</p>
                  <p className="font-mono text-sm text-slate-600">{result.id.substring(0,8)}</p>
                </div>
              </div>
            </div>

            <div className="grid lg:grid-cols-12 gap-8">
              <div className="lg:col-span-7 space-y-4">
                <Card className="glass border-0 shadow-xl overflow-hidden rounded-3xl flex flex-col h-full">
                  <div className="bg-slate-900 px-6 py-4 flex items-center justify-between">
                    <h4 className="text-xs font-bold uppercase tracking-widest text-slate-400 flex items-center gap-2">
                      <Scan className="w-4 h-4" /> PACS Image Viewer
                    </h4>
                    <div className="flex gap-2">
                      <Button variant="ghost" size="icon" className="text-slate-400 hover:text-white hover:bg-slate-800 h-8 w-8 rounded-full" onClick={() => setZoom(z => Math.min(z + 0.5, 3))}><ZoomIn className="h-4 w-4" /></Button>
                      <Button variant="ghost" size="icon" className="text-slate-400 hover:text-white hover:bg-slate-800 h-8 w-8 rounded-full" onClick={() => setZoom(z => Math.max(z - 0.5, 1))}><ZoomOut className="h-4 w-4" /></Button>
                      <Button variant="ghost" size="icon" className="text-slate-400 hover:text-white hover:bg-slate-800 h-8 w-8 rounded-full" onClick={() => setContrast(c => c === 100 ? 150 : 100)}><Contrast className="h-4 w-4" /></Button>
                      <Button variant="ghost" size="icon" className="text-slate-400 hover:text-white hover:bg-slate-800 h-8 w-8 rounded-full" onClick={() => setBrightness(b => b === 100 ? 120 : 100)}><Sun className="h-4 w-4" /></Button>
                      <Button variant="ghost" size="icon" className="text-slate-400 hover:text-white hover:bg-slate-800 h-8 w-8 rounded-full" onClick={() => setInvert(i => !i)}><RotateCcw className="h-4 w-4" /></Button>
                    </div>
                  </div>
                  <div className="relative flex-grow bg-black flex items-center justify-center min-h-[500px] overflow-hidden">
                    {preview && (
                      <img 
                        src={preview} 
                        alt="Scan" 
                        style={{ 
                          transform: `scale(${zoom})`,
                          filter: `contrast(${contrast}%) brightness(${brightness}%) invert(${invert ? 100 : 0}%)`,
                          transition: 'transform 0.3s cubic-bezier(0.4, 0, 0.2, 1), filter 0.3s'
                        }}
                        className="object-contain w-full h-full cursor-move" 
                      />
                    )}
                  </div>
                </Card>
              </div>

              <div className="lg:col-span-5 space-y-6">
                <Card className="glass border-0 overflow-hidden relative group bg-blue-600">
                  <CardContent className="p-8 relative z-10 text-white">
                    <p className="text-sm font-bold uppercase tracking-widest text-blue-200 mb-2">Detection Result</p>
                    <h2 className="text-4xl font-black mb-6 leading-tight">{result.predicted_class}</h2>
                    
                    <div className="bg-white/10 rounded-xl p-4 backdrop-blur-sm border border-white/20">
                      <div className="flex justify-between items-end mb-2">
                        <span className="text-sm font-medium text-blue-100">Certainty Score</span>
                        <span className="text-2xl font-bold">{(result.confidence * 100).toFixed(1)}%</span>
                      </div>
                      <div className="h-2 w-full bg-black/20 rounded-full overflow-hidden">
                        <div className="h-full bg-white rounded-full" style={{ width: `${result.confidence * 100}%` }}></div>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {result.clinical_suggestions && (
                  <Card className="border border-blue-100 shadow-sm bg-white">
                    <CardHeader className="pb-2">
                      <CardTitle className="text-base flex items-center gap-2 text-blue-900">
                        <Activity className="h-5 w-5 text-blue-500" /> Assessment
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <p className="text-slate-700 leading-relaxed text-sm">
                        {result.clinical_suggestions}
                      </p>
                    </CardContent>
                  </Card>
                )}

                <Card className="border border-slate-200 shadow-sm bg-white">
                  <CardHeader className="pb-3 border-b border-slate-100">
                    <CardTitle className="text-sm font-bold uppercase tracking-widest text-slate-500">Visual Scan Report</CardTitle>
                  </CardHeader>
                  <CardContent className="pt-5 space-y-4">
                    {result.explanation_method ? (
                      <div className="p-4 bg-emerald-50 text-emerald-800 rounded-xl border border-emerald-200 text-sm flex items-start gap-3">
                        <FileText className="h-5 w-5 mt-0.5 text-emerald-600" />
                        <div>
                          <p className="font-bold">Scan Highlight Ready</p>
                          <p className="mt-1 text-emerald-700 opacity-90 leading-relaxed">Visual highlights of the region of interest are available in the PDF Report.</p>
                        </div>
                      </div>
                    ) : (
                      <Button 
                        variant="outline" 
                        className="w-full h-12 border-slate-300 hover:bg-slate-50 font-semibold text-slate-700 shadow-sm"
                        onClick={handleExplain}
                        disabled={explainMutation.isPending}
                      >
                        {explainMutation.isPending ? (
                          <Loader2 className="mr-2 h-4 w-4 animate-spin text-blue-600" />
                        ) : (
                          <Scan className="mr-2 h-4 w-4 text-blue-600" />
                        )}
                        Generate Visual Highlight
                      </Button>
                    )}

                    <Button 
                      className="w-full h-12 font-bold shadow-sm transition-shadow bg-slate-900 text-white hover:bg-slate-800"
                      onClick={() => window.print()}
                    >
                      <Download className="mr-2 h-5 w-5" /> Download Full Report
                    </Button>
                  </CardContent>
                </Card>
                
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
