import { useEffect, useMemo, useRef, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";

const WORK_REF_REGEX = /\b(MP\d+[\w-]*W\d+|MP\d+-W\d+|W\d{4,6})\b/g;

const NATIVE_LANG_NAMES = {
  en: "English",
  hi: "हिन्दी (Hindi)",
  ta: "தமிழ் (Tamil)",
  te: "తెలుగు (Telugu)",
  bn: "বাংলা (Bengali)",
  mr: "मराठी (Marathi)",
  gu: "ગુજરાતી (Gujarati)",
  kn: "ಕನ್ನಡ (Kannada)",
  ml: "മലയാളം (Malayalam)",
  pa: "ਪੰਜਾਬੀ (Punjabi)",
  or: "ଓଡ଼ିଆ (Odia)",
  as: "অসমীয়া (Assamese)",
  ur: "اردو (Urdu)",
  es: "Español (Spanish)",
  fr: "Français (French)",
};

const SPEECH_LANG_MAP = {
  en: "en-IN",
  hi: "hi-IN",
  ta: "ta-IN",
  te: "te-IN",
  bn: "bn-IN",
  mr: "mr-IN",
  gu: "gu-IN",
  kn: "kn-IN",
  ml: "ml-IN",
  pa: "pa-IN",
  or: "or-IN",
  as: "as-IN",
  ur: "ur-IN",
  es: "es-ES",
  fr: "fr-FR",
};

/** Render rich text with markdown elements, bolding, lists, tables, and clickable case badges */
function renderFormattedMessage(text, nav) {
  if (!text) return null;

  const lines = text.split("\n");
  const elements = [];
  let inTable = false;
  let tableRows = [];

  const flushTable = (key) => {
    if (tableRows.length > 0) {
      elements.push(
        <div key={`table-${key}`} className="chat-table-wrapper">
          <table className="chat-table">
            <tbody>
              {tableRows.map((row, rIdx) => (
                <tr key={rIdx} className={rIdx === 0 ? "chat-tr-head" : ""}>
                  {row.map((cell, cIdx) => (
                    <td key={cIdx}>{formatInline(cell.trim(), nav)}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      );
      tableRows = [];
    }
    inTable = false;
  };

  lines.forEach((line, lineIdx) => {
    const trimmed = line.trim();

    if (trimmed.startsWith("|") && trimmed.endsWith("|")) {
      const cells = trimmed.slice(1, -1).split("|");
      if (cells.every((c) => /^[-: ]+$/.test(c))) return;
      inTable = true;
      tableRows.push(cells);
      return;
    } else if (inTable) {
      flushTable(lineIdx);
    }

    if (!trimmed) {
      elements.push(<div key={`space-${lineIdx}`} className="chat-line-break" />);
      return;
    }

    if (trimmed.startsWith("• ") || trimmed.startsWith("- ")) {
      elements.push(
        <div key={`bullet-${lineIdx}`} className="chat-bullet-row">
          <span className="chat-bullet-dot">◈</span>
          <span className="chat-bullet-text">{formatInline(trimmed.slice(2), nav)}</span>
        </div>
      );
      return;
    }

    const numMatch = trimmed.match(/^(\d+)\.\s+(.*)$/);
    if (numMatch) {
      elements.push(
        <div key={`num-${lineIdx}`} className="chat-bullet-row">
          <span className="chat-num-badge">{numMatch[1]}</span>
          <span className="chat-bullet-text">{formatInline(numMatch[2], nav)}</span>
        </div>
      );
      return;
    }

    elements.push(
      <p key={`p-${lineIdx}`} className="chat-p">
        {formatInline(trimmed, nav)}
      </p>
    );
  });

  if (inTable) {
    flushTable("end");
  }

  return elements;
}

function formatInline(text, nav) {
  if (!text) return "";
  const boldParts = text.split(/(\*\*.*?\*\*)/g);
  return boldParts.map((part, bIdx) => {
    if (part.startsWith("**") && part.endsWith("**")) {
      const inner = part.slice(2, -2);
      return (
        <strong key={`b-${bIdx}`} className="chat-bold">
          {renderWorkRefs(inner, nav, `b-${bIdx}`)}
        </strong>
      );
    }
    return renderWorkRefs(part, nav, `t-${bIdx}`);
  });
}

function renderWorkRefs(text, nav, keyPrefix) {
  const parts = [];
  let last = 0;
  for (const m of text.matchAll(WORK_REF_REGEX)) {
    if (m.index > last) parts.push(text.slice(last, m.index));
    const ref = m[1];
    parts.push(
      <button
        key={`${keyPrefix}-${m.index}-${ref}`}
        className="chat-ref-badge"
        onClick={() => nav(`/case/${ref}`)}
        title={`Click to open case file for ${ref}`}
      >
        <span className="chat-ref-icon">📂</span>
        <span>{ref}</span>
      </button>
    );
    last = m.index + ref.length;
  }
  if (last < text.length) parts.push(text.slice(last));
  return parts;
}

export default function Chat() {
  const [open, setOpen] = useState(false);
  const [maximized, setMaximized] = useState(false);
  const [cap, setCap] = useState(null);
  const [turns, setTurns] = useState([]);
  const [draft, setDraft] = useState("");
  const [busy, setBusy] = useState(false);
  const [lang, setLang] = useState("en");
  const [activeCategory, setActiveCategory] = useState("all");
  const [copiedIdx, setCopiedIdx] = useState(null);
  const [isListening, setIsListening] = useState(false);
  const [speakingIdx, setSpeakingIdx] = useState(null);

  const bodyRef = useRef(null);
  const inputRef = useRef(null);
  const recognitionRef = useRef(null);
  const nav = useNavigate();
  const location = useLocation();

  useEffect(() => {
    fetch("/api/chat/capabilities")
      .then((r) => r.json())
      .then(setCap)
      .catch(() => {});
  }, []);

  useEffect(() => {
    if (bodyRef.current) {
      bodyRef.current.scrollTop = bodyRef.current.scrollHeight;
    }
  }, [turns, busy, open]);

  useEffect(() => {
    if (open) inputRef.current?.focus();
  }, [open]);

  // Handle Esc key to close or minimize
  useEffect(() => {
    if (!open) return;
    const onKey = (e) => {
      if (e.key === "Escape") {
        if (maximized) setMaximized(false);
        else setOpen(false);
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open, maximized]);

  // Context-aware page prompts
  const pagePrompts = useMemo(() => {
    const p = location.pathname;
    if (p.startsWith("/case/")) {
      const ref = p.split("/case/")[1];
      return [
        `Tell me everything about ${ref}`,
        `What evidence signals flagged ${ref}?`,
        `What is the recommended next step for ${ref}?`,
      ];
    }
    return [
      "How many investigation leads are there in total?",
      "Compare Bihar and Uttar Pradesh",
      "What are the 7 intelligence engines?",
    ];
  }, [location.pathname]);

  async function ask(question) {
    const q = question.trim();
    if (!q || busy) return;
    setDraft("");
    setTurns((prev) => [...prev, { role: "user", content: q }]);
    setBusy(true);

    try {
      const history = turns.slice(-10).map((x) => ({ role: x.role, content: x.content }));
      const resp = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: q, history, lang }),
      });
      const res = await resp.json();
      setTurns((prev) => [
        ...prev,
        {
          role: "assistant",
          content: res.text || res.answer,
          tools: res.tools_used || [],
          source: res.source,
          model: res.model,
          language: res.language || lang,
        },
      ]);
    } catch {
      setTurns((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "The assistant service is momentarily unreachable. Please verify that the backend API server is running on port 8000.",
          source: "error",
        },
      ]);
    } finally {
      setBusy(false);
      inputRef.current?.focus();
    }
  }

  // Voice Input (Speech-to-Text)
  const toggleSpeechRecognition = () => {
    if (isListening) {
      recognitionRef.current?.stop();
      setIsListening(false);
      return;
    }

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      alert("Voice recognition is not supported in this browser. Please use Chrome, Edge, or Safari.");
      return;
    }

    try {
      const recognition = new SpeechRecognition();
      recognition.lang = SPEECH_LANG_MAP[lang] || "en-IN";
      recognition.interimResults = false;
      recognition.maxAlternatives = 1;

      recognition.onstart = () => setIsListening(true);
      recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        if (transcript) {
          ask(transcript);
        }
      };
      recognition.onerror = () => setIsListening(false);
      recognition.onend = () => setIsListening(false);

      recognitionRef.current = recognition;
      recognition.start();
    } catch {
      setIsListening(false);
    }
  };

  // Text-to-Speech (Read Aloud)
  const toggleSpeak = (text, idx) => {
    if (!window.speechSynthesis) return;

    if (speakingIdx === idx) {
      window.speechSynthesis.cancel();
      setSpeakingIdx(null);
      return;
    }

    window.speechSynthesis.cancel();
    const cleanText = text.replace(/[*#|•]/g, "").replace(/\s+/g, " ");
    const utterance = new SpeechSynthesisUtterance(cleanText);
    utterance.lang = SPEECH_LANG_MAP[lang] || "en-IN";
    utterance.onend = () => setSpeakingIdx(null);
    utterance.onerror = () => setSpeakingIdx(null);

    setSpeakingIdx(idx);
    window.speechSynthesis.speak(utterance);
  };

  const copyToClipboard = (text, idx) => {
    navigator.clipboard.writeText(text);
    setCopiedIdx(idx);
    setTimeout(() => setCopiedIdx(null), 2000);
  };

  const exportTranscript = () => {
    if (turns.length === 0) return;
    const formatted = turns
      .map((t) => `### ${t.role.toUpperCase()}\n${t.content}\n${t.tools ? `_Tools: ${t.tools.join(", ")}_\n` : ""}`)
      .join("\n---\n\n");
    const blob = new Blob([formatted], { type: "text/markdown" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `audit-chat-${new Date().toISOString().slice(0, 10)}.md`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <>
      <button
        className={"chat-fab" + (open ? " open" : "")}
        onClick={() => setOpen((o) => !o)}
        aria-label="Ask the AI audit assistant"
        title="Open AI Assistant"
      >
        <span className="chat-fab-icon">{open ? "✕" : "◈"}</span>
        {!open && <span className="chat-fab-label">AI Assistant</span>}
      </button>

      {open && (
        <div className={"chat-panel" + (maximized ? " maximized" : "")}>
          {/* Header */}
          <div className="chat-head">
            <div className="chat-head-left">
              <div className="chat-avatar">◈</div>
              <div>
                <div className="chat-title">Thadam AI Assistant</div>
                <div className="chat-sub">
                  <span className="chat-status-dot online" />
                  {cap
                    ? `${cap.tools?.length || 19} Data Tools · ${cap.live ? "Live LLM" : "Deterministic Engine"}`
                    : "Connecting…"}
                </div>
              </div>
            </div>

            <div className="chat-head-actions">
              <select
                className="chat-lang-select"
                value={lang}
                onChange={(e) => setLang(e.target.value)}
                title="Select Assistant Language"
              >
                {Object.entries(NATIVE_LANG_NAMES).map(([code, label]) => (
                  <option key={code} value={code}>
                    {label}
                  </option>
                ))}
              </select>

              {turns.length > 0 && (
                <button
                  className="chat-head-btn"
                  onClick={exportTranscript}
                  title="Export transcript as Markdown"
                >
                  📥
                </button>
              )}

              {turns.length > 0 && (
                <button
                  className="chat-head-btn"
                  onClick={() => setTurns([])}
                  title="Clear conversation"
                >
                  🗑️
                </button>
              )}

              <button
                className="chat-head-btn"
                onClick={() => setMaximized((m) => !m)}
                title={maximized ? "Restore view" : "Maximize view"}
              >
                {maximized ? "🗗" : "🗖"}
              </button>

              <button
                className="chat-head-btn close"
                onClick={() => setOpen(false)}
                title="Close assistant"
              >
                ✕
              </button>
            </div>
          </div>

          {/* Body */}
          <div className="chat-body" ref={bodyRef}>
            {turns.length === 0 && (
              <div className="chat-intro-container">
                <div className="chat-intro-card">
                  <div className="chat-intro-icon">🏛️</div>
                  <div className="chat-intro-title">MPLADS Forensic Intelligence Assistant</div>
                  <p className="chat-intro-desc">
                    Ground-truth answers across <strong>2,10,993 works</strong>, <strong>36 States/UTs</strong>,
                    and <strong>37,705 investigation leads</strong>. Queries are directly evaluated against
                    the dataset and machine learning models.
                  </p>
                </div>

                <div className="chat-section-label">Suggested for Current Page</div>
                <div className="chat-chips-grid">
                  {pagePrompts.map((prompt) => (
                    <button
                      key={prompt}
                      className="chat-chip context-chip"
                      onClick={() => ask(prompt)}
                    >
                      <span className="chat-chip-arrow">→</span>
                      <span>{prompt}</span>
                    </button>
                  ))}
                </div>

                {cap?.categories && (
                  <>
                    <div className="chat-category-tabs">
                      <button
                        className={"chat-tab" + (activeCategory === "all" ? " active" : "")}
                        onClick={() => setActiveCategory("all")}
                      >
                        All Categories
                      </button>
                      {cap.categories.map((cat) => (
                        <button
                          key={cat.category}
                          className={"chat-tab" + (activeCategory === cat.category ? " active" : "")}
                          onClick={() => setActiveCategory(cat.category)}
                        >
                          {cat.icon} {cat.category.split(" ")[0]}
                        </button>
                      ))}
                    </div>

                    <div className="chat-chips-grid">
                      {(activeCategory === "all"
                        ? cap.categories.flatMap((c) => c.prompts.slice(0, 2))
                        : cap.categories.find((c) => c.category === activeCategory)?.prompts || []
                      ).map((prompt) => (
                        <button
                          key={prompt}
                          className="chat-chip"
                          onClick={() => ask(prompt)}
                        >
                          <span className="chat-chip-arrow">→</span>
                          <span>{prompt}</span>
                        </button>
                      ))}
                    </div>
                  </>
                )}
              </div>
            )}

            {turns.map((turn, i) => (
              <div key={i} className={"chat-turn " + turn.role}>
                <div className="chat-bubble-container">
                  {turn.role === "assistant" && (
                    <div className="chat-turn-avatar">◈</div>
                  )}

                  <div className="chat-bubble">
                    {turn.role === "assistant"
                      ? renderFormattedMessage(turn.content, nav)
                      : turn.content}

                    {turn.role === "assistant" && (
                      <div className="chat-bubble-actions">
                        <button
                          className="chat-action-btn"
                          onClick={() => copyToClipboard(turn.content, i)}
                          title="Copy response"
                        >
                          {copiedIdx === i ? "✓ Copied" : "📋 Copy"}
                        </button>

                        <button
                          className={"chat-action-btn" + (speakingIdx === i ? " active" : "")}
                          onClick={() => toggleSpeak(turn.content, i)}
                          title="Read aloud"
                        >
                          {speakingIdx === i ? "⏹️ Stop" : "🔊 Listen"}
                        </button>
                      </div>
                    )}
                  </div>
                </div>

                {turn.role === "assistant" && turn.tools?.length > 0 && (
                  <div className="chat-tools-trace">
                    <span className="chat-tools-label">Data Tools:</span>
                    {turn.tools.map((tool) => (
                      <span key={tool} className="chat-tool-pill">
                        {tool.replace(/^t_/, "")}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            ))}

            {busy && (
              <div className="chat-turn assistant">
                <div className="chat-bubble-container">
                  <div className="chat-turn-avatar">◈</div>
                  <div className="chat-bubble chat-typing">
                    <span className="chat-typing-dot" />
                    <span className="chat-typing-dot" />
                    <span className="chat-typing-dot" />
                    <span className="chat-typing-text">Evaluating dataset…</span>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Input Form */}
          <form
            className="chat-input-row"
            onSubmit={(e) => {
              e.preventDefault();
              ask(draft);
            }}
          >
            <button
              type="button"
              className={"chat-voice-btn" + (isListening ? " listening" : "")}
              onClick={toggleSpeechRecognition}
              title={isListening ? "Listening… click to stop" : "Speak your question"}
            >
              {isListening ? <span className="chat-voice-pulse" /> : "🎙️"}
            </button>

            <input
              className="input chat-input"
              placeholder={`Ask in ${NATIVE_LANG_NAMES[lang] || "English"} about works, states, leads, or models…`}
              value={draft}
              onChange={(e) => setDraft(e.target.value)}
              ref={inputRef}
              disabled={busy}
            />

            <button
              className="btn btn-primary chat-send-btn"
              type="submit"
              disabled={busy || !draft.trim()}
            >
              Send
            </button>
          </form>
        </div>
      )}
    </>
  );
}
