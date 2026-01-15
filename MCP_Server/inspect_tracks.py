from mcp_tooling.connection import get_ableton_connection
import json

def list_tracks():
    conn = get_ableton_connection()
    try:
        session = conn.send_command("get_session_info")
        count = session.get("track_count", 0)
    except Exception as e:
        print(f"Error getting session: {e}")
        return

    print(f"Total Tracks: {count}")
    
    with open("track_list_clean.txt", "w", encoding="utf-8") as f:
        for i in range(count):
            try:
                # The MCP 'get_track_info' might fail on group tracks if implementation is buggy
                # We will try to get name via property if possible, but we don't have direct property access via this command
                # So we rely on get_track_info
                info = conn.send_command("get_track_info", {"track_index": i})
                name = info.get("name", "Unknown")
                f.write(f"Track {i}: {name}\n")
            except Exception as e:
                f.write(f"Track {i}: Error {str(e)}\n")
            
if __name__ == "__main__":
    list_tracks()
