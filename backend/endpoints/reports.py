from flask import request, jsonify, Response
try:
    from services.data_loader import load_sample_tickets
    from graph import run_classification_only
except ImportError:
    from backend.services.data_loader import load_sample_tickets
    from backend.graph import run_classification_only
from typing import List, Dict, Any
import json
import time
from collections import Counter, defaultdict
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64

def generate_reports():
    """
    Input: { "ticket_ids": [...] } (optional - if not provided, uses all tickets)
    Output: Comprehensive analytics report with charts and insights
    """
    if request.method == "OPTIONS":
        return ("", 200)

    try:
        payload = request.json or {}
        ticket_ids = payload.get("ticket_ids", [])
        
        # Load tickets
        all_tickets = load_sample_tickets()
        if not all_tickets:
            return jsonify({"error": "No tickets found"}), 400
        
        # Filter by ticket IDs if provided
        if ticket_ids:
            tickets = [t for t in all_tickets if t.get("id") in ticket_ids]
        else:
            tickets = all_tickets
        
        # Generate analytics
        analytics = analyze_tickets(tickets)
        
        # Generate charts
        charts = generate_charts(analytics)
        
        # Generate insights
        insights = generate_insights(analytics)
        
        return jsonify({
            "analytics": analytics,
            "charts": charts,
            "insights": insights,
            "summary": {
                "total_tickets": len(tickets),
                "analysis_date": time.strftime("%Y-%m-%d %H:%M:%S"),
                "report_type": "comprehensive_analytics"
            }
        })
        
    except Exception as e:
        return jsonify({"error": f"Report generation failed: {str(e)}"}), 500

def analyze_tickets(tickets: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze tickets and generate comprehensive metrics"""
    
    # Basic stats
    total_tickets = len(tickets)
    
    # Classification analysis
    topics = Counter()
    sentiments = Counter()
    priorities = Counter()
    repeated_queries = Counter()
    high_priority_tickets = []
    
    # Process each ticket
    for ticket in tickets:
        try:
            text = f"{ticket.get('subject','')}\n{ticket.get('body','')}".strip()
            result = run_classification_only(text)
            classification = result["classification"]
            
            # Extract classification data
            labels = classification.get("label", [])
            sentiment = classification.get("sentiment", "Neutral")
            priority = classification.get("priority", "P2")
            
            # Update counters
            for label in labels:
                topics[label] += 1
            sentiments[sentiment] += 1
            priorities[priority] += 1
            
            # Track repeated queries (by subject similarity)
            subject_key = ticket.get('subject', '').lower().strip()
            repeated_queries[subject_key] += 1
            
            # Track high priority tickets
            if priority in ['P0', 'P1']:
                high_priority_tickets.append({
                    "id": ticket.get("id"),
                    "subject": ticket.get("subject"),
                    "priority": priority,
                    "sentiment": sentiment,
                    "topics": labels
                })
                
        except Exception as e:
            print(f"Error processing ticket {ticket.get('id')}: {e}")
            continue
    
    # Calculate metrics
    most_common_topics = topics.most_common(10)
    most_common_sentiments = sentiments.most_common()
    most_common_priorities = priorities.most_common()
    repeated_query_issues = [(query, count) for query, count in repeated_queries.items() if count > 1]
    
    # Time-based analysis (if tickets have timestamps)
    time_analysis = analyze_time_patterns(tickets)
    
    return {
        "total_tickets": total_tickets,
        "topic_distribution": dict(most_common_topics),
        "sentiment_distribution": dict(most_common_sentiments),
        "priority_distribution": dict(most_common_priorities),
        "repeated_queries": repeated_query_issues,
        "high_priority_tickets": high_priority_tickets,
        "time_analysis": time_analysis,
        "top_issues": {
            "most_common_topic": most_common_topics[0][0] if most_common_topics else "N/A",
            "most_common_sentiment": most_common_sentiments[0][0] if most_common_sentiments else "N/A",
            "high_priority_count": len(high_priority_tickets),
            "repeated_query_count": len(repeated_query_issues)
        }
    }

def analyze_time_patterns(tickets: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze time-based patterns in tickets"""
    # This would analyze patterns if tickets had timestamps
    # For now, return basic structure
    return {
        "hourly_distribution": {},
        "daily_distribution": {},
        "trend_analysis": "No timestamp data available"
    }

def generate_charts(analytics: Dict[str, Any]) -> Dict[str, str]:
    """Generate base64-encoded charts"""
    charts = {}
    
    try:
        # Set style
        plt.style.use('seaborn-v0_8')
        
        # 1. Topic Distribution Pie Chart
        if analytics.get("topic_distribution"):
            fig, ax = plt.subplots(figsize=(10, 8))
            topics = analytics["topic_distribution"]
            ax.pie(topics.values(), labels=topics.keys(), autopct='%1.1f%%', startangle=90)
            ax.set_title('Ticket Topics Distribution', fontsize=16, fontweight='bold')
            charts["topic_distribution"] = fig_to_base64(fig)
            plt.close(fig)
        
        # 2. Priority Distribution Bar Chart
        if analytics.get("priority_distribution"):
            fig, ax = plt.subplots(figsize=(10, 6))
            priorities = analytics["priority_distribution"]
            colors = {'P0': 'red', 'P1': 'orange', 'P2': 'green', 'P3': 'blue'}
            bars = ax.bar(priorities.keys(), priorities.values(), 
                         color=[colors.get(p, 'gray') for p in priorities.keys()])
            ax.set_title('Priority Distribution', fontsize=16, fontweight='bold')
            ax.set_ylabel('Number of Tickets')
            ax.set_xlabel('Priority Level')
            
            # Add value labels on bars
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{int(height)}', ha='center', va='bottom')
            
            charts["priority_distribution"] = fig_to_base64(fig)
            plt.close(fig)
        
        # 3. Sentiment Analysis
        if analytics.get("sentiment_distribution"):
            fig, ax = plt.subplots(figsize=(10, 6))
            sentiments = analytics["sentiment_distribution"]
            colors = {'Angry': 'red', 'Frustrated': 'orange', 'Neutral': 'gray', 'Curious': 'blue', 'Happy': 'green'}
            bars = ax.bar(sentiments.keys(), sentiments.values(),
                         color=[colors.get(s, 'gray') for s in sentiments.keys()])
            ax.set_title('Sentiment Analysis', fontsize=16, fontweight='bold')
            ax.set_ylabel('Number of Tickets')
            ax.set_xlabel('Sentiment')
            
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{int(height)}', ha='center', va='bottom')
            
            charts["sentiment_analysis"] = fig_to_base64(fig)
            plt.close(fig)
        
        # 4. High Priority Tickets Overview
        if analytics.get("high_priority_tickets"):
            fig, ax = plt.subplots(figsize=(12, 8))
            high_priority = analytics["high_priority_tickets"]
            
            # Group by priority and sentiment
            priority_sentiment = defaultdict(int)
            for ticket in high_priority:
                key = f"{ticket['priority']} - {ticket['sentiment']}"
                priority_sentiment[key] += 1
            
            if priority_sentiment:
                labels = list(priority_sentiment.keys())
                values = list(priority_sentiment.values())
                bars = ax.bar(labels, values, color=['red', 'orange', 'yellow', 'green'][:len(labels)])
                ax.set_title('High Priority Tickets by Sentiment', fontsize=16, fontweight='bold')
                ax.set_ylabel('Number of Tickets')
                ax.set_xlabel('Priority - Sentiment')
                plt.xticks(rotation=45)
                
                for bar in bars:
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2., height,
                           f'{int(height)}', ha='center', va='bottom')
            
            charts["high_priority_overview"] = fig_to_base64(fig)
            plt.close(fig)
        
    except Exception as e:
        print(f"Error generating charts: {e}")
        charts["error"] = f"Chart generation failed: {str(e)}"
    
    return charts

def generate_insights(analytics: Dict[str, Any]) -> List[Dict[str, str]]:
    """Generate actionable insights from analytics"""
    insights = []
    
    # High priority insights
    high_priority_count = analytics.get("top_issues", {}).get("high_priority_count", 0)
    if high_priority_count > 0:
        insights.append({
            "type": "warning",
            "title": "High Priority Tickets",
            "message": f"{high_priority_count} tickets require immediate attention",
            "action": "Review and prioritize resolution for P0/P1 tickets"
        })
    
    # Repeated queries insights
    repeated_count = analytics.get("top_issues", {}).get("repeated_query_count", 0)
    if repeated_count > 0:
        insights.append({
            "type": "info",
            "title": "Repeated Queries",
            "message": f"{repeated_count} query patterns appear multiple times",
            "action": "Consider creating FAQ or knowledge base entries"
        })
    
    # Topic insights
    topic_dist = analytics.get("topic_distribution", {})
    if topic_dist:
        most_common = max(topic_dist.items(), key=lambda x: x[1])
        insights.append({
            "type": "success",
            "title": "Most Common Issue",
            "message": f"'{most_common[0]}' is the most frequent topic ({most_common[1]} tickets)",
            "action": "Focus resources on improving this area"
        })
    
    # Sentiment insights
    sentiment_dist = analytics.get("sentiment_distribution", {})
    if sentiment_dist:
        negative_sentiments = sum(count for sentiment, count in sentiment_dist.items() 
                                if sentiment.lower() in ['angry', 'frustrated'])
        total_sentiments = sum(sentiment_dist.values())
        if total_sentiments > 0:
            negative_percentage = (negative_sentiments / total_sentiments) * 100
            if negative_percentage > 30:
                insights.append({
                    "type": "warning",
                    "title": "High Negative Sentiment",
                    "message": f"{negative_percentage:.1f}% of tickets show negative sentiment",
                    "action": "Review support processes and response times"
                })
    
    return insights

def fig_to_base64(fig):
    """Convert matplotlib figure to base64 string"""
    img_buffer = io.BytesIO()
    fig.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
    img_buffer.seek(0)
    img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
    return f"data:image/png;base64,{img_base64}"
