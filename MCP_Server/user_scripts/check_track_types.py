import sys
sys.path.append(r"C:\Users\hobo\Desktop\ableton-mcp\ableton-mcp\MCP_Server")
from mcp_tooling.connection import get_ableton_connection

def check_tracks():
    conn = get_ableton_connection()
    info_list = conn.send_command("get_song_context", {"include_clips": False})
    tracks = info_list.get("tracks", [])
    for t in tracks:
        print(f"Track {t['index']}: Name='{t.get('name')}', Type='{t.get('type')}'")

if __name__ == "__main__":
    check_tracks()
