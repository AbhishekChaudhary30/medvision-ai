import { apiClient } from "./client";
import { AnalysisResponse, PaginatedAnalyses } from "./types";
import { Client } from "@gradio/client";

// Get local storage key
const STORAGE_KEY = "medvision_analyses_history";

// Helper to get history
const getLocalHistory = (): AnalysisResponse[] => {
  const data = localStorage.getItem(STORAGE_KEY);
  return data ? JSON.parse(data) : [];
};

// Helper to save history
const saveLocalHistory = (history: AnalysisResponse[]) => {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(history));
};

export const uploadAnalysis = async (
  file: File, 
  modality: string = "chest-xray",
  patientAge?: number,
  patientGender?: string,
  clinicalNotes?: string
): Promise<AnalysisResponse> => {
  try {
    // Connect to the Hugging Face Gradio API directly!
    const client = await Client.connect("Abhishek1130/medvision-api");
    
    // Call the analyze_image function via Gradio REST API
    const result = await client.predict("/analyze_image", {
      image: file,
      modality: modality,
      age: patientAge || 45,
      gender: patientGender || "Male",
      notes: clinicalNotes || "",
    });
    
    // The result.data is an array matching the outputs of the Gradio function:
    // [summary_output, heatmap_output, json_output, details_row]
    const data = result.data as any[];
    
    const summary = data[0] as string;
    const heatmap = data[1] as any; // Usually a URL or base64 object from Gradio
    const rawJsonStr = data[2] as string;
    
    let parsedJson: any = {};
    try {
      parsedJson = JSON.parse(rawJsonStr);
    } catch(e) {}
    
    const url = URL.createObjectURL(file);
    
    const analysisResponse: AnalysisResponse = {
      id: "analysis_" + Date.now().toString(),
      user_id: "user_mock",
      modality: modality,
      patient_age: patientAge || 45,
      patient_gender: patientGender || "Male",
      clinical_notes: clinicalNotes || "",
      model_version: "v3.0.0-gradio",
      model_architecture: "ZeroGPU Ensembled",
      predicted_class: parsedJson.predicted_class || "Pending",
      predicted_class_index: parsedJson.predicted_class_index || 0,
      confidence: parsedJson.confidence || 0,
      probability_normal: parsedJson.probability_normal || 0,
      probability_pneumonia: parsedJson.probability_pneumonia || 0,
      threshold: 0.5,
      uncertainty_status: parsedJson.uncertainty_status || "LOW",
      entropy: 0,
      margin: 0,
      calibration_status: "Calibrated",
      inference_time: 0,
      explanation_method: "gradcam",
      clinical_suggestions: summary,
      review_status: "pending",
      reviewer_id: null,
      reviewer_notes: null,
      reviewed_at: null,
      created_at: new Date().toISOString(),
      artifacts: [
        {
          id: "art_1",
          artifact_type: "original",
          file_path: url,
          content_type: "image/jpeg",
          created_at: new Date().toISOString()
        }
      ]
    };
    
    if (heatmap) {
      analysisResponse.artifacts.push({
        id: "art_2",
        artifact_type: "gradcam_heatmap",
        file_path: heatmap?.url || heatmap || url,
        content_type: "image/jpeg",
        created_at: new Date().toISOString()
      });
    }
    
    // Save to local history
    const history = getLocalHistory();
    history.unshift(analysisResponse);
    saveLocalHistory(history);
    
    return analysisResponse;
  } catch (error) {
    console.error("Gradio API Error:", error);
    throw error;
  }
};

export const getAnalyses = async (skip: number = 0, limit: number = 20): Promise<PaginatedAnalyses> => {
  // Return local history
  const history = getLocalHistory();
  const paginated = history.slice(skip, skip + limit);
  
  return {
    items: paginated,
    total: history.length,
    limit: limit,
    offset: skip
  };
};

export const getAnalysis = async (id: string): Promise<AnalysisResponse> => {
  const history = getLocalHistory();
  const item = history.find(x => x.id === id);
  if (!item) throw new Error("Analysis not found");
  return item;
};

export const explainAnalysis = async (id: string, method: string = "gradcam"): Promise<AnalysisResponse> => {
  // It's already explained in the Gradio step, just return it
  return getAnalysis(id);
};

export const reviewAnalysis = async (
  id: string, 
  review_status: string, 
  reviewer_notes: string | null = null
): Promise<AnalysisResponse> => {
  const history = getLocalHistory();
  const index = history.findIndex(x => x.id === id);
  if (index === -1) throw new Error("Not found");
  
  history[index].review_status = review_status;
  if (reviewer_notes) {
    history[index].reviewer_notes = reviewer_notes;
  }
  
  saveLocalHistory(history);
  return history[index];
};

export const downloadReport = async (id: string): Promise<void> => {
  // Mock report download
  alert("Report download is mocked in serverless mode.");
};

export const deleteAnalysis = async (id: string): Promise<void> => {
  const history = getLocalHistory();
  const newHistory = history.filter(x => x.id !== id);
  saveLocalHistory(newHistory);
};
