import React, { useState, useMemo } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { uploadAnalysis, explainAnalysis, AnalysisResponse } from "../services/api";
import { Button } from "../components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from "../components/ui/card";
import { UploadCloud, AlertCircle, FileText, Loader2, Stethoscope, Brain, Scan, Activity, Microscope, ArrowRight, User, ZoomIn, ZoomOut, Contrast, Sun, RotateCcw, Download } from "lucide-react";
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
      case "HIGH_CONFIDENCE": return "text-emerald-600 bg-emerald-50 border-emerald-200";
      case "LOW_CONFIDENCE": return "text-amber-600 bg-amber-50 border-amber-200";
      case "UNCERTAIN": return "text-rose-600 bg-rose-50 border-rose-200";
      default: return "text-slate-600 bg-slate-50 border-slate-200";
    }
  };

  return (
    <div className="max-w-6xl mx-auto space-y-8 pb-12">
      <div className="flex flex-col sm:flex-row justify-between sm:items-end gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Enterprise Clinical Wizard</h1>
          <p className="text-muted-foreground mt-2 max-w-3xl">
            A comprehensive, multi-modal diagnostic pipeline. Step 1: Select imaging type. Step 2: Provide patient context. Step 3: Run AI analysis.
          </p>
        </div>
        <Button variant="outline" onClick={resetAll}>Reset Workspace</Button>
      </div>

      {/* Progress Bar */}
      <div className="flex items-center justify-between relative px-2 mb-8">
        <div className="absolute left-0 top-1/2 transform -translate-y-1/2 w-full h-1 bg-slate-100 -z-10 rounded-full"></div>
        <div className="absolute left-0 top-1/2 transform -translate-y-1/2 h-1 bg-primary -z-10 rounded-full transition-all duration-500" style={{ width: `${((step - 1) / 3) * 100}%` }}></div>
        
        {[1, 2, 3, 4].map(s => (
          <div key={s} className={cn("w-10 h-10 rounded-full flex items-center justify-center font-bold border-4 transition-colors", step >= s ? "bg-primary border-white text-white shadow-md" : "bg-slate-100 border-white text-slate-400")}>
            {s}
          </div>
        ))}
      </div>

      {step === 1 && (
        <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
          <h2 className="text-xl font-bold">Step 1: Select Imaging Category & Modality</h2>
          <div className="grid md:grid-cols-5 gap-4">
            {CATEGORIES.map(c => {
              const Icon = c.icon;
              return (
                <div 
                  key={c.id}
                  onClick={() => setCategory(c.id)}
                  className={cn("cursor-pointer p-4 rounded-xl border transition-all text-center flex flex-col items-center justify-center gap-2", category === c.id ? "border-primary bg-primary/5 ring-2 ring-primary/20" : "hover:border-primary/40 bg-white")}
                >
                  <Icon className={cn("h-8 w-8", category === c.id ? "text-primary" : "text-slate-400")} />
                  <span className="font-semibold text-sm">{c.label}</span>
                </div>
              );
            })}
          </div>

          <div className="grid md:grid-cols-3 gap-4 mt-6">
            {filteredModalities.map(m => (
              <Card 
                key={m.id} 
                onClick={() => setModality(m.id)}
                className={cn("cursor-pointer transition-all", modality === m.id ? "border-primary ring-2 ring-primary/20 bg-primary/5" : "hover:border-primary/50")}
              >
                <CardContent className="p-4">
                  <h3 className="font-bold text-lg">{m.label}</h3>
                  <p className="text-sm text-muted-foreground">{m.desc}</p>
                </CardContent>
              </Card>
            ))}
          </div>

          <div className="flex justify-end pt-4">
            <Button size="lg" onClick={() => setStep(2)}>Next: Patient Context <ArrowRight className="ml-2 h-4 w-4" /></Button>
          </div>
        </div>
      )}

      {step === 2 && (
        <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
          <h2 className="text-xl font-bold">Step 2: Patient Demographics & Clinical Notes</h2>
          <Card>
            <CardContent className="p-6 space-y-6">
              <div className="grid grid-cols-2 gap-6">
                <div className="space-y-2">
                  <label className="text-sm font-semibold uppercase tracking-wider text-slate-500">Age (Years)</label>
                  <input 
                    type="number" 
                    value={age} 
                    onChange={e => setAge(e.target.value)} 
                    placeholder="e.g. 45"
                    className="flex h-12 w-full rounded-md border border-input bg-transparent px-3 py-1 text-base shadow-sm transition-colors placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
                  />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-semibold uppercase tracking-wider text-slate-500">Gender</label>
                  <select 
                    value={gender} 
                    onChange={e => setGender(e.target.value)}
                    className="flex h-12 w-full rounded-md border border-input bg-transparent px-3 py-1 text-base shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
                  >
                    <option value="M">Male</option>
                    <option value="F">Female</option>
                    <option value="O">Other</option>
                  </select>
                </div>
              </div>
              <div className="space-y-2">
                <label className="text-sm font-semibold uppercase tracking-wider text-slate-500">Clinical Notes / Symptoms / Prior Reports</label>
                <textarea 
                  value={notes} 
                  onChange={e => setNotes(e.target.value)} 
                  placeholder="Enter any presenting symptoms, medical history, or doctor's observations. The Expert AI will integrate this into the final recommendation..."
                  className="flex min-h-[120px] w-full rounded-md border border-input bg-transparent px-3 py-2 text-base shadow-sm placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
                />
              </div>
            </CardContent>
            <CardFooter className="flex justify-between bg-slate-50 p-6 border-t">
              <Button variant="outline" onClick={() => setStep(1)}>Back</Button>
              <Button size="lg" onClick={() => setStep(3)}>Next: Upload Media <ArrowRight className="ml-2 h-4 w-4" /></Button>
            </CardFooter>
          </Card>
        </div>
      )}

      {step === 3 && (
        <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
          <h2 className="text-xl font-bold">Step 3: Upload Image for {MODALITIES.find(m => m.id === modality)?.label}</h2>
          <Card className="border-0 shadow-md">
            <CardContent className="p-8">
              <div className="border-2 border-dashed border-gray-300 rounded-xl p-12 flex flex-col items-center justify-center bg-gray-50/50 hover:bg-gray-50 transition-colors">
                {preview ? (
                  <div className="relative w-full aspect-square max-h-[400px] rounded-lg overflow-hidden shadow-inner">
                    <img src={preview} alt="Preview" className="object-contain w-full h-full bg-black/5" />
                  </div>
                ) : (
                  <div className="text-center py-10">
                    <div className="mx-auto h-20 w-20 rounded-full bg-primary/10 flex items-center justify-center mb-6">
                      <UploadCloud className="h-10 w-10 text-primary" />
                    </div>
                    <div className="flex text-lg leading-6 text-gray-600 justify-center">
                      <label
                        htmlFor="file-upload"
                        className="relative cursor-pointer rounded-md font-semibold text-primary hover:text-primary/80"
                      >
                        <span>Click to browse and upload</span>
                        <input id="file-upload" name="file-upload" type="file" className="sr-only" accept="image/jpeg, image/png" onChange={handleFileChange} />
                      </label>
                    </div>
                    <p className="text-sm text-muted-foreground mt-2">DICOM (converted to JPEG/PNG) up to 10MB</p>
                  </div>
                )}
              </div>

              <div className="flex justify-between mt-8">
                <Button variant="outline" onClick={() => setStep(2)}>Back</Button>
                <Button 
                  size="lg"
                  className="px-10" 
                  onClick={handleUpload} 
                  disabled={!file || uploadMutation.isPending}
                >
                  {uploadMutation.isPending && <Loader2 className="mr-2 h-5 w-5 animate-spin" />}
                  {uploadMutation.isPending ? "Processing..." : "Run AI Prediction"}
                </Button>
              </div>
              
              {uploadMutation.isError && (
                <div className="mt-4 p-4 text-sm text-destructive bg-destructive/10 rounded-lg flex items-center gap-3">
                  <AlertCircle className="h-5 w-5 flex-shrink-0" />
                  <span>Processing failed. Check format or connection.</span>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      )}

      {step === 4 && result && (
        <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
          <div className="flex items-center justify-between bg-primary/5 border border-primary/20 p-4 rounded-xl">
            <div className="flex items-center gap-4">
              <div className="p-3 bg-white rounded-lg shadow-sm">
                <User className="h-6 w-6 text-primary" />
              </div>
              <div>
                <h3 className="font-bold">Patient Demographics</h3>
                <p className="text-sm text-muted-foreground">Age: {result.patient_age || "N/A"} • Gender: {result.patient_gender || "N/A"}</p>
              </div>
            </div>
            {result.clinical_notes && (
              <div className="text-right max-w-sm hidden md:block">
                <p className="text-xs font-bold text-slate-400 uppercase">Clinical Context Included</p>
                <p className="text-sm font-medium italic line-clamp-2">"{result.clinical_notes}"</p>
              </div>
            )}
          </div>

          <Card className="border-0 shadow-lg bg-white overflow-hidden">
            <div className="h-2 w-full bg-primary"></div>
            <CardHeader className="pb-4">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                <div>
                  <CardTitle className="text-2xl flex items-center gap-2">
                    Expert Analysis Results
                  </CardTitle>
                  <CardDescription className="mt-1 font-mono text-xs text-slate-400">Modality: {result.modality.toUpperCase()} • ID: {result.id.substring(0,8)}</CardDescription>
                </div>
                <div className={cn("px-4 py-1.5 rounded-full text-xs font-bold border tracking-wide uppercase self-start", getStatusColor(result.uncertainty_status || ""))}>
                  {(result.uncertainty_status || "ANALYZED").replace("_", " ")}
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-8">
              
              <div className="grid md:grid-cols-2 gap-8">
                {/* Advanced PACS Viewer */}
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <h4 className="text-sm font-bold uppercase tracking-widest text-slate-400">PACS Image Viewer</h4>
                    <div className="flex gap-2">
                      <Button variant="outline" size="icon" onClick={() => setZoom(z => Math.min(z + 0.5, 3))}><ZoomIn className="h-4 w-4" /></Button>
                      <Button variant="outline" size="icon" onClick={() => setZoom(z => Math.max(z - 0.5, 1))}><ZoomOut className="h-4 w-4" /></Button>
                      <Button variant="outline" size="icon" onClick={() => setContrast(c => c === 100 ? 150 : 100)}><Contrast className="h-4 w-4" /></Button>
                      <Button variant="outline" size="icon" onClick={() => setBrightness(b => b === 100 ? 120 : 100)}><Sun className="h-4 w-4" /></Button>
                      <Button variant="outline" size="icon" onClick={() => setInvert(i => !i)}><RotateCcw className="h-4 w-4" /></Button>
                    </div>
                  </div>
                  <div className="relative aspect-square bg-black rounded-2xl overflow-hidden shadow-inner flex items-center justify-center">
                    {preview && (
                      <img 
                        src={preview} 
                        alt="Scan" 
                        style={{ 
                          transform: `scale(${zoom})`,
                          filter: `contrast(${contrast}%) brightness(${brightness}%) invert(${invert ? 100 : 0}%)`,
                          transition: 'transform 0.2s, filter 0.2s'
                        }}
                        className="object-contain w-full h-full cursor-move" 
                      />
                    )}
                  </div>
                  <Button variant="ghost" size="sm" className="w-full text-xs" onClick={resetViewer}>Reset View</Button>
                </div>

                <div className="space-y-6">
                  <div className="grid grid-cols-2 gap-4">
                    <div className="bg-slate-50 border p-6 rounded-2xl shadow-sm">
                      <p className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-2">Detection Output</p>
                      <p className="text-2xl font-black text-slate-800">{result.predicted_class}</p>
                    </div>
                    <div className="bg-slate-50 border p-6 rounded-2xl shadow-sm">
                      <p className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-2">AI Confidence</p>
                      <p className="text-2xl font-black text-primary">{(result.confidence * 100).toFixed(1)}%</p>
                    </div>
                  </div>

                  {result.clinical_suggestions && (
                    <div className="bg-indigo-50 border border-indigo-100 p-6 rounded-2xl shadow-sm">
                      <h4 className="flex items-center gap-2 font-bold text-indigo-900 mb-2">
                        <Activity className="h-5 w-5" /> Integrated Clinical Action Plan
                      </h4>
                      <p className="text-indigo-800 leading-relaxed">
                        {result.clinical_suggestions}
                      </p>
                    </div>
                  )}
                  
                  <Button 
                    className="w-full"
                    variant="outline"
                    onClick={() => window.print()}
                  >
                    <Download className="mr-2 h-4 w-4" /> Download PDF Report
                  </Button>
                </div>
              </div>

              <div className="pt-4 border-t space-y-4">
                <h4 className="text-sm font-bold uppercase tracking-widest text-slate-400 mb-3">Explainable AI (Grad-CAM)</h4>
                
                {result.explanation_method ? (
                  <div className="p-4 bg-emerald-50 text-emerald-800 rounded-xl border border-emerald-200 text-sm flex items-start gap-3">
                    <FileText className="h-5 w-5 mt-0.5 text-emerald-600" />
                    <div>
                      <p className="font-bold">Grad-CAM Heatmap Ready</p>
                      <p className="mt-1 text-emerald-700 opacity-90 leading-relaxed">The heatmap visualization highlights the region of interest. Available in the PDF Report.</p>
                    </div>
                  </div>
                ) : (
                  <Button 
                    variant="outline" 
                    className="w-full h-12 border-slate-300 hover:bg-slate-50 font-semibold"
                    onClick={handleExplain}
                    disabled={explainMutation.isPending}
                  >
                    {explainMutation.isPending ? (
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    ) : (
                      <Scan className="mr-2 h-4 w-4" />
                    )}
                    Generate XAI Visualization Heatmap
                  </Button>
                )}
              </div>
            </CardContent>
          </Card>
        </div>
      )}

    </div>
  );
}
