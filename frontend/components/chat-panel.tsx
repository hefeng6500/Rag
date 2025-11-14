"use client";

import { FormEvent, useMemo, useState } from "react";
import { Bot, Loader2, Sparkles, User } from "lucide-react";

import { sendChat } from "@/lib/api";
import { ChatResponse } from "@/lib/types";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";

interface Message {
  role: "user" | "assistant";
  content: string;
  response?: ChatResponse;
}

export function ChatPanel() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [topK, setTopK] = useState(4);

  const lastResponse = useMemo(() => {
    const assistantMessages = messages.filter((msg) => msg.role === "assistant");
    return assistantMessages.length > 0 ? assistantMessages[assistantMessages.length - 1].response : undefined;
  }, [messages]);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!input.trim()) {
      return;
    }
    const question = input.trim();
    setMessages((prev) => [...prev, { role: "user", content: question }]);
    setInput("");
    setLoading(true);
    try {
      const response = await sendChat(question, topK);
      setMessages((prev) => [...prev, { role: "assistant", content: response.answer, response }]);
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: `请求失败：${(error as Error).message}` }
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex h-full flex-col">
      <header className="flex items-center justify-between border-b border-white/10 px-6 py-4">
        <div>
          <p className="text-xs uppercase tracking-widest text-muted-foreground">智能问答</p>
          <h2 className="text-xl font-semibold">Chat with Knowledge Base</h2>
        </div>
        <div className="text-right text-xs text-muted-foreground">
          {lastResponse ? (
            <p>
              {lastResponse.retrieval_used ? "已引用知识库" : "直接回答"} · 耗时 {lastResponse.latency_ms}ms
            </p>
          ) : (
            <p>准备就绪</p>
          )}
        </div>
      </header>
      <ScrollArea className="flex-1 px-6 py-6">
        <div className="space-y-6">
          {messages.map((message, index) => (
            <div
              key={index}
              className={`flex gap-4 ${message.role === "user" ? "flex-row-reverse text-right" : "flex-row"}`}
            >
              <div className="mt-1 rounded-full bg-white/10 p-2">
                {message.role === "user" ? <User className="h-4 w-4" /> : <Bot className="h-4 w-4" />}
              </div>
              <div className="flex-1 space-y-2 rounded-2xl border border-white/5 bg-white/5 p-4">
                <p className="text-sm leading-relaxed whitespace-pre-wrap">{message.content}</p>
                {message.role === "assistant" && message.response && (
                  <div className="rounded-xl border border-primary/40 bg-primary/5 p-3 text-left text-xs text-primary-foreground/80">
                    <p className="mb-2 flex items-center gap-2 font-semibold text-primary">
                      <Sparkles className="h-4 w-4" />
                      检索说明
                    </p>
                    <p className="mb-1 text-muted-foreground">
                      {message.response.retrieval_used
                        ? "已根据语义匹配读取向量数据库"
                        : "该问题较简单，直接由模型生成答案"}
                    </p>
                    <p className="text-muted-foreground">耗时 {message.response.latency_ms}ms</p>
                    <Separator className="my-3 bg-primary/30" />
                    {message.response.sources.length > 0 ? (
                      <div className="space-y-2">
                        {message.response.sources.map((source) => (
                          <div key={source.chunk_id} className="rounded-lg border border-white/10 bg-black/20 p-2">
                            <p className="text-xs font-semibold">{source.source}</p>
                            <p className="text-[11px] text-muted-foreground">片段 ID：{source.chunk_id}</p>
                            <p className="mt-1 text-xs text-slate-100">{source.content}</p>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p className="text-muted-foreground">未命中任何知识库片段</p>
                    )}
                  </div>
                )}
              </div>
            </div>
          ))}
          {loading && (
            <div className="flex items-center justify-center gap-2 text-sm text-muted-foreground">
              <Loader2 className="h-4 w-4 animate-spin" /> 正在生成回答...
            </div>
          )}
        </div>
      </ScrollArea>
      <form onSubmit={handleSubmit} className="border-t border-white/10 bg-slate-950/70 px-6 py-4">
        <div className="mb-3 flex items-center gap-4 text-xs text-muted-foreground">
          <label className="flex items-center gap-2">
            Top K
            <Input
              className="w-20"
              type="number"
              min={1}
              max={10}
              value={topK}
              onChange={(event) => {
                const parsed = Number(event.target.value);
                if (!Number.isNaN(parsed)) {
                  setTopK(Math.min(10, Math.max(1, parsed)));
                }
              }}
            />
          </label>
          <span>Enter 发送 · Shift+Enter 换行</span>
        </div>
        <Textarea
          value={input}
          onChange={(event) => setInput(event.target.value)}
          placeholder="请输入问题，例如：帮我总结最新的技术报告"
          onKeyDown={(event) => {
            if (event.key === "Enter" && !event.shiftKey) {
              event.preventDefault();
              (event.currentTarget.form as HTMLFormElement)?.requestSubmit();
            }
          }}
        />
        <div className="mt-3 flex justify-end">
          <Button type="submit" disabled={loading || !input.trim()}>
            {loading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Bot className="mr-2 h-4 w-4" />}
            发送
          </Button>
        </div>
      </form>
    </div>
  );
}
