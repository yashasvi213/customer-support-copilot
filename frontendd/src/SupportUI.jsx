import React, { useState, useEffect, useRef } from "react";
import logoUrl from "./images/logo.png";
import { 
  MessageCircle, 
  Send, 
  Bot, 
  User, 
  Clock,
  Tag,
  AlertTriangle,
  CheckCircle,
  FileText,
  Search
} from "lucide-react";
import ReactMarkdown from "react-markdown";

const API_URL = "http://localhost:5000";

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
  const messagesEndRef = useRef(null);

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

  // Load and classify tickets on component mount
  useEffect(() => {
    const loadTickets = async () => {
      setIsLoadingTable(true);
      setFileLoadingError("");
      try {
        const resp = await fetch(`${API_URL}/bulk_classify`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({}) });
        const data = await resp.json();
        if (!resp.ok) {
          throw new Error(data?.error || 'Failed to load tickets');
        }
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
      } catch (e) {
        console.error(e);
        setFileLoadingError(String(e.message || e));
      }
      setIsLoadingTable(false);
    };
    loadTickets();
  }, []);

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
      setTicketResponses(prev => ({ ...prev, [ticket.id]: finalText }));
    } catch (e) {
      console.error(e);
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
      {/* Sidebar */}
      <div style={{
        width: '300px',
        backgroundColor: 'white',
        borderRight: '1px solid #e2e8f0',
        padding: '1.5rem'
      }}>
        <div style={{ marginBottom: '2rem', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
          <img src={logoUrl} alt="Atlan" style={{ height: '24px', width: 'auto', display: 'block', objectFit: 'contain', opacity: 0.98 }} />
          <h1 style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#1e293b', margin: 0 }}>
            Atlan Customer Support
          </h1>
        </div>

        <nav style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
          <button
            onClick={() => setActiveView("dashboard")}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.75rem',
              padding: '0.75rem 1rem',
              backgroundColor: activeView === "dashboard" ? '#e0e7ff' : 'transparent',
              color: activeView === "dashboard" ? '#3730a3' : '#64748b',
              border: 'none',
              borderRadius: '0.5rem',
              cursor: 'pointer',
              fontSize: '0.875rem'
            }}
          >
            <FileText size={16} />
            Bulk Classification
          </button>
          
          <button
            onClick={() => setActiveView("chat")}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.75rem',
              padding: '0.75rem 1rem',
              backgroundColor: activeView === "chat" ? '#e0e7ff' : 'transparent',
              color: activeView === "chat" ? '#3730a3' : '#64748b',
              border: 'none',
              borderRadius: '0.5rem',
              cursor: 'pointer',
              fontSize: '0.875rem'
            }}
          >
            <MessageCircle size={16} />
            Interactive Agent
          </button>
        </nav>

        <div style={{ marginTop: '2rem', padding: '1rem', backgroundColor: '#f1f5f9', borderRadius: '0.5rem' }}>
          <h3 style={{ fontSize: '0.875rem', fontWeight: '600', color: '#374151', marginBottom: '0.5rem' }}>
            Classification Stats
          </h3>
          <div style={{ fontSize: '0.75rem', color: '#6b7280' }}>
            <div>Total Tickets: {classifiedTickets.length}</div>
            <div>P0 Priority: {classifiedTickets.filter(t => t.classification.priority === 'P0').length}</div>
            <div>Automated: {classifiedTickets.filter(t => ['How-to', 'Product', 'Best practices', 'API/SDK', 'SSO'].includes(t.classification.topic)).length}</div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
        {activeView === "dashboard" ? (
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
                  setIsLoadingTable(true);
                  const resp = await fetch(`${API_URL}/bulk_classify`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ tickets: parsed }) });
                  const data = await resp.json();
                  if (!resp.ok) throw new Error(data?.error || 'Failed to classify uploaded file');
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
                } catch (err) {
                  setFileLoadingError(String(err.message || err));
                } finally {
                  setIsLoadingTable(false);
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

            <div style={{ backgroundColor: 'white', border: '1px solid #e5e7eb', borderRadius: '0.75rem' }}>
              <div style={{ display: 'grid', gridTemplateColumns: '120px 1.8fr 1fr 1fr 120px', padding: '0.75rem 1rem', borderBottom: '1px solid #e5e7eb', fontSize: '0.8rem', color: '#6b7280', background: '#f9fafb', fontWeight: 600 }}>
                <div>ID</div>
                <div>Subject</div>
                <div>Topic</div>
                <div>Sentiment</div>
                <div>Priority</div>
              </div>
              {isLoadingTable ? (
                <div style={{ padding: '1rem', color: '#6b7280' }}>Loading tickets...</div>
              ) : classifiedTickets.map((ticket) => (
                <div key={ticket.id} style={{ borderTop: '1px solid #f3f4f6', padding: '0.75rem 1rem' }}>
                  <div style={{ display: 'grid', gridTemplateColumns: '120px 1.8fr 1fr 1fr 120px', alignItems: 'center', gap: '0.5rem' }}>
                    <div style={{ fontSize: '0.8rem', color: '#475569' }}>#{ticket.id}</div>
                    <div style={{ fontSize: '0.9rem', color: '#111827' }}>{ticket.subject}</div>
                    <div style={{ fontSize: '0.85rem', color: '#1f2937' }}>{ticket.classification.topic}</div>
                    <div style={{ fontSize: '0.85rem' }}>{ticket.classification.sentiment}</div>
                    <div>
                      <span style={{ padding: '0.125rem 0.5rem', border: `1px solid ${getPriorityColor(ticket.classification.priority)}`, color: getPriorityColor(ticket.classification.priority), borderRadius: '0.375rem', fontSize: '0.75rem' }}>
                        {ticket.classification.priority}
                      </span>
                    </div>
                  </div>
                  <div style={{ marginTop: '0.5rem', color: '#334155', lineHeight: 1.55 }}>{ticket.body}</div>
                  <div style={{ marginTop: '0.75rem' }}>
                    <button onClick={() => handleGenerateResponseForTicket(ticket)} style={{ border: '1px solid #3b82f6', color: '#3b82f6', background: 'transparent', padding: '0.375rem 0.75rem', borderRadius: '0.375rem', cursor: 'pointer' }}>Generate response</button>
                  </div>
                  {ticketResponses[ticket.id] && (
                    <div style={{ marginTop: '0.75rem', backgroundColor: '#f9fafb', border: '1px solid #e5e7eb', borderRadius: '0.5rem', padding: '1rem' }}>
                      {renderResponse(ticketResponses[ticket.id])}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        ) : (
          // Interactive AI Agent
          <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
            {/* Header */}
            <div style={{
              padding: '1.5rem 2rem',
              backgroundColor: 'white',
              borderBottom: '1px solid #e2e8f0'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                <div style={{
                  width: '40px',
                  height: '40px',
                  backgroundColor: '#3b82f6',
                  borderRadius: '50%',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center'
                }}>
                  <Bot size={20} color="white" />
                </div>
                <div>
                  <h2 style={{ fontSize: '1.125rem', fontWeight: '600', color: '#1e293b', margin: 0 }}>
                    Atlan AI Support Agent
                  </h2>
                  <p style={{ fontSize: '0.875rem', color: '#64748b', margin: 0 }}>
                    {isAnalyzing ? "Analyzing your request..." : "Ready to help with classification and responses"}
                  </p>
                </div>
              </div>
            </div>

            {/* Content Area */}
            <div style={{ 
              flex: 1, 
              padding: '2rem',
              overflow: 'auto',
              display: 'flex',
              flexDirection: 'column',
              gap: '2rem'
            }}>
              {currentAnalysis && (
                <>
                  {/* Internal Analysis View */}
                  <div style={{ backgroundColor: '#f8fafc', border: '1px solid #e5e7eb', borderRadius: '0.5rem', padding: '1rem' }}>
                    <h3 style={{ 
                      fontSize: '1rem', 
                      fontWeight: '600', 
                      color: '#374151',
                      marginBottom: '1rem',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '0.5rem'
                    }}>
                      <Search size={16} />
                      AI Internal Analysis 
                    </h3>
                    
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
                      <div style={{ padding: '1rem', backgroundColor: 'white', borderRadius: '0.5rem', border: '1px solid #e5e7eb' }}>
                        <div style={{ fontSize: '0.75rem', color: '#6b7280', marginBottom: '0.5rem', fontWeight: '600', textTransform: 'uppercase' }}>
                          Topic Classification
                        </div>
                        <div style={{ fontSize: '0.8rem', color: '#6b7280', fontWeight: '500' }}>
                          {currentAnalysis.topic}
                        </div>
                      </div>
                      
                      <div style={{ padding: '1rem', backgroundColor: 'white', borderRadius: '0.5rem', border: '1px solid #e5e7eb' }}>
                        <div style={{ fontSize: '0.75rem', color: '#6b7280', marginBottom: '0.5rem', fontWeight: '600', textTransform: 'uppercase' }}>
                          Sentiment
                        </div>
                      </div>
                      
                      <div style={{ padding: '1rem', backgroundColor: 'white', borderRadius: '0.5rem', border: '1px solid #e5e7eb' }}>
                        <div style={{ fontSize: '0.75rem', color: '#6b7280', marginBottom: '0.5rem', fontWeight: '600', textTransform: 'uppercase' }}>
                          Priority
                        </div>
                        <div style={{ fontSize: '0.8rem', fontWeight: '500', color: '#6b7280' }}>
                          {currentAnalysis.priority} ({currentAnalysis.priority === 'P0' ? 'High' : 
                                                   currentAnalysis.priority === 'P1' ? 'Medium' : 'Low'})
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Final Response View */}
                  <div style={{
                    backgroundColor: 'white',
                    border: '1px solid #e2e8f0',
                    borderRadius: '0.75rem',
                    padding: '1.5rem'
                  }}>
                    <h3 style={{ 
                      fontSize: '1rem', 
                      fontWeight: '600', 
                      color: '#374151',
                      marginBottom: '1rem',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '0.5rem'
                    }}>
                      <MessageCircle size={16} />
                      AI Response 
                    </h3>
                    
                    <div style={{ backgroundColor: '#f9fafb', border: '1px solid #e5e7eb', borderRadius: '0.5rem', padding: '1rem' }}>
                      {renderResponse(currentResponse)}
                    </div>
                  </div>
                </>
              )}
            </div>

            {/* Input Area */}
            <div style={{
              padding: '1.5rem 2rem',
              backgroundColor: 'white',
              borderTop: '1px solid #e2e8f0'
            }}>
              <div style={{ display: 'flex', gap: '1rem', alignItems: 'end' }}>
                <div style={{ flex: 1 }}>
                  <label style={{ 
                    display: 'block', 
                    fontSize: '0.875rem', 
                    fontWeight: '500', 
                    color: '#374151', 
                    marginBottom: '0.5rem' 
                  }}>
                    Submit a new support ticket
                  </label>
                  <textarea
                    value={newTicketText}
                    onChange={(e) => setNewTicketText(e.target.value)}
                    placeholder="Describe your issue or question here..."
                    style={{
                      width: '100%',
                      minHeight: '100px',
                      padding: '0.75rem',
                      border: '1px solid #d1d5db',
                      borderRadius: '0.5rem',
                      fontSize: '0.875rem',
                      resize: 'vertical',
                      fontFamily: 'inherit'
                    }}
                    disabled={isAnalyzing}
                  />
                </div>
                <button
                  onClick={handleNewTicketSubmit}
                  disabled={!newTicketText.trim() || isAnalyzing}
                  style={{
                    padding: '0.75rem 1.5rem',
                    backgroundColor: !newTicketText.trim() || isAnalyzing ? '#9ca3af' : '#3b82f6',
                    color: 'white',
                    border: 'none',
                    borderRadius: '0.5rem',
                    cursor: !newTicketText.trim() || isAnalyzing ? 'not-allowed' : 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.5rem',
                    fontSize: '0.875rem',
                    fontWeight: '500'
                  }}
                >
                  {isAnalyzing ? (
                    <>
                      <div style={{
                        width: '16px',
                        height: '16px',
                        border: '2px solid rgba(255,255,255,0.3)',
                        borderTop: '2px solid white',
                        borderRadius: '50%',
                        animation: 'spin 1s linear infinite'
                      }} />
                      Analyzing...
                    </>
                  ) : (
                    <>
                      <Send size={16} />
                      Analyze
                    </>
                  )}
                </button>
              </div>
              <p style={{ fontSize: '0.75rem', color: '#6b7280', marginTop: '0.5rem' }}>
                The AI will classify your ticket and provide an appropriate response based on the topic
              </p>
            </div>
          </div>
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