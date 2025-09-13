import React from "react";
import { Bot, MessageCircle, Send, Search } from "lucide-react";

const InteractiveAgent = ({ 
  currentAnalysis, 
  currentResponse, 
  isAnalyzing, 
  newTicketText, 
  setNewTicketText, 
  handleNewTicketSubmit, 
  renderResponse 
}) => {
  return (
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
                  <div style={{ fontSize: '0.8rem', color: '#6b7280', fontWeight: '500' }}>
                    {currentAnalysis.sentiment}
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
  );
};

export default InteractiveAgent;
