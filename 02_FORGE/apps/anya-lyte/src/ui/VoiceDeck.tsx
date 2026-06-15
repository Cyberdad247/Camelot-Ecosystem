import React, { useState, useEffect, useRef } from 'react';
import { YStack, XStack, Text, Button, Theme, AnimatePresence, Circle, ZStack, styled } from 'tamagui';
import { Mic, Volume2, Music, Save, MicOff } from 'lucide-react-native';
import { TitanLinkClient } from '../titanLinkClient';

/**
 * Anya Lyte: Voice Deck (Sir Sonus Resonance)
 * High-fidelity "The Orb" visualizer with multi-layered pulse.
 */
const PulseCircle = styled(Circle, {
  position: 'absolute',
  bc: '$blue10',
  opacity: 0.15,
  animation: 'lazy',
  enterStyle: { scale: 0.8, opacity: 0 },
  exitStyle: { scale: 2, opacity: 0 },
});

export const VoiceDeck = () => {
  const [isListening, setIsListening] = useState(false);
  const [pulseCount, setPulseCount] = useState(0);
  const [isStreaming, setIsStreaming] = useState(false);
  const [client] = useState(() => new TitanLinkClient("ws://127.0.0.1:18788"));

  useEffect(() => {
    client.connect();
    let interval: any;
    if (isListening) {
      interval = setInterval(() => {
        setPulseCount(prev => (prev + 1) % 5);
      }, 600);
    } else {
      setPulseCount(0);
    }

    const unsubscribe = client.onEvent((msg) => {
      if (msg.kind === 'audio_chunk') {
        setIsStreaming(true);
        if (msg.isFinal) {
          setTimeout(() => setIsStreaming(false), 1000);
        }
      }
    });

    return () => {
      clearInterval(interval);
      unsubscribe();
    };
  }, [isListening]);

  const toggleMic = () => {
    const newState = !isListening;
    setIsListening(newState);
    if (newState) {
      client.send({ kind: 'start_voice_stream', persona: 'Merlin_Omega' });
    }
  };

  const pushToMemory = () => {
    client.send({
      kind: 'memorize_intent',
      text: "Captured voice resonance for Ouroboros sync.",
      metadata: { persona: 'Merlin_Omega', timestamp: new Date().toISOString() }
    });
    alert("Intent crystallized.");
  };

  return (
    <Theme name="dark">
      <YStack f={1} jc="center" ai="center" space="$8" bg="$background">
        
        {/* The Orb: Sovereign Resonance Layer */}
        <ZStack jc="center" ai="center" w={300} h={300}>
          <AnimatePresence>
            {isListening && [1, 2, 3].map((i) => (
              <PulseCircle
                key={`pulse-${i}-${pulseCount}`}
                size={200 + i * 40}
                animation="lazy"
                scale={1}
              />
            ))}
          </AnimatePresence>
          
          <Circle 
            size={160} 
            bg="linear-gradient(135deg, $blue8, $purple8)" 
            elevate 
            ai="center" 
            jc="center"
            bw={1}
            boc="$blue10"
            style={{ shadowColor: 'cyan', shadowRadius: 20, shadowOpacity: 0.4 }}
          >
            {isListening ? (
              <YStack space="$2" ai="center">
                <Music size={40} color="white" />
                <Text fS={10} fOW="bold" col="white" ls={2}>RESONATING</Text>
              </YStack>
            ) : (
              <Mic size={50} color="white" />
            )}
          </Circle>
          
          {isStreaming && (
            <Text pos="absolute" b={-40} fS={10} col="$yellow10" fOW="bold" ls={2}>
              SONUS_STREAM_ACTIVE
            </Text>
          )}
        </ZStack>

        <YStack ai="center" space="$2">
          <Text fS={26} fOW="bold" col="$blue10">
            {isListening ? 'ANYA IS LISTENING' : 'RESONANCE READY'}
          </Text>
          <XStack ai="center" space="$2">
            <Circle size={8} bg={isListening ? '$green10' : '$colorSecondary'} />
            <Text col="$colorSecondary" ls={1}>SIR SONUS Omega ACTIVE</Text>
          </XStack>
        </YStack>

        <XStack space="$4">
          <Button 
            size="$7" 
            circular 
            icon={isListening ? MicOff : Mic} 
            onPress={toggleMic}
            onLongPress={pushToMemory}
            theme={isListening ? 'active' : 'alt2'}
            elevate
          />
          <Button
            size="$7"
            circular
            icon={Save}
            onPress={pushToMemory}
            theme="active"
          />
        </XStack>
        <Text fS={10} col="$colorSecondary" opa={0.5}>Hold 'Resonate' or tap Save for Ouroboros sync</Text>
      </YStack>
    </Theme>
  );
};
