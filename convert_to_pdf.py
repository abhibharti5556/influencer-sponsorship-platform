import markdown
import pdfkit
import os

def convert_md_to_html(md_file, html_file):
    """Convert markdown file to HTML."""
    with open(md_file, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # Convert markdown to HTML
    html = markdown.markdown(md_content, extensions=['tables', 'fenced_code'])
    
    # Add CSS styling
    styled_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                margin: 40px;
                color: #333;
            }}
            h1 {{
                text-align: center;
                color: #2c3e50;
                border-bottom: 2px solid #3498db;
                padding-bottom: 10px;
            }}
            h2 {{
                color: #2980b9;
                border-bottom: 1px solid #eee;
                padding-bottom: 5px;
            }}
            h3 {{
                color: #3498db;
            }}
            code {{
                background-color: #f7f7f7;
                padding: 2px 5px;
                border-radius: 3px;
                font-family: Consolas, monospace;
            }}
            pre {{
                background-color: #f7f7f7;
                padding: 15px;
                border-radius: 5px;
                overflow: auto;
            }}
            table {{
                border-collapse: collapse;
                width: 100%;
                margin: 20px 0;
            }}
            th, td {{
                border: 1px solid #ddd;
                padding: 8px;
                text-align: left;
            }}
            th {{
                background-color: #f2f2f2;
            }}
            .directory-structure {{
                white-space: pre;
                font-family: Consolas, monospace;
            }}
        </style>
    </head>
    <body>
    {html}
    </body>
    </html>
    """
    
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(styled_html)
    
    return html_file

def html_to_pdf(html_file, pdf_file):
    """Convert HTML file to PDF."""
    try:
        # For Windows
        wkhtmltopdf_path = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
        config = pdfkit.configuration(wkhtmltopdf=wkhtmltopdf_path)
        pdfkit.from_file(html_file, pdf_file, configuration=config)
        print(f"Successfully created PDF: {pdf_file}")
    except Exception as e:
        print(f"Error creating PDF: {e}")
        print("\nNote: This script requires wkhtmltopdf to be installed.")
        print("Download it from: https://wkhtmltopdf.org/downloads.html")
        print("Or install pdfkit directly: pip install pdfkit")

if __name__ == "__main__":
    md_file = "project_report.md"
    html_file = "project_report.html"
    pdf_file = "ISCP_Project_Report.pdf"
    
    if os.path.exists(md_file):
        html_path = convert_md_to_html(md_file, html_file)
        html_to_pdf(html_path, pdf_file)
    else:
        print(f"Error: File {md_file} not found.") 