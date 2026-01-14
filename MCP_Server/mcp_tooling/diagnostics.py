import logging
from .connection import get_ableton_connection

logger = logging.getLogger("mcp_server.diagnostics")

def list_tracks() -> str:
    """
    Query the Live Set and return a formatted table of all tracks.
    """
    conn = get_ableton_connection()
    
    # Get basic context
    try:
        context = conn.send_command("get_song_context", {"include_clips": False})
        tracks = context.get("tracks", [])
    except Exception as e:
        return f"Error querying Ableton: {e}"

    if not tracks:
        return "No tracks found (or connection issue)."
        
    # Build Table
    # Headers
    headers = ["ID", "Name", "Color", "Group", "Muted"]
    rows = []
    
    for t in tracks:
        tid = str(t.get("track_index", "?"))
        name = t.get("name", "Unknown")
        color = str(t.get("color", ""))
        is_group = "Yes" if t.get("is_group") else ""
        muted = "Muted" if t.get("mute") else ""
        
        # Try to get more info if missing? 
        # get_song_context is usually summary heavy.
        
        rows.append([tid, name, color, is_group, muted])
        
    # Format
    # Calculate widths
    widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(cell))
            
    # Print
    lines = []
    
    # Separator
    sep = "+" + "+".join(["-" * (w + 2) for w in widths]) + "+"
    lines.append(sep)
    
    # Header
    header_line = "|"
    for i, h in enumerate(headers):
        header_line += f" {h.ljust(widths[i])} |"
    lines.append(header_line)
    lines.append(sep)
    
    # Rows
    for row in rows:
        line = "|"
        for i, cell in enumerate(row):
            line += f" {cell.ljust(widths[i])} |"
        lines.append(line)
        
    lines.append(sep)
    
    return "\n".join(lines)

def print_status():
    """Print status to stdout."""
    print(list_tracks())

if __name__ == "__main__":
    print_status()
