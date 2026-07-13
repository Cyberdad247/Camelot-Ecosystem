import { listEvents } from "@/lib/control-plane";
import { isAuthorized } from "@/lib/cockpit-auth";
import { NextRequest } from "next/server";

export const dynamic = "force-dynamic";
export const runtime = "nodejs";

export function GET(request: NextRequest) {
  if (!isAuthorized(request)) return new Response("Operator pairing required.", { status: 401 });
  const encoder = new TextEncoder();
  let lastEventId = "";
  let interval: ReturnType<typeof setInterval> | undefined;
  let closeTimer: ReturnType<typeof setTimeout> | undefined;
  let closed = false;

  const stream = new ReadableStream<Uint8Array>({
    start(controller) {
      const cleanup = () => {
        if (interval) clearInterval(interval);
        if (closeTimer) clearTimeout(closeTimer);
        interval = undefined;
        closeTimer = undefined;
      };

      const close = () => {
        if (closed) return;
        closed = true;
        cleanup();
        try {
          controller.close();
        } catch {
          // The browser may close first during a reconnect or navigation.
        }
      };

      const send = (event: string, data: unknown) => {
        if (closed) return;
        try {
          controller.enqueue(encoder.encode(`event: ${event}\ndata: ${JSON.stringify(data)}\n\n`));
        } catch {
          close();
        }
      };

      controller.enqueue(encoder.encode("retry: 3000\n\n"));
      send("ready", { ts: new Date().toISOString(), source: "pwa-cockpit-sse" });

      const flush = () => {
        const events = listEvents();
        const cursor = lastEventId ? events.findIndex((item) => item.id === lastEventId) : -1;
        const unseen = cursor > -1 ? events.slice(0, cursor) : events.slice(0, 20);
        unseen.reverse().forEach((event) => send("cockpit-event", event));
        lastEventId = events[0]?.id ?? lastEventId;
        send("heartbeat", { ts: new Date().toISOString() });
      };

      flush();
      interval = setInterval(flush, 5000);
      closeTimer = setTimeout(close, 55000);

      request.signal.addEventListener("abort", close, { once: true });
    },
    cancel() {
      if (interval) clearInterval(interval);
      if (closeTimer) clearTimeout(closeTimer);
      closed = true;
    },
  });

  return new Response(stream, {
    headers: {
      "Content-Type": "text/event-stream; charset=utf-8",
      "Cache-Control": "no-cache, no-transform",
      Connection: "keep-alive",
      "X-Accel-Buffering": "no",
    },
  });
}
