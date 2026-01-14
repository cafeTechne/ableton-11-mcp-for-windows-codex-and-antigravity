from mcp_tooling.connection import get_ableton_connection

def list_tracks():
    conn = get_ableton_connection()
    try:
        ctx = conn.send_command("get_song_context", {"include_clips": False})
        tracks = ctx.get("tracks", [])
        print(f"--- Found {len(tracks)} Tracks ---")
        for tr in tracks:
            print(f"Index {tr['index']}: '{tr['name']}' (Color: {tr.get('color')})")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    list_tracks()
