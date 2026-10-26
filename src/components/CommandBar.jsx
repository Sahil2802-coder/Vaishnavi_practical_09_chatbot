import React, { useState, useRef, useEffect } from 'react';
import {
  Compass,
  Cpu,
  FileText,
  BarChart3,
  Mic,
  MicOff,
  ArrowUp,
  AlertCircle,
} from 'lucide-react';

export default function CommandBar({
  onSendMessage,
  taskMode,
  setTaskMode,
  isLoading,
}) {
  const [text, setText] = useState('');
  const [isListening, setIsListening] = useState(false);
  const [recordSeconds, setRecordSeconds] = useState(0);
  const [micError, setMicError] = useState(null);
  const textareaRef = useRef(null);
  const recognitionRef = useRef(null);
  const timerRef = useRef(null);
  const baseTextRef = useRef('');
  const isListeningRef = useRef(false);

  // Initialize Web Speech API
  useEffect(() => {
    const SpeechRecognition =
      window.SpeechRecognition || window.webkitSpeechRecognition;

    if (SpeechRecognition) {
      const recognition = new SpeechRecognition();
      recognition.continuous = true;
      recognition.interimResults = true;
      recognition.lang = 'en-US';

      recognition.onresult = (event) => {
        let finalTranscript = '';
        let interimTranscript = '';

        for (let i = 0; i < event.results.length; i++) {
          const item = event.results[i];
          const transcript = item[0]?.transcript || '';
          if (item.isFinal) {
            finalTranscript += transcript + ' ';
          } else {
            interimTranscript += transcript;
          }
        }

        let speech = `${finalTranscript}${interimTranscript}`.trim();
        // Technical acronym casing enhancement
        speech = speech
          .replace(/\ba\.i\.\b/gi, 'AI')
          .replace(/\bai\b/gi, 'AI')
          .replace(/\bllm\b/gi, 'LLM')
          .replace(/\bnlp\b/gi, 'NLP');

        const base = baseTextRef.current;
        const combined = base ? `${base} ${speech}` : speech;
        setText(combined);
      };

      recognition.onerror = (event) => {
        if (event.error === 'no-speech') {
          // Normal pause in speech, don't abort
          return;
        }
        console.warn('Speech recognition error:', event.error);
        setMicError(`Microphone notice: ${event.error}`);
        setTimeout(() => setMicError(null), 4000);
        setIsListening(false);
        isListeningRef.current = false;
      };

      recognition.onend = () => {
        setIsListening(false);
        isListeningRef.current = false;
      };

      recognitionRef.current = recognition;
    }
  }, []);

  // Timer for recording
  useEffect(() => {
    if (isListening) {
      timerRef.current = setInterval(() => {
        setRecordSeconds((s) => s + 1);
      }, 1000);
    } else {
      if (timerRef.current) clearInterval(timerRef.current);
      setRecordSeconds(0);
    }
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [isListening]);

  const startListening = () => {
    setMicError(null);
    if (!recognitionRef.current) {
      setMicError('Web Speech API is not supported in this browser. Please use Chrome or Edge.');
      setTimeout(() => setMicError(null), 4000);
      return;
    }
    try {
      baseTextRef.current = text.trim();
      recognitionRef.current.start();
      setIsListening(true);
      isListeningRef.current = true;
    } catch (err) {
      if (err.name === 'InvalidStateError') {
        try {
          recognitionRef.current.stop();
        } catch {
          // ignore
        }
        setTimeout(() => {
          try {
            recognitionRef.current.start();
            setIsListening(true);
            isListeningRef.current = true;
          } catch (e) {
            console.warn('Restart speech error:', e);
          }
        }, 150);
      } else {
        console.warn('Recognition start error:', err);
      }
    }
  };

  const stopListening = () => {
    if (recognitionRef.current) {
      try {
        recognitionRef.current.stop();
      } catch (err) {
        console.warn('Recognition stop error:', err);
      }
    }
    setIsListening(false);
    isListeningRef.current = false;
  };

  const handleToggleVoice = () => {
    if (isListening) {
      stopListening();
    } else {
      startListening();
    }
  };

  // Auto-expand textarea
  useEffect(() => {
    const el = textareaRef.current;
    if (el) {
      el.style.height = 'auto';
      el.style.height = `${Math.min(el.scrollHeight, 180)}px`;
    }
  }, [text]);

  const handleSubmit = (e) => {
    if (e) e.preventDefault();
    if (!text.trim() || isLoading) return;
    if (isListening) stopListening();
    onSendMessage(text.trim());
    setText('');
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const formatTimer = (sec) => {
    const m = Math.floor(sec / 60);
    const s = sec % 60;
    return `${m}:${s < 10 ? '0' : ''}${s}`;
  };

  const modes = [
    { id: 'auto', label: 'Auto-Detect', icon: Compass },
    { id: 'qa', label: 'QA', icon: Cpu },
    { id: 'summarize', label: 'Summarize', icon: FileText },
    { id: 'classify', label: 'Classify', icon: BarChart3 },
  ];

  return (
    <div className="absolute bottom-2.5 sm:bottom-6 left-0 right-0 z-30 px-2 sm:px-4 pointer-events-none">
      <div className="max-w-[780px] mx-auto pointer-events-auto">
        {/* Error Toast */}
        {micError && (
          <div className="mb-2 p-2.5 rounded-lg bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs font-mono flex items-center gap-2">
            <AlertCircle className="w-3.5 h-3.5 shrink-0" strokeWidth={1.5} />
            <span>{micError}</span>
          </div>
        )}

        {/* Floating Composer Container - Pure Dark Black Premium Transparent Glass with Edge Hover Glow */}
        <div className="group relative rounded-[22px] sm:rounded-[24px] transition-all duration-500">
          {/* Ambient Outer Edge Glow Halo on Hover & Focus */}
          <div className="absolute -inset-[2px] rounded-[24px] sm:rounded-[26px] bg-gradient-to-r from-indigo-500/0 via-indigo-500/60 to-purple-500/0 opacity-0 group-hover:opacity-100 group-focus-within:opacity-100 blur-xl transition-all duration-500 pointer-events-none" />
          
          {/* Sharp Edge Glow Ring on Hover */}
          <div className="absolute -inset-[1px] rounded-[23px] sm:rounded-[25px] bg-gradient-to-r from-indigo-400/40 via-indigo-300/80 to-purple-400/40 opacity-0 group-hover:opacity-100 group-focus-within:opacity-100 blur-[2px] transition-all duration-300 pointer-events-none" />

          {/* Outer Border with Edge Gradient */}
          <div className="relative rounded-[22px] sm:rounded-[24px] p-[1px] bg-gradient-to-b from-white/[0.18] via-white/[0.06] to-white/[0.02] group-hover:from-indigo-400/90 group-hover:via-indigo-500/40 group-hover:to-purple-500/30 group-focus-within:from-indigo-400/90 group-focus-within:via-indigo-500/50 group-focus-within:to-indigo-500/20 shadow-[0_20px_50px_rgba(0,0,0,0.9)] group-hover:shadow-[0_0_35px_rgba(99,102,241,0.35),0_25px_60px_rgba(0,0,0,0.95)] transition-all duration-500">
            {/* Pure Dark Black Transparent Glass Body */}
            <div className="rounded-[21px] sm:rounded-[23px] bg-black/60 backdrop-blur-2xl backdrop-saturate-150 border border-white/[0.08] group-hover:border-indigo-400/40 group-focus-within:border-indigo-400/60 shadow-[inset_0_1px_0_0_rgba(255,255,255,0.18),inset_0_-1px_0_0_rgba(0,0,0,0.8)] p-2.5 sm:p-3.5 transition-all duration-300">
              {/* Input Area */}
              <textarea
                ref={textareaRef}
                value={text}
                onChange={(e) => setText(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Ask anything, paste text to summarize, or enter a review..."
                rows={1}
                disabled={isLoading}
                className="w-full bg-transparent text-sm text-zinc-100 placeholder-zinc-400/70 focus:outline-none resize-none px-1.5 sm:px-2 py-0.5 sm:py-1 leading-relaxed font-sans max-h-[140px] sm:max-h-[180px]"
              />

              {/* Bottom Actions Row */}
              <div className="flex items-center justify-between pt-2 sm:pt-2.5 border-t border-white/[0.06] mt-1 sm:mt-1.5">
                {/* Task Mode Selector Pill Bar */}
                <div className="flex items-center gap-0.5 sm:gap-1 bg-black/50 backdrop-blur-md p-0.5 sm:p-1 rounded-xl border border-white/[0.07] shadow-inner shrink-0">
                  {modes.map((m) => {
                    const Icon = m.icon;
                    const isSelected = taskMode === m.id;
                    return (
                      <button
                        key={m.id}
                        type="button"
                        onClick={() => setTaskMode(m.id)}
                        className={`flex items-center gap-1 sm:gap-1.5 px-2 sm:px-2.5 py-1 rounded-lg text-xs font-medium transition-all ${
                          isSelected
                            ? 'bg-indigo-500/25 text-indigo-200 border border-indigo-400/40 shadow-[0_0_15px_rgba(99,102,241,0.2)] backdrop-blur-sm'
                            : 'text-zinc-400 hover:text-zinc-200 border border-transparent hover:bg-white/[0.04]'
                        }`}
                      >
                        <Icon className="w-3 h-3" strokeWidth={1.5} />
                        <span className="hidden sm:inline text-[11px]">{m.label}</span>
                      </button>
                    );
                  })}
                </div>

                {/* Action Controls: Dictation & Submit */}
                <div className="flex items-center gap-1.5 sm:gap-2">
                  {/* Voice-to-Text Button */}
                  {isListening ? (
                    <button
                      type="button"
                      onClick={handleToggleVoice}
                      className="flex items-center gap-1.5 sm:gap-2 px-2.5 sm:px-3.5 py-1 sm:py-1.5 rounded-full bg-rose-500/20 backdrop-blur-md border border-rose-400/40 text-rose-200 text-xs font-mono transition-all animate-pulse shadow-lg shadow-rose-500/25"
                      title="Stop Dictation"
                    >
                      <div className="flex items-center gap-0.5 h-3">
                        <span className="w-1 bg-rose-400 rounded-full waveform-bar-1" />
                        <span className="w-1 bg-rose-400 rounded-full waveform-bar-2" />
                        <span className="w-1 bg-rose-400 rounded-full waveform-bar-3" />
                        <span className="w-1 bg-rose-400 rounded-full waveform-bar-4" />
                        <span className="w-1 bg-rose-400 rounded-full waveform-bar-5" />
                      </div>
                      <span className="text-[11px] font-mono">{formatTimer(recordSeconds)}<span className="hidden sm:inline ml-1">Listening...</span></span>
                    </button>
                  ) : (
                    <button
                      type="button"
                      onClick={handleToggleVoice}
                      className="p-2 rounded-xl text-zinc-300 hover:text-white bg-black/40 hover:bg-white/[0.08] backdrop-blur-md border border-white/[0.08] hover:border-indigo-400/30 shadow-sm transition-all hover:scale-105 active:scale-95"
                      title="Voice Dictation (Web Speech API)"
                    >
                      <Mic className="w-4 h-4" strokeWidth={1.5} />
                    </button>
                  )}

                  {/* Send Button */}
                  <button
                    type="button"
                    onClick={handleSubmit}
                    disabled={!text.trim() || isLoading}
                    className={`p-2 rounded-xl transition-all ${
                      text.trim() && !isLoading
                        ? 'bg-gradient-to-br from-indigo-500 to-indigo-600 hover:from-indigo-400 hover:to-indigo-500 text-white shadow-[0_0_20px_rgba(99,102,241,0.4)] border border-indigo-400/40 hover:scale-105 active:scale-95'
                        : 'bg-white/[0.03] text-zinc-600 border border-white/[0.04] cursor-not-allowed'
                    }`}
                    title="Send Query"
                  >
                    <ArrowUp className="w-4 h-4" strokeWidth={1.5} />
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
