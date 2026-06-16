"use client";
import { useCallback, useEffect, useState } from "react";
import apiClient from "@/lib/api-client";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Upload, FileText, Loader2, Trash2, X } from "lucide-react";
import { toast } from "sonner";
import { formatDistanceToNow } from "date-fns";

interface Document {
  id: string;
  filename: string;
  content_type: string;
  created_at: string;
}

export default function AdminDocumentsPage() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [uploading, setUploading] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [dragOver, setDragOver] = useState(false);

  useEffect(() => { fetchDocs(); }, []);

  const fetchDocs = async () => {
    try {
      const res = await apiClient.get("/documents");
      setDocuments(res.data.items);
    } catch { /* ignore */ }
  };

  const handleFile = (file: File) => {
    const allowed = [".pdf", ".txt", ".docx"];
    if (!allowed.some((ext) => file.name.endsWith(ext))) {
      toast.error("Supported: PDF, TXT, DOCX");
      return;
    }
    setSelectedFile(file);
  };

  const handleUpload = async () => {
    if (!selectedFile) return;
    setUploading(true);
    const form = new FormData();
    form.append("file", selectedFile);
    try {
      const res = await apiClient.post("/documents/upload", form, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      toast.success(`Indexed ${res.data.chunks_indexed} chunks from ${res.data.filename}`);
      setSelectedFile(null);
      await fetchDocs();
    } catch (e: any) {
      toast.error(e.response?.data?.detail || "Upload failed");
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (id: string, name: string) => {
    try {
      await apiClient.delete(`/documents/${id}`);
      toast.success(`Deleted ${name}`);
      setDocuments((prev) => prev.filter((d) => d.id !== id));
    } catch {
      toast.error("Delete failed");
    }
  };

  return (
    <div className="p-8 space-y-6">
      <div>
        <h1 className="text-3xl font-bold gradient-text">Documents</h1>
        <p className="text-muted-foreground mt-1">Upload knowledge base documents (PDF, TXT, DOCX)</p>
      </div>

      <Card className="glass border-border/50">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base">
            <Upload className="w-4 h-4 text-primary" />
            Upload Document
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div
            onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
            onDragLeave={() => setDragOver(false)}
            onDrop={(e) => { e.preventDefault(); setDragOver(false); const f = e.dataTransfer.files[0]; if (f) handleFile(f); }}
            onClick={() => document.getElementById("doc-input")?.click()}
            className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all ${
              dragOver ? "border-primary bg-primary/5" : "border-border/50 hover:border-primary/50"
            }`}
          >
            <input id="doc-input" type="file" accept=".pdf,.txt,.docx" className="hidden"
              onChange={(e) => { const f = e.target.files?.[0]; if (f) handleFile(f); }} />
            <FileText className="w-8 h-8 text-muted-foreground mx-auto mb-2" />
            {selectedFile ? (
              <p className="text-sm font-medium">{selectedFile.name}</p>
            ) : (
              <>
                <p className="text-sm font-medium">Drop document or click to browse</p>
                <p className="text-xs text-muted-foreground mt-1">PDF, TXT, DOCX supported</p>
              </>
            )}
          </div>
          {selectedFile && (
            <div className="flex gap-2">
              <Button id="upload-doc-btn" onClick={handleUpload} disabled={uploading} className="gap-2 text-white"
                style={{ background: "linear-gradient(135deg, oklch(0.58 0.23 25), oklch(0.65 0.21 40))" }}>
                {uploading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Upload className="w-4 h-4" />}
                {uploading ? "Processing..." : "Upload & Index"}
              </Button>
              <Button variant="outline" onClick={() => setSelectedFile(null)}><X className="w-4 h-4" /></Button>
            </div>
          )}
        </CardContent>
      </Card>

      <Card className="glass border-border/50">
        <CardHeader><CardTitle className="text-base">Indexed Documents ({documents.length})</CardTitle></CardHeader>
        <CardContent>
          {documents.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground text-sm">No documents uploaded yet</div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Filename</TableHead>
                  <TableHead>Type</TableHead>
                  <TableHead>Uploaded</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {documents.map((doc) => (
                  <TableRow key={doc.id}>
                    <TableCell className="font-medium text-sm">{doc.filename}</TableCell>
                    <TableCell className="text-xs text-muted-foreground">{doc.content_type}</TableCell>
                    <TableCell className="text-xs text-muted-foreground">
                      {formatDistanceToNow(new Date(doc.created_at), { addSuffix: true })}
                    </TableCell>
                    <TableCell className="text-right">
                      <Button variant="ghost" size="icon" className="h-7 w-7 hover:text-destructive"
                        onClick={() => handleDelete(doc.id, doc.filename)}>
                        <Trash2 className="w-3.5 h-3.5" />
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
