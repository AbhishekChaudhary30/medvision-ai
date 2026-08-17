import { apiClient } from "./client";
import { AnalysisResponse, PaginatedAnalyses } from "./types";

export const uploadAnalysis = async (
  file: File, 
  modality: string = "chest-xray",
  patientAge?: number,
  patientGender?: string,
  clinicalNotes?: string
): Promise<AnalysisResponse> => {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("modality", modality);
  if (patientAge) formData.append("patient_age", patientAge.toString());
  if (patientGender) formData.append("patient_gender", patientGender);
  if (clinicalNotes) formData.append("clinical_notes", clinicalNotes);
  
  const { data } = await apiClient.post<AnalysisResponse>("/analyses", formData, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });
  return data;
};

export const getAnalyses = async (skip: number = 0, limit: number = 20): Promise<PaginatedAnalyses> => {
  const { data } = await apiClient.get<PaginatedAnalyses>("/analyses", {
    params: { skip, limit }
  });
  return data;
};

export const getAnalysis = async (id: string): Promise<AnalysisResponse> => {
  const { data } = await apiClient.get<AnalysisResponse>(`/analyses/${id}`);
  return data;
};

export const explainAnalysis = async (id: string, method: string = "gradcam"): Promise<AnalysisResponse> => {
  const { data } = await apiClient.post<AnalysisResponse>(`/analyses/${id}/explain`, { method });
  return data;
};

export const reviewAnalysis = async (
  id: string, 
  review_status: string, 
  reviewer_notes: string | null = null
): Promise<AnalysisResponse> => {
  const { data } = await apiClient.post<AnalysisResponse>(`/analyses/${id}/review`, {
    review_status,
    reviewer_notes
  });
  return data;
};

export const downloadReport = async (id: string): Promise<void> => {
  const response = await apiClient.get(`/analyses/${id}/report`, {
    responseType: "blob",
  });
  
  // Create a blob from the PDF stream
  const file = new Blob([response.data], { type: "application/pdf" });
  const fileURL = URL.createObjectURL(file);
  
  // Create a temporary link to download
  const link = document.createElement("a");
  link.href = fileURL;
  link.download = `analysis_${id}.pdf`;
  document.body.appendChild(link);
  link.click();
  
  // Clean up
  link.remove();
  URL.revokeObjectURL(fileURL);
};

export const deleteAnalysis = async (id: string): Promise<void> => {
  await apiClient.delete(`/analyses/${id}`);
};
