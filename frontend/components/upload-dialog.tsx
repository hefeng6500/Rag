"use client";

import { ChangeEvent, useRef, useState } from "react";
import { Upload, Loader2 } from "lucide-react";

import { uploadDocuments } from "@/lib/api";
import { Button } from "@/components/ui/button";

interface UploadDialogProps {
  onUploaded?: () => void;
}

export function UploadDialog({ onUploaded }: UploadDialogProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [status, setStatus] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleChange = async (event: ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (!files || files.length === 0) {
      return;
    }
    setLoading(true);
    setStatus(null);
    try {
      const result = await uploadDocuments(files);
      const chunkCount = result.reduce((sum, item) => sum + item.chunks_indexed, 0);
      setStatus(`成功索引 ${chunkCount} 条切片`);
      onUploaded?.();
    } catch (error) {
      setStatus((error as Error).message);
    } finally {
      setLoading(false);
      event.target.value = "";
    }
  };

  return (
    <div className="px-4 pb-4">
      <input ref={inputRef} type="file" multiple className="hidden" onChange={handleChange} />
      <Button
        className="w-full"
        onClick={() => inputRef.current?.click()}
        disabled={loading}
        variant="secondary"
      >
        {loading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Upload className="mr-2 h-4 w-4" />}
        {loading ? "正在上传" : "上传新文档"}
      </Button>
      {status && <p className="mt-2 text-xs text-muted-foreground">{status}</p>}
    </div>
  );
}
