import React, { useState, useMemo } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { uploadAnalysis, explainAnalysis, AnalysisResponse } from "../services/api";
import { Button } from "../components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from "../components/ui/card";
import { UploadCloud, AlertCircle, FileText, Loader2, Stethoscope, Brain, Scan, Activity, Microscope, ArrowRight, User, ZoomIn, ZoomOut, Contrast, Sun, RotateCcw, Download, Sparkles } from "lucide-react";
import { cn } from "../lib/utils";

const CATEGORIES = [
  { id: "X-Ray", label: "Radiography (X-Ray)", icon: Scan },
  { id: "CT Scan", label: "Computed Tomography (CT)", icon: Activity },
  { id: "MRI", label: "Magnetic Resonance (MRI)", icon: Brain },
  { id: "Ultrasound", label: "Ultrasound (Sonography)", icon: Stethoscope },
  { id: "Other", label: "Pathology & Other", icon: Microscope },
];

const MODALITIES = [
  // X-Ray
  { id: "chest-xray", label: "Chest X-Ray", category: "X-Ray", desc: "Pneumonia / Lungs" },
  { id: "bone-xray", label: "Bone X-Ray", category: "X-Ray", desc: "Fracture Detection" },
  { id: "dental-xray", label: "Dental X-Ray", category: "X-Ray", desc: "Caries / Decay" },
  { id: "mammography", label: "Mammography", category: "X-Ray", desc: "Breast Cancer (BI-RADS)" },
  // CT
  { id: "head-ct", label: "Head CT", category: "CT Scan", desc: "Hemorrhage / Stroke" },
  { id: "chest-ct", label: "Chest CT", category: "CT Scan", desc: "Nodules / Cancer" },
  { id: "abdomen-ct", label: "Abdomen CT", category: "CT Scan", desc: "Appendicitis / Organs" },
  // MRI
  { id: "brain-mri", label: "Brain MRI", category: "MRI", desc: "Tumor / Parenchyma" },
  { id: "spine-mri", label: "Spine MRI", category: "MRI", desc: "Herniated Disc" },
  { id: "knee-mri", label: "Knee MRI", category: "MRI", desc: "ACL / Meniscus Tear" },
  // Ultrasound
  { id: "fetal-ultrasound", label: "Fetal Ultrasound", category: "Ultrasound", desc: "Obstetric Anomalies" },
  { id: "echocardiogram", label: "Echocardiogram", category: "Ultrasound", desc: "Heart Failure / EF" },
  { id: "abdominal-ultrasound", label: "Abdominal US", category: "Ultrasound", desc: "Gallstones / Liver" },
  // Other
  { id: "skin-lesion", label: "Skin Lesion", category: "Other", desc: "Melanoma (Dermoscopy)" },
  { id: "retinal-fundus", label: "Retinal Fundus", category: "Other", desc: "Diabetic Retinopathy" },
  { id: "histopathology", label: "Histopathology", category: "Other", desc: "Invasive Carcinoma" },
  { id: "colonoscopy", label: "Colonoscopy", category: "Other", desc: "Polyp Detection" },
];

export function AnalyzePage() {
  const [step, setStep] = useState(1);
  const [category, setCategory] = useState<string>("X-Ray");
  const [modality, setModality] = useState<string>("chest-xray");
  
  // Patient Context
  const [age, setAge] = useState<string>("");
  const [gender, setGender] = useState<string>("M");
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

  const filteredModalities = useMemo(() => MODALITIES.filter(m => m.category === category), [category]);

  const uploadMutation = useMutation({
    mutationFn: (f: File) => uploadAnalysis(
      f, 
      modality, 
      age ? parseInt(age) : undefined, 
      gender, 
      notes
    ),
    onSuccess: (data) => {
      setResult(data);
      setStep(4);
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
    setCategory("X-Ray");
    setModality("chest-xray");
    setAge("");
    setGender("M");
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
      {/* Abstract Background Element */}
      <div className="absolute top-0 right-0 -z-10 w-96 h-96 bg-blue-400/10 rounded-full blur-3xl animate-pulse-slow"></div>
      <div className="absolute bottom-0 left-0 -z-10 w-96 h-96 bg-indigo-400/10 rounded-full blur-3xl animate-pulse-slow" style={{ animationDelay: '1.5s' }}></div>

      <div className="flex flex-col md:flex-row justify-between md:items-end gap-6 animate-fade-in-up">
        <div className="space-y-3">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-100 text-blue-700 font-semibold text-xs tracking-wide">
            <Sparkles className="w-4 h-4" /> ENTERPRISE AI SUITE
          </div>
          <h1 className="text-4xl md:text-5xl font-extrabold tracking-tight text-slate-900">
            Clinical <span className="text-gradient">Diagnostic Wizard</span>
          </h1>
          <p className="text-lg text-slate-600 max-w-2xl leading-relaxed">
            A state-of-the-art, multi-modal diagnostic pipeline. Step 1: Select imaging type. Step 2: Provide patient context. Step 3: Run AI analysis.
          </p>
        </div>
        <Button variant="outline" onClick={resetAll} className="shadow-sm hover:shadow transition-shadow">Reset Workspace</Button>
      </div>

      {/* Progress Bar */}
      <div className="relative px-4 py-8 mb-4 animate-fade-in-up" style={{ animationDelay: '0.1s' }}>
        <div className="absolute left-4 right-4 top-1/2 transform -translate-y-1/2 h-1.5 bg-slate-200/50 -z-10 rounded-full overflow-hidden">
          <div className="h-full bg-gradient-to-r from-blue-500 to-indigo-500 transition-all duration-700 ease-out" style={{ width: `${((step - 1) / 3) * 100}%` }}></div>
        </div>
        
        <div className="flex items-center justify-between">
          {[1, 2, 3, 4].map(s => (
            <div key={s} className={cn(
              "w-12 h-12 rounded-full flex items-center justify-center font-bold border-4 transition-all duration-500 z-10", 
              step >= s 
                ? "bg-gradient-to-br from-blue-600 to-indigo-600 border-white text-white shadow-[0_0_20px_rgba(59,130,246,0.5)] scale-110" 
                : "bg-white border-slate-100 text-slate-400"
            )}>
              {step > s ? <span className="text-xl">✓</span> : s}
            </div>
          ))}
        </div>
      </div>

      <div className="min-h-[400px]">
        {step === 1 && (
          <div className="space-y-8 animate-fade-in-up">
            <div className="text-center space-y-2 mb-8">
              <h2 className="text-2xl font-bold text-slate-800">Select Imaging Category</h2>
              <p className="text-slate-500">Choose the primary modality of your clinical scan</p>
            </div>
            
            <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
              {CATEGORIES.map(c => {
                const Icon = c.icon;
                const isActive = category === c.id;
                return (
                  <div 
                    key={c.id}
                    onClick={() => setCategory(c.id)}
                    className={cn(
                      "cursor-pointer p-6 rounded-2xl border-2 transition-all duration-300 text-center flex flex-col items-center justify-center gap-3", 
                      isActive 
                        ? "border-blue-500 bg-blue-50/50 shadow-lg shadow-blue-500/10 scale-105" 
                        : "border-slate-100 bg-white hover:border-blue-200 hover:shadow-md hover:-translate-y-1"
                    )}
                  >
                    <div className={cn("p-4 rounded-full transition-colors", isActive ? "bg-blue-100 text-blue-600" : "bg-slate-50 text-slate-400")}>
                      <Icon className="h-8 w-8" />
                    </div>
                    <span className={cn("font-bold text-sm tracking-wide", isActive ? "text-blue-900" : "text-slate-600")}>{c.label}</span>
                  </div>
                );
              })}
            </div>

            <div className="pt-8 mt-8 border-t border-slate-100">
              <h3 className="text-lg font-semibold text-slate-800 mb-6 flex items-center gap-2">
                <Scan className="w-5 h-5 text-blue-500" /> Specific Modality
              </h3>
              <div className="grid sm:grid-cols-2 md:grid-cols-3 gap-5">
                {filteredModalities.map(m => (
                  <Card 
                    key={m.id} 
                    onClick={() => setModality(m.id)}
                    className={cn(
                      "cursor-pointer transition-all duration-300 border-2 overflow-hidden group", 
                      modality === m.id 
                        ? "border-indigo-500 shadow-md shadow-indigo-500/10" 
                        : "border-transparent hover:border-slate-200 hover:shadow-lg bg-white/80"
                    )}
                  >
                    <div className={cn("h-1 w-full transition-colors", modality === m.id ? "bg-indigo-500" : "bg-slate-100 group-hover:bg-slate-200")} />
                    <CardContent className="p-5">
                      <h3 className={cn("font-bold text-lg mb-1", modality === m.id ? "text-indigo-900" : "text-slate-700")}>{m.label}</h3>
                      <p className="text-sm text-slate-500">{m.desc}</p>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>

            <div className="flex justify-end pt-6">
              <Button size="lg" className="h-14 px-8 text-lg shadow-xl shadow-blue-500/20 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 transition-all hover:scale-105" onClick={() => setStep(2)}>
                Continue to Patient Details <ArrowRight className="ml-2 h-5 w-5" />
              </Button>
            </div>
          </div>
        )}

        {step === 2 && (
          <div className="space-y-6 animate-fade-in-up">
            <div className="text-center space-y-2 mb-8">
              <h2 className="text-2xl font-bold text-slate-800">Patient Context</h2>
              <p className="text-slate-500">Provide demographic and clinical information for accurate AI synthesis</p>
            </div>
            
            <Card className="glass overflow-hidden border-0">
              <div className="h-1 w-full bg-gradient-to-r from-blue-500 to-indigo-500" />
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
                      <option value="M">Male</option>
                      <option value="F">Female</option>
                      <option value="O">Other</option>
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
                    placeholder="Enter any presenting symptoms, medical history, or prior observations. The Expert AI will integrate this into the final recommendation..."
                    className="flex min-h-[160px] w-full rounded-xl border-2 border-slate-100 bg-white/50 px-4 py-3 text-base transition-colors placeholder:text-slate-300 focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 outline-none resize-y"
                  />
                </div>
              </CardContent>
              <CardFooter className="flex justify-between bg-slate-50/80 p-6 border-t border-slate-100">
                <Button variant="ghost" size="lg" onClick={() => setStep(1)} className="text-slate-500 hover:text-slate-800">Back</Button>
                <Button size="lg" className="h-12 px-8 shadow-lg shadow-indigo-500/20 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 transition-all hover:scale-105" onClick={() => setStep(3)}>
                  Next: Upload Media <ArrowRight className="ml-2 h-5 w-5" />
                </Button>
              </CardFooter>
            </Card>
          </div>
        )}

        {step === 3 && (
          <div className="space-y-6 animate-fade-in-up">
            <div className="text-center space-y-2 mb-8">
              <h2 className="text-2xl font-bold text-slate-800">Upload Clinical Image</h2>
              <p className="text-slate-500">Upload {MODALITIES.find(m => m.id === modality)?.label} for AI synthesis</p>
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
                        <UploadCloud className="h-12 w-12 text-blue-500 animate-pulse-slow" />
                      </div>
                      <h3 className="text-xl font-bold text-slate-700 mb-2">Drag & drop your scan here</h3>
                      <p className="text-slate-500 mb-8">DICOM (converted to JPEG/PNG) up to 10MB</p>
                      
                      <label
                        htmlFor="file-upload"
                        className="cursor-pointer inline-flex items-center justify-center h-14 px-8 rounded-full font-bold text-white bg-slate-900 hover:bg-slate-800 shadow-xl transition-all hover:scale-105"
                      >
                        <Sparkles className="w-5 h-5 mr-2" /> Browse Files
                        <input id="file-upload" type="file" className="sr-only" accept="image/jpeg, image/png" onChange={handleFileChange} />
                      </label>
                    </div>
                  )}
                </div>

                <div className="flex justify-between items-center mt-10">
                  <Button variant="ghost" size="lg" onClick={() => setStep(2)} className="text-slate-500 hover:text-slate-800">Back</Button>
                  <Button 
                    size="lg"
                    className={cn("h-14 px-10 text-lg shadow-xl transition-all", file && !uploadMutation.isPending ? "bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 hover:scale-105 shadow-indigo-500/30" : "bg-slate-200 text-slate-400")} 
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
                        <Brain className="mr-2 h-5 w-5" /> Run AI Synthesizer
                      </>
                    )}
                  </Button>
                </div>
                
                {uploadMutation.isError && (
                  <div className="mt-6 p-5 text-sm text-red-700 bg-red-50 border border-red-200 rounded-xl flex items-start gap-4 animate-fade-in-up">
                    <AlertCircle className="h-6 w-6 flex-shrink-0 text-red-500 mt-0.5" />
                    <div>
                      <h4 className="font-bold text-red-800 text-base">Processing Failed</h4>
                      <p className="mt-1 opacity-90">{uploadMutation.error instanceof Error ? uploadMutation.error.message : "Please check your network connection and ensure the image format is supported (JPEG/PNG)."}</p>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        )}

        {step === 4 && result && (
          <div className="space-y-8 animate-fade-in-up">
            
            {/* Header Status Bar */}
            <div className="glass rounded-2xl p-6 flex flex-col md:flex-row md:items-center justify-between gap-6 relative overflow-hidden">
              <div className="absolute right-0 top-0 w-64 h-full bg-gradient-to-l from-white/50 to-transparent pointer-events-none"></div>
              <div className="flex items-center gap-5 z-10">
                <div className="p-4 bg-blue-600 rounded-2xl shadow-lg shadow-blue-600/30">
                  <User className="h-8 w-8 text-white" />
                </div>
                <div>
                  <h3 className="text-sm font-bold text-slate-400 uppercase tracking-widest mb-1">Patient Profile</h3>
                  <p className="text-xl font-bold text-slate-800">
                    {result.patient_age ? `${result.patient_age} Years` : "Age N/A"} <span className="text-slate-300 mx-2">|</span> {result.patient_gender === 'M' ? 'Male' : result.patient_gender === 'F' ? 'Female' : 'Other'}
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
              
              {/* PACS Viewer - Left Column */}
              <div className="lg:col-span-7 space-y-4">
                <Card className="glass border-0 shadow-2xl overflow-hidden rounded-3xl flex flex-col h-full">
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

              {/* Results - Right Column */}
              <div className="lg:col-span-5 space-y-6">
                
                {/* Primary Metric */}
                <Card className="glass border-0 overflow-hidden relative group">
                  <div className="absolute inset-0 bg-gradient-to-br from-blue-600 to-indigo-700 opacity-90 transition-opacity"></div>
                  <CardContent className="p-8 relative z-10 text-white">
                    <Sparkles className="absolute top-6 right-6 w-12 h-12 text-white/10" />
                    <p className="text-sm font-bold uppercase tracking-widest text-blue-200 mb-2">Detection Result</p>
                    <h2 className="text-4xl font-black mb-6 leading-tight">{result.predicted_class}</h2>
                    
                    <div className="bg-white/10 rounded-xl p-4 backdrop-blur-sm border border-white/20">
                      <div className="flex justify-between items-end mb-2">
                        <span className="text-sm font-medium text-blue-100">AI Confidence</span>
                        <span className="text-2xl font-bold">{(result.confidence * 100).toFixed(1)}%</span>
                      </div>
                      <div className="h-2 w-full bg-black/20 rounded-full overflow-hidden">
                        <div className="h-full bg-white rounded-full" style={{ width: `${result.confidence * 100}%` }}></div>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {/* Clinical Plan */}
                {result.clinical_suggestions && (
                  <Card className="border border-indigo-100 shadow-lg bg-white/80 backdrop-blur-sm">
                    <CardHeader className="pb-2">
                      <CardTitle className="text-base flex items-center gap-2 text-indigo-900">
                        <Activity className="h-5 w-5 text-indigo-500" /> Integrated Action Plan
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <p className="text-slate-700 leading-relaxed text-sm">
                        {result.clinical_suggestions}
                      </p>
                    </CardContent>
                  </Card>
                )}

                {/* Explainability Tools */}
                <Card className="border border-slate-200 shadow-md bg-white">
                  <CardHeader className="pb-3 border-b border-slate-100">
                    <CardTitle className="text-sm font-bold uppercase tracking-widest text-slate-500">Explainable AI (XAI)</CardTitle>
                  </CardHeader>
                  <CardContent className="pt-5 space-y-4">
                    {result.explanation_method ? (
                      <div className="p-4 bg-emerald-50 text-emerald-800 rounded-xl border border-emerald-200 text-sm flex items-start gap-3">
                        <FileText className="h-5 w-5 mt-0.5 text-emerald-600" />
                        <div>
                          <p className="font-bold">Grad-CAM Heatmap Ready</p>
                          <p className="mt-1 text-emerald-700 opacity-90 leading-relaxed">Visual highlights of the region of interest are available in the comprehensive PDF Report.</p>
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
                        Generate XAI Heatmap
                      </Button>
                    )}

                    <Button 
                      className="w-full h-12 font-bold shadow-md hover:shadow-lg transition-shadow bg-slate-900 text-white hover:bg-slate-800"
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
