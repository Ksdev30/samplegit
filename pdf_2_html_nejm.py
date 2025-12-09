import os
import tempfile
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinter.scrolledtext import ScrolledText
import fitz  # PyMuPDF

print ("Hello World - trying out this git and Github pushes and stuff. Let's see if this works")
def extract_content_and_images(pdf_path):
    doc = fitz.open(pdf_path)
    media_path = tempfile.mkdtemp()
    pages = []

    for pnum, page in enumerate(doc):
        blocks = page.get_text("blocks")
        page_html = ""

        for b in sorted(blocks, key=lambda x: (x[1], x[0])):
            text = b[4].strip()
            if not text or len(text.split()) < 2:
                continue
            if text.lower().startswith(("references", "citations")):
                continue

            if text.lower().startswith(("chapter", "section")):
                page_html += f"<h2>{text}</h2>\n"
            else:
                page_html += f"<p>{text}</p>\n"

        for img_index, img_info in enumerate(page.get_images(full=True)):
            xref = img_info[0]
            img = doc.extract_image(xref)
            ext = img["ext"]
            img_bytes = img["image"]
            img_path = os.path.join(media_path, f"img_p{pnum}_{img_index}.{ext}")
            with open(img_path, "wb") as f:
                f.write(img_bytes)
            page_html += (
                f'<figure><img src="{img_path}" alt="Figure" />'
                f'<figcaption>Figure</figcaption></figure>\n'
            )

        pages.append(page_html)

    return pages


def generate_nejm_html(pages):
    css = """
    <style>
      body { font-family: Cambria, Georgia, serif; max-width: 800px;
             margin: 40px auto; line-height: 1.6; color: #111; }
      h1, h2 { font-family: 'Segoe UI', sans-serif; color: #2a4d8f;
               margin-top: 1.6em; margin-bottom: .4em; }
      p { margin: 1em 0; font-size: 18px; }
      figure { margin: 30px 0; text-align: center; }
      figure img { max-width: 100%; height: auto; }
      figcaption { font-size: 14px; color: #555; margin-top: 5px; }
      hr.nejm { border: none; border-top: 2px solid #e0e0e0; margin: 60px 0; }
    </style>"""

    html = f"<!DOCTYPE html><html lang='en'><head><meta charset='UTF-8'><title>Converted PDF</title>{css}</head><body>"
    html += "<h1>Converted PDF Document</h1>\n"

    for page_html in pages:
        html += page_html + "<hr class='nejm'>\n"

    html += "</body></html>"
    return html


def browse_pdf():
    path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
    if path:
        pdf_var.set(path)


def convert_and_preview():
    pdf_path = pdf_var.get()
    if not os.path.isfile(pdf_path) or not pdf_path.lower().endswith(".pdf"):
        messagebox.showerror("Error", "Select a valid PDF file.")
        return

    status.set("Extracting content…")
    root.update()

    try:
        pages = extract_content_and_images(pdf_path)
        html_out = generate_nejm_html(pages)
        show_preview(html_out, pdf_path)
    except Exception as e:
        messagebox.showerror("Error", str(e))
        status.set("Error.")
    else:
        status.set("Ready.")


def show_preview(html, pdf_path):
    win = tk.Toplevel(root)
    win.title("HTML Preview (plain text)")
    win.geometry("900x600")

    txt = ScrolledText(win, wrap=tk.WORD, font=("Courier New", 10))
    txt.pack(fill="both", expand=True)
    txt.insert("1.0", html)
    txt.config(state="disabled")

    def accept():
        out = os.path.splitext(pdf_path)[0] + "_nejm_converted.html"
        with open(out, "w", encoding="utf-8") as f:
            f.write(html)
        messagebox.showinfo("Saved", f"HTML saved to:\n{out}")
        win.destroy()

    def reject():
        messagebox.showinfo("Canceled", "Output not saved.")
        win.destroy()

    btnf = ttk.Frame(win)
    btnf.pack(pady=10)
    ttk.Button(btnf, text="✅ Save", command=accept).pack(side="left", padx=5)
    ttk.Button(btnf, text="❌ Cancel", command=reject).pack(side="left", padx=5)


# --- GUI setup ---
root = tk.Tk()
root.title("PDF → NEJM‑Style HTML Converter")
root.geometry("600x220")
root.resizable(False, False)

pdf_var = tk.StringVar()
status = tk.StringVar(value="Select PDF and click Convert.")

frm = ttk.Frame(root, padding=20)
frm.pack(fill="both", expand=True)

ttk.Label(frm, text="PDF file:").grid(row=0, column=0, sticky="w")
ttk.Entry(frm, width=50, textvariable=pdf_var).grid(row=1, column=0, padx=(0, 5))
ttk.Button(frm, text="Browse...", command=browse_pdf).grid(row=1, column=1)

ttk.Button(root, text="Convert to NEJM‑style HTML", command=convert_and_preview).pack(pady=10)
ttk.Label(root, textvariable=status, foreground="blue").pack()

root.mainloop()
