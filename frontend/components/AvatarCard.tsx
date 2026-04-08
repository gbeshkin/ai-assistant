"use client";

type Props = {
  mode?: "idle" | "listening" | "talking";
};

export default function AvatarCard({ mode = "idle" }: Props) {
  const mouthRy = mode === "talking" ? 24 : mode === "listening" ? 18 : 10;
  const shellClass = `avatar-shell ${mode}`;
  const dotClass = mode === "talking" ? "dot busy" : mode === "listening" ? "dot live" : "dot";
  const statusText =
    mode === "talking" ? "Speaking" : mode === "listening" ? "Listening" : "Ready";

  return (
    <div className="card avatar-card">
      <div className="avatar-stage">
        <svg
          className="avatar-svg"
          viewBox="0 0 800 900"
          role="img"
          aria-label="Tallinn AI Assistant animated avatar"
        >
          <g className={shellClass}>
            <rect x="80" y="70" width="640" height="730" rx="34" fill="#F8FAFC" stroke="#D1D5DB" strokeWidth="4" />
            <circle cx="400" cy="290" r="120" fill="#F1C9A5" />
            <path d="M290 250C300 180 350 145 400 145C450 145 500 180 510 250C500 235 490 225 470 215C455 240 430 255 400 255C370 255 345 240 330 215C310 225 300 235 290 250Z" fill="#374151" />
            <ellipse cx="355" cy="290" rx="12" ry="10" fill="#1F2937" />
            <ellipse cx="445" cy="290" rx="12" ry="10" fill="#1F2937" />
            <path d="M322 263C344 252 365 252 386 263" stroke="#374151" strokeWidth="6" strokeLinecap="round" />
            <path d="M414 263C435 252 456 252 478 263" stroke="#374151" strokeWidth="6" strokeLinecap="round" />
            <path d="M400 305V335" stroke="#D4A373" strokeWidth="6" strokeLinecap="round" />
            <ellipse
              className="avatar-mouth"
              cx="400"
              cy="356"
              rx="34"
              ry={mouthRy}
              fill="#9A3412"
            />
            <rect x="280" y="390" width="240" height="65" rx="30" fill="#F1C9A5" />
            <path d="M250 760C255 620 315 540 400 540C485 540 545 620 550 760" fill="#1F4B99" />
            <path d="M325 540L400 610L475 540" fill="#FFFFFF" />
            <rect x="360" y="560" width="80" height="150" rx="10" fill="#D1D5DB" />
            <rect x="80" y="70" width="640" height="730" rx="34" stroke="#D1D5DB" strokeWidth="4" fill="none" />
          </g>
          <text x="400" y="855" textAnchor="middle" fontFamily="Arial, Helvetica, sans-serif" fontSize="28" fill="#374151">
            Tallinn Digital Assistant
          </text>
        </svg>
      </div>

      <h2 className="avatar-title">Tallinn AI Assistant</h2>
      <p className="avatar-subtitle">
        Digital city representative with a microphone mode, voice responses, and an animated face for demo conversations.
      </p>

      <div className="status-row">
        <span className={dotClass} />
        <strong>{statusText}</strong>
      </div>

      <div className="badges">
        <span className="badge">Russian</span>
        <span className="badge">Estonian</span>
        <span className="badge">English</span>
        <span className="badge">Microphone</span>
        <span className="badge">Animated face</span>
        <span className="badge">Voice response</span>
      </div>
    </div>
  );
}
