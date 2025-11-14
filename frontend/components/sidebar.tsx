"use client";

import { useCallback, useEffect, useState } from "react";
import { FileText, Loader2, RefreshCcw } from "lucide-react";

import { fetchDocuments } from "@/lib/api";
import { DocumentRecord } from "@/lib/types";
import { UploadDialog } from "@/components/upload-dialog";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";

function formatSize(size: number) {
  if (size < 1024) return `${size} B`;
  if (size < 1024 * 1024) return `${(size / 1024).toFixed(1)} KB`;
  return `${(size / (1024 * 1024)).toFixed(1)} MB`;
}

function formatDate(value: string) {
  return new Date(value).toLocaleString("zh-CN", { hour12: false });
}

export function Sidebar() {
  const [documents, setDocuments] = useState<DocumentRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadDocuments = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const list = await fetchDocuments();
      setDocuments(list);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadDocuments();
  }, [loadDocuments]);

  return (
    <aside className="flex h-full w-80 flex-col border-r border-white/10 bg-slate-950/60">
      <div className="flex items-center justify-between px-4 py-4">
        <div>
          <p className="text-xs uppercase tracking-widest text-muted-foreground">RAG 控制台</p>
          <h1 className="text-lg font-semibold">文档中心</h1>
        </div>
        <Button size="icon" variant="ghost" onClick={loadDocuments} disabled={loading}>
          {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <RefreshCcw className="h-4 w-4" />}
        </Button>
      </div>
      <UploadDialog onUploaded={loadDocuments} />
      <Separator className="bg-white/10" />
      <div className="px-4 py-2 text-xs text-muted-foreground">历史文档</div>
      <ScrollArea className="flex-1 px-4 pb-6">
        {error && <p className="mb-3 text-sm text-red-400">{error}</p>}
        {!error && documents.length === 0 && !loading && (
          <p className="text-sm text-muted-foreground">暂未上传任何文档</p>
        )}
        <div className="space-y-3">
          {documents.map((doc) => (
            <div
              key={doc.document_id}
              className="rounded-xl border border-white/10 bg-white/5 p-3 shadow-sm backdrop-blur"
            >
              <div className="flex items-center gap-2">
                <FileText className="h-4 w-4 text-primary" />
                <p className="text-sm font-medium">{doc.filename}</p>
              </div>
              <div className="mt-2 grid grid-cols-2 gap-2 text-xs text-muted-foreground">
                <span>{formatSize(doc.size)}</span>
                <span className="text-right">{doc.content_type ?? "未知类型"}</span>
                <span className="col-span-2">上传时间：{formatDate(doc.uploaded_at)}</span>
              </div>
            </div>
          ))}
        </div>
      </ScrollArea>
    </aside>
  );
}
