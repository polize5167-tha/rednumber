from flask import Flask, request, send_file, render_template, jsonify
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import red
import io
import os

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/generate_pdf", methods=["POST"])
def generate_pdf():
    try:
        data = request.get_json(silent=True)

        if not data:
            return jsonify({"error": "ไม่พบข้อมูล JSON จากหน้าเว็บ"}), 400

        docs = data.get("documents", [])
        reverse = bool(data.get("reverse", False))

        if not isinstance(docs, list) or len(docs) == 0:
            return jsonify({"error": "ไม่มีรายการเอกสารสำหรับสร้าง PDF"}), 400

        if reverse:
            docs = list(reversed(docs))

        buffer = io.BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=A4)

        page_width, page_height = A4
        total_docs = len(docs)

        font_size = 18
        right_margin = 20
        top_margin = 30

        for index, doc in enumerate(docs):
            if not isinstance(doc, dict):
                continue

            document_number = total_docs - index if reverse else index + 1

            try:
                pages = int(doc.get("pages", 1))
            except (TypeError, ValueError):
                pages = 1

            pages = max(1, pages)

            for page in range(1, pages + 1):
                page_number = pages - page + 1 if reverse else page

                pdf.setFont("Helvetica-Bold", font_size)
                pdf.setFillColor(red)

                pdf.drawRightString(
                    page_width - right_margin,
                    page_height - top_margin,
                    f"{document_number}/{page_number}"
                )

                pdf.showPage()

        pdf.save()
        buffer.seek(0)

        return send_file(
            buffer,
            as_attachment=True,
            download_name="thaeng_daeng.pdf",
            mimetype="application/pdf"
        )

    except Exception as error:
        print("PDF ERROR:", error)
        return jsonify({"error": f"สร้าง PDF ไม่สำเร็จ: {error}"}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)