import React, { useState } from 'react';
import { YStack, XStack, Text, Button, Theme, Sheet, Card } from 'tamagui';
import { ShieldAlert, Fingerprint, XCircle } from 'lucide-react-native';

/**
 * Anya Lyte: Iron Gate Approval Sheet
 * Triggered for high-risk actions (Biometric Gated)
 */
export const ApprovalSheet = ({ visible, action, onApprove, onReject }) => {
  const [approving, setApproving] = useState(false);

  const handleApprove = () => {
    setApproving(true);
    // Simulate biometric check
    setTimeout(() => {
      setApproving(false);
      onApprove();
    }, 1500);
  };

  return (
    <Sheet
      open={visible}
      dismissOnSnapToBottom
      animation="bouncy"
      modal
      snapPoints={[40]}
    >
      <Sheet.Frame p="$4" bg="$color3">
        <Theme name="dark">
          <YStack space="$4" ai="center">
            <XStack ai="center" space="$2">
              <ShieldAlert size={28} color="$orange10" />
              <Text fS={20} fOW="bold">IRON GATE APPROVAL</Text>
            </XStack>

            <Card p="$4" bg="$color2" w="100%">
              <YStack space="$2">
                <Text fOW="bold" fS={16}>{action?.summary || 'High Risk Action'}</Text>
                <Text col="$colorSecondary" fS={12}>{action?.description}</Text>
                <XStack jc="space-between" mt="$2">
                  <Text fS={12} col="$red10">RISK: {action?.riskLevel}</Text>
                  <Text fS={12} col="$colorSecondary">TTL: {action?.ttl}s</Text>
                </XStack>
              </YStack>
            </Card>

            <YStack w="100%" space="$3">
              <Button 
                theme="active" 
                size="$5" 
                icon={approving ? null : Fingerprint}
                onPress={handleApprove}
                disabled={approving}
              >
                {approving ? 'VERIFYING BIOMETRICS...' : 'SIGN & APPROVE'}
              </Button>
              <Button 
                chromeless 
                icon={XCircle} 
                onPress={onReject}
                disabled={approving}
              >
                REJECT ACTION
              </Button>
            </YStack>
          </YStack>
        </Theme>
      </Sheet.Frame>
    </Sheet>
  );
};
