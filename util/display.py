from IPython.display import Markdown, display
from typing import List


def render_table(_headers: List[str], _rows: List[List[str]]):
    # Create the header row
    md = "| " + " | ".join(_headers) + " |\n"
    md += "| " + " | ".join(["---"] * len(_headers)) + " |\n"  # Separator row

    # Add each row of data
    for row in _rows:
        # Replace newline characters with <br> for Markdown rendering
        sanitized_row = [str(cell).replace("\n", "<br>") for cell in row]
        md += "| " + " | ".join(sanitized_row) + " |\n"

    display(Markdown(md))
