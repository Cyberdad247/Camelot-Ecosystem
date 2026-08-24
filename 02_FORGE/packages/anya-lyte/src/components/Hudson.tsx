// HUDSON (The Smart HUD)
// Reacts to TitanLink events to update the Avatar

import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { AvatarManager, KnightPersona } from '../services/AvatarManager';
import TitanLink from '../services/TitanLink';

interface HudsonProps {
  link: TitanLink;
}

export default function Hudson({ link }: HudsonProps) {
  const [persona, setPersona] = useState<KnightPersona>("Anya_Omega");
  const [cue, setCue] = useState<string>("System Online");

  useEffect(() => {
    // Listen for Swarm Handoffs
    link.on("HANDOFF", (data: any) => {
      console.log(`[📱] HUD Recieved Handoff: ${data.to}`);
      setPersona(data.to);
      setCue(data.vocal_cue);
    });
  }, [link]);

  const state = AvatarManager.getState(persona);

  return (
    <View style={[styles.card, { borderColor: state.color }]}>
      <Text style={styles.avatar}>{state.asset}</Text>
      <Text style={[styles.role, { color: state.color }]}>{state.id}</Text>
      <Text style={styles.status}>{state.statusMsg}</Text>
      <View style={styles.terminal}>
        <Text style={styles.log}>&gt; {cue}</Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    width: '90%', padding: 20, borderWidth: 2, borderRadius: 15,
    backgroundColor: '#1a1b26', alignItems: 'center'
  },
  avatar: { fontSize: 60, marginBottom: 10 },
  role: { fontSize: 20, fontWeight: 'bold', textTransform: 'uppercase' },
  status: { color: '#888', fontStyle: 'italic', marginBottom: 15 },
  terminal: {
    width: '100%', backgroundColor: '#000', padding: 10, borderRadius: 5
  },
  log: { color: '#00FF00', fontFamily: 'monospace' }
});