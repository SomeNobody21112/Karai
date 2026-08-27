import { useEffect, useMemo, useRef, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { api } from "../api.js";
import { useI18n } from "../I18nContext.jsx";
import "./Chat.css";

/**
 * The assistant. Everything it says comes from a tool call against the computed
 * artifacts — it has no independent knowledge of MPLADS and cannot do arithmetic, so it
 * cannot invent a figure.
 *
 * Two decisions here are worth knowing about:
 *
 * The language list is served by the API rather than written here. A picker offering
 * Spanish when nothing downstream speaks Spanish is a promise the product cannot keep.
 *
 * When a reply comes back from the deterministic router while a non-English language is
 * selected, the panel says so. The router answers in English whatever it was asked in,
 * and silently returning English to a Tamil question is exactly the kind of quiet
 * failure this project refuses everywhere else.
 */

const WORK_REF = /\b(MP\d+-W\d+)\b/g;

/** Browser speech codes for the languages the backend actually supports. */
const SPEECH_LANG = {
  en: "en-IN", hi: "hi-IN", bn: "bn-IN", ta: "ta-IN", te: "te-IN", mr: "mr-IN",
  gu: "gu-IN", kn: "kn-IN", ml: "ml-IN", pa: "pa-IN", or: "or-IN", as: "as-IN",
};

/** Native names, so a reader picks their language in their own script. */
const NATIVE_NAME = {
  en: "English", hi: "हिन्दी", bn: "বাংলা", ta: "தமிழ்", te: "తెలుగు", mr: "मराठी",
  gu: "ગુજરાતી", kn: "ಕನ್ನಡ", ml: "മലയാളം", pa: "ਪੰਜਾਬੀ", or: "ଓଡ଼ିଆ", as: "অসমীয়া",
};

/** Render one line's inline syntax: bold spans, then work references inside them. */
function formatInline(text, nav, key) {
  if (!text) return null;
  return text.split(/(\*\*.*?\*\*)/g).map((part, i) => {
    if (part.startsWith("**") && part.endsWith("**") && part.length > 4) {
      return (
        <strong key={`${key}-b${i}`} className="chat-bold">
          {withRefs(part.slice(2, -2), nav, `${key}-b${i}`)}
        </strong>
      );
    }
    return <span key={`${key}-t${i}`}>{withRefs(part, nav, `${key}-t${i}`)}</span>;
  });
}

/** Turn every work reference into a button that opens its case file. */
function withRefs(text, nav, key) {
  const parts = [];
  let last = 0;
  for (const m of text.matchAll(WORK_REF)) {
    if (m.index > last) parts.push(text.slice(last, m.index));
    parts.push(
      <button key={`${key}-${m.index}`} className="chat-ref-badge"
        onClick={() => nav(`/case/${m[1]}`)} title={`Open the case file for ${m[1]}`}>
        {m[1]}
      </button>
    );
    last = m.index + m[1].length;
  }
  if (last < text.length) parts.push(text.slice(last));
  return parts;
}

/**
 * Render an answer's block structure: tables, bullets, numbered steps, paragraphs.
 *
 * The deterministic router replies in plain prose and none of this fires. It is here for
 * the live model, which formats, and for anyone reading a transcript later.
 */
function renderAnswer(text, nav) {
  if (!text) return null;
  const out = [];
  let table = [];

  const flushTable = (key) => {
    if (!table.length) return;
    out.push(
      <div key={`tbl-${key}`} className="chat-table-wrapper">
        <table className="chat-table"><tbody>
          {table.map((row, r) => (
            <tr key={r} className={r === 0 ? "chat-tr-head" : ""}>
              {row.map((cell, c) => <td key={c}>{formatInline(cell.trim(), nav, `${key}-${r}-${c}`)}</td>)}
            </tr>
          ))}
        </tbody></table>
      </div>
    );
    table = [];
  };

  text.split("\n").forEach((line, i) => {
    const trimmed = line.trim();

    if (trimmed.startsWith("|") && trimmed.endsWith("|")) {
      const cells = trimmed.slice(1, -1).split("|");
      if (!cells.every((c) => /^[-: ]*$/.test(c))) table.push(cells);
      return;
    }
    flushTable(i);

    if (!trimmed) { out.push(<div key={`sp-${i}`} className="chat-line-break" />); return; }

    if (trimmed.startsWith("• ") || trimmed.startsWith("- ")) {
      out.push(
        <div key={`li-${i}`} className="chat-bullet-row">
          <span className="chat-bullet-dot">◆</span>
          <span className="chat-bullet-text">{formatInline(trimmed.slice(2), nav, `li-${i}`)}</span>
        </div>
      );
      return;
    }

    const numbered = trimmed.match(/^(\d+)\.\s+(.*)$/);
    if (numbered) {
      out.push(
        <div key={`no-${i}`} className="chat-bullet-row">
          <span className="chat-num-badge">{numbered[1]}</span>
          <span className="chat-bullet-text">{formatInline(numbered[2], nav, `no-${i}`)}</span>
        </div>
      );
      return;
    }

    out.push(<p key={`p-${i}`} className="chat-p">{formatInline(trimmed, nav, `p-${i}`)}</p>);
  });

  flushTable("end");
  return out;
}

export default function Chat() {
  const [open, setOpen] = useState(false);
  const [maximized, setMaximized] = useState(false);
  const [cap, setCap] = useState(null);
  const [turns, setTurns] = useState([]);
  const [draft, setDraft] = useState("");
  const [busy, setBusy] = useState(false);
  const [category, setCategory] = useState("all");
  const [copied, setCopied] = useState(null);
  const [listening, setListening] = useState(false);
  const [speaking, setSpeaking] = useState(null);

  const bodyRef = useRef(null);
  const inputRef = useRef(null);
  const recognitionRef = useRef(null);
  const nav = useNavigate();
  const location = useLocation();
  const { lang: uiLang } = useI18n();
  const [lang, setLang] = useState(uiLang || "en");

  useEffect(() => { api.chatCapabilities().then(setCap).catch(() => {}); }, []);
  // Follow the site's language when the reader changes it, until they override it here.
  useEffect(() => { setLang(uiLang || "en"); }, [uiLang]);

  useEffect(() => {
    if (bodyRef.current) bodyRef.current.scrollTop = bodyRef.current.scrollHeight;
  }, [turns, busy, open]);

  useEffect(() => { if (open) inputRef.current?.focus(); }, [open]);

  useEffect(() => {
    if (!open) return;
    const onKey = (e) => {
      if (e.key !== "Escape") return;
      if (maximized) setMaximized(false);
      else setOpen(false);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open, maximized]);

  // Stop any narration when the panel closes — a voice reading on from a closed panel
  // is startling, and there is no visible control to stop it.
  useEffect(() => {
    if (!open && window.speechSynthesis) {
      window.speechSynthesis.cancel();
      setSpeaking(null);
    }
  }, [open]);

  const languages = cap?.languages || { en: "English" };

  /** Prompts that make sense for the screen the reader is already on. */
  const pagePrompts = useMemo(() => {
    const path = location.pathname;
    if (path.startsWith("/case/")) {
      const ref = path.split("/case/")[1];
      return [
        `Tell me about ${ref}`,
        `What have officers verified about ${ref}?`,
      ];
    }
    if (path.startsWith("/transparency")) {
      return ["What is the only real ground truth here?", "Can you detect cost overruns?"];
    }
    if (path.startsWith("/duplicates")) return ["What counts as a concerning duplicate?"];
    if (path.startsWith("/compliance")) return ["What compliance checks are there?"];
    if (path.startsWith("/archetypes")) return ["What work types did you discover?"];
    if (path.startsWith("/trends")) return ["Has agency behaviour changed?"];
    return ["Show me the top leads", "How do you rank leads?"];
  }, [location.pathname]);

  async function ask(question) {
    const q = question.trim();
    if (!q || busy) return;
    setDraft("");
    setTurns((prev) => [...prev, { role: "user", content: q }]);
    setBusy(true);
    try {
      const history = turns.slice(-10).map((x) => ({ role: x.role, content: x.content }));
      const res = await api.chat({ question: q, history, lang });
      setTurns((prev) => [...prev, {
        role: "assistant",
        content: res.text || "",
        tools: res.tools_used || [],
        source: res.source,
        model: res.model,
        askedIn: lang,
      }]);
    } catch {
      setTurns((prev) => [...prev, {
        role: "assistant",
        content: "I could not reach the assistant service. Check that the API is running "
                 + "on port 8000, then ask again.",
        source: "error",
      }]);
    } finally {
      setBusy(false);
      inputRef.current?.focus();
    }
  }

  function toggleListening() {
    if (listening) { recognitionRef.current?.stop(); setListening(false); return; }
    const Recognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!Recognition) {
      setTurns((prev) => [...prev, {
        role: "assistant",
        content: "This browser cannot listen. Chrome, Edge and Safari can; type the "
                 + "question instead.",
        source: "error",
      }]);
      return;
    }
    try {
      const recognition = new Recognition();
      recognition.lang = SPEECH_LANG[lang] || "en-IN";
      recognition.interimResults = false;
      recognition.maxAlternatives = 1;
      recognition.onstart = () => setListening(true);
      recognition.onresult = (e) => {
        const said = e.results[0]?.[0]?.transcript;
        if (said) ask(said);
      };
      recognition.onerror = () => setListening(false);
      recognition.onend = () => setListening(false);
      recognitionRef.current = recognition;
      recognition.start();
    } catch {
      setListening(false);
    }
  }

  function toggleSpeak(text, i) {
    if (!window.speechSynthesis) return;
    if (speaking === i) { window.speechSynthesis.cancel(); setSpeaking(null); return; }
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(
      text.replace(/[*#|•◆]/g, " ").replace(/\s+/g, " ").trim()
    );
    utterance.lang = SPEECH_LANG[lang] || "en-IN";
    utterance.onend = () => setSpeaking(null);
    utterance.onerror = () => setSpeaking(null);
    setSpeaking(i);
    window.speechSynthesis.speak(utterance);
  }

  function copy(text, i) {
    navigator.clipboard?.writeText(text).then(() => {
      setCopied(i);
      setTimeout(() => setCopied(null), 2000);
    }).catch(() => {});
  }

  /** Download the conversation, tool trace included, so a finding can be filed. */
  function exportTranscript() {
    if (!turns.length) return;
    const lines = turns.map((t) => {
      const who = t.role === "user" ? "Question" : "Assistant";
      const trace = t.tools?.length ? `\n\n_Answered using: ${t.tools.join(", ")}_` : "";
      return `### ${who}\n\n${t.content}${trace}`;
    });
    const header = [
      "# MPLADS assistant transcript",
      "",
      `Exported ${new Date().toISOString().slice(0, 16).replace("T", " ")}.`,
      "",
      "Every figure below came from a tool call against the computed artifacts. This is a",
      "record of an enquiry, not a finding — nothing here concludes anything about anyone.",
      "",
      "---",
      "",
    ].join("\n");
    const blob = new Blob([header + lines.join("\n\n---\n\n") + "\n"],
                          { type: "text/markdown" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `mplads-assistant-${new Date().toISOString().slice(0, 10)}.md`;
    a.click();
    URL.revokeObjectURL(url);
  }

  const portfolio = cap?.portfolio;
  const chips = category === "all"
    ? (cap?.categories || []).flatMap((c) => c.prompts.slice(0, 2))
    : (cap?.categories || []).find((c) => c.category === category)?.prompts || [];

  return (
    <>
      <button className={"chat-fab" + (open ? " open" : "")} onClick={() => setOpen((o) => !o)}
        aria-label="Ask the assistant" title="Ask the assistant">
        <span className="chat-fab-icon">{open ? "✕" : "◈"}</span>
        {!open && <span className="chat-fab-label">Ask</span>}
      </button>

      {open && (
        <div className={"chat-panel" + (maximized ? " maximized" : "")}>
          <div className="chat-head">
            <div className="chat-head-left">
              <div className="chat-avatar">◈</div>
              <div style={{ minWidth: 0 }}>
                <div className="chat-title">MPLADS assistant</div>
                <div className="chat-sub">
                  <span className={"chat-status-dot" + (cap ? " online" : "")} />
                  {cap
                    ? `${cap.tools.length} data tools · ${cap.live ? "live model" : "deterministic engine"}`
                    : "connecting…"}
                </div>
              </div>
            </div>

            <div className="chat-head-actions">
              <select className="chat-lang-select" value={lang} title="Answer language"
                onChange={(e) => setLang(e.target.value)}>
                {Object.entries(languages).map(([code, english]) => (
                  <option key={code} value={code}>{NATIVE_NAME[code] || english}</option>
                ))}
              </select>

              {turns.length > 0 && (
                <>
                  <button className="chat-head-btn" onClick={exportTranscript}
                    title="Download this conversation">↓</button>
                  <button className="chat-head-btn" onClick={() => setTurns([])}
                    title="Clear this conversation">⌫</button>
                </>
              )}
              <button className="chat-head-btn" onClick={() => setMaximized((m) => !m)}
                title={maximized ? "Restore" : "Maximise"}>{maximized ? "⤡" : "⤢"}</button>
              <button className="chat-head-btn close" onClick={() => setOpen(false)}
                title="Close">✕</button>
            </div>
          </div>

          <div className="chat-body" ref={bodyRef}>
            {turns.length === 0 && (
              <>
                <div className="chat-intro-card">
                  <div className="chat-intro-title">Ask about any work in the portfolio</div>
                  <p className="chat-intro-desc">
                    {portfolio ? (
                      <>
                        Grounded in all <b>{portfolio.works?.toLocaleString("en-IN")}</b> works
                        across <b>{portfolio.states}</b> states and{" "}
                        <b>{portfolio.agencies?.toLocaleString("en-IN")}</b> implementing
                        agencies — not only the{" "}
                        <b>{portfolio.leads?.toLocaleString("en-IN")}</b> surfaced for review.
                        Every figure comes from a tool call against the computed results;
                        I have no independent knowledge of this data and cannot invent one.
                      </>
                    ) : (
                      <>Every figure comes from a tool call against the computed results.
                      I have no independent knowledge of this data and cannot invent one.</>
                    )}
                  </p>
                </div>

                <div className="chat-section-label">For this screen</div>
                <div className="chat-chips-grid">
                  {pagePrompts.map((p) => (
                    <button key={p} className="chat-chip context-chip" onClick={() => ask(p)}>
                      <span className="chat-chip-arrow">▸</span><span>{p}</span>
                    </button>
                  ))}
                </div>

                {cap?.categories?.length > 0 && (
                  <>
                    <div className="chat-category-tabs">
                      <button className={"chat-tab" + (category === "all" ? " active" : "")}
                        onClick={() => setCategory("all")}>Everything</button>
                      {cap.categories.map((c) => (
                        <button key={c.category}
                          className={"chat-tab" + (category === c.category ? " active" : "")}
                          onClick={() => setCategory(c.category)}>
                          {c.icon} {c.category}
                        </button>
                      ))}
                    </div>
                    <div className="chat-chips-grid">
                      {chips.map((p) => (
                        <button key={p} className="chat-chip" onClick={() => ask(p)}>
                          <span className="chat-chip-arrow">▸</span><span>{p}</span>
                        </button>
                      ))}
                    </div>
                  </>
                )}
              </>
            )}

            {turns.map((turn, i) => (
              <div key={i} className={"chat-turn " + turn.role}>
                <div className="chat-bubble-container">
                  {turn.role === "assistant" && <div className="chat-turn-avatar">◈</div>}
                  <div className="chat-bubble">
                    {turn.role === "assistant"
                      ? renderAnswer(turn.content, nav)
                      : turn.content}

                    {turn.role === "assistant" && turn.content && (
                      <div className="chat-bubble-actions">
                        <button className="chat-action-btn" onClick={() => copy(turn.content, i)}
                          title="Copy this answer">
                          {copied === i ? "✓ copied" : "copy"}
                        </button>
                        <button
                          className={"chat-action-btn" + (speaking === i ? " active" : "")}
                          onClick={() => toggleSpeak(turn.content, i)} title="Read aloud">
                          {speaking === i ? "◼ stop" : "▶ listen"}
                        </button>
                      </div>
                    )}
                  </div>
                </div>

                {turn.role === "assistant" && turn.tools?.length > 0 && (
                  <div className="chat-tools-trace">
                    <span className="chat-tools-label">answered using</span>
                    {turn.tools.map((tool) => (
                      <span key={tool} className="chat-tool">{tool.replace(/^t_/, "")}</span>
                    ))}
                  </div>
                )}

                {turn.role === "assistant" && turn.source === "offline"
                  && turn.askedIn && turn.askedIn !== "en" && (
                  <div className="chat-lang-notice">
                    Answered in English. {languages[turn.askedIn] || turn.askedIn} needs the
                    live model, which is unreachable — so the deterministic engine replied
                    from the same data instead of translating.
                  </div>
                )}
              </div>
            ))}

            {busy && (
              <div className="chat-turn assistant">
                <div className="chat-bubble-container">
                  <div className="chat-turn-avatar">◈</div>
                  <div className="chat-bubble chat-typing">
                    <i /><i /><i />
                    <span className="chat-typing-text">reading the data…</span>
                  </div>
                </div>
              </div>
            )}
          </div>

          <form className="chat-input-row"
            onSubmit={(e) => { e.preventDefault(); ask(draft); }}>
            <button type="button" className={"chat-voice-btn" + (listening ? " listening" : "")}
              onClick={toggleListening}
              title={listening ? "Listening — click to stop" : "Speak your question"}>
              {listening ? <span className="chat-voice-pulse" /> : "🎙"}
            </button>
            <input className="input chat-input" ref={inputRef} value={draft}
              onChange={(e) => setDraft(e.target.value)} disabled={busy}
              placeholder="Ask about a work, a state, an agency, or the method…" />
            <button className="btn btn-primary" type="submit" disabled={busy || !draft.trim()}>
              Ask
            </button>
          </form>
        </div>
      )}
    </>
  );
}
