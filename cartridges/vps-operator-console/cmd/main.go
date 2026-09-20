package main

import (
	"fmt"
	"html/template"
	"log"
	"net/http"
	"time"

	"github.com/Cyberdad247/Camelot-Ecosystem/cartridges/vps-operator-console/internal/omarchy"
)

type PageData struct {
	Title    string
	TenantID string
}

func main() {
	mux := http.NewServeMux()

	fs := http.FileServer(http.Dir("./static"))
	mux.Handle("/static/", http.StripPrefix("/static/", fs))

	tmpl := template.Must(template.New("index").Parse(`
<!DOCTYPE html>
<html lang="en" class="bg-[#050505] text-slate-300">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{.Title}}</title>
    <script src="https://unpkg.com/htmx.org@1.9.10"></script>
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {
            theme: {
                extend: {
                    colors: {
                        luxora: '#D4AF37',
                        obsidian: '#050505',
                        royal: '#2E0854'
                    }
                }
            }
        }
    </script>
</head>
<body class="h-screen w-full flex flex-col overflow-hidden font-sans">
    <header class="h-14 border-b border-white/10 flex items-center justify-between px-6 bg-obsidian/80 backdrop-blur-md z-50">
        <div class="flex items-center gap-3">
            <div class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></div>
            <h1 class="font-bold tracking-widest text-luxora text-sm">CAMELOT VPS OPERATOR CONSOLE</h1>
        </div>
        <div class="flex items-center gap-4 text-xs font-mono text-slate-500">
            <span>TENANT: {{.TenantID}}</span>
            <span class="px-2 py-1 border border-white/10 rounded">PORT: 3004</span>
        </div>
    </header>

    <main class="flex-1 relative w-full h-full flex">
        <aside class="w-80 border-r border-white/10 bg-obsidian/50 p-4 flex flex-col gap-6 overflow-y-auto z-10">
            <div>
                <h2 class="text-[10px] font-bold text-white/50 tracking-wider mb-4">ACTIVE MISSIONS</h2>
                <div id="mission-list" hx-get="/api/missions" hx-trigger="load, every 5s" class="space-y-2">
                    <div class="p-3 border border-white/5 rounded-lg bg-white/5 animate-pulse h-16"></div>
                </div>
            </div>

            <div class="mt-auto border-t border-white/10 pt-4">
                <h2 class="text-[10px] font-bold text-white/50 tracking-wider mb-4 flex justify-between">
                    <span>OMARCHY HOST HEALTH</span>
                    <span class="text-luxora">8GB LIMIT</span>
                </h2>
                <div id="omarchy-metrics" hx-get="/api/omarchy/status" hx-trigger="load, every 10s" class="space-y-2">
                    <div class="p-3 border border-white/5 rounded-lg bg-white/5 animate-pulse h-24"></div>
                </div>
            </div>
        </aside>

        <section class="flex-1 relative bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-royal/20 via-obsidian to-obsidian">
            <div id="world-tree-canvas" class="absolute inset-0 z-0"></div>
            <div class="absolute bottom-6 left-1/2 -translate-x-1/2 z-10 pointer-events-none">
                <div class="bg-black/60 border border-white/10 px-4 py-2 rounded-full backdrop-blur-sm text-xs font-mono text-luxora/80">
                    3D KINETIC SPATIAL ORBIT ACTIVE
                </div>
            </div>
        </section>

        <aside class="w-80 border-l border-white/10 bg-obsidian/50 p-4 overflow-y-auto z-10">
            <h2 class="text-[10px] font-bold text-white/50 tracking-wider mb-4">CRYPTOGRAPHIC LEDGER</h2>
            <div id="receipt-feed" hx-get="/api/receipts" hx-trigger="load, every 2s" class="space-y-3">
                <div class="p-3 border border-white/5 rounded-lg bg-white/5 animate-pulse h-20"></div>
            </div>
        </aside>
    </main>

    <script type="module">
        import { WorldTreeScene } from '/static/js/WorldTreeScene.js';
        const scene = new WorldTreeScene('world-tree-canvas');
        const eventSource = new EventSource('/api/graph/stream');
        eventSource.onmessage = function(event) {
            try {
                const data = JSON.parse(event.data);
                if (data.event === 'graph_update') {
                    window.dispatchEvent(new CustomEvent('graph_update', { detail: data }));
                }
            } catch (e) {
                console.error("SSE parse error", e);
            }
        };
    </script>
</body>
</html>
`))

	mux.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		data := PageData{
			Title:    "Camelot VPS Operator Console",
			TenantID: "ROOT_SOVEREIGN",
		}
		tmpl.Execute(w, data)
	})

	mux.HandleFunc("/api/omarchy/status", func(w http.ResponseWriter, r *http.Request) {
		metrics := omarchy.GetHealth()
		w.Header().Set("Content-Type", "text/html")

		for _, m := range metrics {
			statusColor := "text-emerald-400"
			if m.Status != "ACTIVE" {
				statusColor = "text-amber-400"
			}
			html := fmt.Sprintf(`
			<div class="p-2 border border-white/10 rounded bg-black/40 text-[10px] font-mono mb-1">
				<div class="flex justify-between text-white/70">
					<span>%s</span>
					<span class="%s">%s</span>
				</div>
				<div class="flex justify-between mt-1 text-slate-500">
					<span>MEM: %s</span>
					<span>TASKS: %s</span>
				</div>
			</div>
			`, m.Name, statusColor, m.Status, m.MemoryUse, m.Tasks)
			w.Write([]byte(html))
		}
	})

	mux.HandleFunc("/api/missions", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "text/html")
		w.Write([]byte(`
        <div class="p-3 border border-luxora/30 rounded-lg bg-luxora/5 text-xs">
            <div class="flex justify-between items-center mb-1">
                <span class="text-luxora font-bold">Kinetic Swarm Forge</span>
                <span class="text-emerald-400">RUNNING</span>
            </div>
            <div class="text-slate-400 font-mono">DAG-7B1628B9</div>
        </div>
        `))
	})

	mux.HandleFunc("/api/receipts", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "text/html")
		w.Write([]byte(`
        <div class="p-3 border border-white/10 rounded-lg bg-black/40 text-[10px] font-mono">
            <div class="text-purple-400 mb-1">VFS_ATTESTATION</div>
            <div class="text-slate-500 truncate">Hash: sha256:b1fb...fc0a</div>
            <div class="text-slate-600 mt-1">2s ago</div>
        </div>
        `))
	})

	mux.HandleFunc("/api/graph/stream", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "text/event-stream")
		w.Header().Set("Cache-Control", "no-cache")
		w.Header().Set("Connection", "keep-alive")

		flusher, ok := w.(http.Flusher)
		if !ok {
			http.Error(w, "Streaming unsupported", http.StatusInternalServerError)
			return
		}

		for i := 0; i < 3; i++ {
			msg := fmt.Sprintf(`{"event": "graph_update", "node_id": "NODE-%d", "type": "memory.promoted"}`, i)
			fmt.Fprintf(w, "data: %s\n\n", msg)
			flusher.Flush()
			time.Sleep(2 * time.Second)
		}
	})

	log.Println("VPS Operator Console listening on :3004")
	if err := http.ListenAndServe(":3004", mux); err != nil {
		log.Fatalf("Server failed: %v", err)
	}
}
