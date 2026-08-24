import React, { useState, useEffect } from 'react';
import { YStack, XStack, Text, ScrollView, Card, Badge, Theme } from 'tamagui';
import { Activity, Package, CheckCircle, AlertCircle } from 'lucide-react-native';
import { TitanLinkClient } from '../api/titanlink_client';

/**
 * Anya Lyte: Jobs Screen (ClaraVerse Style)
 * Displays Swarm jobs and artifacts from titan_ledger.json
 */
export const JobsScreen = () => {
  const [jobs, setJobs] = useState<any[]>([]);
  const [client] = useState(() => new TitanLinkClient());

  useEffect(() => {
    client.connect();
    // Simulate fetching titan_ledger data via TitanLink
    client.send({ type: 'SYNC_DELTA', payload: { target: 'titan_ledger' } });

    client.addListener((msg) => {
      if (msg.type === 'SYNC_DELTA' && msg.payload?.nodes) {
        // Map ledger nodes to job cards
        const ledgerNode = msg.payload.nodes.find(n => n.type === 'UKGRoot');
        if (ledgerNode) {
          // This is a mock placeholder for real ledger parsing
          setJobs([
            { id: '1', title: 'Repo Assimilation: clawdbot', status: 'COMPLETED', type: 'FORGE' },
            { id: '2', title: 'TitanLink Server Deploy', status: 'COMPLETED', type: 'KERNEL' },
            { id: '3', title: 'Anya Lyte UI Scaffolding', status: 'IN_PROGRESS', type: 'MOBILE' }
          ]);
        }
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
          {jobs.map((job) => (
            <Card key={job.id} p="$4" br="$4" bg="$color3" elevate>
              <XStack jc="space-between" ai="center">
                <YStack space="$1">
                  <XStack ai="center" space="$2">
                    <Package size={16} color="$colorSecondary" />
                    <Text fS={16} fOW="bold">{job.title}</Text>
                  </XStack>
                  <Text col="$colorSecondary" fS={12}>Type: {job.type}</Text>
                </YStack>
                <Badge
                  bc={job.status === 'COMPLETED' ? '$green10' : '$orange10'}
                  p="$1"
                  px="$2"
                  br="$10"
                >
                  <Text fS={10} fOW="bold" col="white">{job.status}</Text>
                </Badge>
              </XStack>
            </Card>
          ))}
        </ScrollView>
      </YStack>
    </Theme>
  );
};
