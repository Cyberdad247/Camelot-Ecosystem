import React, { useState, useEffect } from 'react';
import { YStack, XStack, Text, Input, Button, ScrollView, Theme } from 'tamagui';
import { Send } from 'lucide-react-native';
import { TitanLinkClient } from '../api/titanlink_client';

/**
 * Anya Lyte: Chat Surface (Sprint 01 Prototype)
 */
export const ChatScreen = () => {
  const [messages, setMessages] = useState<any[]>([]);
  const [input, setInput] = useState('');
  const [client] = useState(() => new TitanLinkClient());

  useEffect(() => {
    client.connect();
    client.addListener((msg) => {
      if (msg.kind === 'chat_delta') {
        const delta = msg.delta;
        setMessages(prev => [...prev, {
          id: msg.id,
          text: delta.text,
          role: delta.role
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
    <YStack f={1} bg="$background" p="$4">
      <ScrollView f={1} space="$2">
        {messages.map((m) => (
          <XStack
            key={m.id}
            jc={m.role === 'user' ? 'flex-end' : 'flex-start'}
            w="100%"
          >
            <YStack
              bg={m.role === 'user' ? '$blue10' : '$color4'}
              p="$3"
              br="$4"
              maxW="80%"
            >
              <Text col="white">{m.text}</Text>
            </YStack>
          </XStack>
        ))}
      </ScrollView>

      <XStack space="$2" ai="center" mt="$4">
        <Input
          f={1}
          value={input}
          onChangeText={setInput}
          placeholder="Speak to Merlin..."
          br="$10"
        />
        <Button circle icon={Send} onPress={sendMessage} />
      </XStack>
    </YStack>
  );
};
