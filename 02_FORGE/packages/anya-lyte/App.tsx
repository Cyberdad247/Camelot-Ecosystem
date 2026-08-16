// ANYA LYTE: ENTRY POINT
import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet } from 'react-native';
import TitanLink from './src/services/TitanLink';
import Hudson from './src/components/Hudson';

export default function App() {
  const [status, setStatus] = useState<string>('DISCONNECTED');

  useEffect(() => {
    const link = new TitanLink('ws://localhost:18788');
    link.on('CONNECT', () => setStatus('SECURE LINK ESTABLISHED'));
    link.connect();
  }, []);

  return (
    <View style={styles.container}>
      <Text style={styles.header}>ANYA LYTE Omega</Text>
      <Text style={styles.status}>STATUS: {status}</Text>
      <Hudson />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#121212',
    alignItems: 'center',
    justifyContent: 'center',
  },
  header: { color: '#D4AF37', fontSize: 24, fontWeight: 'bold' },
  status: { color: '#00FFFF', marginTop: 10 },
});
