// Path: src/hooks/useCampaignSocket.ts
import { useState, useEffect, useRef } from 'react';
import type { EncounterState } from '../types/campaign';

export interface WebSocketMessage {
    type: 'chat' | 'dice_roll' | 'user_join' | 'user_leave' | 'error' | 'encounter_update' | 'turn_update';
    payload: any;
    sender: string;
    timestamp?: string;
}

export interface SystemMessage {
    type: 'encounter_update' | 'turn_update';
    payload: any;
}

const WEBSOCKET_URL = import.meta.env.VITE_WEBSOCKET_BASE_URL || 'ws://localhost:8000';

export const useCampaignSocket = (campaignId: string | undefined, token: string | null) => {
    const [chatLogMessages, setChatLogMessages] = useState<WebSocketMessage[]>([]);
    const [encounterState, setEncounterState] = useState<EncounterState | null>(null);
    const [isConnected, setIsConnected] = useState(false);
    const websocket = useRef<WebSocket | null>(null);

    useEffect(() => {
        if (!campaignId || !token) return;

        const wsUrl = `${WEBSOCKET_URL}/ws/campaign/${campaignId}?token=${encodeURIComponent(token)}`;
        websocket.current = new WebSocket(wsUrl);

        websocket.current.onopen = () => setIsConnected(true);
        websocket.current.onclose = () => setIsConnected(false);
        websocket.current.onerror = (error) => console.error("WebSocket error:", error);

        websocket.current.onmessage = (event) => {
            try {
                const messageData = JSON.parse(event.data);
                switch(messageData.type) {
                    case 'encounter_update':
                        setEncounterState(messageData.payload);
                        break;
                    case 'turn_update':
                        setEncounterState(prev => prev ? { ...prev, active_entry_id: messageData.payload.active_entry_id, turn_index: messageData.payload.turn_index } : null);
                        break;
                    default:
                        setChatLogMessages(prev => [...prev, messageData]);
                        break;
                }
            } catch (error) { console.error("Failed to parse WebSocket message:", error); }
        };

        return () => { websocket.current?.close(); };
    }, [campaignId, token]);

    const sendMessage = (type: string, payload: any) => {
        if (websocket.current?.readyState === WebSocket.OPEN) {
            websocket.current.send(JSON.stringify({ type, payload }));
        } else { console.error("WebSocket is not connected."); }
    };

    return { chatLogMessages, encounterState, setEncounterState, isConnected, sendMessage };
};
