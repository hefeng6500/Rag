import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "RAG 控制台",
  description: "用于管理文档知识库与对话的前端控制台"
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="zh-CN">
      <body className="min-h-screen bg-background text-foreground">{children}</body>
    </html>
  );
}
