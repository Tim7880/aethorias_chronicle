// Path: src/pages/CampaignRoomPage.tsx
import React, { useState, useEffect, useRef, useMemo } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { campaignService } from '../services/campaignService';
import type { Campaign } from '../types/campaign';
import styles from './CampaignRoomPage.module.css';
import ThemedButton from '../components/common/ThemedButton';
import { useCampaignSocket } from '../hooks/useCampaignSocket';
import DiceRoller from '../components/game/DiceRoller';

const CampaignRoomPage: React.FC = () => {
    const { campaignId } = useParams<{ campaignId: string }>();
    const auth = useAuth();
    const navigate = useNavigate();

    const [campaign, setCampaign] = useState<Campaign | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [isDm, setIsDm] = useState(false);
    
    // --- NEW: Initiative Text State ---
    const [initiativeText, setInitiativeText] = useState('');
    
    const { messages, isConnected, sendMessage } = useCampaignSocket(campaignId, auth.token);
    const [chatInput, setChatInput] = useState('');
    const chatLogRef = useRef<HTMLDivElement>(null);

    const myCharacter = useMemo(() => {
        if (!auth.user || !campaign?.members) return null;
        const myMembership = campaign.members.find(m => m.user_id === auth.user?.id);
        return myMembership?.character || null;
    }, [auth.user, campaign]);

    // Main message handler for WebSocket
    useEffect(() => {
        const lastMessage = messages[messages.length - 1];
        if (lastMessage) {
            switch (lastMessage.type) {
                // --- NEW: Handle initiative text updates ---
                case 'initiative_text_update':
                    setInitiativeText(lastMessage.payload.text);
                    break;
            }
        }
    }, [messages]);

    useEffect(() => {
        if (chatLogRef.current) {
            chatLogRef.current.scrollTop = chatLogRef.current.scrollHeight;
        }
    }, [messages]);

    useEffect(() => {
        const fetchCampaignData = async () => {
            if (auth.token && campaignId) {
                try {
                    const data = await campaignService.getCampaignById(auth.token, parseInt(campaignId));
                    setCampaign(data);
                    if (auth.user && data.dm_user_id === auth.user.id) {
                        setIsDm(true);
                    }
                } catch (err: any) {
                    setError(err.message || 'Failed to load campaign data.');
                    if (err.message.includes("Unauthorized")) navigate('/dashboard');
                } finally {
                    setIsLoading(false);
                }
            }
        };
        fetchCampaignData();
    }, [auth.token, campaignId, auth.user, navigate]);

    const handleSendMessage = (e: React.FormEvent) => {
        e.preventDefault();
        if (chatInput.trim() && isConnected) {
            const senderName = myCharacter?.name || auth.user?.username || 'Anonymous';
            sendMessage('chat', { text: chatInput, characterName: senderName });
            setChatInput('');
        }
    };

    const handleRollDice = (sides: number, count: number) => {
        if (isConnected) {
            const rollerName = myCharacter?.name || auth.user?.username || 'A player';
            sendMessage('dice_roll', { sides, count, characterName: rollerName });
        }
    };

    // --- NEW: Initiative Text Handler ---
    const handleInitiativeChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
        const newText = e.target.value;
        setInitiativeText(newText);
        sendMessage('initiative_text_update', { text: newText });
    };

    const handleClearInitiative = () => {
        if(window.confirm("Are you sure you want to clear the initiative order?")) {
            setInitiativeText("");
            sendMessage('initiative_text_update', { text: "" });
        }
    };

    if (isLoading) return <div className={styles.pageContainer}>Loading Campaign Room...</div>;
    if (error) return <div className={styles.pageContainer}>Error: {error}</div>;
    if (!campaign) return <div className={styles.pageContainer}>Campaign not found.</div>;

    return (
        <div className={styles.pageContainer}>
            <header className={styles.header}>
                <h1 className={styles.title}>{campaign.title}</h1>
                <p className={isConnected ? styles.connected : styles.disconnected}>
                    {isConnected ? '● Connected' : '● Connecting...'}
                </p>
            </header>

            <div className={styles.mainContent}>
                <aside className={styles.leftColumn}>
                    <div className={styles.widget}>
                        {/* --- MODIFIED: Initiative Widget --- */}
                        <div className={styles.initiativeHeader}>
                            <h2 className={styles.widgetTitle}>Initiative</h2>
                            {isDm && (
                                <ThemedButton 
                                    onClick={handleClearInitiative}
                                    variant="red"
                                    className={styles.dmButtonSmall}
                                >
                                    Clear
                                </ThemedButton>
                            )}
                        </div>
                        <textarea
                            className={styles.initiativeTextArea}
                            value={initiativeText}
                            onChange={handleInitiativeChange}
                            disabled={!isDm || !isConnected}
                            placeholder={isDm ? "Enter turn order..." : "Waiting for DM..."}
                        />
                    </div>
                    <div className={styles.widget}>
                        <h2 className={styles.widgetTitle}>Players</h2>
                        <ul>
                            {campaign.members?.map(member => (
                                <li key={member.id}>{member.character?.name || 'Unknown Character'}</li>
                            ))}
                        </ul>
                    </div>
                </aside>

                <main className={styles.centerColumn}>
                    <div className={styles.mapContainer}><p>Map Area</p></div>
                    {isDm && (
                        <div className={styles.dmControls}>
                            <ThemedButton onClick={() => alert("Award XP!")} shape="pill">Award XP</ThemedButton>
                            <ThemedButton onClick={() => alert("Award Gold!")} shape="pill">Award Gold</ThemedButton>
                            <ThemedButton onClick={() => alert("Award Items!")} shape="pill">Award Items</ThemedButton>
                            <ThemedButton onClick={() => alert("End Session!")} shape="pill">End Session</ThemedButton>
                        </div>
                    )}
                </main>
                
                <aside className={styles.rightColumn}>
                    <div className={`${styles.widget} ${styles.chatContainer}`}>
                        <h2 className={styles.widgetTitle}>Chat Log</h2>
                        <div ref={chatLogRef} className={styles.chatLog}>
                            {messages.map((msg, index) => (
                                <div key={index}>
                                    {msg.type === 'dice_roll' ? (
                                        <div className={styles.diceRollMessage}>
                                            <strong>{msg.payload.characterName || msg.sender}</strong> rolled {msg.payload.count}d{msg.payload.sides}: <strong> {msg.payload.total}</strong>
                                            <span className={styles.diceRollBreakdown}> ({msg.payload.rolls.join(' + ')})</span>
                                        </div>
                                    ) : (
                                        <div className={styles.chatMessage}>
                                            <strong>{msg.payload.characterName || msg.sender}:</strong> {msg.payload.text || msg.payload}
                                        </div>
                                    )}
                                </div>
                            ))}
                        </div>
                        <form onSubmit={handleSendMessage} className={styles.chatForm}>
                            <input type="text" placeholder="Type a message..." value={chatInput} onChange={(e) => setChatInput(e.target.value)} className={styles.chatInput} disabled={!isConnected} />
                            <ThemedButton type="submit" disabled={!isConnected} shape="pill">Send</ThemedButton>
                        </form>
                    </div>
                    <div className={styles.widget}>
                        <h2 className={styles.widgetTitle}>Dice Roller</h2>
                        <DiceRoller onRoll={handleRollDice} disabled={!isConnected} />
                    </div>
                </aside>
            </div>
        </div>
    );
};

export default CampaignRoomPage;
