import { Cpu, Globe, Settings, ShieldCheck } from 'lucide-react-native';
import React, { useState } from 'react';
import { Label, ScrollView, Separator, Switch, Text, Theme, XStack, YStack } from 'tamagui';

/**
 * Anya Lyte: Settings & Providers Hub
 * Mapped to api_manifest.yaml and dna.json
 */
export const SettingsScreen = () => {
  const [providers, setProviders] = useState({
    openai: true,
    anthropic: true,
    local_llama: false,
    clawdbot: true,
  });

  const toggleProvider = (key: string) => {
    setProviders((prev) => ({ ...prev, [key]: !prev[key] }));
  };

  return (
    <Theme name="dark">
      <YStack f={1} bg="$background" p="$4">
        <XStack ai="center" space="$2" mb="$4">
          <Settings size={23} color="$blue10" />
          <Text fS={22} fOW="bold">
            System Configuration
          </Text>
        </XStack>

        <ScrollView f={1} space="$4">
          {/* System Health Section */}
          <YStack space="$2">
            <XStack ai="center" space="$2">
              <Cpu size={18} color="$colorSecondary" />
              <Text fS={14} fOW="bold" col="$colorSecondary">
                KERNEL STATUS
              </Text>
            </XStack>
            <YStack p="$3" br="$4" bg="$color3">
              <XStack jc="space-between" ai="center">
                <Text>Status</Text>
                <Text col="$green10" fOW="bold">
                  RADIANT
                </Text>
              </XStack>
            </YStack>
          </YStack>

          <Separator />

          {/* Providers Section */}
          <YStack space="$3">
            <XStack ai="center" space="$2">
              <Globe size={18} color="$colorSecondary" />
              <Text fS={14} fOW="bold" col="$colorSecondary">
                COGNITIVE PROVIDERS
              </Text>
            </XStack>

            <ProviderItem
              label="OpenAI (GPT-4.5)"
              active={providers.openai}
              onToggle={() => toggleProvider('openai')}
            />
            <ProviderItem
              label="Anthropic (Claude-3.5)"
              active={providers.anthropic}
              onToggle={() => toggleProvider('anthropic')}
            />
            <ProviderItem
              label="Local Llama (LLM-3-8B)"
              active={providers.local_llama}
              onToggle={() => toggleProvider('local_llama')}
            />
            <ProviderItem
              label="Clawdbot Gateway"
              active={providers.clawdbot}
              onToggle={() => toggleProvider('clawdbot')}
            />
          </YStack>

          <Separator />

          {/* Security Section */}
          <YStack space="$2">
            <XStack ai="center" space="$2">
              <ShieldCheck size={18} color="$colorSecondary" />
              <Text fS={14} fOW="bold" col="$colorSecondary">
                SECURITY & ACCESS
              </Text>
            </XStack>
            <YStack p="$3" br="$4" bg="$color3">
              <XStack jc="space-between" ai="center">
                <Text>Biometric Encryption</Text>
                <Text col="$blue10">ENABLED</Text>
              </XStack>
              <XStack jc="space-between" ai="center" mt="$2">
                <Text>Tailscale Tunnel</Text>
                <Text col="$green10">VERIFIED</Text>
              </XStack>
            </YStack>
          </YStack>
        </ScrollView>
      </YStack>
    </Theme>
  );
};

function ProviderItem({ label, active, onToggle }) {
  return (
    <XStack jc="space-between" ai="center" p="$3" br="$4" bg="$color2">
      <Label f={1} fS={16}>
        {label}
      </Label>
      <Switch size="$3" checked={active} onCheckedChange={onToggle}>
        <Switch.Thumb animation="bouncy" />
      </Switch>
    </XStack>
  );
}
