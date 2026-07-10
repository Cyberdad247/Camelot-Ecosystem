import { useAnyaCodecStore } from './store';
import { encodeNativeMessage, fetchNanoSwarmStatus } from './nativeBridge';
import { OpenHumanAvatar } from './OpenHumanAvatar';
import './style.css';

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
      setLastMessage(encodeNativeMessage({
        type: 'camelot.status',
        payload: {
          rune: '//STATUS',
          fallback: true,
          reason: error instanceof Error ? error.message : 'router unavailable',
        },
      }));
    }
  }

  return (
    <main>
      <section className="hero">
        <div>
          <p className="eyebrow">Cybertronia Node A</p>
          <h1>OpenHuman persona bridge</h1>
          <p>
            Frontend cartridge for status probes, kinematic persona frames, and
            HITL-gated Aaliyah comms intent previews.
          </p>
          <button type="button" onClick={() => void prepareStatusProbe()}>
            Prepare status probe
          </button>
        </div>
        <OpenHumanAvatar />
      </section>
      <section className="panel">
        <p>Bridge status: <strong>{bridgeStatus}</strong></p>
        <pre>{lastMessage || 'Awaiting Bifrost / nano-swarm router response.'}</pre>
      </section>
    </main>
  );
}
