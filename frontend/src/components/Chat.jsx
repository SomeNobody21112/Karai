import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api.js";
import { useI18n } from "../I18nContext.jsx";

const WORK_REF = /\b(MP\d+-W\d+)\b/g;

/** Turn work references in the answer into links to their case file. */
function withLinks(text, nav) {
  const parts = [];
  let last = 0;
  for (const m of text.matchAll(WORK_REF)) {
    if (m.index > last) parts.push(text.slice(last, m.index));
    parts.push(
      <a
        key={`${m.index}-${m[1]}`}
        className="chat-ref"
        onClick={() => nav(`/case/${m[1]}`)}
        title="Open this case file"
      >
        {m[1]}
      </a>
    );
    last = m.index + m[1].length;
  }
  if (last < text.length) parts.push(text.slice(last));
  return parts;
}

export default function Chat() {
  const [open, setOpen] = useState(false);
  const [cap, setCap] = useState(null);
  const [turns, setTurns] = useState([]);
  const [draft, setDraft] = useState("");
  const [busy, setBusy] = useState(false);
  const bodyRef = useRef(null);
  const inputRef = useRef(null);
  const nav = useNavigate();
  const { lang, t } = useI18n();

  useEffect(() => {
    api.chatCapabilities().then(setCap).catch(() => {});
  }, []);

  useEffect(() => {
    if (bodyRef.current) bodyRef.current.scrollTop = bodyRef.current.scrollHeight;
  }, [turns, busy, open]);

  useEffect(() => { if (open) inputRef.current?.focus(); }, [open]);

  // Esc closes the panel, the way every other overlay on the web does.
  useEffect(() => {
    if (!open) return;
    const onKey = (e) => { if (e.key === "Escape") setOpen(false); };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open]);

  async function ask(question) {
    const q = question.trim();
    if (!q || busy) return;
    setDraft("");
    setTurns((prev) => [...prev, { role: "user", content: q }]);
    setBusy(true);
    try {
      const history = turns.slice(-8).map((x) => ({ role: x.role, content: x.content }));
      const res = await api.chat({ question: q, history, lang });
      setTurns((prev) => [
        ...prev,
        { role: "assistant", content: res.text, tools: res.tools_used, source: res.source },
      ]);
    } catch {
      setTurns((prev) => [
        ...prev,
        { role: "assistant", content: "The assistant is unreachable. Is the API running?", source: "error" },
      ]);
    } finally {
      setBusy(false);
      inputRef.current?.focus();
    }
  }

  return (
    <>
      <button
        className={"chat-fab" + (open ? " open" : "")}
        onClick={() => setOpen((o) => !o)}
        aria-label="Ask the assistant"
      >
        {open ? "✕" : "◈"}
      </button>

      {open && (
        <div className="chat-panel">
          <div className="chat-head">
            <div>
              <div className="chat-title">Ask the assistant</div>
              <div className="chat-sub">
                {cap
                  ? cap.live
                    ? `${cap.tools.length} data tools · live`
                    : `${cap.tools.length} data tools · offline mode`
                  : "connecting…"}
              </div>
            </div>
            <button className="chat-x" onClick={() => setOpen(false)}>✕</button>
          </div>

          <div className="chat-body" ref={bodyRef}>
            {turns.length === 0 && (
              <div className="chat-intro">
                <p>
                  I answer only by looking things up in the computed results — I have no
                  independent knowledge of this data, and I never state a figure a tool did
                  not give me.
                </p>
                <div className="chat-chips">
                  {(cap?.suggestions || []).map((s) => (
                    <button key={s} className="chat-chip" onClick={() => ask(s)}>{s}</button>
                  ))}
                </div>
              </div>
            )}

            {turns.map((turn, i) => (
              <div key={i} className={"chat-turn " + turn.role}>
                <div className="chat-bubble">
                  {turn.role === "assistant" ? withLinks(turn.content, nav) : turn.content}
                </div>
                {turn.role === "assistant" && turn.tools?.length > 0 && (
                  <div className="chat-tools">
                    {turn.tools.map((tool) => (
                      <span key={tool} className="chat-tool">{tool.replace(/^t_/, "")}</span>
                    ))}
                  </div>
                )}
              </div>
            ))}

            {busy && (
              <div className="chat-turn assistant">
                <div className="chat-bubble chat-typing"><i /><i /><i /></div>
              </div>
            )}
          </div>

          <form
            className="chat-input-row"
            onSubmit={(e) => { e.preventDefault(); ask(draft); }}
          >
            <input
              className="input chat-input"
              placeholder="Ask about a work, a state, or the numbers…"
              value={draft}
              onChange={(e) => setDraft(e.target.value)}
              ref={inputRef}
              readOnly={busy}
            />
            <button className="btn btn-primary" type="submit" disabled={busy || !draft.trim()}>
              Send
            </button>
          </form>
        </div>
      )}
    </>
  );
}
