import json
import time
import matplotlib.pyplot as plt
import seaborn as sns
from typing import List, Dict, Any
try:
    from graph import run_rag_graph, run_classification_only
except ImportError:
    from backend.graph import run_rag_graph, run_classification_only
import pandas as pd

class EvaluationMetrics:
    def __init__(self):
        self.results = []
    
    def evaluate_classification(self, test_tickets: List[Dict[str, Any]]) -> Dict[str, Any]:
        start_time = time.time()
        results = []
        
        for ticket in test_tickets:
            text = f"{ticket.get('subject','')}\n{ticket.get('body','')}".strip()
            ticket_start = time.time()
            
            try:
                result = run_classification_only(text)
                processing_time = time.time() - ticket_start
                
                results.append({
                    "id": ticket.get("id"),
                    "processing_time": processing_time,
                    "classification": result["classification"],
                    "resolution_decision": result["resolution_decision"],
                    "success": True
                })
            except Exception as e:
                processing_time = time.time() - ticket_start
                results.append({
                    "id": ticket.get("id"),
                    "processing_time": processing_time,
                    "error": str(e),
                    "success": False
                })
        
        total_time = time.time() - start_time
        
        successful = [r for r in results if r["success"]]
        success_rate = len(successful) / len(results) if results else 0
        avg_processing_time = sum(r["processing_time"] for r in successful) / len(successful) if successful else 0
        
        topics = {}
        for result in successful:
            labels = result["classification"].get("label", [])
            for label in labels:
                topics[label] = topics.get(label, 0) + 1
        
        priorities = {}
        for result in successful:
            priority = result["classification"].get("priority", "P2")
            priorities[priority] = priorities.get(priority, 0) + 1
        
        sentiments = {}
        for result in successful:
            sentiment = result["classification"].get("sentiment", "Neutral")
            sentiments[sentiment] = sentiments.get(sentiment, 0) + 1
        
        return {
            "total_tickets": len(results),
            "successful_classifications": len(successful),
            "success_rate": success_rate,
            "total_processing_time": total_time,
            "avg_processing_time_per_ticket": avg_processing_time,
            "topic_distribution": topics,
            "priority_distribution": priorities,
            "sentiment_distribution": sentiments,
            "results": results
        }
    
    def evaluate_rag_performance(self, test_questions: List[str]) -> Dict[str, Any]:
        start_time = time.time()
        results = []
        
        for question in test_questions:
            question_start = time.time()
            
            try:
                result = run_rag_graph(question)
                processing_time = time.time() - question_start
                
                results.append({
                    "question": question,
                    "processing_time": processing_time,
                    "confidence": result.get("confidence", 0.0),
                    "answer_length": len(result.get("answer", "")),
                    "sources_count": len(result.get("sources", [])),
                    "needs_rag": result.get("resolution_decision", {}).get("needs_rag", False),
                    "routing_team": result.get("resolution_decision", {}).get("routing_team", "Unknown"),
                    "success": True
                })
            except Exception as e:
                processing_time = time.time() - question_start
                results.append({
                    "question": question,
                    "processing_time": processing_time,
                    "error": str(e),
                    "success": False
                })
        
        total_time = time.time() - start_time
        
        successful = [r for r in results if r["success"]]
        success_rate = len(successful) / len(results) if results else 0
        avg_processing_time = sum(r["processing_time"] for r in successful) / len(successful) if successful else 0
        avg_confidence = sum(r["confidence"] for r in successful) / len(successful) if successful else 0
        
        return {
            "total_questions": len(results),
            "successful_rag": len(successful),
            "success_rate": success_rate,
            "total_processing_time": total_time,
            "avg_processing_time_per_question": avg_processing_time,
            "avg_confidence": avg_confidence,
            "results": results
        }
    
    def generate_visualizations(self, classification_metrics: Dict, rag_metrics: Dict, save_path: str = "evaluation_results"):
        plt.style.use('seaborn-v0_8')
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        fig.suptitle('Customer Support AI Agent Evaluation Results', fontsize=16, fontweight='bold')
        
        if classification_metrics.get("topic_distribution"):
            topics = classification_metrics["topic_distribution"]
            axes[0, 0].pie(topics.values(), labels=topics.keys(), autopct='%1.1f%%', startangle=90)
            axes[0, 0].set_title('Topic Distribution')
        
        if classification_metrics.get("priority_distribution"):
            priorities = classification_metrics["priority_distribution"]
            axes[0, 1].bar(priorities.keys(), priorities.values(), color=['red', 'orange', 'green', 'blue'])
            axes[0, 1].set_title('Priority Distribution')
            axes[0, 1].set_ylabel('Count')
        
        if classification_metrics.get("sentiment_distribution"):
            sentiments = classification_metrics["sentiment_distribution"]
            axes[0, 2].bar(sentiments.keys(), sentiments.values(), color=['red', 'orange', 'yellow', 'green'])
            axes[0, 2].set_title('Sentiment Distribution')
            axes[0, 2].set_ylabel('Count')
        
        if classification_metrics.get("results"):
            processing_times = [r["processing_time"] for r in classification_metrics["results"] if r["success"]]
            if processing_times:
                axes[1, 0].hist(processing_times, bins=20, alpha=0.7, color='skyblue', edgecolor='black')
                axes[1, 0].set_title('Classification Processing Time Distribution')
                axes[1, 0].set_xlabel('Time (seconds)')
                axes[1, 0].set_ylabel('Frequency')
        
        if rag_metrics.get("results"):
            confidences = [r["confidence"] for r in rag_metrics["results"] if r["success"]]
            if confidences:
                axes[1, 1].hist(confidences, bins=20, alpha=0.7, color='lightgreen', edgecolor='black')
                axes[1, 1].set_title('RAG Confidence Distribution')
                axes[1, 1].set_xlabel('Confidence Score')
                axes[1, 1].set_ylabel('Frequency')
        
        summary_data = {
            'Metric': ['Classification Success Rate', 'RAG Success Rate', 'Avg Classification Time', 'Avg RAG Time'],
            'Value': [
                f"{classification_metrics.get('success_rate', 0):.2%}",
                f"{rag_metrics.get('success_rate', 0):.2%}",
                f"{classification_metrics.get('avg_processing_time_per_ticket', 0):.2f}s",
                f"{rag_metrics.get('avg_processing_time_per_question', 0):.2f}s"
            ]
        }
        
        axes[1, 2].axis('tight')
        axes[1, 2].axis('off')
        table = axes[1, 2].table(cellText=[[summary_data['Metric'][i], summary_data['Value'][i]] for i in range(len(summary_data['Metric']))],
                               colLabels=['Metric', 'Value'],
                               cellLoc='center',
                               loc='center')
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        axes[1, 2].set_title('Performance Summary')
        
        plt.tight_layout()
        plt.savefig(f"{save_path}.png", dpi=300, bbox_inches='tight')
        plt.show()
        
        return f"{save_path}.png"
    
    def save_detailed_report(self, classification_metrics: Dict, rag_metrics: Dict, save_path: str = "evaluation_report.json"):
        report = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "classification_metrics": classification_metrics,
            "rag_metrics": rag_metrics,
            "summary": {
                "total_classification_tickets": classification_metrics.get("total_tickets", 0),
                "total_rag_questions": rag_metrics.get("total_questions", 0),
                "overall_classification_success_rate": classification_metrics.get("success_rate", 0),
                "overall_rag_success_rate": rag_metrics.get("success_rate", 0),
                "avg_classification_time": classification_metrics.get("avg_processing_time_per_ticket", 0),
                "avg_rag_time": rag_metrics.get("avg_processing_time_per_question", 0),
                "avg_rag_confidence": rag_metrics.get("avg_confidence", 0)
            }
        }
        
        with open(save_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        return save_path

def run_evaluation():
    evaluator = EvaluationMetrics()
    
    try:
        from services.data_loader import load_sample_tickets
    except ImportError:
        from backend.services.data_loader import load_sample_tickets
    test_tickets = load_sample_tickets()
    
    if not test_tickets:
        print("No test tickets found. Please ensure sample_tickets.json exists.")
        return
    
    test_questions = [f"{t.get('subject','')}\n{t.get('body','')}".strip() for t in test_tickets[:10]]
    
    print("Running classification evaluation...")
    classification_metrics = evaluator.evaluate_classification(test_tickets)
    
    print("Running RAG evaluation...")
    rag_metrics = evaluator.evaluate_rag_performance(test_questions)
    
    print("Generating visualizations...")
    chart_path = evaluator.generate_visualizations(classification_metrics, rag_metrics)
    
    print("Saving detailed report...")
    report_path = evaluator.save_detailed_report(classification_metrics, rag_metrics)
    
    print(f"\nEvaluation Complete!")
    print(f"Classification Success Rate: {classification_metrics['success_rate']:.2%}")
    print(f"RAG Success Rate: {rag_metrics['success_rate']:.2%}")
    print(f"Average Classification Time: {classification_metrics['avg_processing_time_per_ticket']:.2f}s")
    print(f"Average RAG Time: {rag_metrics['avg_processing_time_per_question']:.2f}s")
    print(f"Average RAG Confidence: {rag_metrics['avg_confidence']:.2f}")
    print(f"Charts saved to: {chart_path}")
    print(f"Detailed report saved to: {report_path}")

if __name__ == "__main__":
    run_evaluation()