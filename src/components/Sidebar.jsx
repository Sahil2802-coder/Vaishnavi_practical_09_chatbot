import React, { useState } from 'react';
import {
  Plus,
  KeyRound,
  Sliders,
  Layers,
  Terminal,
  GitBranch,
  ChevronDown,
  ChevronRight,
  CheckCircle2,
  Clock,
  Activity,
  Cpu,
  SlidersHorizontal,
  PanelLeftClose,
  PanelLeftOpen,
} from 'lucide-react';
import { TECHNIQUES, LAB_TEST_CASES } from '../services/geminiService';

export default function Sidebar({
  apiKey,
  setApiKey,
  activeTechnique,
  setActiveTechnique,
  onNewSession,
  onRunTestCase,
  testCaseStatuses,
  rqsScores,
  setRqsScores,
  isCollapsed,
  setIsCollapsed,
}) {
  const [suiteExpanded, setSuiteExpanded] = useState(true);
  const [slidersOpen, setSlidersOpen] = useState(false);

  const compRqs = (
    (rqsScores.accuracy + rqsScores.relevance + rqsScores.consistency + rqsScores.fluency) / 4
  ).toFixed(2);

  const techniqueIcons = {
    'zero-shot': Sliders,
    'few-shot': Layers,
    'role-prompting': Terminal,
    'chain-of-thought': GitBranch,
  };

  return (
    <>
      {/* Mobile Backdrop Overlay (Closes drawer on outside tap) */}
      {!isCollapsed && (
        <div
          onClick={() => setIsCollapsed(true)}
          className="fixed inset-0 bg-black/75 backdrop-blur-sm z-30 md:hidden transition-opacity"
          aria-hidden="true"
        />
      )}

      <aside
        className={`fixed md:relative z-40 top-0 bottom-0 left-0 flex flex-col bg-[#11131A] border-r border-white/[0.07] shadow-2xl md:shadow-none transition-all duration-300 ease-in-out ${
          isCollapsed
            ? 'w-0 -translate-x-full md:w-16 md:translate-x-0'
            : 'w-[84vw] max-w-[310px] md:w-[280px] translate-x-0'
        }`}
      >
        {/* Sidebar Header */}
        <div className="flex items-center justify-between p-4 border-b border-white/[0.06] min-h-[64px]">
          {!isCollapsed && (
            <div className="flex items-center gap-2.5">
              <div className="w-7 h-7 rounded-lg bg-indigo-500/10 border border-indigo-500/30 flex items-center justify-center">
                <Cpu className="w-4 h-4 text-indigo-400" strokeWidth={1.5} />
              </div>
              <div>
                <div className="text-sm font-semibold tracking-tight text-white">Nexus LLM Studio</div>
                <div className="text-[10px] font-mono uppercase tracking-wider text-zinc-500">Practical No. 9</div>
              </div>
            </div>
          )}

          <button
            onClick={() => setIsCollapsed(!isCollapsed)}
            className="p-1.5 rounded-md hover:bg-white/[0.05] text-zinc-400 hover:text-white transition-colors"
            title={isCollapsed ? 'Expand Sidebar' : 'Collapse Sidebar'}
          >
            {isCollapsed ? (
              <PanelLeftOpen className="w-4 h-4" strokeWidth={1.5} />
            ) : (
              <PanelLeftClose className="w-4 h-4" strokeWidth={1.5} />
            )}
          </button>
        </div>

        {!isCollapsed && (
          <div className="flex-1 overflow-y-auto px-3 py-3 space-y-4">
            {/* New Session Action */}
            <button
              onClick={() => {
                onNewSession();
                if (window.innerWidth < 768) setIsCollapsed(true);
              }}
              className="w-full flex items-center justify-between px-3 py-2.5 rounded-lg bg-white/[0.04] hover:bg-white/[0.08] border border-white/[0.08] text-zinc-200 hover:text-white text-xs font-medium transition-all group active:scale-[0.98]"
            >
              <div className="flex items-center gap-2">
                <Plus className="w-4 h-4 text-indigo-400 group-hover:scale-110 transition-transform" strokeWidth={1.5} />
                <span>New Session</span>
              </div>
              <kbd className="text-[10px] font-mono text-zinc-500 bg-black/40 px-1.5 py-0.5 rounded border border-white/[0.06]">
                Cmd K
              </kbd>
            </button>

          {/* API Credentials Vault */}
          <div className="p-2.5 rounded-lg bg-black/30 border border-white/[0.05]">
            <div className="flex items-center justify-between mb-2">
              <span className="text-[11px] font-mono uppercase tracking-wider text-zinc-400 flex items-center gap-1.5">
                <KeyRound className="w-3 h-3 text-zinc-400" strokeWidth={1.5} />
                API Vault
              </span>
              <div className="flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                <span className="text-[10px] font-mono text-emerald-400">Live</span>
              </div>
            </div>
            <input
              type="password"
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              placeholder="Gemini API Key"
              className="w-full bg-[#090A0F] border border-white/[0.08] rounded-md px-2.5 py-1.5 text-xs text-zinc-200 focus:outline-none focus:border-indigo-500/60 font-mono"
            />
          </div>

          {/* Segmented Prompt Engineering Engine */}
          <div className="space-y-1.5">
            <div className="text-[11px] font-mono uppercase tracking-wider text-zinc-500 px-1 flex items-center justify-between">
              <span>Prompt Engine</span>
              <span className="text-[10px] text-indigo-400">Active</span>
            </div>
            <div className="space-y-1">
              {Object.values(TECHNIQUES).map((t) => {
                const Icon = techniqueIcons[t.id] || Sliders;
                const isSelected = activeTechnique === t.id;
                return (
                  <button
                    key={t.id}
                    onClick={() => setActiveTechnique(t.id)}
                    className={`w-full text-left p-2 rounded-lg border transition-all ${
                      isSelected
                        ? 'bg-indigo-500/10 border-indigo-500/40 text-white'
                        : 'bg-transparent border-transparent hover:bg-white/[0.03] text-zinc-400 hover:text-zinc-200'
                    }`}
                  >
                    <div className="flex items-center gap-2">
                      <Icon className={`w-3.5 h-3.5 ${isSelected ? 'text-indigo-400' : 'text-zinc-500'}`} strokeWidth={1.5} />
                      <span className="text-xs font-medium">{t.label}</span>
                    </div>
                    <div className="text-[10px] text-zinc-500 pl-5.5 mt-0.5 line-clamp-1">{t.description}</div>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Lab Validation Suite Accordion */}
          <div className="pt-2 border-t border-white/[0.06]">
            <button
              onClick={() => setSuiteExpanded(!suiteExpanded)}
              className="w-full flex items-center justify-between py-1 px-1 text-[11px] font-mono uppercase tracking-wider text-zinc-500 hover:text-zinc-300"
            >
              <span>Lab Validation Suite</span>
              {suiteExpanded ? <ChevronDown className="w-3.5 h-3.5" /> : <ChevronRight className="w-3.5 h-3.5" />}
            </button>

            {suiteExpanded && (
              <div className="mt-2 space-y-1">
                {LAB_TEST_CASES.map((tc) => {
                  const status = testCaseStatuses[tc.id] || 'READY';
                  const isPassed = status === 'PASSED';
                  return (
                    <button
                      key={tc.id}
                      onClick={() => {
                        onRunTestCase(tc);
                        if (window.innerWidth < 768) setIsCollapsed(true);
                      }}
                      className="w-full flex items-center justify-between px-2.5 py-1.5 rounded-md bg-white/[0.02] hover:bg-white/[0.06] border border-white/[0.04] text-left transition-colors group active:scale-[0.98]"
                    >
                      <div className="flex items-center gap-2 overflow-hidden">
                        <span className="text-[10px] font-mono text-zinc-400 font-semibold">{tc.label}</span>
                        <span className="text-xs text-zinc-300 truncate group-hover:text-white">{tc.badge}</span>
                      </div>
                      <div className="flex items-center gap-1 shrink-0">
                        {isPassed ? (
                          <span className="flex items-center gap-1 text-[10px] font-mono text-emerald-400 bg-emerald-500/10 px-1.5 py-0.5 rounded border border-emerald-500/20">
                            <CheckCircle2 className="w-2.5 h-2.5" strokeWidth={1.5} />
                            PASS
                          </span>
                        ) : (
                          <span className="flex items-center gap-1 text-[10px] font-mono text-zinc-500 bg-white/[0.04] px-1.5 py-0.5 rounded border border-white/[0.06]">
                            <Clock className="w-2.5 h-2.5" strokeWidth={1.5} />
                            READY
                          </span>
                        )}
                      </div>
                    </button>
                  );
                })}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Live RQS Telemetry Dock (Pinned to Bottom) */}
      {!isCollapsed && (
        <div className="p-3 border-t border-white/[0.06] bg-[#0E1017]">
          <div className="flex items-center justify-between mb-2">
            <span className="text-[11px] font-mono uppercase tracking-wider text-zinc-400 flex items-center gap-1.5">
              <Activity className="w-3 h-3 text-indigo-400" strokeWidth={1.5} />
              RQS Model
            </span>
            <div className="text-xs font-mono font-bold text-indigo-400">{compRqs} / 10</div>
          </div>

          <div className="space-y-1.5 mb-2">
            {[
              { key: 'accuracy', label: 'Acc', val: rqsScores.accuracy },
              { key: 'relevance', label: 'Rel', val: rqsScores.relevance },
              { key: 'consistency', label: 'Cons', val: rqsScores.consistency },
              { key: 'fluency', label: 'Flu', val: rqsScores.fluency },
            ].map((m) => (
              <div key={m.key} className="space-y-0.5">
                <div className="flex justify-between text-[9px] font-mono text-zinc-500">
                  <span>{m.label}</span>
                  <span>{m.val.toFixed(1)}</span>
                </div>
                <div className="h-1 bg-white/[0.06] rounded-full overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-indigo-500 to-emerald-400 rounded-full transition-all duration-300"
                    style={{ width: `${(m.val / 10) * 100}%` }}
                  />
                </div>
              </div>
            ))}
          </div>

          <button
            onClick={() => setSlidersOpen(!slidersOpen)}
            className="w-full flex items-center justify-center gap-1.5 py-1 text-[10px] font-mono text-zinc-400 hover:text-white bg-white/[0.03] hover:bg-white/[0.06] rounded border border-white/[0.05] transition-colors"
          >
            <SlidersHorizontal className="w-3 h-3" strokeWidth={1.5} />
            <span>{slidersOpen ? 'Hide Calibration' : 'Calibrate Sliders'}</span>
          </button>

          {slidersOpen && (
            <div className="mt-2 pt-2 border-t border-white/[0.06] space-y-2">
              {['accuracy', 'relevance', 'consistency', 'fluency'].map((key) => (
                <div key={key}>
                  <div className="flex justify-between text-[10px] font-mono text-zinc-400 capitalize mb-0.5">
                    <span>{key}</span>
                    <span>{rqsScores[key]}</span>
                  </div>
                  <input
                    type="range"
                    min="1"
                    max="10"
                    step="0.1"
                    value={rqsScores[key]}
                    onChange={(e) =>
                      setRqsScores({
                        ...rqsScores,
                        [key]: parseFloat(e.target.value),
                      })
                    }
                    className="w-full h-1 bg-white/[0.1] rounded-lg appearance-none cursor-pointer accent-indigo-500"
                  />
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </aside>
  </>
  );
}
