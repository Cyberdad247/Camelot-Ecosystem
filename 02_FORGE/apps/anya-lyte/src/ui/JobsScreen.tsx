import React, { useState, useEffect } from 'react';
import { YStack, XStack, Text, ScrollView, Card, Badge, Theme } from 'tamagui';
import { Activity, Package, CheckCircle, AlertCircle } from 'lucide-react-native';
import { TitanLinkClient } from '../titanLinkClient';

/**
 * Anya Lyte: Jobs Screen (ClaraVerse Style)
 * Displays Swarm jobs and artifacts from titan_ledger.json
 */
export const JobsScreen = () => {
  const [jobs, setJobs] = useState<any[]>([]);
  const [client] = useState(() => new TitanLinkClient("ws://127.0.0.1:18788"));

  useEffect(() => {
    client.connect();
    // Simulate fetching titan_ledger data via TitanLink
    client.send({ kind: 'request_approval', actionId: 'sync_ledger' }); // Dummy command
    
    return client.onEvent((msg) => {
      if (msg.kind === 'ukg_delta') {
        // Map ledger nodes to job cards
        setJobs([
          { id: '1', title: 'Repo Assimilation: clawdbot', status: 'COMPLETED', type: 'FORGE' },
          { id: '2', title: 'TitanLink Server Deploy', status: 'COMPLETED', type: 'KERNEL' },
          { id: '3', title: 'Anya Lyte UI Scaffolding', status: 'IN_PROGRESS', type: 'MOBILE' }
        ]);
      }
    });
  }, []);

  return (
    <Theme name="dark">
      <YStack f={1} bg="$background" p="$4">
        <XStack ai="center" space="$2" mb="$4">
          <Activity size={24} color="$blue10" />
          <Text fS={22} fOW="bold">Swarm Monitor</Text>
        </XStack>

        <ScrollView f={1} space="$3">
          <Text fS={14} fOW="bold" opa={0.5} mb="$2">ACTIVE SWARMS</Text>
          {jobs.map((job) => (
            <Card key={job.id} p="$4" br="$4" bg="$color2" mb="$3">
              <XStack jc="space-between" ai="center">
                <YStack space="$1">
                  <XStack ai="center" space="$2">
                    <Package size={16} color="$blue10" />
                    <Text fS={16} fOW="bold">{job.title}</Text>
                  </XStack>
                  <Text col="$colorSecondary" fS={12}>Type: {job.type}</Text>
                </YStack>
                <Badge 
                  bc={job.status === 'COMPLETED' ? '$green10' : '$orange10'}
                  px="$2"
                  br="$10"
                >
                  <Text fS={10} fOW="bold" col="white">{job.status}</Text>
                </Badge>
              </XStack>
            </Card>
          ))}

          <Text fS={14} fOW="bold" opa={0.5} mt="$4" mb="$2">CLARA-INSPIRED WORKFLOWS</Text>
          <Card p="$4" br="$4" bg="$color2" boc="$purple10" bw={1}>
            <XStack jc="space-between" ai="center">
              <YStack f={1} space="$1">
                <Text fS={16} fOW="bold">Adaptive CRM Sync</Text>
                <Text fS={12} col="$colorSecondary">LeadSquared ↔ HubSpot ↔ GSheets</Text>
              </YStack>
              <Activity size={20} color="$purple10" />
            </XStack>
          </Card>
          <Card p="$4" br="$4" bg="$color2" mt="$2">
            <XStack jc="space-between" ai="center">
              <YStack f={1} space="$1">
                <Text fS={16} fOW="bold">Intelligent Lead Nurturer</Text>
                <Text fS={12} col="$colorSecondary">Discord ↔ Telegram ↔ SendGrid</Text>
              </YStack>
              <Activity size={20} color="$purple10" />
            </XStack>
          </Card>
        </ScrollView>
      </YStack>
    </Theme>
  );
};
