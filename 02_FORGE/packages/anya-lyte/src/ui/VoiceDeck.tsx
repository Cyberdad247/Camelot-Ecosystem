import React, { useState } from 'react';
import { YStack, Text, Button, Theme, AnimatePresence, Circle } from 'tamagui';
import { Mic, Volume2 } from 'lucide-react-native';

/**
 * Anya Lyte: Voice Deck (Sir Sonus / Sir Sonus Integration)
 * High-velocity voice interface with "The Orb" visualizer
 */
export const VoiceDeck = () => {
  const [isListening, setIsListening] = useState(false);

  const toggleMic = () => {
    setIsListening(!isListening);
    // In production, this hooks into Expo Audio mic recording
  };

  return (
    <Theme name="dark">
      <YStack f={1} jc="center" ai="center" space="$8" bg="$background">
        
        {/* The Orb (Visualizer Placeholder) */}
        <YStack jc="center" ai="center">
          <AnimatePresence>
            {isListening && (
              <Circle
                key="pulse"
                size={200}
                bc="$blue10"
                opacity={0.3}
                animation="lazy"
                enterStyle={{ scale: 0.5, opacity: 0 }}
                exitStyle={{ scale: 1.5, opacity: 0 }}
                position="absolute"
              />
            )}
          </AnimatePresence>
          <Circle size={150} bg="$color3" elevate ai="center" jc="center">
            {isListening ? (
              <ActivityIndicator color="cyan" />
            ) : (
              <Mic size={50} color="$blue10" />
            )}
          </Circle>
        </YStack>

        <YStack ai="center" space="$2">
          <Text fS={24} fOW="bold">{isListening ? 'Anya is listening...' : 'Ready to Conduct'}</Text>
          <Text col="$colorSecondary">Sir Sonus Resonance active</Text>
        </YStack>

        <Button 
          size="$6" 
          circular 
          icon={isListening ? Volume2 : Mic} 
          onPress={toggleMic}
          theme={isListening ? 'active' : 'alt1'}
          elevate
        />
      </YStack>
    </Theme>
  );
};

function ActivityIndicator({ color }) {
  return (
    <YStack space="$2" ai="center">
      <XStack space="$1">
        {[1, 2, 3].map(i => (
          <Circle key={i} size={8} bg={color} animation="bouncy" />
        ))}
      </XStack>
    </YStack>
  );
}

function XStack({ children, space, ai }) {
  return (
    <Theme name="dark">
      <YStack fd="row" space={space} ai={ai}>
        {children}
      </YStack>
    </Theme>
  );
}
