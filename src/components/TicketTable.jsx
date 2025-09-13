import React from "react";

const TicketTable = ({ 
  classifiedTickets, 
  isLoadingTable, 
  isStreaming, 
  handleGenerateResponseForTicket, 
  ticketResponses, 
  renderResponse, 
  getPriorityColor 
}) => {
  return (
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
      ) : isStreaming && classifiedTickets.length === 0 ? (
        <div style={{ padding: '1rem', color: '#6b7280' }}>Starting classification...</div>
      ) : (
        classifiedTickets.map((ticket) => (
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
        ))
      )}
    </div>
  );
};

export default TicketTable;
