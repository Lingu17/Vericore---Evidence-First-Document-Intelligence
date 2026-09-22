import { useState, useEffect } from 'react';
import { useDocuments } from './hooks/useDocuments';
import { useChat } from './hooks/useChat';
import { Header } from './components/layout/Header';
import { Sidebar } from './components/layout/Sidebar';
import { MainWorkspace } from './components/layout/MainWorkspace';
import { EvidencePanel } from './components/evidence/EvidencePanel';
import { EvidenceDrawer } from './components/evidence/EvidenceDrawer';
import { api } from './services/api';
import { HealthResponse } from './types';

export function App() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [isEvidencePanelOpen, setIsEvidencePanelOpen] = useState<boolean>(true);

  const {
    documents,
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
    api.getHealth().then(setHealth).catch(() => {});
  }, []);

  const handleSelectEvidence = (evidence: any) => {
    openEvidence(evidence);
    setIsEvidencePanelOpen(true);
  };

  const handleCloseEvidencePanel = () => {
    setIsEvidencePanelOpen(false);
    closeEvidence();
  };

  return (
    <div className="flex flex-col h-screen w-screen overflow-hidden bg-[#F8FAFC]">
      {/* Top Header */}
      <Header
        health={health}
        onToggleEvidence={() => setIsEvidencePanelOpen((prev) => !prev)}
        isEvidenceOpen={isEvidencePanelOpen}
        onClearChat={clearMessages}
        hasMessages={messages.length > 0}
      />

      {/* 3-Column Workspace Layout */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Sidebar */}
        <Sidebar
          documents={documents}
          selectedDocId={selectedDocId}
          onSelectDoc={setSelectedDocId}
          onDeleteDoc={deleteDocument}
          onClearAll={clearAll}
          onUpload={uploadFile}
          isUploading={isUploading}
          uploadProgress={uploadProgress}
        />

        {/* Center Main Workspace */}
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
