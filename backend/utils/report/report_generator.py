from fpdf import FPDF
from typing import Dict
from datetime import datetime

def generate_report(data: Dict) -> bytes:
    """Generate a PDF report from the processed data"""
    try:
        # Initialize PDF
        pdf = FPDF()
        pdf.add_page()
        
        # Title
        pdf.set_font('Times', 'B', 16)
        pdf.cell(0, 10, 'Design Thinking Analysis Report', 0, 1, 'C')
        
        # Add date
        pdf.set_font('Times', '', 10)
        pdf.cell(0, 10, f'Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', 0, 1)
        
        # Problem Statement
        if data.get('problem_statement'):
            pdf.set_font('Times', 'B', 14)
            pdf.cell(0, 10, 'Problem Statement', 0, 1)
            
            pdf.set_font('Times', '', 10)
            text = str(data['problem_statement']).encode('ascii', errors='ignore').decode()
            pdf.multi_cell(0, 10, text)
        
        # Affinity Map
        if data.get('clustering'):
            pdf.set_font('Times', 'B', 14)
            pdf.cell(0, 10, 'Affinity Map', 0, 1)
            
            clusters = data['clustering']['clusters']
            for cluster_id, cluster_items in clusters.items():
                # Theme header
                pdf.set_font('Times', 'B', 12)
                pdf.cell(0, 10, f'Theme {cluster_id + 1}', 0, 1)
                
                # Process statements
                for item in cluster_items:
                    pdf.set_font('Times', '', 10)
                    text = str(item['text']).encode('ascii', errors='ignore').decode()
                    pdf.cell(5, 10, '*', 0, 0)
                    pdf.multi_cell(0, 10, text)
        
        # Additional Themes
        if data.get('keywords_with_statements'):
            pdf.set_font('Times', 'B', 14)
            pdf.cell(0, 10, 'Additional Themes', 0, 1)
            
            for i, item in enumerate(data['keywords_with_statements'][:10], 1):
                pdf.set_font('Times', 'B', 12)
                text = str(item['keyword']).encode('ascii', errors='ignore').decode()
                pdf.cell(0, 10, f"{i}. {text}", 0, 1)
                
                for statement in item['statements']:
                    pdf.set_font('Times', '', 10)
                    text = str(statement).encode('ascii', errors='ignore').decode()
                    pdf.cell(5, 10, '*', 0, 0)
                    pdf.multi_cell(0, 10, text)
        
        # Entity Recognition
        if data.get('entities'):
            pdf.set_font('Times', 'B', 14)
            pdf.cell(0, 10, 'Entity Recognition', 0, 1)
            
            for category in ['organizations', 'products', 'locations', 'people']:
                entities = set()
                for entity_dict in data['entities']:
                    entities.update(entity_dict.get(category, []))
                
                if entities:
                    pdf.set_font('Times', 'B', 12)
                    pdf.cell(0, 10, f"{category.capitalize()}:", 0, 1)
                    
                    pdf.set_font('Times', '', 10)
                    for entity in list(entities)[:5]:
                        text = str(entity).encode('ascii', errors='ignore').decode()
                        pdf.cell(5, 10, '*', 0, 0)
                        pdf.multi_cell(0, 10, text)
        
        # Sentiment Analysis
        if data.get('sentiments'):
            pdf.set_font('Times', 'B', 14)
            pdf.cell(0, 10, 'Sentiment Analysis', 0, 1)
            
            total = len(data['sentiments'])
            if total > 0:
                positive = sum(1 for s in data['sentiments'] if s['polarity'] > 0)
                negative = sum(1 for s in data['sentiments'] if s['polarity'] < 0)
                neutral = total - positive - negative
                
                pdf.set_font('Times', '', 10)
                pdf.cell(60, 10, f'Positive: {(positive/total)*100:.1f}%')
                pdf.cell(60, 10, f'Neutral: {(neutral/total)*100:.1f}%')
                pdf.cell(60, 10, f'Negative: {(negative/total)*100:.1f}%')
        
        # Get PDF as bytes
        try:
            return pdf.output(dest='S').encode('latin-1')
        except Exception as e:
            print(f"Error encoding PDF output: {str(e)}")
            try:
                return pdf.output(dest='S').encode('latin-1', errors='ignore')
            except Exception as e:
                print(f"Error encoding PDF output with ignore: {str(e)}")
                raise Exception(f"Failed to generate PDF: {str(e)}")
                
    except Exception as e:
        print(f"Error generating PDF: {str(e)}")
        raise Exception(f"Failed to generate PDF: {str(e)}")
