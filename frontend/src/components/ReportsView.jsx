import React from "react";
import { BarChart3, RefreshCw, FileText, AlertCircle, TrendingUp } from "lucide-react";

const ReportsView = ({ 
  reports, 
  isGeneratingReports, 
  classifiedTickets, 
  generateReports 
}) => {
  return (
    <div style={{ padding: '2rem', overflow: 'auto' }}>
      <div style={{ marginBottom: '2rem' }}>
        <h2 style={{ fontSize: '1.25rem', fontWeight: '600', color: '#1e293b', marginBottom: '0.5rem' }}>
          Analytics & Reports
        </h2>
        <p style={{ color: '#64748b', fontSize: '0.875rem' }}>
          Generate comprehensive reports and analytics from your support tickets
        </p>
      </div>

      <div style={{ marginBottom: '2rem' }}>
        <button
          onClick={generateReports}
          disabled={isGeneratingReports || classifiedTickets.length === 0}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
            padding: '0.75rem 1.5rem',
            backgroundColor: isGeneratingReports || classifiedTickets.length === 0 ? '#9ca3af' : '#3b82f6',
            color: 'white',
            border: 'none',
            borderRadius: '0.5rem',
            cursor: isGeneratingReports || classifiedTickets.length === 0 ? 'not-allowed' : 'pointer',
            fontSize: '0.875rem',
            fontWeight: '500'
          }}
        >
          {isGeneratingReports ? (
            <>
              <RefreshCw size={16} style={{ animation: 'spin 1s linear infinite' }} />
              Generating Reports...
            </>
          ) : (
            <>
              <BarChart3 size={16} />
              Generate Reports
            </>
          )}
        </button>
        {classifiedTickets.length === 0 && (
          <p style={{ fontSize: '0.75rem', color: '#6b7280', marginTop: '0.5rem' }}>
            Upload and classify tickets first to generate reports
          </p>
        )}
      </div>

      {reports && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
          {/* Summary Cards */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
            <div style={{ backgroundColor: 'white', border: '1px solid #e5e7eb', borderRadius: '0.75rem', padding: '1.5rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
                <FileText size={20} color="#3b82f6" />
                <h3 style={{ fontSize: '0.875rem', fontWeight: '600', color: '#374151', margin: 0 }}>
                  Total Tickets
                </h3>
              </div>
              <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#1f2937' }}>
                {reports.summary?.total_tickets || 0}
              </div>
            </div>

            <div style={{ backgroundColor: 'white', border: '1px solid #e5e7eb', borderRadius: '0.75rem', padding: '1.5rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
                <AlertCircle size={20} color="#dc2626" />
                <h3 style={{ fontSize: '0.875rem', fontWeight: '600', color: '#374151', margin: 0 }}>
                  High Priority
                </h3>
              </div>
              <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#dc2626' }}>
                {reports.analytics?.high_priority_tickets?.length || 0}
              </div>
            </div>

            <div style={{ backgroundColor: 'white', border: '1px solid #e5e7eb', borderRadius: '0.75rem', padding: '1.5rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
                <TrendingUp size={20} color="#10b981" />
                <h3 style={{ fontSize: '0.875rem', fontWeight: '600', color: '#374151', margin: 0 }}>
                  Automation Rate
                </h3>
              </div>
              <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#10b981' }}>
                {reports.analytics?.automation_rate || 0}%
              </div>
            </div>

            <div style={{ backgroundColor: 'white', border: '1px solid #e5e7eb', borderRadius: '0.75rem', padding: '1.5rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
                <RefreshCw size={20} color="#f59e0b" />
                <h3 style={{ fontSize: '0.875rem', fontWeight: '600', color: '#374151', margin: 0 }}>
                  Repeated Queries
                </h3>
              </div>
              <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#f59e0b' }}>
                {reports.analytics?.repeated_queries?.length || 0}
              </div>
            </div>
          </div>

          {/* Charts */}
          {reports.charts && (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: '1.5rem' }}>
              {reports.charts.topic_distribution && (
                <div style={{ backgroundColor: 'white', border: '1px solid #e5e7eb', borderRadius: '0.75rem', padding: '1.5rem' }}>
                  <h3 style={{ fontSize: '1rem', fontWeight: '600', color: '#374151', marginBottom: '1rem' }}>
                    Topic Distribution
                  </h3>
                  <img 
                    src={reports.charts.topic_distribution.startsWith('data:') ? reports.charts.topic_distribution : `data:image/png;base64,${reports.charts.topic_distribution}`} 
                    alt="Topic Distribution" 
                    style={{ width: '100%', height: 'auto', borderRadius: '0.5rem' }}
                    onError={(e) => {
                      e.target.style.display = 'none';
                      e.target.nextSibling.style.display = 'block';
                    }}
                  />
                  <div style={{ display: 'none', padding: '2rem', textAlign: 'center', color: '#6b7280' }}>
                    Chart failed to load
                  </div>
                </div>
              )}

              {reports.charts.priority_distribution && (
                <div style={{ backgroundColor: 'white', border: '1px solid #e5e7eb', borderRadius: '0.75rem', padding: '1.5rem' }}>
                  <h3 style={{ fontSize: '1rem', fontWeight: '600', color: '#374151', marginBottom: '1rem' }}>
                    Priority Distribution
                  </h3>
                  <img 
                    src={reports.charts.priority_distribution.startsWith('data:') ? reports.charts.priority_distribution : `data:image/png;base64,${reports.charts.priority_distribution}`} 
                    alt="Priority Distribution" 
                    style={{ width: '100%', height: 'auto', borderRadius: '0.5rem' }}
                    onError={(e) => {
                      e.target.style.display = 'none';
                      e.target.nextSibling.style.display = 'block';
                    }}
                  />
                  <div style={{ display: 'none', padding: '2rem', textAlign: 'center', color: '#6b7280' }}>
                    Chart failed to load
                  </div>
                </div>
              )}

              {reports.charts.sentiment_analysis && (
                <div style={{ backgroundColor: 'white', border: '1px solid #e5e7eb', borderRadius: '0.75rem', padding: '1.5rem' }}>
                  <h3 style={{ fontSize: '1rem', fontWeight: '600', color: '#374151', marginBottom: '1rem' }}>
                    Sentiment Analysis
                  </h3>
                  <img 
                    src={reports.charts.sentiment_analysis.startsWith('data:') ? reports.charts.sentiment_analysis : `data:image/png;base64,${reports.charts.sentiment_analysis}`} 
                    alt="Sentiment Analysis" 
                    style={{ width: '100%', height: 'auto', borderRadius: '0.5rem' }}
                    onError={(e) => {
                      e.target.style.display = 'none';
                      e.target.nextSibling.style.display = 'block';
                    }}
                  />
                  <div style={{ display: 'none', padding: '2rem', textAlign: 'center', color: '#6b7280' }}>
                    Chart failed to load
                  </div>
                </div>
              )}

              {reports.charts.trend_analysis && (
                <div style={{ backgroundColor: 'white', border: '1px solid #e5e7eb', borderRadius: '0.75rem', padding: '1.5rem' }}>
                  <h3 style={{ fontSize: '1rem', fontWeight: '600', color: '#374151', marginBottom: '1rem' }}>
                    Trend Analysis
                  </h3>
                  <img 
                    src={reports.charts.trend_analysis.startsWith('data:') ? reports.charts.trend_analysis : `data:image/png;base64,${reports.charts.trend_analysis}`} 
                    alt="Trend Analysis" 
                    style={{ width: '100%', height: 'auto', borderRadius: '0.5rem' }}
                    onError={(e) => {
                      e.target.style.display = 'none';
                      e.target.nextSibling.style.display = 'block';
                    }}
                  />
                  <div style={{ display: 'none', padding: '2rem', textAlign: 'center', color: '#6b7280' }}>
                    Chart failed to load
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Insights */}
          {reports.insights && (
            <div style={{ backgroundColor: 'white', border: '1px solid #e5e7eb', borderRadius: '0.75rem', padding: '1.5rem' }}>
              <h3 style={{ fontSize: '1rem', fontWeight: '600', color: '#374151', marginBottom: '1rem' }}>
                Key Insights & Recommendations
              </h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                {reports.insights.map((insight, index) => (
                  <div key={index} style={{ 
                    padding: '1rem', 
                    backgroundColor: '#f8fafc', 
                    border: '1px solid #e2e8f0', 
                    borderRadius: '0.5rem' 
                  }}>
                    <div style={{ fontSize: '0.875rem', color: '#374151', lineHeight: 1.6 }}>
                      <div style={{ fontWeight: '600', marginBottom: '0.5rem', color: '#1f2937' }}>
                        {insight.title || `Insight ${index + 1}`}
                      </div>
                      <div style={{ marginBottom: '0.5rem' }}>
                        {insight.message}
                      </div>
                      {insight.action && (
                        <div style={{ 
                          fontSize: '0.8rem', 
                          color: '#3b82f6', 
                          fontStyle: 'italic',
                          padding: '0.5rem',
                          backgroundColor: '#eff6ff',
                          borderRadius: '0.375rem',
                          border: '1px solid #dbeafe'
                        }}>
                          💡 {insight.action}
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default ReportsView;
