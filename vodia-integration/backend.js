/**
 * Zangbot Infrastructure Router - Vodia v70 Integration
 * Backend Code (JavaScript/Node.js)
 * 
 * Handles incoming webhooks from Vodia and routes to Zangbot Router
 */

module.exports = {
  name: "Zangbot Infrastructure Router",
  identifier: "zangbotinfrastructurerouter",
  version: "1.0.0",
  
  /**
   * Initialize integration
   */
  async init(app, config) {
    console.log("[Zangbot] Initializing integration...");
    
    // Store config
    this.config = config;
    this.routerUrl = "http://72.62.97.23:8001";
    
    // Register webhook handler
    app.post("/webhook/vodia", async (req, res) => {
      await this.handleWebhook(req, res);
    });
    
    console.log("[Zangbot] Ready to receive webhooks");
  },
  
  /**
   * Handle incoming webhook from Vodia
   * 
   * Webhook format from Vodia may include:
   * - Extension state changes (offline, online, busy)
   * - Call events (incoming, outgoing, duration)
   * - Queue events (call waiting, abandoned)
   * - IVR events (menu options selected)
   */
  async handleWebhook(req, res) {
    try {
      const payload = req.body;
      
      console.log(`[Zangbot] Received webhook:`, JSON.stringify(payload, null, 2));
      
      // Transform Vodia webhook to Zangbot format
      const transformed = {
        source: "vodia",
        event: this.parseEvent(payload),
        device_id: payload.extension || payload.account || "unknown",
        details: {
          ...payload,
          timestamp: new Date().toISOString()
        }
      };
      
      // Forward to Zangbot Router
      const response = await fetch(`${this.routerUrl}/webhook/vodia`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(transformed)
      });
      
      if (!response.ok) {
        console.error(`[Zangbot] Router error: ${response.status}`);
        return res.status(502).json({ error: "Router unavailable" });
      }
      
      const ticketResult = await response.json();
      
      console.log(`[Zangbot] Created ticket: ${ticketResult.ticket_id}`);
      
      // Return success to Vodia
      res.json({
        success: true,
        integration: "zangbotinfrastructurerouter",
        ticket_id: ticketResult.ticket_id
      });
      
    } catch (error) {
      console.error(`[Zangbot] Error processing webhook:`, error);
      res.status(400).json({ error: error.message });
    }
  },
  
  /**
   * Parse Vodia event type from webhook payload
   * Adapt based on actual Vodia webhook format
   */
  parseEvent(payload) {
    // Common Vodia webhook event types
    if (payload.type === "extension_state_changed") {
      return payload.state === "offline" ? "extension_offline" : `extension_${payload.state}`;
    }
    if (payload.type === "call_started") return "call_started";
    if (payload.type === "call_ended") return "call_ended";
    if (payload.type === "queue_event") return `queue_${payload.event}`;
    if (payload.type === "ivr_event") return `ivr_${payload.action}`;
    
    // Default
    return payload.type || "unknown_event";
  },
  
  /**
   * User frontend (optional UI for configuration)
   * Vodia may display this in admin panel
   */
  getUI() {
    return {
      html: `
        <div class="zangbot-panel">
          <h3>Zangbot Infrastructure Router</h3>
          <p>Status: <span id="status">Checking...</span></p>
          <p>Router: <strong>http://72.62.97.23:8001</strong></p>
          <button onclick="testConnection()">Test Connection</button>
          <div id="result"></div>
        </div>
      `,
      css: `
        .zangbot-panel {
          padding: 20px;
          border: 1px solid #ddd;
          border-radius: 4px;
          font-family: monospace;
        }
        .zangbot-panel button {
          padding: 8px 16px;
          background: #007bff;
          color: white;
          border: none;
          border-radius: 4px;
          cursor: pointer;
        }
        .zangbot-panel button:hover {
          background: #0056b3;
        }
      `,
      js: `
        async function testConnection() {
          const result = document.getElementById("result");
          const status = document.getElementById("status");
          
          try {
            status.textContent = "Testing...";
            
            const response = await fetch("http://72.62.97.23:8001/health");
            const data = await response.json();
            
            if (data.status === "ok") {
              status.textContent = "✓ Connected";
              status.style.color = "green";
              result.innerHTML = "<p>Router is reachable and responding</p>";
            } else {
              status.textContent = "✗ Disconnected";
              status.style.color = "red";
              result.innerHTML = "<p>Router responded but status unknown</p>";
            }
          } catch (error) {
            status.textContent = "✗ Error";
            status.style.color = "red";
            result.innerHTML = "<p>Error: " + error.message + "</p>";
          }
        }
        
        // Test on load
        window.addEventListener("load", testConnection);
      `
    };
  }
};
