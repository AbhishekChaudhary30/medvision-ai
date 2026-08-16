export type Role = "USER" | "REVIEWER" | "ADMIN";

export interface User {
  id: string;
  email: string;
  role: Role;
  is_active: boolean;
}

export interface AnalysisArtifact {
  id: string;
  artifact_type: string;
  file_path: string;
  content_type: string;
  created_at: string;
}

export interface AnalysisResponse {
  id: string;
  user_id: string;
  modality: string;
  patient_age?: number;
  patient_gender?: string;
  clinical_notes?: string;
  model_version: string;
  model_architecture: string;
  predicted_class: string;
  predicted_class_index: number;
  confidence: number;
  probability_normal: number;
  probability_pneumonia: number;
  threshold: number;
  uncertainty_status: string;
  entropy: number;
  margin: number;
  calibration_status: string;
  inference_time: number;
  explanation_method: string | null;
  clinical_suggestions: string | null;
  created_at: string;
  
  review_status: string;
  reviewer_id: string | null;
  reviewer_notes: string | null;
  reviewed_at: string | null;
  
  artifacts: AnalysisArtifact[];
}

export interface PaginatedAnalyses {
  items: AnalysisResponse[];
  total: number;
  limit: number;
  offset: number;
}
