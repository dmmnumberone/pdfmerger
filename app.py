from flask import Flask, request, jsonify
from PyPDF2 import PdfFileMerger
import requests
import os

app = Flask(__name__)

@app.route('/merge', methods=['POST'])
def merge_pdfs():
    data = request.get_json()
    if not data or 'urls' not in data:
        return jsonify({"error": "No URLs provided"}), 400
    
    urls = data['urls']
    if len(urls) < 2:
        return jsonify({"error": "Please provide at least two PDF URLs"}), 400

    merger = PdfFileMerger()
    temp_files = []

    try:
        for url in urls:
            response = requests.get(url)
            if response.status_code == 200:
                temp_filename = url.split('/')[-1]
                with open(temp_filename, 'wb') as temp_file:
                    temp_file.write(response.content)
                    temp_files.append(temp_filename)
                    merger.append(temp_filename)
            else:
                return jsonify({"error": f"Failed to download file from {url}"}), 400

        output_filename = "merged.pdf"
        merger.write(output_filename)
        merger.close()

        for temp_file in temp_files:
            os.remove(temp_file)

        return jsonify({"message": "PDFs merged successfully", "output_file": output_filename})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0')
