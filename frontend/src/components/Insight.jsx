import { useEffect, useState } from "react";
import { api } from "../api.js";
import { useI18n } from "../I18nContext.jsx";

/**
 * A written briefing over numbers the pipeline already computed.
 *
 * The panel always says where the words came from: a language model, or the
 * deterministic template used when no API key is configured. Never hide which.
 */
export default function Insight({ kind, workRef, params = {} }) {
  const { lang, t } = useI18n();
  const [data, setData] = useState(null);
  const [failed, setFailed] = useState(false);

  useEffect(() => {
    setData(null);
    setFailed(false);
    const call =
      kind === "case"
        ? api.caseInsight(workRef, lang)
        : api.portfolioInsight({ lang, ...params });
    call.then(setData).catch(() => setFailed(true));
  }, [kind, workRef, lang, params.role, params.scope]);

  if (failed) return null;

  const generated = data?.source?.startsWith("llm") || data?.source === "template+llm";

  return (
    <div className="insight">
      <div className="insight-head">
        <span className="insight-mark">◈</span>
        <span className="insight-title">{t("case.aiBrief", "AI briefing")}</span>
        {data && (
          <span className="insight-src">
            {generated ? `generated · ${data.model || "claude"}` : "deterministic template"}
          </span>
        )}
      </div>
      {!data ? (
        <div className="insight-skel">
          <div className="skeleton" style={{ height: 12, width: "94%" }} />
          <div className="skeleton" style={{ height: 12, width: "88%" }} />
          <div className="skeleton" style={{ height: 12, width: "62%" }} />
        </div>
      ) : (
        <p className="insight-body">{data.text}</p>
      )}
    </div>
  );
}
