import { API_BASE, handleResponse } from "@/lib/utils";
import { ChatResponse, DocumentRecord, UploadResponse } from "@/lib/types";

export async function fetchDocuments(): Promise<DocumentRecord[]> {
  const response = await fetch(`${API_BASE}/documents`, { cache: "no-store" });
  const payload = await handleResponse<{ documents: DocumentRecord[] }>(response);
  return payload.documents;
}

export async function uploadDocuments(files: FileList | File[]): Promise<UploadResponse[]> {
  const data = new FormData();
  Array.from(files).forEach((file) => data.append("files", file));
  const response = await fetch(`${API_BASE}/documents`, {
    method: "POST",
    body: data
  });
  return handleResponse<UploadResponse[]>(response);
}

export async function sendChat(message: string, topK = 4): Promise<ChatResponse> {
  const response = await fetch(`${API_BASE}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, top_k: topK })
  });
  return handleResponse<ChatResponse>(response);
}
