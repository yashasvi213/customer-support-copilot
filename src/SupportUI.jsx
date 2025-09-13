import React, { useState, useEffect } from "react";
import Sidebar from "./components/Sidebar";
import TicketTable from "./components/TicketTable";
import InteractiveAgent from "./components/InteractiveAgent";
import ReportsView from "./components/ReportsView";

const API_URL = "https://customer-support-backend-1052532391820.asia-south1.run.app";

const SupportDashboard = () => {
  const [classifiedTickets, setClassifiedTickets] = useState([]);
  const [newTicketText, setNewTicketText] = useState("");
  const [currentAnalysis, setCurrentAnalysis] = useState(null);
  const [currentResponse, setCurrentResponse] = useState("");
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [activeView, setActiveView] = useState("dashboard");
  const [ticketResponses, setTicketResponses] = useState({});
  const [isLoadingTable, setIsLoadingTable] = useState(false);
  const [fileLoadingError, setFileLoadingError] = useState("");
  const [streamingProgress, setStreamingProgress] = useState({ current: 0, total: 0 });
  const [isStreaming, setIsStreaming] = useState(false);
  const [reports, setReports] = useState(null);
  const [isGeneratingReports, setIsGeneratingReports] = useState(false);

  const inferSentiment = (text) => {
    const t = (text || "").toLowerCase();
    if (/(angry|furious|terrible|awful|hate|disgusted|mad|rage)/.test(t)) return "Angry";
    if (/(urgent|blocked|blocking|frustrated|hours|stuck|asap|critical|issue!|problem!|!)/.test(t)) return "Frustrated";
    if (/(curious|interested|wonder|could you|\?|how)/.test(t)) return "Curious";
    return "Neutral";
  };

  const renderResponse = (text) => {
    const lines = (text || "").split('\n');
    const elements = [];
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      const trimmed = line.trim();
      if (!trimmed) { elements.push(<br key={`br-${i}`} />); continue; }
      if (/^sources\s*:/i.test(trimmed)) {
        elements.push(<div key={`src-h-${i}`} style={{ fontWeight: 600, marginTop: '0.5rem' }}>Sources:</div>);
        continue;
      }
      // bullet sources like "- https://..."
      const bulletMatch = trimmed.match(/^-\s*(https?:\/\/\S+)/i);
      if (bulletMatch) {
        const url = bulletMatch[1];
        elements.push(
          <div key={`src-${i}`}>
            <a href={url} target="_blank" rel="noreferrer" style={{ color: '#2563eb' }}>{url}</a>
          </div>
        );
        continue;
      }
      // inline url in text
      const urlMatch = trimmed.match(/(https?:\/\/\S+)/i);
      if (urlMatch) {
        const url = urlMatch[1];
        const [before, after] = trimmed.split(url);
        elements.push(
          <div key={`p-${i}`}> 
            {before}
            <a href={url} target="_blank" rel="noreferrer" style={{ color: '#2563eb' }}>{url}</a>
            {after}
          </div>
        );
        continue;
      }
      elements.push(<div key={`p-${i}`}>{line}</div>);
    }
    return (
      <div style={{ whiteSpace: 'pre-wrap', lineHeight: 1.6, color: '#111827' }}>
        {elements}
      </div>
    );
  };

  // Load sample tickets on component mount
  useEffect(() => {
    const loadSampleTickets = async () => {
      try {
        const response = await fetch(`${API_URL}/bulk_classify`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({})
        });
        
        if (response.ok) {
          const data = await response.json();
          const results = data?.results || [];
          const mapped = results.map(r => ({
            id: r.id || Math.random().toString(36).slice(2),
            subject: (r.classification?.original_question || '').split('\n')[0],
            body: (r.classification?.original_question || ''),
            classification: {
              topic: (r.classification?.label || [])[0] || 'Product',
              sentiment: r.classification?.sentiment || 'Neutral',
              priority: r.classification?.priority || 'P2'
            }
          }));
          setClassifiedTickets(mapped);
        }
      } catch (e) {
        console.error('Failed to load sample tickets:', e);
      }
    };
    loadSampleTickets();
  }, []);

  // Function to handle streaming classification
  const loadTicketsStreaming = async (tickets) => {
    if (!tickets) return;
    
    setIsStreaming(true);
    setFileLoadingError("");
    setClassifiedTickets([]);
    setStreamingProgress({ current: 0, total: 0 });

    try {
      const response = await fetch(`${API_URL}/bulk_classify_stream`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Accept': 'text/event-stream'
        },
        body: JSON.stringify({ tickets }),
        cache: 'no-cache'
      });

      if (!response.ok) {
        throw new Error(`Failed to start streaming: ${response.status} ${response.statusText}`);
      }

      if (!response.body) {
        throw new Error('Response body is null - streaming not supported');
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.trim() === '') continue;
          
          if (line.startsWith('data: ')) {
            try {
              const jsonStr = line.slice(6).trim();
              if (jsonStr === '') continue;
              
              const data = JSON.parse(jsonStr);
              
              if (data.type === 'start') {
                setStreamingProgress({ current: 0, total: data.total });
              } else if (data.type === 'ticket') {
                const ticketData = data.data;
                const mappedTicket = {
                  id: ticketData.id || Math.random().toString(36).slice(2),
                  subject: (ticketData.classification?.original_question || '').split('\n')[0],
                  body: (ticketData.classification?.original_question || ''),
                  classification: {
                    topic: (ticketData.classification?.label || [])[0] || 'Product',
                    sentiment: ticketData.classification?.sentiment || 'Neutral',
                    priority: ticketData.classification?.priority || 'P2'
                  }
                };
                
                setClassifiedTickets(prev => [...prev, mappedTicket]);
                setStreamingProgress(prev => ({ ...prev, current: prev.current + 1 }));
              } else if (data.type === 'error') {
                console.error('Error processing ticket:', data.data);
                setStreamingProgress(prev => ({ ...prev, current: prev.current + 1 }));
              } else if (data.type === 'complete') {
                setIsStreaming(false);
                return;
              }
            } catch (e) {
              console.error('Error parsing SSE data:', e);
            }
          }
        }
      }
    } catch (e) {
      console.error('Streaming error:', e);
      setFileLoadingError(`Streaming failed: ${e.message}`);
      setIsStreaming(false);
    }
  };

  const handleNewTicketSubmit = async () => {
    if (!newTicketText.trim()) return;
    
    setIsAnalyzing(true);
    try {
      const classifyResp = await fetch(`${API_URL}/classify`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ question: newTicketText }) });
      const classification = (await classifyResp.json())?.classification;
      const analysis = {
        topic: (classification?.label || [])[0] || 'Product',
        sentiment: classification?.sentiment || inferSentiment(newTicketText),
        priority: classification?.priority || 'P2'
      };
      setCurrentAnalysis(analysis);
      const resolveResp = await fetch(`${API_URL}/resolve`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ classification }) });
      const resolution = await resolveResp.json();
      const finalText = resolution?.response || resolution?.routed_message || resolution?.reason || '';
      setCurrentResponse(finalText);
    } catch (e) {
      console.error(e);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleGenerateResponseForTicket = async (ticket) => {
    try {
      const question = `${ticket.subject}\n${ticket.body}`;
      const classifyResp = await fetch(`${API_URL}/classify`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ question }) });
      const classification = (await classifyResp.json())?.classification;
      const resolveResp = await fetch(`${API_URL}/resolve`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ classification }) });
      const resolution = await resolveResp.json();
      const finalText = resolution?.response || resolution?.routed_message || resolution?.reason || '';
      
      // Set the current analysis and response for the interactive agent
      setCurrentAnalysis({
        topic: (classification?.label || [])[0] || 'Product',
        sentiment: classification?.sentiment || 'Neutral',
        priority: classification?.priority || 'P2'
      });
      setCurrentResponse(finalText);
      
      // Switch to interactive agent view
      setActiveView("chat");
      
      // Also store in ticket responses for the dashboard view
      setTicketResponses(prev => ({ ...prev, [ticket.id]: finalText }));
    } catch (e) {
      console.error(e);
    }
  };

  const generateReports = async () => {
    setIsGeneratingReports(true);
    try {
      const response = await fetch(`${API_URL}/reports`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ tickets: classifiedTickets })
      });
      
      if (response.ok) {
        const data = await response.json();
        console.log('Reports data received:', data);
        // The backend returns data in {analytics, charts, insights, summary} structure
        setReports({
          analytics: data.analytics,
          charts: data.charts,
          insights: data.insights,
          summary: data.summary
        });
      } else {
        console.error('Failed to generate reports:', response.statusText);
      }
    } catch (e) {
      console.error('Error generating reports:', e);
    } finally {
      setIsGeneratingReports(false);
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case "P0": return "#dc2626"; // red
      case "P1": return "#f59e0b"; // amber  
      case "P2": return "#10b981"; // green
      default: return "#6b7280"; // gray
    }
  };

  return (
    <div style={{ 
      display: 'flex', 
      height: '100vh', 
      fontFamily: 'system-ui, -apple-system, sans-serif',
      backgroundColor: '#f8fafc'
    }}>
      <Sidebar 
        activeView={activeView} 
        setActiveView={setActiveView} 
        classifiedTickets={classifiedTickets} 
      />

      {/* Main Content */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
        {activeView === "reports" ? (
          <ReportsView 
            reports={reports}
            isGeneratingReports={isGeneratingReports}
            classifiedTickets={classifiedTickets}
            generateReports={generateReports}
          />
        ) : activeView === "dashboard" ? (
          // Bulk Classification Dashboard
          <div style={{ padding: '2rem', overflow: 'auto' }}>
            <div style={{ marginBottom: '2rem' }}>
              <h2 style={{ fontSize: '1.25rem', fontWeight: '600', color: '#1e293b', marginBottom: '0.5rem' }}>
                Ticket Classification Dashboard
              </h2>
              <p style={{ color: '#64748b', fontSize: '0.875rem' }}>
                AI-powered analysis of support tickets with topic classification, sentiment analysis, and priority scoring
              </p>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.75rem' }}>
              <input type="file" accept=".json" onChange={async (e) => {
                const file = e.target.files?.[0];
                if (!file) return;
                try {
                  const text = await file.text();
                  const parsed = JSON.parse(text);
                  await loadTicketsStreaming(parsed);
                } catch (err) {
                  setFileLoadingError(String(err.message || err));
                }
              }} />
              <div style={{ flex: 1 }} />
              <input
                placeholder="Quick classify a single question..."
                style={{ flexBasis: '50%', padding: '0.5rem 0.75rem', border: '1px solid #d1d5db', borderRadius: '0.5rem' }}
                value={newTicketText}
                onChange={(e) => setNewTicketText(e.target.value)}
                onKeyDown={(e) => { if (e.key === 'Enter') handleNewTicketSubmit(); }}
              />
              <button onClick={handleNewTicketSubmit} disabled={!newTicketText.trim() || isAnalyzing} style={{ border: '1px solid #3b82f6', background: '#3b82f6', color: 'white', padding: '0.5rem 0.75rem', borderRadius: '0.5rem', cursor: !newTicketText.trim() || isAnalyzing ? 'not-allowed' : 'pointer' }}>Analyze</button>
            </div>

            {fileLoadingError && <div style={{ color: '#b91c1c', fontSize: '0.8rem', marginBottom: '0.5rem' }}>{fileLoadingError}</div>}

            {/* Progress indicator for streaming */}
            {isStreaming && streamingProgress.total > 0 && (
              <div style={{ 
                backgroundColor: 'white', 
                border: '1px solid #e5e7eb', 
                borderRadius: '0.75rem', 
                padding: '1rem',
                marginBottom: '1rem'
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                  <span style={{ fontSize: '0.875rem', fontWeight: '500', color: '#374151' }}>
                    Processing tickets...
                  </span>
                  <span style={{ fontSize: '0.75rem', color: '#6b7280' }}>
                    {streamingProgress.current} / {streamingProgress.total}
                  </span>
                </div>
                <div style={{ 
                  width: '100%', 
                  height: '8px', 
                  backgroundColor: '#f3f4f6', 
                  borderRadius: '4px',
                  overflow: 'hidden'
                }}>
                  <div style={{
                    width: `${(streamingProgress.current / streamingProgress.total) * 100}%`,
                    height: '100%',
                    backgroundColor: '#3b82f6',
                    transition: 'width 0.3s ease'
                  }} />
                </div>
              </div>
            )}

            <TicketTable 
              classifiedTickets={classifiedTickets}
              isLoadingTable={isLoadingTable}
              isStreaming={isStreaming}
              handleGenerateResponseForTicket={handleGenerateResponseForTicket}
              ticketResponses={ticketResponses}
              renderResponse={renderResponse}
              getPriorityColor={getPriorityColor}
            />
          </div>
        ) : (
          <InteractiveAgent 
            currentAnalysis={currentAnalysis}
            currentResponse={currentResponse}
            isAnalyzing={isAnalyzing}
            newTicketText={newTicketText}
            setNewTicketText={setNewTicketText}
            handleNewTicketSubmit={handleNewTicketSubmit}
            renderResponse={renderResponse}
          />
        )}
      </div>
      
      <style>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
};

export default SupportDashboard;