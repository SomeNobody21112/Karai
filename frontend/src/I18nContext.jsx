import { createContext, useContext, useEffect, useState } from "react";
import { api } from "./api.js";

const Ctx = createContext({ lang: "en", t: (k, f) => f ?? k, setLang: () => {} });

const STORAGE_KEY = "mplads.lang";

export function I18nProvider({ children }) {
  const [lang, setLangState] = useState(() => {
    try {
      return localStorage.getItem(STORAGE_KEY) || "en";
    } catch {
      return "en";
    }
  });
  const [strings, setStrings] = useState({});
  const [meta, setMeta] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    api.languages().then(setMeta).catch(() => {});
  }, []);

  useEffect(() => {
    setLoading(true);
    api
      .strings(lang)
      .then((d) => setStrings(d.strings || {}))
      .catch(() => setStrings({}))
      .finally(() => setLoading(false));
    try {
      localStorage.setItem(STORAGE_KEY, lang);
    } catch {
      /* private mode — the language simply won't persist */
    }
    document.documentElement.lang = lang;
  }, [lang]);

  /** t("nav.overview", "Overview") — the English fallback is always the second arg. */
  const t = (key, fallback) => strings[key] ?? fallback ?? key;

  return (
    <Ctx.Provider value={{ lang, setLang: setLangState, t, meta, loading }}>
      {children}
    </Ctx.Provider>
  );
}

export const useI18n = () => useContext(Ctx);

const NATIVE = {
  en: "English", hi: "हिन्दी", bn: "বাংলা", ta: "தமிழ்", te: "తెలుగు",
  mr: "मराठी", gu: "ગુજરાતી", kn: "ಕನ್ನಡ", ml: "മലയാളം", pa: "ਪੰਜਾਬੀ",
  or: "ଓଡ଼ିଆ", as: "অসমীয়া",
};

export function LanguageSwitcher() {
  const { lang, setLang, meta, loading } = useI18n();
  if (!meta) return null;
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
      <select
        className="select"
        value={lang}
        onChange={(e) => setLang(e.target.value)}
        title={meta.llm_available ? "Live translation" : "Translation needs an API key"}
      >
        {Object.keys(meta.languages).map((code) => (
          <option key={code} value={code}>
            {NATIVE[code] || meta.languages[code]}
          </option>
        ))}
      </select>
      {loading && <span className="muted" style={{ fontSize: 11 }}>…</span>}
    </div>
  );
}
