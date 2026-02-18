import time
from video_loop import start_mjpeg_server

VIDEO = r"C:\Users\msi\Documents\rada-ai-v1\media\videos\Record.mp4"

if __name__ == "__main__":
    server = start_mjpeg_server(VIDEO, host="127.0.0.1", port=8088, fps=10, width=1280)
    print("✅ MJPEG live feed running:")
    print("➡️  http://127.0.0.1:8088/cam_1.mjpg")
    print("➡️  http://127.0.0.1:8088/cam_2.mjpg")
    print("➡️  http://127.0.0.1:8088/cam_3.mjpg")
    print("➡️  http://127.0.0.1:8088/cam_4.mjpg")
    print("\nPress Ctrl+C to stop.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        server.shutdown()
        print("Stopped.")