import csv

def extract_text_from_csv(file_path, max_rows=50):
    """
    Extract text from CSV with better formatting
    """
    text = []

    try:
        with open(file_path, newline="", encoding="utf-8", errors="ignore") as f:
            reader = csv.reader(f)
            rows = list(reader)

            if not rows:
                return "[Empty CSV file]"

            # Headers
            headers = rows[0]
            text.append("Columns: " + ", ".join(str(h).strip() for h in headers if h))
            
            # Count total rows
            total_rows = len(rows) - 1
            rows_to_show = min(max_rows, total_rows)
            text.append(f"Showing {rows_to_show} of {total_rows} rows:\n")

            # Data rows
            data_count = 0
            for row in rows[1:max_rows + 1]:
                if not any(row):
                    continue
                text.append(" | ".join(str(cell).strip() for cell in row if cell))
                data_count += 1
            
            if data_count == 0:
                text.append("[No data rows found]")
            
            if total_rows > max_rows:
                text.append(f"\n[{total_rows - max_rows} more rows not shown]")

    except Exception as e:
        return f"[ERROR reading CSV: {str(e)}]"

    return "\n".join(text)