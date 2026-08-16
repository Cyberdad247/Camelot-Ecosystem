import { useAnyaCodecStore } from './store';
import { encodeNativeMessage, fetchNanoSwarmStatus } from './nativeBridge';

export function App() {
  const { bridgeStatus, lastMessage, setBridgeStatus, setLastMessage } = useAnyaCodecStore();

  async function prepareStatusProbe() {
    setBridgeStatus('connecting');
    try {
      const status = await fetchNanoSwarmStatus();
      setBridgeStatus('connected');
      setLastMessage(JSON.stringify(status, null, 2));
    } catch (error) {
      setBridgeStatus('idle');
      setLastMessage(
        encodeNativeMessage({
          type: 'camelot.status',
          payload: {
            rune: '//STATUS',
            fallback: true,
            reason: error instanceof Error ? error.message : 'router unavailable',
          },
        }),
      );
    }
  }

  return (
    <main>
      <h1>Camelot Node A Frontend</h1>
      <p>Bridge status: {bridgeStatus}</p>
      <button type="button" onClick={() => void prepareStatusProbe()}>
        Prepare status probe
      </button>
      <pre>{lastMessage}</pre>
    </main>
  );
}
