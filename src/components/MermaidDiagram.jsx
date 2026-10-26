import React, { useEffect, useRef, useState } from 'react';
import mermaid from 'mermaid';
import { Copy, Check, GitBranch } from 'lucide-react';

mermaid.initialize({
  startOnLoad: false,
  theme: 'dark',
  securityLevel: 'loose',
  themeVariables: {
    darkMode: true,
    background: '#11131A',
    primaryColor: '#1E293B',
    primaryTextColor: '#F8FAFC',
    primaryBorderColor: '#6366F1',
    lineColor: '#818CF8',
    secondaryColor: '#161922',
    tertiaryColor: '#090A0F',
    fontFamily: 'Inter',
  },
});

export default function MermaidDiagram({ code }) {
  const containerRef = useRef(null);
  const [svgContent, setSvgContent] = useState('');
  const [copied, setCopied] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!code) return;
    let isMounted = true;
    const uniqueId = `mermaid-${Math.random().toString(36).substr(2, 9)}`;

    mermaid.render(uniqueId, code.trim())
      .then((result) => {
        if (isMounted) {
          setSvgContent(result.svg);
          setError(null);
        }
      })
      .catch((err) => {
        if (isMounted) {
          setError(err.message || 'Syntax error in concept diagram');
        }
      });

    return () => { isMounted = false; };
  }, [code]);

  const handleCopy = () => {
    navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="my-4 rounded-xl border border-white/[0.08] bg-[#11131A] overflow-hidden">
      <div className="flex items-center justify-between px-3 sm:px-4 py-2 sm:py-2.5 border-b border-white/[0.06] bg-white/[0.02]">
        <div className="flex items-center gap-2 text-xs font-mono text-zinc-400">
          <GitBranch className="w-3.5 h-3.5 text-indigo-400 shrink-0" strokeWidth={1.5} />
          <span className="uppercase tracking-wider text-[11px] sm:text-xs">Concept Architecture</span>
        </div>
        <button
          onClick={handleCopy}
          className="flex items-center gap-1.5 px-2 sm:px-2.5 py-1 text-xs font-mono text-zinc-400 hover:text-white bg-white/[0.04] hover:bg-white/[0.08] rounded-md transition-colors"
        >
          {copied ? (
            <>
              <Check className="w-3 h-3 text-emerald-400" strokeWidth={1.5} />
              <span>Copied</span>
            </>
          ) : (
            <>
              <Copy className="w-3 h-3" strokeWidth={1.5} />
              <span>Source</span>
            </>
          )}
        </button>
      </div>

      <div className="p-3 sm:p-4 flex items-center justify-start sm:justify-center overflow-x-auto touch-pan-x min-h-[180px] sm:min-h-[220px]">
        {error ? (
          <div className="text-xs font-mono text-rose-400 bg-rose-500/10 px-3 py-2 rounded-lg border border-rose-500/20">
            {error}
          </div>
        ) : svgContent ? (
          <div
            ref={containerRef}
            className="w-full flex justify-start sm:justify-center min-w-[340px] sm:min-w-0 [&>svg]:max-w-none sm:[&>svg]:max-w-full [&>svg]:h-auto"
            dangerouslySetInnerHTML={{ __html: svgContent }}
          />
        ) : (
          <div className="text-xs font-mono text-zinc-500 animate-pulse">
            Compiling concept topology...
          </div>
        )}
      </div>
    </div>
  );
}
