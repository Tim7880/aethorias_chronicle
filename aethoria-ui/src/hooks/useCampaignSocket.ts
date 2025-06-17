// Path: src/hooks/useCampaignSocket.ts
import { useState, useEffect, useRef } from 'react';

// --- MODIFICATION: Added 'export' to the interface ---
export interface WebSocketMessage {
    type: 'chat' | 'dice_roll' | 'initiative_update' | 'map_update' | 'user_join' | 'user_leave';
    payload: any;
    sender: string;
    timestamp: string;
}
// --- END MODIFICATION ---

const WEBSOCKET_URL = import.meta.env.VITE_WEBSOCKET_BASE_URL || 'ws://localhost:8000';

export const useCampaignSocket = (campaignId: string | undefined, token: string | null) => {
    const [messages, setMessages] = useState<WebSocketMessage[]>([]);
    const [isConnected, setIsConnected] = useState(false);
    const websocket = useRef<WebSocket | null>(null);

    useEffect(() => {
        if (!campaignId || !token) {
            return;
        }

        const wsUrl = `${WEBSOCKET_URL}/ws/campaign/${campaignId}?token=${encodeURIComponent(token)}`;
        
        websocket.current = new WebSocket(wsUrl);

        websocket.current.onopen = () => {
            console.log("WebSocket connection established");
            setIsConnected(true);
        };

        websocket.current.onmessage = (event) => {
            try {
                const messageData = JSON.parse(event.data);
                console.log("Received message:", messageData);
                setMessages(prevMessages => [...prevMessages, messageData]);
            } catch (error) {
                console.error("Failed to parse WebSocket message:", error);
                const rawMessage: WebSocketMessage = {
                    type: 'chat',
                    payload: event.data,
                    sender: 'Server',
                    timestamp: new Date().toISOString()
                }
                setMessages(prevMessages => [...prevMessages, rawMessage]);
            }
        };

        websocket.current.onerror = (error) => {
            console.error("WebSocket error:", error);
        };

        websocket.current.onclose = () => {
            console.log("WebSocket connection closed");
            setIsConnected(false);
        };

        return () => {
            if (websocket.current) {
                websocket.current.close();
            }
        };
    }, [campaignId, token]);

    const sendMessage = (type: string, payload: any) => {
        if (websocket.current && websocket.current.readyState === WebSocket.OPEN) {
            // NOTE: The backend now expects the entire message object,
            // and it will add the sender info itself.
            const message = { type, payload };
            websocket.current.send(JSON.stringify(message));
        } else {
            console.error("WebSocket is not connected.");
        }
    };

    return { messages, isConnected, sendMessage };
};
