// Path: src/pages/CampaignRoomPage.tsx
import React, { useState, useEffect, useRef, useMemo } from 'react';
import { useParams } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { campaignService } from '../services/campaignService';
import { characterService } from '../services/characterService';
import { gameDataService } from '../services/gameDataService';
import type { Campaign, Character } from '../types/campaign';
import type { Monster } from '../types/monster';
import EncounterModal, { type Combatant } from '../components/game/EncounterModal';
import styles from './CampaignRoomPage.module.css';
import ThemedButton from '../components/common/ThemedButton';
import { useCampaignSocket } from '../hooks/useCampaignSocket';
import DiceRoller from '../components/game/DiceRoller';
import CharacterStatModal from '../components/game/CharacterStatModal';
import InitiativeTracker from '../components/game/InitiativeTracker';

const CampaignRoomPage: React.FC = () => {
    const { campaignId } = useParams<{ campaignId: string }>();
    const auth = useAuth();

    const [campaign, setCampaign] = useState<Campaign | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [isDm, setIsDm] = useState(false);
    
    const [modalCharacter, setModalCharacter] = useState<Character | null>(null);
    const [isEncounterModalOpen, setIsEncounterModalOpen] = useState(false);
    const [monsters, setMonsters] = useState<Monster[]>([]);
    
    // --- START FIX: Destructure the CORRECT setters from the hook ---
    const { chatLogMessages, encounterState, setEncounterState, isConnected, sendMessage } = useCampaignSocket(campaignId, auth.token);
    // --- END FIX ---
    
    const [chatInput, setChatInput] = useState('');
    const chatLogRef = useRef<HTMLDivElement>(null);

    const myCharacter = useMemo(() => {
        if (!auth.user || !campaign?.members) return null;
        const myMembership = campaign.members.find(m => m.user_id === auth.user?.id);
        return myMembership?.character || null;
    }, [auth.user, campaign]);

    useEffect(() => {
        if (chatLogRef.current) chatLogRef.current.scrollTop = chatLogRef.current.scrollHeight;
    }, [chatLogMessages]);

    useEffect(() => {
        const fetchAllData = async () => {
            if (!auth.token || !campaignId) return;
            try {
                const id = parseInt(campaignId, 10);
                const [campaignData, monsterData, sessionData] = await Promise.all([
                    campaignService.getCampaignById(auth.token, id),
                    gameDataService.getMonsters(auth.token),
                    campaignService.getActiveSession(auth.token, id)
                ]);
                
                setCampaign(campaignData);
                setMonsters(monsterData.sort((a, b) => a.name.localeCompare(b.name)));
                if (sessionData) setEncounterState(sessionData);

                const dmStatus = !!(auth.user && campaignData.dm_user_id === auth.user.id);
                setIsDm(dmStatus);

                if (!sessionData && dmStatus) {
                    const newSession = await campaignService.startCampaignSession(auth.token, id);
                    setEncounterState(newSession);
                }
            } catch (err: any) {
                if (!err.message.includes("404")) {
                    setError(err.message || 'Failed to load campaign data.');
                }
            } finally {
                setIsLoading(false);
            }
        };
        fetchAllData();
    }, [auth.token, campaignId, auth.user, setEncounterState]); // Added setEncounterState to dependency array

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
    
    const handlePlayerNameClick = async (characterId: number) => {
        if (!isDm || !auth.token) return;
        try {
            setModalCharacter(await characterService.getCharacterById(auth.token, characterId));
        } catch (err: any) {
            setError("Could not fetch character details.");
        }
    };

    const handleStartEncounter = (combatants: Combatant[]) => {
        sendMessage('start_encounter', combatants);
        setIsEncounterModalOpen(false);
    };

    const activeInitiativeEntries = encounterState?.is_active ? encounterState.initiative_entries : [];
    const activeTurnId = encounterState?.is_active ? encounterState.active_initiative_entry_id : null;

    if (isLoading) return <div className={styles.pageContainer}><h1>Loading...</h1></div>;
    if (error) return <div className={styles.pageContainer}><h1>Error: {error}</h1></div>;
    if (!campaign) return <div className={styles.pageContainer}><h1>Campaign not found.</h1></div>;
    if (!encounterState && !isDm) return <div className={styles.pageContainer}><p>The Dungeon Master has not started the session yet.</p></div>

    return (
        <>
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
                            <InitiativeTracker entries={activeInitiativeEntries} activeEntryId={activeTurnId} />
                        </div>
                        <div className={styles.widget}>
                            <h2 className={styles.widgetTitle}>Players</h2>
                            <ul className={styles.playerList}>
                                {campaign.members?.filter(m => m.character).map(member => (
                                    <li key={member.id} className={isDm ? styles.playerListItemClickable : styles.playerListItem} onClick={() => isDm && handlePlayerNameClick(member.character!.id)}>
                                        {member.character!.name}
                                    </li>
                                ))}
                            </ul>
                        </div>
                    </aside>

                    <main className={styles.centerColumn}>
                        <div className={styles.mapContainer}><p>Map Area</p></div>
                        {isDm && (
                            <div className={styles.dmControls}>
                                <ThemedButton onClick={() => setIsEncounterModalOpen(true)} shape="pill" className={styles.dmButton}>Setup Encounter</ThemedButton>
                                <ThemedButton onClick={() => sendMessage('next_turn', {})} shape="pill" className={styles.dmButton} disabled={!encounterState?.is_active}>Next Turn</ThemedButton>
                                <ThemedButton onClick={() => sendMessage('end_encounter', {})} shape="pill" variant="red" className={styles.dmButton} disabled={!encounterState?.is_active}>End Encounter</ThemedButton>
                            </div>
                        )}
                    </main>
                    
                    <aside className={styles.rightColumn}>
                        <div className={`${styles.widget} ${styles.chatContainer}`}>
                            <h2 className={styles.widgetTitle}>Chat Log</h2>
                            <div ref={chatLogRef} className={styles.chatLog}>
                                {chatLogMessages.map((msg, index) => (
                                    <div key={index} className={styles.chatMessage}>
                                        <strong>{msg.sender}:</strong> {msg.payload.text || msg.payload}
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
            
            <CharacterStatModal character={modalCharacter} onClose={() => setModalCharacter(null)} />

            {isDm && (
                <EncounterModal 
                    isOpen={isEncounterModalOpen}
                    onClose={() => setIsEncounterModalOpen(false)}
                    onSubmit={handleStartEncounter}
                    players={campaign.members}
                    monsters={monsters}
                />
            )}
        </>
    );
};

export default CampaignRoomPage;