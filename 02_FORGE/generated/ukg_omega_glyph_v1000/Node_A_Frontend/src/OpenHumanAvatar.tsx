import { usePersona, type PersonaFrame } from './usePersona';

export interface OpenHumanAvatarProps {
  frame?: PersonaFrame;
}

export function OpenHumanAvatar({ frame }: OpenHumanAvatarProps) {
  const persona = usePersona(frame);
  const eyeScale = Math.max(0.18, 1 - persona.blink);
  const mouthHeight = 8 + persona.jawOpen * 34;
  const smileOffset = persona.smile * 12;

  return (
    <section className="avatar-card" aria-label="OpenHuman avatar preview">
      <div
        className="avatar-head"
        style={{
          transform: `rotate(${persona.headYaw}deg) translateY(${persona.headPitch}px)`,
        }}
      >
        <div className="avatar-eye left" style={{ transform: `scaleY(${eyeScale})` }} />
        <div className="avatar-eye right" style={{ transform: `scaleY(${eyeScale})` }} />
        <div
          className="avatar-mouth"
          style={{
            height: `${mouthHeight}px`,
            borderRadius: `${16 + smileOffset}px ${16 + smileOffset}px 24px 24px`,
          }}
        />
      </div>
      <p>Persona stream: LERP blendshape preview active</p>
    </section>
  );
}
