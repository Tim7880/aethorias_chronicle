// Path: src/pages/CampaignRoomPage.tsx
import React, { useState, useEffect, useRef, useMemo } from 'react';
import { useParams } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { campaignService } from '../services/campaignService';
import { gameDataService } from '../services/gameDataService';
import type { Campaign, CampaignSession, InitiativeEntry } from '../types/campaign';
import type { Monster } from '../types/monster';
import styles from './CampaignRoomPage.module.css';
import ThemedButton from '../components/common/ThemedButton';
import ThemedInput from '../components/common/ThemedInput';
import { useCampaignSocket } from '../hooks/useCampaignSocket';
import DiceRoller from '../components/game/DiceRoller';
import InitiativeTracker from '../components/game/InitiativeTracker';

const CampaignRoomPage: React.FC = () => {
    const { campaignId } = useParams<{ campaignId: string }>();
    const auth = useAuth();

    const [campaign, setCampaign] = useState<Campaign | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [isDm, setIsDm] = useState(false);
    
    const [activeSession, setActiveSession] = useState<CampaignSession | null>(null);
    const [initiativeOrder, setInitiativeOrder] = useState<InitiativeEntry[]>([]);
    const [activeTurnId, setActiveTurnId] = useState<number | null>(null);
    const [monsters, setMonsters] = useState<Monster[]>([]);
    
    const [isSessionLoading, setIsSessionLoading] = useState(false);
    const [addInitiativeTarget, setAddInitiativeTarget] = useState<string>('');
    const [addInitiativeRoll, setAddInitiativeRoll] = useState('');
    
    const { messages, isConnected, sendMessage } = useCampaignSocket(campaignId, auth.token);
    const [chatInput, setChatInput] = useState('');
    const chatLogRef = useRef<HTMLDivElement>(null);

    const myCharacter = useMemo(() => {
        if (!auth.user || !campaign?.members) return null;
        const myMembership = campaign.members.find(m => m.user_id === auth.user?.id);
        return myMembership?.character || null;
    }, [auth.user, campaign]);

    useEffect(() => {
        const lastMessage = messages[messages.length - 1];
        if (lastMessage) {
            switch (lastMessage.type) {
                case 'initiative_update':
                    setInitiativeOrder(lastMessage.payload);
                    break;
                case 'turn_update':
                    setActiveTurnId(lastMessage.payload.active_entry_id);
                    break;
            }
        }
    }, [messages]);

    useEffect(() => {
        if (chatLogRef.current) chatLogRef.current.scrollTop = chatLogRef.current.scrollHeight;
    }, [messages]);

    useEffect(() => {
        const fetchAllData = async () => {
            if (auth.token && campaignId) {
                try {
                    const id = parseInt(campaignId, 10);
                    const [campaignData, sessionData, monsterData] = await Promise.all([
                        campaignService.getCampaignById(auth.token, id),
                        campaignService.getActiveSession(auth.token, id),
                        gameDataService.getMonsters(auth.token)
                    ]);
                    
                    setCampaign(campaignData);
                    setActiveSession(sessionData);
                    if (sessionData) setInitiativeOrder(sessionData.initiative_entries);
                    setMonsters(monsterData.sort((a, b) => a.name.localeCompare(b.name)));
                    if (auth.user && campaignData.dm_user_id === auth.user.id) setIsDm(true);
                } catch (err: any) {
                    setError(err.message || 'Failed to load campaign data.');
                } finally {
                    setIsLoading(false);
                }
            }
        };
        fetchAllData();
    }, [auth.token, campaignId, auth.user]);

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

    const handleStartCombat = () => {
        // This button now sends the clear_initiative message to start fresh
        if (window.confirm("Start a new combat? This will clear the current initiative order.")) {
            sendMessage('clear_initiative', {});
        }
    };

    const handleAddInitiative = (e: React.FormEvent) => {
        e.preventDefault();
        const roll = parseInt(addInitiativeRoll, 10);
        if (!addInitiativeTarget || isNaN(roll)) {
            alert("Please select a creature and enter a valid initiative roll.");
            return;
        }
        const isCharacter = addInitiativeTarget.startsWith('char_');
        const payload = {
            character_id: isCharacter ? parseInt(addInitiativeTarget.split('_')[1], 10) : null,
            monster_name: isCharacter ? null : addInitiativeTarget,
            initiative_roll: roll,
        };
        sendMessage('add_initiative', payload);
        setAddInitiativeTarget('');
        setAddInitiativeRoll('');
    };

    if (isLoading) return <div className={styles.pageContainer}>Loading Campaign Room...</div>;
    if (error) return <div className={styles.pageContainer}>Error: {error}</div>;
    if (!campaign) return <div className={styles.pageContainer}>Campaign not found.</div>;
    if (!activeSession && !isDm) return <div className={styles.pageContainer}><p>The Dungeon Master has not started the session yet.</p></div>

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
                        <h2 className={styles.widgetTitle}>Initiative</h2>
                        <InitiativeTracker entries={initiativeOrder} activeEntryId={activeTurnId} />
                    </div>
                    {isDm && (
                         <div className={styles.widget}>
                             <h2 className={styles.widgetTitle}>Add to Combat</h2>
                             <form onSubmit={handleAddInitiative} className={styles.addInitiativeForm}>
                                <select value={addInitiativeTarget} onChange={e => setAddInitiativeTarget(e.target.value)} className={styles.initiativeSelect} required>
                                    <option value="">-- Select Creature --</option>
                                    <optgroup label="Players">
                                        {campaign.members?.filter(m => m.character).map(m => (
                                            <option key={m.character!.id} value={`char_${m.character!.id}`}>{m.character!.name}</option>
                                        ))}
                                    </optgroup>
                                    <optgroup label="Monsters">
                                        {monsters.map(monster => (
                                            <option key={monster.id} value={monster.name}>{monster.name}</option>
                                        ))}
                                    </optgroup>
                                </select>
                                <input id="add-init-roll" type="number" placeholder="Roll" value={addInitiativeRoll} onChange={e => setAddInitiativeRoll(e.target.value)} className={styles.initiativeInput} required />
                                <ThemedButton type="submit" className={styles.dmButton}>Add</ThemedButton>
                            </form>
                         </div>
                    )}
                    <div className={styles.widget}>
                        <h2 className={styles.widgetTitle}>Players</h2>
                        <ul className={styles.playerList}>
                            {campaign.members?.filter(m => m.character).map(m => (
                                <li key={m.id} className={styles.playerListItem}>{m.character!.name}</li>
                            ))}
                        </ul>
                    </div>
                </aside>

                <main className={styles.centerColumn}>
                    <div className={styles.mapContainer}><p>Map Area</p></div>
                    {isDm && (
                        <div className={styles.dmControls}>
                            <ThemedButton onClick={handleStartCombat} shape="pill" className={styles.dmButton}>Start Combat</ThemedButton>
                            <ThemedButton onClick={() => sendMessage('next_turn', {})} shape="pill" className={styles.dmButton}>Next Turn</ThemedButton>
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
