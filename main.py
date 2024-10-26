import tkinter as tk
import pyperclip
import time
import threading
import re
import PyPDF2

# List of PDF file paths to search through
pdf_paths = ["scrum.pdf"]  # Add paths to your PDF files

# Function to search for text in multiple PDF files, returning results with context and page numbers
def search_in_pdfs(selected_text, pdf_paths):
    results = []
    for pdf_path in pdf_paths:
        with open(pdf_path, "rb") as f:
            pdf_reader = PyPDF2.PdfReader(f)
            for page_num, page in enumerate(pdf_reader.pages, start=1):
                text = page.extract_text()
                if not text:
                    continue

                # Search for the selected text within the page
                matches = [m.start() for m in re.finditer(re.escape(selected_text), text, re.IGNORECASE)]
                for match_pos in matches:
                    # Find 100 characters before and after the match
                    start = max(0, match_pos - 100)
                    end = min(len(text), match_pos + len(selected_text) + 100)
                    context = text[start:end].replace("\n", " ")  # Remove newlines for better readability

                    # Add result with context and page number
                    result = {
                        "file": pdf_path,
                        "page": page_num,
                        "context": context,
                        "highlight_start": match_pos - start,
                        "highlight_end": match_pos - start + len(selected_text)
                    }
                    results.append(result)
    return results

# Function to update the display with selected text and search results
def update_display(selected_text, results):
    text_box.delete("1.0", tk.END)
    text_box.insert(tk.END, f"Selected Text: '{selected_text}'\n\n")
    text_box.insert(tk.END, "Search Results:\n\n")
    text_box.tag_configure("highlight", background="yellow", foreground="black")

    if results:
        for result in results:
            line = f"File: {result['file']}\nPage: {result['page']}\nContext:\n... {result['context']} ...\n"
            start_idx = text_box.index(tk.END)
            text_box.insert(tk.END, line + "\n" + "-" * 50 + "\n\n")
            end_idx = text_box.index(tk.END)

            # Apply highlight to the found text in context
            context_start = f"{start_idx} + {result['highlight_start']} chars"
            context_end = f"{start_idx} + {result['highlight_end']} chars"
            text_box.tag_add("highlight", context_start, context_end)
    else:
        text_box.insert(tk.END, "No matches found.")

# Function to monitor clipboard and update search results
def monitor_clipboard():
    previous_text = ""
    while True:
        time.sleep(1)  # Polling interval
        current_text = pyperclip.paste()
        if current_text != previous_text:
            previous_text = current_text
            results = search_in_pdfs(current_text, pdf_paths)
            update_display(current_text, results)

# Set up the GUI
root = tk.Tk()
root.title("PDF Text Search Monitor")
root.geometry("700x500")

text_box = tk.Text(root, wrap="word", font=("Helvetica", 12))
text_box.pack(expand=True, fill="both")

# Start the clipboard monitor in a separate thread
thread = threading.Thread(target=monitor_clipboard, daemon=True)
thread.start()

root.mainloop()
