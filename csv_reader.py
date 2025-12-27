import csv

def extract_text_from_csv(file_path, max_rows=50):
    text = []

    try:
        with open(file_path, newline="", encoding="utf-8", errors="ignore") as f:
            reader = csv.reader(f)
            rows = list(reader)

            if not rows:
                return ""

            headers = rows[0]
            text.append("Columns: " + ", ".join(headers))
            text.append(f"Showing up to {max_rows} rows")

            for row in rows[1:max_rows]:
                if not any(row):
                    continue
                text.append(" | ".join(cell.strip() for cell in row))

    except Exception as e:
        return f"[ERROR reading CSV: {str(e)}]"

    return "\n".join(text)
