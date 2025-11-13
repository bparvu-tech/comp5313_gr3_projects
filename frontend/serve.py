#!/usr/bin/env python3
"""Simple HTTP server for testing the frontend locally."""

import http.server
import socketserver
import sys
from pathlib import Path


def main():
    """Start a simple HTTP server for the frontend."""
    port = 8080
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print(f"Invalid port: {sys.argv[1]}")
            print("Usage: python serve.py [port]")
            sys.exit(1)

    # Change to frontend directory
    frontend_dir = Path(__file__).parent
    handler = http.server.SimpleHTTPRequestHandler

    print("=" * 80)
    print("Lakehead University Chatbot - Frontend Server")
    print("=" * 80)
    print()
    print(f"Starting server on port {port}...")
    print(f"Serving files from: {frontend_dir}")
    print()
    print(f"Open your browser to: http://localhost:{port}")
    print()
    print("Make sure the backend is running on http://localhost:5000")
    print()
    print("Press Ctrl+C to stop the server")
    print("=" * 80)
    print()

    try:
        with socketserver.TCPServer(("", port), handler) as httpd:
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\nServer stopped.")
        sys.exit(0)
    except OSError as e:
        print(f"\nError starting server: {e}")
        print(f"Port {port} might already be in use. Try a different port.")
        sys.exit(1)


if __name__ == "__main__":
    main()

