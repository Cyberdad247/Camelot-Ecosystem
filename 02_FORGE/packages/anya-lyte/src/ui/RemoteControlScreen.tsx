import React, { useState, useEffect, useCallback } from 'react';
import {
  YStack,
  XStack,
  Text,
  ScrollView,
  Card,
  Button,
  Input,
  Theme,
  Sheet,
  Spinner,
} from 'tamagui';
import {
  Monitor,
  Mic,
  MicOff,
  Shield,
  ShieldAlert,
  Wifi,
  WifiOff,
  Terminal,
  Power,
  Camera,
  Send,
} from 'lucide-react-native';
import { TitanLinkClient } from '../api/titanlink_client';

interface RemoteDevice {
  id: string;
  label: string;
  os?: string;
  isOnline: boolean;
  trustLevel: 'LOW' | 'MEDIUM' | 'HIGH';
}

interface RemoteSession {
  sessionId: string;
  deviceId: string;
  status: 'connected' | 'connecting' | 'disconnected';
  commandsExecuted: number;
}

export const RemoteControlScreen = () => {
  const [devices, setDevices] = useState<RemoteDevice[]>([]);
  const [activeSession, setActiveSession] = useState<RemoteSession | null>(null);
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [manualInput, setManualInput] = useState('');
  const [connectingId, setConnectingId] = useState<string | null>(null);
  const [ironGateOpen, setIronGateOpen] = useState(false);
  const [client] = useState(() => new TitanLinkClient());

  useEffect(() => {
    client.connect();
    client.send({ kind: 'device_topology_request', includeOffline: true });

    client.addListener((msg) => {
      if (msg.kind === 'device_topology') setDevices(msg.topology.devices);
      if (msg.kind === 'rustdesk_session' && msg.status === 'connected') {
        setActiveSession({
          sessionId: msg.sessionId,
          deviceId: msg.deviceId,
          status: 'connected',
          commandsExecuted: 0,
        });
        setConnectingId(null);
      }
      if (msg.kind === 'approval_request') setIronGateOpen(true);
    });

    // Demo devices
    setDevices([
      {
        id: '987654321',
        label: 'Home Server',
        os: 'Ubuntu 22.04',
        isOnline: true,
        trustLevel: 'HIGH',
      },
      {
        id: '123456789',
        label: 'Office PC',
        os: 'Windows 11',
        isOnline: true,
        trustLevel: 'MEDIUM',
      },
    ]);
    return () => client.disconnect();
  }, []);

  const handleConnect = (deviceId: string) => {
    setConnectingId(deviceId);
    client.send({
      kind: 'rustdesk_connect',
      deviceId,
      authMethod: 'biometric',
      requireApproval: true,
    });
  };

  const handleVoiceCommand = (text: string) => {
    if (!activeSession) return;
    client.send({
      kind: 'remote_control',
      sessionId: activeSession.sessionId,
      action: 'voice_command',
      voiceIntent: text,
    });
    setTranscript(text);
  };

  const handleEndSession = () => {
    if (activeSession)
      client.send({ kind: 'rustdesk_disconnect', sessionId: activeSession.sessionId });
    setActiveSession(null);
  };

  const trustColors = { LOW: '$red10', MEDIUM: '$yellow10', HIGH: '$green10' };

  return (
    <Theme name="dark">
      <YStack f={1} bg="$background" p="$4">
        <XStack ai="center" jc="space-between" mb="$4">
          <XStack ai="center" space="$2">
            <Monitor size={28} color="#8b5cf6" />
            <Text fS={22} fOW="bold">
              Remote Control
            </Text>
          </XStack>
          <XStack ai="center" space="$2">
            <Shield size={20} color="#10b981" />
            <Text fS={12} col="$green10">
              Iron Gate
            </Text>
          </XStack>
        </XStack>

        {activeSession ? (
          <YStack space="$4" f={1}>
            <Card p="$3" br="$4" bg="$green3" borderWidth={1} borderColor="$green8">
              <XStack jc="space-between" ai="center">
                <XStack ai="center" space="$2">
                  <YStack w={10} h={10} br="$10" bc="$green10" />
                  <Text fOW="bold" col="$green11">
                    Connected
                  </Text>
                </XStack>
                <XStack space="$2">
                  <Button
                    size="$3"
                    bg="$blue10"
                    onPress={() =>
                      client.send({
                        kind: 'remote_control',
                        sessionId: activeSession.sessionId,
                        action: 'screen_capture',
                      })
                    }
                    icon={<Camera size={16} color="white" />}
                  />
                  <Button
                    size="$3"
                    bg="$red10"
                    onPress={handleEndSession}
                    icon={<Power size={16} color="white" />}
                  />
                </XStack>
              </XStack>
            </Card>

            <Card f={1} bg="$color2" br="$4" ai="center" jc="center">
              <Terminal size={64} color="#6b7280" />
              <Text col="$colorSecondary" mt="$3">
                Remote Screen
              </Text>
            </Card>

            <Card p="$4" br="$6" bg={isListening ? '$purple3' : '$color3'}>
              <XStack jc="space-between" ai="center" mb="$3">
                <Text fOW="bold">{isListening ? '🎤 Listening...' : '💬 Voice Command'}</Text>
                <Button
                  size="$3"
                  circular
                  bg={isListening ? '$red10' : '$purple10'}
                  onPress={() => setIsListening(!isListening)}
                  icon={
                    isListening ? (
                      <MicOff size={18} color="white" />
                    ) : (
                      <Mic size={18} color="white" />
                    )
                  }
                />
              </XStack>
              {transcript && (
                <Card p="$2" bg="$color2" br="$3" mb="$2">
                  <Text fontStyle="italic">"{transcript}"</Text>
                </Card>
              )}
              <XStack space="$2">
                <Input
                  flex={1}
                  placeholder="Type command..."
                  value={manualInput}
                  onChangeText={setManualInput}
                  bg="$color2"
                />
                <Button
                  size="$4"
                  bg="$blue10"
                  onPress={() => {
                    if (manualInput.trim()) {
                      handleVoiceCommand(manualInput);
                      setManualInput('');
                    }
                  }}
                  icon={<Send size={18} color="white" />}
                />
              </XStack>
            </Card>
          </YStack>
        ) : (
          <ScrollView f={1} space="$3">
            <Text fS={14} col="$colorSecondary" mb="$2">
              Devices ({devices.filter((d) => d.isOnline).length} online)
            </Text>
            {devices.map((d) => (
              <Card
                key={d.id}
                p="$4"
                br="$4"
                bg="$color3"
                elevate
                pressStyle={{ scale: 0.98 }}
                onPress={() => d.isOnline && handleConnect(d.id)}
                opacity={d.isOnline ? 1 : 0.5}
              >
                <XStack jc="space-between" ai="center">
                  <XStack ai="center" space="$3">
                    {d.isOnline ? (
                      <Wifi size={24} color="#10b981" />
                    ) : (
                      <WifiOff size={24} color="#6b7280" />
                    )}
                    <YStack>
                      <Text fS={16} fOW="bold">
                        {d.label}
                      </Text>
                      <Text fS={12} col="$colorSecondary">
                        {d.os} • {d.id.slice(0, 8)}...
                      </Text>
                    </YStack>
                  </XStack>
                  <XStack ai="center" space="$2">
                    <YStack w={8} h={8} br="$10" bc={trustColors[d.trustLevel]} />
                    {connectingId === d.id ? (
                      <Spinner size="small" color="$blue10" />
                    ) : (
                      <Monitor size={20} color="#8b5cf6" />
                    )}
                  </XStack>
                </XStack>
              </Card>
            ))}
          </ScrollView>
        )}

        <Sheet open={ironGateOpen} onOpenChange={setIronGateOpen} snapPoints={[40]} modal>
          <Sheet.Overlay />
          <Sheet.Frame p="$4" bg="$color2">
            <YStack space="$4" ai="center">
              <ShieldAlert size={48} color="#f59e0b" />
              <Text fS={18} fOW="bold" ta="center">
                Iron Gate Authorization
              </Text>
              <Text col="$colorSecondary" ta="center">
                Biometric verification required
              </Text>
              <XStack space="$3" w="100%">
                <Button flex={1} bg="$red10" onPress={() => setIronGateOpen(false)}>
                  <Text col="white">Deny</Text>
                </Button>
                <Button
                  flex={1}
                  bg="$green10"
                  onPress={() => {
                    client.send({ kind: 'approval_response', approved: true });
                    setIronGateOpen(false);
                  }}
                >
                  <Text col="white">Approve</Text>
                </Button>
              </XStack>
            </YStack>
          </Sheet.Frame>
        </Sheet>
      </YStack>
    </Theme>
  );
};
