import React from "react";
import { FileText, MessageCircle, BarChart3 } from "lucide-react";
import logoUrl from "../images/logo.png";

const Sidebar = ({ activeView, setActiveView, classifiedTickets }) => {
  return (
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
        
        <button
          onClick={() => setActiveView("reports")}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.75rem',
            padding: '0.75rem 1rem',
            backgroundColor: activeView === "reports" ? '#e0e7ff' : 'transparent',
            color: activeView === "reports" ? '#3730a3' : '#64748b',
            border: 'none',
            borderRadius: '0.5rem',
            cursor: 'pointer',
            fontSize: '0.875rem'
          }}
        >
          <BarChart3 size={16} />
          Analytics & Reports
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
  );
};

export default Sidebar;
