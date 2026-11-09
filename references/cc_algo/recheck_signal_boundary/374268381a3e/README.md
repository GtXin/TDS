# Signal-transport source supplement

Source: `/Users/coder/Public/EngineGit/cc`, clean HEAD `374268381a3eaeee4d220e67d63364b3907405f4`; captured2026-11-09 for memo018003 second-pass audit. This separate supplement keeps the previous19-file source snapshot unchanged. Original bytes copied with hashes in [manifest.json](manifest.json); no source code imported or executed.

- [ws.py](src/cc/api/routes/ws.py),151–164: `/ws/signal` accepts/registers a socket, emits hello, receives text and responds pong; cleanup unregisters it.
- [useSignalStream.ts](frontend/src/composables/useSignalStream.ts),16–39: frontend connection, JSON message storage and cleanup.
- [SignalPanel.vue](frontend/src/components/LeftPane/SignalPanel.vue),1–22: connection status and raw last-message/placeholder display.

These functions provide transport/display; they do not implement divergence or point detection. Future-phase comments do not establish executable detector availability.
