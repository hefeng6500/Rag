import { ChatPanel } from "@/components/chat-panel";
import { Sidebar } from "@/components/sidebar";

export default function HomePage() {
  return (
    <div className="flex h-screen w-full overflow-hidden">
      <Sidebar />
      <main className="flex-1 bg-gradient-to-b from-slate-900 via-slate-900 to-slate-950">
        <ChatPanel />
      </main>
    </div>
  );
}
