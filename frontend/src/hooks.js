import { useEffect, useRef, useState } from "react";

const REDUCED = () =>
  typeof window !== "undefined" &&
  window.matchMedia?.("(prefers-reduced-motion: reduce)").matches;

/**
 * Reveal an element when it scrolls into view.
 * Returns [ref, isVisible]. Attach ref to the element and use `reveal` classes.
 */
export function useReveal({ threshold = 0.12, once = true, rootMargin = "0px 0px -8% 0px" } = {}) {
  const ref = useRef(null);
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const node = ref.current;
    if (!node) return;
    if (REDUCED()) {
      setVisible(true);
      return;
    }
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setVisible(true);
          if (once) observer.unobserve(node);
        } else if (!once) {
          setVisible(false);
        }
      },
      { threshold, rootMargin }
    );
    observer.observe(node);
    return () => observer.disconnect();
  }, [threshold, once, rootMargin]);

  return [ref, visible];
}

/** Count from 0 up to `end` once `active` turns true. Eased, frame-based. */
export function useCountUp(end, { duration = 1500, active = true, decimals = 0 } = {}) {
  const [value, setValue] = useState(0);
  const started = useRef(false);

  useEffect(() => {
    if (!active || started.current || end == null) return;
    started.current = true;
    if (REDUCED()) {
      setValue(end);
      return;
    }
    let raf;
    const t0 = performance.now();
    const tick = (now) => {
      const p = Math.min(1, (now - t0) / duration);
      // easeOutExpo — fast start, gentle landing
      const eased = p === 1 ? 1 : 1 - Math.pow(2, -10 * p);
      const next = end * eased;
      setValue(decimals ? Number(next.toFixed(decimals)) : Math.round(next));
      if (p < 1) raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, [end, duration, active, decimals]);

  return value;
}

/** Current scroll position in pixels, throttled to animation frames. */
export function useScrollY() {
  const [y, setY] = useState(0);
  useEffect(() => {
    let raf = null;
    const onScroll = () => {
      if (raf) return;
      raf = requestAnimationFrame(() => {
        setY(window.scrollY);
        raf = null;
      });
    };
    window.addEventListener("scroll", onScroll, { passive: true });
    onScroll();
    return () => {
      window.removeEventListener("scroll", onScroll);
      if (raf) cancelAnimationFrame(raf);
    };
  }, []);
  return y;
}

/** 0 -> 1 progress through the whole document. Drives the top progress bar. */
export function useScrollProgress() {
  const [progress, setProgress] = useState(0);
  useEffect(() => {
    let raf = null;
    const update = () => {
      if (raf) return;
      raf = requestAnimationFrame(() => {
        const max = document.body.scrollHeight - window.innerHeight;
        setProgress(max > 0 ? Math.min(1, window.scrollY / max) : 0);
        raf = null;
      });
    };
    window.addEventListener("scroll", update, { passive: true });
    window.addEventListener("resize", update);
    update();
    return () => {
      window.removeEventListener("scroll", update);
      window.removeEventListener("resize", update);
      if (raf) cancelAnimationFrame(raf);
    };
  }, []);
  return progress;
}

/** Track the cursor inside an element, as 0..1 coordinates, for spotlight effects. */
export function usePointerSpotlight() {
  const ref = useRef(null);
  useEffect(() => {
    const node = ref.current;
    if (!node || REDUCED()) return;
    const onMove = (e) => {
      const rect = node.getBoundingClientRect();
      node.style.setProperty("--mx", `${((e.clientX - rect.left) / rect.width) * 100}%`);
      node.style.setProperty("--my", `${((e.clientY - rect.top) / rect.height) * 100}%`);
    };
    node.addEventListener("pointermove", onMove);
    return () => node.removeEventListener("pointermove", onMove);
  }, []);
  return ref;
}
