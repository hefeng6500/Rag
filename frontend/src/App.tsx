import { useState } from "react";
import axios from "axios";

interface UploadSummary {
  document_id: string;
  filename: string;
  status: string;
}

const API_PREFIX = "/api/v1";

export default function App() {
  const [files, setFiles] = useState<FileList | null>(null);
  const [uploadSummaries, setUploadSummaries] = useState<UploadSummary[]>([]);
  const [question, setQuestion] = useState("Hello RAG platform!");
  const [answer, setAnswer] = useState("Send a question to view the response.");

  const handleUpload = async () => {
    if (!files?.length) return;
    const formData = new FormData();
    Array.from(files).forEach((file) => formData.append("files", file));
    const { data } = await axios.post<UploadSummary[]>(`${API_PREFIX}/documents`, formData, {
      headers: { "Content-Type": "multipart/form-data" }
    });
    setUploadSummaries(data);
  };

  const handleAsk = async () => {
    const { data } = await axios.post(`${API_PREFIX}/search`, { query: question });
    setAnswer(data.answer);
  };

  return (
    <main style={{ maxWidth: 960, margin: "0 auto", padding: "2rem" }}>
      <header>
        <h1>LangChain RAG Console</h1>
        <p>Stage 01 focuses on scaffolding the upload flow and API contract.</p>
      </header>

      <section style={{ marginBottom: "2rem" }}>
        <h2>1. Upload local files</h2>
        <input type="file" multiple onChange={(event) => setFiles(event.target.files)} />
        <button onClick={handleUpload} style={{ marginLeft: "1rem" }}>
          Upload
        </button>
        <ul>
          {uploadSummaries.map((summary) => (
            <li key={summary.document_id}>
              {summary.filename} – <strong>{summary.status}</strong>
            </li>
          ))}
        </ul>
      </section>

      <section>
        <h2>2. Ask a question</h2>
        <textarea
          rows={4}
          style={{ width: "100%" }}
          value={question}
          onChange={(event) => setQuestion(event.target.value)}
        />
        <div style={{ marginTop: "1rem" }}>
          <button onClick={handleAsk}>Send to RAG backend</button>
        </div>
        <article style={{ marginTop: "1rem", padding: "1rem", background: "white", borderRadius: 8 }}>
          <h3>Model answer</h3>
          <p>{answer}</p>
        </article>
      </section>
    </main>
  );
}
