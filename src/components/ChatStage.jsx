import React, { useState, useEffect, useRef } from 'react';
import {
  Sparkles,
  ArrowUpRight,
  Code2,
  Copy,
  Check,
  RotateCcw,
  Layers,
  Cpu,
  BarChart3,
  FileText,
  Activity,
  AudioWaveform,
  CheckCircle2,
  AlertTriangle,
  HelpCircle,
} from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from 'recharts';
import MermaidDiagram from './MermaidDiagram';
import { LAB_TEST_CASES } from '../services/geminiService';

export default function ChatStage({
  messages,
  isLoading,
  loadingStep,
  onSelectStarter,
  onRegenerate,
}) {
  const [copiedIdx, setCopiedIdx] = useState(null);
  const [expandedXrays, setExpandedXrays] = useState({});
  const [elapsedSeconds, setElapsedSeconds] = useState(0);
  const latestQueryRef = useRef(null);
  const scrollContainerRef = useRef(null);

  // Soothing elapsed timer for the neural loading state
  useEffect(() => {
    let interval = null;
    if (isLoading) {
      setElapsedSeconds(0);
      interval = setInterval(() => {
        setElapsedSeconds((prev) => +(prev + 0.2).toFixed(1));
      }, 200);
    } else {
      setElapsedSeconds(0);
    }
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [isLoading]);

  const getThinkingStage = (sec) => {
    if (loadingStep) return loadingStep;
    if (sec < 2.0) return 'Formulating prompt strategy & system instructions...';
    if (sec < 4.5) return 'Consulting Google Gemini 3.5 Flash neural core...';
    if (sec < 7.0) return 'Synthesizing visual telemetry, diagrams & schemas...';
    return 'Polishing generative UI presentation & telemetry...';
  };

  // Auto-focus and scroll to newly entered query (Gemini style)
  useEffect(() => {
    if (messages.length === 0) return;
    const lastMsg = messages[messages.length - 1];

    // Scroll to the user query when it is entered
    if (lastMsg && lastMsg.role === 'user') {
      const timer = setTimeout(() => {
        if (latestQueryRef.current) {
          latestQueryRef.current.scrollIntoView({
            behavior: 'smooth',
            block: 'start',
          });
        }
      }, 50);
      return () => clearTimeout(timer);
    }
  }, [messages]);

  const handleCopy = (text, idx) => {
    navigator.clipboard.writeText(text);
    setCopiedIdx(idx);
    setTimeout(() => setCopiedIdx(null), 2000);
  };

  const toggleXray = (idx) => {
    setExpandedXrays((prev) => ({
      ...prev,
      [idx]: !prev[idx],
    }));
  };

  const starterCards = [
    {
      tc: LAB_TEST_CASES[0],
      icon: Cpu,
      title: 'Question Answering',
      query: 'What is Artificial Intelligence?',
      meta: 'Mindmap & comparison matrix',
    },
    {
      tc: LAB_TEST_CASES[1],
      icon: FileText,
      title: 'Text Summarization',
      query: 'Artificial Intelligence is transforming healthcare, education, banking and transportation through automation and intelligent decision making.',
      meta: 'Compression analytics & domain table',
    },
    {
      tc: LAB_TEST_CASES[2],
      icon: Sparkles,
      title: 'Sentiment (Positive)',
      query: 'This mobile phone has excellent battery backup and good camera.',
      meta: 'Aspect-level polarity evaluation',
    },
    {
      tc: LAB_TEST_CASES[3],
      icon: BarChart3,
      title: 'Sentiment (Negative)',
      query: 'Worst experience, the device lags constantly and battery life is poor.',
      meta: 'Negative latency & hardware diagnostics',
    },
  ];

  return (
    <div
      ref={scrollContainerRef}
      className="flex-1 overflow-y-auto px-4 sm:px-8 pt-6 pb-36 max-w-[880px] w-full mx-auto scroll-smooth"
    >
      {/* Zero-State Canvas */}
      {messages.length === 0 ? (
        <div className="min-h-[70vh] flex flex-col justify-center items-center text-center">
          {/* Centered Geometric SVG Emblem with Breathing Glow */}
          <div className="relative mb-6">
            <div className="absolute inset-0 rounded-2xl bg-indigo-500/20 blur-xl animate-pulse" />
            <div className="relative w-16 h-16 rounded-2xl bg-gradient-to-b from-white/[0.1] to-white/[0.02] border border-white/[0.12] flex items-center justify-center shadow-2xl">
              <Sparkles className="w-8 h-8 text-indigo-400" strokeWidth={1.5} />
            </div>
          </div>

          <h1 className="text-2xl sm:text-3xl font-semibold tracking-tight text-white mb-2">
            Ready to engineer your next query.
          </h1>
          <p className="text-sm text-zinc-400 max-w-md mb-10 leading-relaxed">
            Execute Question Answering, Text Summarization, and Sentiment Classification with real-time generative UI telemetry.
          </p>

          {/* 2x2 Bento Grid of Starter Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 w-full max-w-2xl text-left">
            {starterCards.map((card, i) => {
              const Icon = card.icon;
              return (
                <button
                  key={i}
                  onClick={() => onSelectStarter(card.tc)}
                  className="spotlight-card rounded-xl p-4 flex flex-col justify-between group transition-all"
                >
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2 text-xs font-mono uppercase tracking-wider text-zinc-400">
                      <Icon className="w-3.5 h-3.5 text-indigo-400" strokeWidth={1.5} />
                      <span>{card.title}</span>
                    </div>
                    <ArrowUpRight
                      className="w-4 h-4 text-zinc-500 group-hover:text-indigo-400 group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-all"
                      strokeWidth={1.5}
                    />
                  </div>
                  <div className="text-sm text-zinc-200 group-hover:text-white line-clamp-2 font-normal mb-2">
                    {card.query}
                  </div>
                  <div className="text-[11px] font-mono text-zinc-500">{card.meta}</div>
                </button>
              );
            })}
          </div>
        </div>
      ) : (
        /* Chat Message Stream */
        <div className="space-y-6">
          {(() => {
            const latestUserIdx = messages.map((m) => m.role).lastIndexOf('user');
            return messages.map((msg, idx) => (
              <div
                key={idx}
                ref={idx === latestUserIdx ? latestQueryRef : null}
                className="space-y-2 scroll-mt-6"
              >
              {msg.role === 'user' ? (
                /* User Message Bubble */
                <div className="flex justify-end">
                  <div className="max-w-[85%] rounded-2xl px-4 py-3 bg-[#1A1F2C] border border-indigo-500/20 text-sm text-white shadow-lg leading-relaxed">
                    {msg.content}
                  </div>
                </div>
              ) : (
                /* Assistant Generative UI Bubble */
                <div className="flex justify-start">
                  <div className="w-full rounded-2xl p-5 bg-[#11131A] border border-white/[0.08] shadow-2xl space-y-4 animate-response-reveal">
                    {/* Editorial Prose / Hero Text */}
                    {msg.payload?.hero_answer && (
                      <div className="text-sm sm:text-[15px] text-zinc-200 leading-relaxed font-normal animate-sub-reveal">
                        {msg.payload.hero_answer}
                      </div>
                    )}

                    {/* Question Answering Artifact */}
                    {msg.task === 'Question Answering' && (
                      <div className="space-y-4 pt-1">
                        {/* 3 Architectural Pillars */}
                        {msg.payload?.key_takeaways?.length > 0 && (
                          <div className="grid grid-cols-1 sm:grid-cols-3 gap-2.5">
                            {msg.payload.key_takeaways.map((tk, i) => (
                              <div
                                key={i}
                                className="p-3 rounded-xl bg-white/[0.02] border border-white/[0.06]"
                              >
                                <div className="text-[10px] font-mono uppercase tracking-wider text-indigo-400 font-semibold mb-1">
                                  Pillar 0{i + 1}
                                </div>
                                <div className="text-xs text-zinc-300 leading-normal">{tk}</div>
                              </div>
                            ))}
                          </div>
                        )}

                        {/* Mermaid Concept Diagram */}
                        {msg.payload?.mermaid_diagram && (
                          <MermaidDiagram code={msg.payload.mermaid_diagram} />
                        )}

                        {/* Structured Comparison Matrix */}
                        {msg.payload?.comparison_table?.length > 0 && (
                          <div className="rounded-xl border border-white/[0.08] overflow-hidden bg-white/[0.01]">
                            <div className="px-3.5 py-2 border-b border-white/[0.06] bg-white/[0.02] text-[11px] font-mono uppercase tracking-wider text-zinc-400">
                              Architectural Dimensions & Impact Matrix
                            </div>
                            <div className="overflow-x-auto">
                              <table className="w-full text-left text-xs font-sans">
                                <thead>
                                  <tr className="border-b border-white/[0.06] text-zinc-400 bg-white/[0.01]">
                                    <th className="py-2.5 px-3.5 font-medium">Dimension</th>
                                    <th className="py-2.5 px-3.5 font-medium">Details</th>
                                    <th className="py-2.5 px-3.5 font-medium">Impact</th>
                                  </tr>
                                </thead>
                                <tbody className="divide-y divide-white/[0.04]">
                                  {msg.payload.comparison_table.map((row, i) => (
                                    <tr key={i} className="hover:bg-white/[0.02] transition-colors">
                                      <td className="py-2.5 px-3.5 font-medium text-indigo-300 whitespace-nowrap">
                                        {row.Dimension}
                                      </td>
                                      <td className="py-2.5 px-3.5 text-zinc-300">{row.Details}</td>
                                      <td className="py-2.5 px-3.5 text-zinc-400">{row.Impact}</td>
                                    </tr>
                                  ))}
                                </tbody>
                              </table>
                            </div>
                          </div>
                        )}
                      </div>
                    )}

                    {/* Text Summarization Artifact */}
                    {msg.task === 'Text Summarization' && (
                      <div className="space-y-4 pt-1">
                        {/* Executive TL;DR Callout */}
                        {msg.payload?.tldr && (
                          <div className="p-3.5 rounded-xl bg-emerald-500/[0.05] border-l-2 border-emerald-400 border-y border-r border-white/[0.06]">
                            <div className="text-[10px] font-mono uppercase tracking-wider text-emerald-400 font-semibold mb-1">
                              Executive TL;DR
                            </div>
                            <div className="text-sm text-zinc-100 font-medium leading-relaxed">
                              {msg.payload.tldr}
                            </div>
                          </div>
                        )}

                        {/* Recharts Compression Telemetry */}
                        {msg.payload?.metrics && (
                          <div className="p-3.5 rounded-xl bg-white/[0.02] border border-white/[0.06]">
                            <div className="flex items-center justify-between mb-3">
                              <span className="text-[11px] font-mono uppercase tracking-wider text-zinc-400">
                                Compression Telemetry
                              </span>
                              <div className="flex items-center gap-2">
                                <span className="text-xs font-mono text-emerald-400 font-medium">
                                  {msg.payload.metrics.compression_ratio_pct}% Reduction
                                </span>
                                <span className="text-[11px] font-mono text-zinc-500">
                                  ~{msg.payload.metrics.reading_time_saved_sec}s Saved
                                </span>
                              </div>
                            </div>
                            <div className="h-28 w-full">
                              <ResponsiveContainer width="100%" height="100%">
                                <BarChart
                                  layout="vertical"
                                  data={[
                                    { name: 'Original', count: msg.payload.metrics.original_words },
                                    { name: 'Summary', count: msg.payload.metrics.summary_words },
                                  ]}
                                  margin={{ top: 5, right: 20, left: 20, bottom: 5 }}
                                >
                                  <XAxis type="number" stroke="#52525b" fontSize={11} />
                                  <YAxis type="category" dataKey="name" stroke="#a1a1aa" fontSize={11} width={60} />
                                  <Tooltip
                                    contentStyle={{ background: '#090A0F', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px', fontSize: '11px' }}
                                  />
                                  <Bar dataKey="count" fill="#6366F1" radius={[0, 4, 4, 0]} />
                                </BarChart>
                              </ResponsiveContainer>
                            </div>
                          </div>
                        )}

                        {/* Key Takeaways */}
                        {msg.payload?.bullet_takeaways?.length > 0 && (
                          <div className="space-y-1.5">
                            <div className="text-[11px] font-mono uppercase tracking-wider text-zinc-400">
                              Key Takeaways
                            </div>
                            <div className="space-y-1">
                              {msg.payload.bullet_takeaways.map((b, i) => (
                                <div key={i} className="flex items-start gap-2 text-xs text-zinc-300">
                                  <span className="w-1.5 h-1.5 rounded-full bg-indigo-400 mt-1.5 shrink-0" />
                                  <span>{b}</span>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}

                        {/* Extracted Domain Impact Table */}
                        {msg.payload?.domain_impact_table?.length > 0 && (
                          <div className="rounded-xl border border-white/[0.08] overflow-hidden bg-white/[0.01]">
                            <div className="px-3.5 py-2 border-b border-white/[0.06] bg-white/[0.02] text-[11px] font-mono uppercase tracking-wider text-zinc-400">
                              Domain Impact Breakdown
                            </div>
                            <table className="w-full text-left text-xs font-sans">
                              <thead>
                                <tr className="border-b border-white/[0.06] text-zinc-400 bg-white/[0.01]">
                                  <th className="py-2.5 px-3.5 font-medium">Domain</th>
                                  <th className="py-2.5 px-3.5 font-medium">Transformative Impact</th>
                                </tr>
                              </thead>
                              <tbody className="divide-y divide-white/[0.04]">
                                {msg.payload.domain_impact_table.map((row, i) => (
                                  <tr key={i} className="hover:bg-white/[0.02] transition-colors">
                                    <td className="py-2.5 px-3.5 font-medium text-emerald-300 whitespace-nowrap">
                                      {row.Domain}
                                    </td>
                                    <td className="py-2.5 px-3.5 text-zinc-300">{row.Impact}</td>
                                  </tr>
                                ))}
                              </tbody>
                            </table>
                          </div>
                        )}
                      </div>
                    )}

                    {/* Text Classification Artifact */}
                    {msg.task === 'Text Classification' && (
                      <div className="space-y-4 pt-1">
                        {/* Sentiment Header Card */}
                        {msg.payload?.primary_sentiment && (
                          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-3.5 rounded-xl bg-white/[0.02] border border-white/[0.06]">
                            <div>
                              <div className="text-[10px] font-mono uppercase tracking-wider text-zinc-400 mb-1">
                                Classification Verdict
                              </div>
                              <div className="flex items-center gap-2">
                                <span
                                  className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-mono font-semibold uppercase tracking-wider ${
                                    msg.payload.primary_sentiment === 'Positive'
                                      ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30'
                                      : msg.payload.primary_sentiment === 'Negative'
                                      ? 'bg-rose-500/10 text-rose-400 border border-rose-500/30'
                                      : 'bg-amber-500/10 text-amber-400 border border-amber-500/30'
                                  }`}
                                >
                                  <span className="w-1.5 h-1.5 rounded-full bg-current" />
                                  {msg.payload.primary_sentiment}
                                </span>
                              </div>
                            </div>
                            <div className="text-xs text-zinc-300 max-w-sm">
                              {msg.payload.sentiment_summary}
                            </div>
                          </div>
                        )}

                        {/* Confidence Distribution Donut */}
                        {msg.payload?.confidence_scores && (
                          <div className="p-3.5 rounded-xl bg-white/[0.02] border border-white/[0.06]">
                            <div className="text-[11px] font-mono uppercase tracking-wider text-zinc-400 mb-2">
                              Confidence Distribution
                            </div>
                            <div className="flex flex-col sm:flex-row items-center gap-4">
                              <div className="w-32 h-32 shrink-0">
                                <ResponsiveContainer width="100%" height="100%">
                                  <PieChart>
                                    <Pie
                                      data={[
                                        { name: 'Positive', value: msg.payload.confidence_scores.Positive || 0, color: '#10B981' },
                                        { name: 'Neutral', value: msg.payload.confidence_scores.Neutral || 0, color: '#F59E0B' },
                                        { name: 'Negative', value: msg.payload.confidence_scores.Negative || 0, color: '#F43F5E' },
                                      ]}
                                      innerRadius={36}
                                      outerRadius={56}
                                      paddingAngle={3}
                                      dataKey="value"
                                    >
                                      {[{ color: '#10B981' }, { color: '#F59E0B' }, { color: '#F43F5E' }].map((entry, index) => (
                                        <Cell key={index} fill={entry.color} />
                                      ))}
                                    </Pie>
                                  </PieChart>
                                </ResponsiveContainer>
                              </div>

                              <div className="flex-1 grid grid-cols-3 gap-2 w-full">
                                {[
                                  { label: 'Positive', val: msg.payload.confidence_scores.Positive || 0, color: 'text-emerald-400' },
                                  { label: 'Neutral', val: msg.payload.confidence_scores.Neutral || 0, color: 'text-amber-400' },
                                  { label: 'Negative', val: msg.payload.confidence_scores.Negative || 0, color: 'text-rose-400' },
                                ].map((item) => (
                                  <div key={item.label} className="p-2.5 rounded-lg bg-black/40 border border-white/[0.04] text-center">
                                    <div className="text-[10px] font-mono text-zinc-400">{item.label}</div>
                                    <div className={`text-base font-mono font-bold ${item.color} mt-0.5`}>
                                      {item.val}%
                                    </div>
                                  </div>
                                ))}
                              </div>
                            </div>
                          </div>
                        )}

                        {/* Aspect-Level Polarity Table */}
                        {msg.payload?.aspect_breakdown?.length > 0 && (
                          <div className="rounded-xl border border-white/[0.08] overflow-hidden bg-white/[0.01]">
                            <div className="px-3.5 py-2 border-b border-white/[0.06] bg-white/[0.02] text-[11px] font-mono uppercase tracking-wider text-zinc-400">
                              Aspect-Level Feature Breakdown
                            </div>
                            <table className="w-full text-left text-xs font-sans">
                              <thead>
                                <tr className="border-b border-white/[0.06] text-zinc-400 bg-white/[0.01]">
                                  <th className="py-2.5 px-3.5 font-medium">Feature</th>
                                  <th className="py-2.5 px-3.5 font-medium">Extracted Phrase</th>
                                  <th className="py-2.5 px-3.5 font-medium">Polarity</th>
                                  <th className="py-2.5 px-3.5 font-medium">Confidence</th>
                                </tr>
                              </thead>
                              <tbody className="divide-y divide-white/[0.04]">
                                {msg.payload.aspect_breakdown.map((row, i) => (
                                  <tr key={i} className="hover:bg-white/[0.02] transition-colors">
                                    <td className="py-2.5 px-3.5 font-medium text-zinc-200">{row.Aspect}</td>
                                    <td className="py-2.5 px-3.5 text-zinc-400 italic">"{row.Extracted_Phrase}"</td>
                                    <td className="py-2.5 px-3.5">
                                      <span
                                        className={`inline-block px-1.5 py-0.5 rounded text-[10px] font-mono uppercase font-semibold ${
                                          row.Polarity === 'Positive'
                                            ? 'text-emerald-400 bg-emerald-500/10'
                                            : row.Polarity === 'Negative'
                                            ? 'text-rose-400 bg-rose-500/10'
                                            : 'text-amber-400 bg-amber-500/10'
                                        }`}
                                      >
                                        {row.Polarity}
                                      </span>
                                    </td>
                                    <td className="py-2.5 px-3.5 font-mono text-zinc-300">{row.Confidence}%</td>
                                  </tr>
                                ))}
                              </tbody>
                            </table>
                          </div>
                        )}
                      </div>
                    )}

                    {/* Message Action Footer */}
                    <div className="flex items-center justify-between pt-3 border-t border-white/[0.06] mt-2">
                      <div className="flex items-center gap-1.5">
                        <button
                          onClick={() => handleCopy(msg.content || JSON.stringify(msg.payload), idx)}
                          className="flex items-center gap-1 px-2.5 py-1 text-xs font-mono text-zinc-400 hover:text-white bg-white/[0.03] hover:bg-white/[0.08] rounded-md transition-colors"
                        >
                          {copiedIdx === idx ? (
                            <>
                              <Check className="w-3 h-3 text-emerald-400" strokeWidth={1.5} />
                              <span>Copied</span>
                            </>
                          ) : (
                            <>
                              <Copy className="w-3 h-3" strokeWidth={1.5} />
                              <span>Copy</span>
                            </>
                          )}
                        </button>

                        <button
                          onClick={() => onRegenerate(idx)}
                          className="flex items-center gap-1 px-2.5 py-1 text-xs font-mono text-zinc-400 hover:text-white bg-white/[0.03] hover:bg-white/[0.08] rounded-md transition-colors"
                        >
                          <RotateCcw className="w-3 h-3" strokeWidth={1.5} />
                          <span>Regenerate</span>
                        </button>
                      </div>

                      <button
                        onClick={() => toggleXray(idx)}
                        className={`flex items-center gap-1.5 px-2.5 py-1 text-xs font-mono rounded-md border transition-colors ${
                          expandedXrays[idx]
                            ? 'bg-indigo-500/20 text-indigo-300 border-indigo-500/30'
                            : 'text-zinc-400 hover:text-zinc-200 bg-white/[0.03] border-white/[0.06]'
                        }`}
                      >
                        <Code2 className="w-3.5 h-3.5" strokeWidth={1.5} />
                        <span>Prompt X-Ray</span>
                      </button>
                    </div>

                    {/* Expandable Prompt X-Ray Drawer */}
                    {expandedXrays[idx] && msg.xray && (
                      <div className="mt-3 p-3.5 rounded-xl bg-black/60 border border-white/[0.08] font-mono text-xs space-y-2">
                        <div className="text-[10px] uppercase tracking-wider text-zinc-500 flex items-center justify-between">
                          <span>Prompt Engineering Deconstruction</span>
                          <span className="text-indigo-400">{msg.xray.techniqueName}</span>
                        </div>
                        <div className="space-y-1.5 pt-1">
                          <div className="p-2 rounded bg-purple-500/10 border border-purple-500/20 text-purple-200">
                            <span className="text-purple-400 font-bold">[SYSTEM ROLE]</span>: {msg.xray.systemRole}
                          </div>
                          <div className="p-2 rounded bg-cyan-500/10 border border-cyan-500/20 text-cyan-200">
                            <span className="text-cyan-400 font-bold">[TASK DIRECTIVE]</span>: {msg.xray.taskDirective}
                          </div>
                          <div className="p-2 rounded bg-emerald-500/10 border border-emerald-500/20 text-emerald-200">
                            <span className="text-emerald-400 font-bold">[USER INPUT]</span>: {msg.xray.userText}
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          ));
        })()}

          {/* Soothing & Mesmerizing Neural Loading State */}
          {isLoading && (
            <div className="relative w-full rounded-2xl p-6 bg-[#0E1017]/90 backdrop-blur-xl border border-indigo-500/30 space-y-4 shadow-2xl overflow-hidden animate-response-reveal">
              {/* Ambient Breathing Aura Behind the Card */}
              <div className="absolute -inset-10 bg-gradient-to-r from-indigo-600/15 via-purple-600/10 to-cyan-500/10 rounded-full pointer-events-none animate-breathing-aura" />

              {/* Top Laser Beam Sweep Line */}
              <div className="absolute top-0 left-0 right-0 h-[1.5px] overflow-hidden bg-white/[0.05]">
                <div className="w-1/3 h-full bg-gradient-to-r from-transparent via-indigo-400 to-transparent animate-beam-sweep" />
              </div>

              {/* Header with Mesmerizing Neural Core & Elapsed Timer */}
              <div className="relative z-10 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  {/* Mesmerizing Multi-Ring Neural Core */}
                  <div className="relative flex items-center justify-center w-7 h-7 shrink-0">
                    <div className="absolute inset-0 rounded-full bg-indigo-500/20 animate-neural-ring-1" />
                    <div className="absolute -inset-1 rounded-full border border-indigo-400/30 animate-neural-ring-2" />
                    <div className="absolute -inset-2 rounded-full border border-purple-400/20 animate-neural-ring-3" />
                    <Sparkles className="w-3.5 h-3.5 text-indigo-300 relative z-10 animate-spin" style={{ animationDuration: '9s' }} strokeWidth={1.5} />
                  </div>

                  {/* Dynamic Cognitive Thinking Stage */}
                  <div className="space-y-0.5">
                    <div className="text-xs font-mono text-indigo-200 font-medium transition-all duration-300">
                      {getThinkingStage(elapsedSeconds)}
                    </div>
                    <div className="text-[10px] font-mono text-zinc-500">
                      Gemini 3.5 Flash • Active Generative Synthesis
                    </div>
                  </div>
                </div>

                {/* Live Stopwatch Badge with Pulsing Emerald Beacon */}
                <div className="flex items-center gap-2 px-2.5 py-1 rounded-full bg-black/60 border border-white/[0.08] backdrop-blur-md shrink-0 shadow-inner">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                  <span className="text-[11px] font-mono text-zinc-300">{elapsedSeconds.toFixed(1)}s</span>
                </div>
              </div>

              {/* Fluid Multi-Stage Wave Progress Bar */}
              <div className="relative z-10 h-1.5 w-full bg-white/[0.05] rounded-full overflow-hidden p-[0.5px]">
                <div className="h-full rounded-full bg-gradient-to-r from-indigo-500 via-purple-500 via-cyan-400 to-indigo-500 animate-fluid-gradient animate-shimmer" />
              </div>

              {/* Calming Tactile Wireframe Preview */}
              <div className="relative z-10 space-y-2.5 pt-1">
                <div className="h-4 w-4/5 bg-gradient-to-r from-white/[0.06] via-white/[0.03] to-white/[0.06] rounded-md animate-pulse" />
                <div className="h-4 w-3/5 bg-gradient-to-r from-white/[0.05] via-white/[0.02] to-white/[0.05] rounded-md animate-pulse" style={{ animationDelay: '200ms' }} />
                
                {/* Visual Skeleton Tiles Hinting at Incoming Diagram & Columns */}
                <div className="grid grid-cols-3 gap-2 pt-2">
                  <div className="h-12 rounded-xl bg-white/[0.02] border border-white/[0.04] animate-pulse flex items-center justify-center" style={{ animationDelay: '100ms' }}>
                    <div className="w-12 h-2 rounded bg-white/[0.04]" />
                  </div>
                  <div className="h-12 rounded-xl bg-white/[0.02] border border-white/[0.04] animate-pulse flex items-center justify-center" style={{ animationDelay: '250ms' }}>
                    <div className="w-16 h-2 rounded bg-white/[0.04]" />
                  </div>
                  <div className="h-12 rounded-xl bg-white/[0.02] border border-white/[0.04] animate-pulse flex items-center justify-center" style={{ animationDelay: '400ms' }}>
                    <div className="w-10 h-2 rounded bg-white/[0.04]" />
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
