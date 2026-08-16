import React from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Loader2, CheckCircle2, ShieldAlert } from "lucide-react";
import { useAuth } from "../contexts/AuthContext";

// In a real app, these would be imported from a central api.ts file
const fetchModels = async () => {
  const res = await fetch("http://localhost:8000/api/v1/models", {
    headers: { Authorization: `Bearer ${localStorage.getItem("token")}` }
  });
  if (!res.ok) throw new Error("Failed to fetch models");
  return res.json();
};

const promoteModel = async (versionTag: string) => {
  const res = await fetch(`http://localhost:8000/api/v1/models/${versionTag}/promote`, {
    method: "POST",
    headers: { Authorization: `Bearer ${localStorage.getItem("token")}` }
  });
  if (!res.ok) throw new Error("Failed to promote model");
  return res.json();
};

export function ModelCenter() {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  
  const { data: models, isLoading, isError } = useQuery({
    queryKey: ["models"],
    queryFn: fetchModels,
  });

  const promoteMutation = useMutation({
    mutationFn: promoteModel,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["models"] });
    },
  });

  if (isLoading) return <div className="flex justify-center mt-10"><Loader2 className="animate-spin h-8 w-8 text-primary" /></div>;
  if (isError) return <div className="text-destructive text-center mt-10">Failed to load model registry.</div>;

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Model Center</h1>
        <p className="text-muted-foreground mt-2">Manage, evaluate, and deploy MedVision AI models.</p>
      </div>

      <div className="grid gap-6">
        {models?.map((model: any) => (
          <Card key={model.id} className={model.is_active_production ? "border-emerald-500 shadow-sm" : ""}>
            <CardHeader className="flex flex-row items-start justify-between space-y-0">
              <div>
                <CardTitle className="flex items-center gap-2">
                  {model.version_tag}
                  {model.is_active_production && (
                    <span className="bg-emerald-100 text-emerald-800 text-xs px-2 py-1 rounded-full flex items-center">
                      <CheckCircle2 className="w-3 h-3 mr-1" /> PRODUCTION
                    </span>
                  )}
                  {!model.is_active_production && model.status === "RETIRED" && (
                    <span className="bg-gray-100 text-gray-800 text-xs px-2 py-1 rounded-full">
                      RETIRED
                    </span>
                  )}
                </CardTitle>
                <CardDescription className="mt-1">Architecture: {model.architecture}</CardDescription>
              </div>
              
              {user?.role === "ADMIN" && !model.is_active_production && model.status !== "RETIRED" && (
                <Button 
                  variant="outline" 
                  size="sm"
                  onClick={() => promoteMutation.mutate(model.version_tag)}
                  disabled={promoteMutation.isPending}
                >
                  Promote to Production
                </Button>
              )}
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-2">
                <div className="bg-secondary/40 p-3 rounded-md">
                  <p className="text-xs text-muted-foreground mb-1 uppercase">Validation Loss</p>
                  <p className="text-lg font-semibold">{model.val_loss?.toFixed(4) || "N/A"}</p>
                </div>
                <div className="bg-secondary/40 p-3 rounded-md">
                  <p className="text-xs text-muted-foreground mb-1 uppercase">Validation AUROC</p>
                  <p className="text-lg font-semibold">{model.val_auroc?.toFixed(4) || "N/A"}</p>
                </div>
                <div className="bg-secondary/40 p-3 rounded-md">
                  <p className="text-xs text-muted-foreground mb-1 uppercase">Validation F1</p>
                  <p className="text-lg font-semibold">{model.val_f1?.toFixed(4) || "N/A"}</p>
                </div>
                <div className="bg-secondary/40 p-3 rounded-md">
                  <p className="text-xs text-muted-foreground mb-1 uppercase">Calibration Temp</p>
                  <p className="text-lg font-semibold">{model.calibration_temp?.toFixed(4) || "N/A"}</p>
                </div>
              </div>
              
              {model.status === "EXPERIMENTAL" && (
                <div className="mt-4 p-3 bg-amber-50 text-amber-800 rounded-md flex items-start text-sm">
                  <ShieldAlert className="w-4 h-4 mr-2 mt-0.5" />
                  <p>This model is experimental and has not been validated for clinical research support.</p>
                </div>
              )}
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
