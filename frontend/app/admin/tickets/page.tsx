"use client";
import { useCallback, useState } from "react";
import apiClient from "@/lib/api-client";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Upload, FileText, Loader2, CheckCircle, AlertCircle, X } from "lucide-react";
import { toast } from "sonner";

export default function AdminTicketsPage() {
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState<{ inserted: number; skipped: number; message: string } | null>(null);
  const [dragOver, setDragOver] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const handleFile = useCallback(async (file: File) => {
    if (!file.name.endsWith(".csv")) {
      toast.error("Only CSV files are supported");
      return;
    }
    setSelectedFile(file);
  }, []);

  const handleUpload = async () => {
    if (!selectedFile) return;
    setUploading(true);
    setResult(null);
    const form = new FormData();
    form.append("file", selectedFile);
    try {
      const res = await apiClient.post("/tickets/upload", form, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setResult(res.data);
      toast.success(res.data.message);
      setSelectedFile(null);
    } catch (e: any) {
      toast.error(e.response?.data?.detail || "Upload failed");
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="p-8 space-y-6">
      <div>
        <h1 className="text-3xl font-bold gradient-text">Tickets</h1>
        <p className="text-muted-foreground mt-1">Upload CSV datasets to populate the knowledge base</p>
      </div>

      <Card className="glass border-border/50">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base">
            <Upload className="w-4 h-4 text-primary" />
            Upload Ticket CSV
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Drop zone */}
          <div
            onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
            onDragLeave={() => setDragOver(false)}
            onDrop={(e) => { e.preventDefault(); setDragOver(false); const f = e.dataTransfer.files[0]; if (f) handleFile(f); }}
            onClick={() => document.getElementById("file-input")?.click()}
            className={`border-2 border-dashed rounded-xl p-10 text-center cursor-pointer transition-all ${
              dragOver ? "border-primary bg-primary/5" : "border-border/50 hover:border-primary/50 hover:bg-secondary/20"
            }`}
          >
            <input id="file-input" type="file" accept=".csv" className="hidden"
              onChange={(e) => { const f = e.target.files?.[0]; if (f) handleFile(f); }} />
            <FileText className="w-10 h-10 text-muted-foreground mx-auto mb-3" />
            {selectedFile ? (
              <div className="space-y-1">
                <p className="font-medium text-sm">{selectedFile.name}</p>
                <p className="text-xs text-muted-foreground">{(selectedFile.size / 1024).toFixed(1)} KB</p>
              </div>
            ) : (
              <>
                <p className="text-sm font-medium mb-1">Drop CSV file here or click to browse</p>
                <p className="text-xs text-muted-foreground">
                  Supports Kaggle IT Support, Customer Support, and ITSM datasets
                </p>
              </>
            )}
          </div>

          {selectedFile && (
            <div className="flex gap-2">
              <Button id="upload-ticket-btn" onClick={handleUpload} disabled={uploading}
                className="gap-2 text-white" style={{ background: "linear-gradient(135deg, oklch(0.58 0.23 25), oklch(0.65 0.21 40))" }}>
                {uploading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Upload className="w-4 h-4" />}
                {uploading ? "Uploading..." : "Upload & Ingest"}
              </Button>
              <Button variant="outline" onClick={() => setSelectedFile(null)} className="gap-2">
                <X className="w-4 h-4" /> Clear
              </Button>
            </div>
          )}

          {result && (
            <div className="grid grid-cols-3 gap-3">
              {[
                { label: "Inserted", value: result.inserted, color: "text-green-400" },
                { label: "Skipped", value: result.skipped, color: "text-yellow-400" },
                { label: "Errors", value: 0, color: "text-red-400" },
              ].map(({ label, value, color }) => (
                <div key={label} className="glass rounded-lg p-3 text-center">
                  <div className={`text-xl font-bold ${color}`}>{value}</div>
                  <div className="text-xs text-muted-foreground">{label}</div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      <Card className="glass border-border/50">
        <CardHeader><CardTitle className="text-base">Supported Datasets</CardTitle></CardHeader>
        <CardContent>
          <div className="space-y-2">
            {[
              "Kaggle IT Support Tickets (ticket text, priority, department)",
              "Customer Support Ticket Dataset (descriptions, status, product)",
              "Customer IT Support Dataset (emails, agent responses, priorities)",
              "MindWeave Help Desk Dataset (ITSM tickets with comments and categories)",
            ].map((ds, i) => (
              <div key={i} className="flex items-center gap-2 text-sm text-muted-foreground">
                <div className="w-1.5 h-1.5 rounded-full bg-primary shrink-0" />
                {ds}
              </div>
            ))}
          </div>
          <p className="text-xs text-muted-foreground mt-4">
            After uploading, go to Dashboard and click <strong>Reindex Tickets</strong> to embed them into ChromaDB.
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
