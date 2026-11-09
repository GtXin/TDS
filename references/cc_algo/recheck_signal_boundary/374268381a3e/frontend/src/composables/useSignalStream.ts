// useSignalStream: subscribes to /ws/signal (stage-03-execution-plan.md §3.8).
// Stage 3: server returns pong stub; stage 5+ carries real Chanlun signal events.
// §5.6 dispose discipline: WebSocket closed on onUnmounted.

import { ref, onUnmounted } from "vue";

export interface SignalMessage {
  type: string;
  [key: string]: unknown;
}

export function useSignalStream() {
  const last = ref<SignalMessage | null>(null);
  const connected = ref(false);
  let ws: WebSocket | null = null;

  function connect(): void {
    if (ws) return;
    const proto = location.protocol === "https:" ? "wss:" : "ws:";
    ws = new WebSocket(`${proto}//${location.host}/ws/signal`);
    ws.onopen = () => { connected.value = true; };
    ws.onmessage = (e: MessageEvent) => {
      try { last.value = JSON.parse(e.data as string) as SignalMessage; } catch { /* ignore malformed */ }
    };
    ws.onclose = () => { connected.value = false; ws = null; };
    // Clear ws on error so connect() can be re-called without being blocked by `if (ws) return`.
    ws.onerror = () => { connected.value = false; ws = null; };
  }

  function disconnect(): void {
    ws?.close();
    ws = null;
    connected.value = false;
  }

  // §5.6: always disconnect on unmount
  onUnmounted(disconnect);

  return { last, connected, connect, disconnect };
}
