import React, { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { getAnalyses, reviewAnalysis } from "../services/api";
import { Card, CardContent, CardHeader, CardTitle, CardFooter } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import { CheckCircle, AlertTriangle, Loader2 } from "lucide-react";

export function ReviewsPage() {
  const [selectedAnalysis, setSelectedAnalysis] = useState<string | null>(null);
  const [notes, setNotes] = useState("");
  const queryClient = useQueryClient();

  const { data, isLoading } = useQuery({
    queryKey: ["analyses", "review"],
    queryFn: () => getAnalyses(0, 100),
  });

  const reviewMutation = useMutation({
    mutationFn: (params: { id: string, status: string, notes: string }) => 
      reviewAnalysis(params.id, params.status, params.notes),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["analyses"] });
      setSelectedAnalysis(null);
      setNotes("");
    },
  });

  if (isLoading) {
    return <div className="flex h-64 items-center justify-center"><Loader2 className="h-8 w-8 animate-spin text-primary" /></div>;
  }

  const items = data?.items || [];
  // For demo, we just show all items that are uncertain or not reviewed
  const pendingItems = items.filter(a => a.review_status === "NOT_REVIEWED");
  const reviewedItems = items.filter(a => a.review_status !== "NOT_REVIEWED");

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Review Queue</h1>
        <p className="text-muted-foreground mt-2">Audit and verify model predictions.</p>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Pending Reviews</CardTitle>
          </CardHeader>
          <CardContent>
            {pendingItems.length === 0 ? (
              <div className="text-center py-6 text-muted-foreground">Queue is empty! 🎉</div>
            ) : (
              <div className="space-y-3">
                {pendingItems.map((analysis) => (
                  <div 
                    key={analysis.id} 
                    className={`p-3 border rounded cursor-pointer transition-colors ${selectedAnalysis === analysis.id ? "border-primary bg-primary/5" : "hover:border-gray-300"}`}
                    onClick={() => setSelectedAnalysis(analysis.id)}
                  >
                    <div className="flex justify-between items-start">
                      <div>
                        <p className="font-semibold">{analysis.predicted_class}</p>
                        <p className="text-xs text-muted-foreground">ID: {analysis.id.substring(0,8)}</p>
                      </div>
                      <div className="text-right">
                        <p className="text-sm font-medium">{(analysis.confidence * 100).toFixed(1)}%</p>
                        <p className={`text-xs ${analysis.uncertainty_status === "UNCERTAIN" ? "text-rose-600" : "text-emerald-600"}`}>
                          {analysis.uncertainty_status}
                        </p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        <div>
          {selectedAnalysis ? (
            <Card className="sticky top-24">
              <CardHeader>
                <CardTitle>Review Form</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="bg-secondary/50 p-3 rounded text-sm mb-4">
                  Reviewing Analysis ID: <span className="font-mono">{selectedAnalysis.substring(0,8)}</span>
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="notes">Reviewer Notes</Label>
                  <textarea 
                    id="notes"
                    className="flex min-h-[80px] w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-sm placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
                    placeholder="Enter findings or corrections..."
                    value={notes}
                    onChange={(e) => setNotes(e.target.value)}
                  />
                </div>
              </CardContent>
              <CardFooter className="flex gap-3">
                <Button 
                  className="w-full bg-emerald-600 hover:bg-emerald-700" 
                  onClick={() => reviewMutation.mutate({ id: selectedAnalysis, status: "APPROVED", notes })}
                  disabled={reviewMutation.isPending}
                >
                  <CheckCircle className="mr-2 h-4 w-4" /> Approve
                </Button>
                <Button 
                  variant="destructive"
                  className="w-full" 
                  onClick={() => reviewMutation.mutate({ id: selectedAnalysis, status: "REJECTED", notes })}
                  disabled={reviewMutation.isPending}
                >
                  <AlertTriangle className="mr-2 h-4 w-4" /> Reject
                </Button>
              </CardFooter>
            </Card>
          ) : (
            <Card className="flex h-64 items-center justify-center bg-gray-50/50">
              <div className="text-center text-muted-foreground">
                <CheckCircle className="mx-auto h-8 w-8 mb-2 opacity-20" />
                Select an item from the queue to review
              </div>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}
