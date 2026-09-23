import { useEffect } from 'react';
import { useLocation } from 'react-router-dom';

/**
 * Scrolls to the element matching the current URL hash inside the
 * nearest scrollable container. Falls back to the window.
 */
export function ScrollManager() {
  const { hash } = useLocation();

  useEffect(() => {
    if (!hash) {
      window.scrollTo?.({ top: 0 });
      return;
    }

    const id = hash.replace('#', '');
    // Wait a frame so the target section is laid out.
    const raf = requestAnimationFrame(() => {
      const el = document.getElementById(id);
      if (el) {
        el.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });

    return () => cancelAnimationFrame(raf);
  }, [hash]);

  return null;
}
