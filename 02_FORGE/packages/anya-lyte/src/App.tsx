import React from 'react';
import { TamaguiProvider, createTamagui, YStack, Text, Button, Theme } from 'tamagui';
import { config } from '@tamagui/config/v3';
import { Database, Zap, Shield, Menu } from 'lucide-react-native';

const tamaguiConfig = createTamagui(config);

export default function App() {
  return (
    <TamaguiProvider config={tamaguiConfig}>
      <Theme name="dark">
        <YStack f={1} bg="$background" jc="center" ai="center" p="$4" space>
          {/* Header */}
          <YStack ai="center" space="$2">
            <Text fOW="bold" fS={28} col="$color">ANYA LYTE</Text>
            <Text col="$colorSecondary" fS={14}>v1.0 • Singularity Lattice</Text>
          </YStack>

          {/* Status Hub */}
          <YStack w="100%" br="$4" p="$4" bg="$color3" space="$3">
            <StatusItem icon={<Zap size={20} color="gold" />} label="TitanLink" status="STABLE" />
            <StatusItem icon={<Database size={20} color="cyan" />} label="UKG Sync" status="98%" />
            <StatusItem icon={<Shield size={20} color="lightgreen" />} label="Iron Gate" status="ACTIVE" />
          </YStack>

          {/* Actions */}
          <Button theme="active" w="100%" icon={Zap} size="$5">
            INITIATE INTENT
          </Button>

          <Button chromeless icon={Menu}>
            KNOWLEDGE GRAPH
          </Button>
        </YStack>
      </Theme>
    </TamaguiProvider>
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
