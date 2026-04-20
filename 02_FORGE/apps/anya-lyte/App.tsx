import React, { useState, useEffect } from 'react';
import { TamaguiProvider, createTamagui, YStack, XStack, Text, Button, Theme } from 'tamagui';
import { config } from '@tamagui/config/v3';
import { Database, Zap, Shield, Menu, MessageSquare, Activity, Settings as SettingsIcon, Mic } from 'lucide-react-native';
import { ChatScreen } from './src/ui/ChatScreen';
import { JobsScreen } from './src/ui/JobsScreen';
import { SettingsScreen } from './src/ui/SettingsScreen';
import { VoiceDeck } from './src/ui/VoiceDeck';
import { ApprovalSheet } from './src/ui/ApprovalSheet';
import { TitanLinkClient } from './src/titanLinkClient';
import { TitanLinkEvent } from '@camelot/anya-domain';

const tamaguiConfig = createTamagui(config);

export default function App() {
  const [activeTab, setActiveTab] = useState<'CHAT' | 'VOICE' | 'MONITOR' | 'SETTINGS'>('CHAT');
  const [approvalVisible, setApprovalVisible] = useState(false);
  const [pendingAction, setPendingAction] = useState<any>(null);
  const [client] = useState(() => new TitanLinkClient("ws://100.118.224.52:18788"));

  useEffect(() => {
    client.connect();
    return client.onEvent((msg) => {
      if (msg.kind === 'approval_request') {
        setPendingAction(msg.action);
        setApprovalVisible(true);
      }
    });
  }, []);

  const handleApprove = () => {
    client.send({
      kind: 'approval_response',
      actionId: pendingAction.id,
      approved: true,
      signedAt: new Date().toISOString(),
      signature: `SIG_${Math.random().toString(16).slice(2)}` // Simulated biometric signature
    });
    setApprovalVisible(false);
  };

  const renderScreen = () => {
    switch (activeTab) {
      case 'CHAT': return <ChatScreen />;
      case 'VOICE': return <VoiceDeck />;
      case 'MONITOR': return <JobsScreen />;
      case 'SETTINGS': return <SettingsScreen />;
    }
  };

  return (
    <TamaguiProvider config={tamaguiConfig}>
      <Theme name="dark">
        <YStack f={1} bg="$background">
          {/* Main Content Area */}
          <YStack f={1}>
            {renderScreen()}
          </YStack>

          {/* Iron Gate Overlay */}
          <ApprovalSheet
            visible={approvalVisible}
            action={pendingAction}
            onApprove={() => setApprovalVisible(false)}
            onReject={() => setApprovalVisible(false)}
          />

          {/* Tab Navigation Bar */}
          <XStack
            h={80}
            bg="$color3"
            jc="space-around"
            ai="center"
            bbw={0}
            btw={1}
            bc="$color5"
            pb="$4"
          >
            <NavTab
              icon={<MessageSquare size={24} color={activeTab === 'CHAT' ? '$blue10' : '$colorSecondary'} />}
              label="Anya"
              active={activeTab === 'CHAT'}
              onPress={() => setActiveTab('CHAT')}
            />
            <NavTab
              icon={<Mic size={24} color={activeTab === 'VOICE' ? '$blue10' : '$colorSecondary'} />}
              label="Conductor"
              active={activeTab === 'VOICE'}
              onPress={() => setActiveTab('VOICE')}
            />
            <NavTab
              icon={<Activity size={24} color={activeTab === 'MONITOR' ? '$blue10' : '$colorSecondary'} />}
              label="Swarm"
              active={activeTab === 'MONITOR'}
              onPress={() => setActiveTab('MONITOR')}
            />
            <NavTab
              icon={<SettingsIcon size={24} color={activeTab === 'SETTINGS' ? '$blue10' : '$colorSecondary'} />}
              label="System"
              active={activeTab === 'SETTINGS'}
              onPress={() => setActiveTab('SETTINGS')}
            />
          </XStack>
        </YStack>
      </Theme>
    </TamaguiProvider>
  );
}

function NavTab({ icon, label, active, onPress }) {
  return (
    <YStack ai="center" onPress={onPress} opacity={active ? 1 : 0.6} space="$1">
      {icon}
      <Text fS={10} col={active ? '$blue10' : '$colorSecondary'}>{label}</Text>
    </YStack>
  );
}

function StatusItem({ icon, label, status }) {
  return (
    <YStack fd="row" jc="space-between" ai="center">
      <YStack fd="row" ai="center" space="$2">
        {icon}
        <Text fD="bold">{label}</Text>
      </YStack>
      <Text col="$blue10">{status}</Text>
    </YStack>
  );
}
