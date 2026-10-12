import { useState, useEffect } from "react";
import { EvidenceLab } from "./components/layout/EvidenceLab";
import { useDocuments } from "./hooks/useDocuments";
import { useChat } from "./hooks/useChat";
import { Header } from "./components/layout/Header";
import { Sidebar } from "./components/layout/Sidebar";
import { MainWorkspace } from "./components/layout/MainWorkspace";
import { EvidencePanel } from "./components/evidence/EvidencePanel";
import { EvidenceDrawer } from "./components/evidence/EvidenceDrawer";
import { api } from "./services/api";
import { HealthResponse } from "./types";

export function App() {
  const [demoBusy, setDemoBusy] = useState(false);
  const [demoError, setDemoError] = useState("");
  const [view, setView] = useState("ask");
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [isEvidencePanelOpen, setIsEvidencePanelOpen] = useState<boolean>(true);
  const [isSidebarOpen, setIsSidebarOpen] = useState<boolean>(false);

  const {
    documents,
    refreshDocuments,
    error: documentError,
    selectedDocId,
    setSelectedDocId,
    uploadFile,
    deleteDocument,
    clearAll,
    isUploading,
    uploadProgress,
    allSuggestedQuestions,
  } = useDocuments();

  const {
    messages,
    isQuerying,
    queryStep,
    selectedEvidence,
    isEvidenceDrawerOpen,
    openEvidence,
    closeEvidence,
    chatError,
    sendQuery,
    clearMessages,
  } = useChat();

  useEffect(() => {
    api
      .getHealth()
      .then(setHealth)
      .catch(() => {});
  }, []);

  const loadDemo = async () => {
    setDemoBusy(true);
    setDemoError("");
    try {
      const response = await fetch("/api/demo", { method: "POST" });
      if (!response.ok)
        throw new Error("Policy demo could not be loaded. Please retry.");
      await refreshDocuments();
      setSelectedDocId(null);
      setView("ask");
    } catch (error) {
      setDemoError(error instanceof Error ? error.message : "Demo failed.");
    } finally {
      setDemoBusy(false);
    }
  };

  const handleSelectEvidence = (evidence: any) => {
    openEvidence(evidence);
    setIsEvidencePanelOpen(true);
  };

  const handleCloseEvidencePanel = () => {
    setIsEvidencePanelOpen(false);
    closeEvidence();
  };

  const handleToggleEvidence = () => {
    const isMobile =
      typeof window !== "undefined" &&
      window.matchMedia("(max-width: 1023px)").matches;
    if (isMobile) {
      if (selectedEvidence) {
        openEvidence(selectedEvidence);
      }
      return;
    }
    setIsEvidencePanelOpen((prev) => !prev);
  };

  return (
    <div className="flex flex-col h-screen w-screen overflow-hidden bg-[#F8FAFC] text-slate-900">
      {/* Top Header */}
      <Header
        health={health}
        onToggleSidebar={() => setIsSidebarOpen((prev) => !prev)}
        onToggleEvidence={handleToggleEvidence}
        isEvidenceOpen={isEvidencePanelOpen}
        onClearChat={clearMessages}
        hasMessages={messages.length > 0}
      />

      <nav
        className="flex flex-wrap items-center gap-2 px-5 py-3 border-b bg-white"
        aria-label="Workspace views"
      >
        <button
          className={`px-4 py-2 rounded-lg text-sm font-medium ${view === "ask" ? "bg-slate-900 text-white" : "text-slate-500 hover:bg-slate-100"}`}
          aria-pressed={view === "ask"}
          onClick={() => setView("ask")}
        >
          Ask & verify
        </button>
        <button
          className={`px-4 py-2 rounded-lg text-sm font-medium ${view === "lab" ? "bg-slate-900 text-white" : "text-slate-500 hover:bg-slate-100"}`}
          aria-pressed={view === "lab"}
          onClick={() => setView("lab")}
        >
          Compare & evaluate
        </button>
        <div className="flex-1" />
        <button
          onClick={() => refreshDocuments()}
          className="text-xs text-slate-600 px-3 py-2 border rounded-lg"
        >
          Refresh documents
        </button>
        <button
          disabled={demoBusy}
          onClick={loadDemo}
          className="text-xs font-semibold text-brand-700 bg-brand-50 border border-brand-200 px-3 py-2 rounded-lg disabled:opacity-50"
        >
          {demoBusy ? "Indexing policies..." : "Load policy demonstration"}
        </button>
      </nav>
      {(demoError || documentError) && (
        <p role="alert" className="bg-rose-50 px-5 py-2 text-sm text-rose-700">
          {demoError || documentError}
        </p>
      )}
      {documents.some((d) => d.filename === "Employee_Policy_2025.txt") &&
        view === "ask" && (
          <div className="flex flex-wrap gap-2 px-5 py-2 border-b bg-slate-50">
            <span className="text-xs text-slate-500 self-center">
              Policy demonstration
            </span>
            {[
              "How many annual leave days do employees receive in each policy version?",
              "How many remote work days per week are allowed in each policy version?",
              "What is the employee stock option vesting schedule?",
            ].map((q, i) => (
              <button
                key={q}
                disabled={isQuerying}
                onClick={() => {
                  setSelectedDocId(null);
                  sendQuery(q, null);
                }}
                className="text-xs border bg-white rounded-full px-3 py-1 hover:border-brand-400"
              >
                {["Compare leave", "Inspect remote work", "Test refusal"][i]}
              </button>
            ))}
          </div>
        )}
      {/* 3-Column Workspace Layout */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Sidebar */}
        <Sidebar
          documents={documents}
          selectedDocId={selectedDocId}
          onSelectDoc={(id) => {
            setSelectedDocId(id);
            setIsSidebarOpen(false);
          }}
          onDeleteDoc={deleteDocument}
          onClearAll={clearAll}
          onUpload={uploadFile}
          isUploading={isUploading}
          uploadProgress={uploadProgress}
          isOpen={isSidebarOpen}
          onClose={() => setIsSidebarOpen(false)}
        />

        {/* Center Main Workspace */}
        {view === "lab" ? (
          <EvidenceLab documents={documents} onSource={handleSelectEvidence} />
        ) : (
          <MainWorkspace
            messages={messages}
            isQuerying={isQuerying}
            queryStep={queryStep}
            hasDocuments={documents.length > 0}
            suggestedQuestions={allSuggestedQuestions}
            chatError={chatError}
            onSendQuery={(q) => sendQuery(q, selectedDocId)}
            onSelectEvidence={handleSelectEvidence}
          />
        )}

        {/* Right Desktop Evidence Panel */}
        <div className="hidden lg:block h-full">
          <EvidencePanel
            selectedEvidence={selectedEvidence}
            onClose={handleCloseEvidencePanel}
            isOpen={isEvidencePanelOpen}
          />
        </div>
      </div>

      {/* Mobile/Compact Screen Evidence Drawer */}
      <EvidenceDrawer
        evidence={selectedEvidence}
        isOpen={isEvidenceDrawerOpen}
        onClose={closeEvidence}
      />
    </div>
  );
}

export default App;
