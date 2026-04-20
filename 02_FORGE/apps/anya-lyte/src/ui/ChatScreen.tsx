import React, { useState, useEffect } from 'react';
import { YStack, XStack, Text, Input, Button, ScrollView, Theme, Circle, styled } from 'tamagui';
import { Send, MessageSquare, Zap, Shield } from 'lucide-react-native';
import { TitanLinkClient } from '../titanLinkClient';

/**
 * Anya Lyte: Hardened Chat UX
 * Premium messaging interface with role-based styling.
 */
const MessageBubble = styled(YStack, {
  p: '$3',
  br: '$4',
  maxW: '85%',
  mb: '$2',
  variants: {
    role: {
      user: {
        bg: '$blue9',
        als: 'flex-end',
        btrr: 0,
      },
      knight: {
        bg: '$color4',
        als: 'flex-start',
        btlr: 0,
      },
      merlin: {
        bg: 'linear-gradient(135deg, $purple9, $blue9)',
        als: 'flex-start',
        btlr: 0,
      }
    }
  } as const
});

export const ChatScreen = () => {
  const [messages, setMessages] = useState<any[]>([]);
  const [input, setInput] = useState('');
  const [client] = useState(() => new TitanLinkClient("ws://127.0.0.1:18788"));

  useEffect(() => {
    client.connect();
    return client.onEvent((msg) => {
      if (msg.kind === 'chat_delta') {
        const delta = msg.delta;
        setMessages(prev => [...prev, { 
          id: msg.id, 
          text: delta.text, 
          role: delta.role,
          confidence: delta.metadata?.confidence
        }]);
      }
    });
  }, []);

  const sendMessage = () => {
    if (!input) return;
    const msgId = Date.now().toString();
    const newMsg = { id: msgId, text: input, role: 'user' };
    setMessages(prev => [...prev, newMsg]);
    client.send({
      kind: 'send_message',
      conversationId: 'default',
      message: {
        id: msgId,
        role: 'user',
        text: input,
        createdAt: new Date().toISOString()
      }
    });
    setInput('');
  };

  return (
    <Theme name="dark">
      <YStack f={1} bg="$background">
        <XStack ai="center" p="$4" space="$2" boc="$color4" bbw={1}>
          <MessageSquare size={20} color="$blue10" />
          <Text fS={18} fOW="bold">Anya Conductor</Text>
        </XStack>

        <ScrollView f={1} p="$3" contentContainerStyle={{ pb: 20 }}>
          {messages.map((m) => (
            <MessageBubble key={m.id} role={m.role}>
              <XStack ai="center" space="$2" mb="$1">
                {m.role === 'user' ? <Circle size={4} bg="white" /> : <Zap size={10} color="$yellow10" />}
                <Text fS={10} fOW="bold" opa={0.7} col="white" ls={1}>
                  {m.role.toUpperCase()}
                </Text>
              </XStack>
              <Text col="white" fS={15}>{m.text}</Text>
              {m.confidence && (
                <Text fS={9} col="$colorSecondary" mt="$1">Confidence: {(m.confidence * 100).toFixed(0)}%</Text>
              )}
            </MessageBubble>
          ))}
        </ScrollView>

        <XStack p="$4" space="$2" boc="$color4" btw={1} bg="$background">
          <Input 
            f={1} 
            placeholder="Relay intent..." 
            value={input} 
            onChangeText={setInput}
            bg="$color2"
            br="$10"
            px="$4"
          />
          <Button 
            circular 
            icon={Send} 
            onPress={sendMessage} 
            theme="active"
            disabled={!input}
          />
        </XStack>
      </YStack>
    </Theme>
  );
};
