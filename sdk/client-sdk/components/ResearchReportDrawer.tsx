'use client';

import React, { useState } from 'react';
import { Sparkles, X, Check, AlertCircle, ShoppingBag, ShieldCheck, Award } from 'lucide-react';

interface ResearchReportDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  report: any | null;
  onAddToCart?: (productId: string, variantId: string) => void;
}

export const ResearchReportDrawer: React.FC<ResearchReportDrawerProps> = ({
  isOpen,
  onClose,
  report,
  onAddToCart,
}) => {
  const [selectedSize, setSelectedSize] = useState<string>('10');

  if (!isOpen || !report) return null;

  const top = report.top_product;
  const runner = report.runner_up;
  const availableSizes = ['8', '8.5', '9', '9.5', '10', '10.5', '11'];

  return (
    <div className="fixed inset-0 z-50 overflow-hidden font-sans">
      {/* Backdrop */}
      <div
        onClick={onClose}
        className="absolute inset-0 bg-black/75 backdrop-blur-sm transition-opacity"
      />

      <div className="fixed inset-y-0 right-0 max-w-full flex pl-10">
        <div className="w-screen max-w-md border-l border-zinc-800 bg-zinc-950/95 flex flex-col shadow-2xl">
          {/* Header */}
          <div className="p-5 border-b border-zinc-800 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-2xl bg-gradient-to-tr from-purple-500 to-indigo-500 text-white flex items-center justify-center shadow-lg shadow-indigo-500/30">
                <Sparkles className="w-5 h-5 animate-pulse" />
              </div>
              <div>
                <h3 className="font-extrabold text-base text-white">Deep Research Analysis</h3>
                <p className="text-xs text-zinc-400">Biomechanical fit & multi-constraint synthesis</p>
              </div>
            </div>
            <button
              onClick={onClose}
              className="w-8 h-8 rounded-full bg-zinc-800 hover:bg-zinc-700 text-zinc-400 hover:text-white flex items-center justify-center transition-colors"
            >
              <X className="w-4 h-4" />
            </button>
          </div>

          {/* Content */}
          <div className="flex-1 overflow-y-auto p-5 space-y-6">
            {/* Top Match Card */}
            {top && (
              <div className="rounded-3xl p-5 border-2 border-indigo-500/40 bg-indigo-950/20 space-y-4 shadow-xl relative overflow-hidden">
                <div className="flex items-center justify-between">
                  <span className="px-3 py-1 rounded-full bg-indigo-500 text-white text-[11px] font-extrabold flex items-center gap-1 shadow-md shadow-indigo-500/30">
                    <Award className="w-3.5 h-3.5" />
                    <span>Top Pick: {top.match_score}% Match</span>
                  </span>
                  <span className="text-base font-extrabold text-white">
                    ₹{top.price?.toLocaleString('en-IN')}
                  </span>
                </div>

                <div>
                  <h4 className="font-extrabold text-lg text-white">{top.title}</h4>
                  <p className="text-xs text-zinc-300 mt-1 leading-relaxed">{top.reasoning}</p>
                </div>

                {/* Interactive Size Pill Selector */}
                <div className="space-y-1.5 pt-1">
                  <div className="flex items-center justify-between text-[11px]">
                    <span className="font-medium text-zinc-400">Select UK Size:</span>
                    <span className="text-indigo-400 font-semibold">Size {selectedSize} recommended</span>
                  </div>
                  <div className="flex flex-wrap gap-1.5">
                    {availableSizes.map((sz) => (
                      <button
                        key={sz}
                        onClick={() => setSelectedSize(sz)}
                        className={`px-2.5 py-1 rounded-lg text-xs font-bold transition-all ${
                          selectedSize === sz
                            ? 'bg-indigo-600 text-white shadow-md ring-2 ring-indigo-400'
                            : 'bg-zinc-800 text-zinc-300 hover:bg-zinc-700'
                        }`}
                      >
                        UK {sz}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Strengths / Tradeoffs */}
                <div className="space-y-2 pt-2 border-t border-indigo-500/20">
                  {top.strengths?.map((str: string, i: number) => (
                    <div key={i} className="flex items-start gap-2 text-xs text-emerald-400">
                      <Check className="w-4 h-4 shrink-0 mt-0.5" />
                      <span>{str}</span>
                    </div>
                  ))}
                  {top.tradeoffs?.map((tr: string, i: number) => (
                    <div key={i} className="flex items-start gap-2 text-xs text-amber-400">
                      <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
                      <span>{tr}</span>
                    </div>
                  ))}
                </div>

                <button
                  onClick={() => onAddToCart?.(top.id, `var_${top.id}_${selectedSize}`)}
                  className="w-full py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 font-bold text-white text-xs flex items-center justify-center gap-2 transition-all shadow-lg shadow-indigo-600/30"
                >
                  <ShoppingBag className="w-4 h-4" />
                  <span>Add Recommended Pair to Cart</span>
                </button>
              </div>
            )}

            {/* 🌲 Specialized AI Sub-Agent Council Breakdown (Prime Architecture) */}
            {report.subagent_council && report.subagent_council.length > 0 && (
              <div className="space-y-3 pt-2">
                <div className="flex items-center gap-2 text-xs font-extrabold text-indigo-300 uppercase tracking-wider">
                  <ShieldCheck className="w-4 h-4 text-indigo-400" />
                  <span>AI Specialist Council Evaluations</span>
                </div>
                <div className="space-y-2.5">
                  {report.subagent_council.map((sub: any, idx: number) => (
                    <div
                      key={idx}
                      className="p-3.5 rounded-2xl bg-zinc-900/60 border border-indigo-500/20 space-y-1.5 shadow-sm"
                    >
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-bold text-white flex items-center gap-1.5">
                          {sub.role_name}
                        </span>
                        <span className="px-2 py-0.5 rounded-md bg-indigo-500/20 text-[10px] font-extrabold text-indigo-300">
                          {sub.confidence_score}% Conf.
                        </span>
                      </div>
                      <p className="text-xs text-zinc-300 leading-relaxed italic">"{sub.verdict}"</p>
                      {sub.badges && sub.badges.length > 0 && (
                        <div className="flex flex-wrap gap-1 pt-1">
                          {sub.badges.map((b: string, bIdx: number) => (
                            <span
                              key={bIdx}
                              className="px-1.5 py-0.5 rounded bg-zinc-800 text-[9px] font-semibold text-zinc-400"
                            >
                              🏷️ {b}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Runner-Up Match Card */}
            {runner && (
              <div className="rounded-3xl p-5 border border-zinc-800 bg-zinc-900/40 space-y-3 shadow-lg">
                <div className="flex items-center justify-between">
                  <span className="px-2.5 py-1 rounded-full bg-zinc-800 text-zinc-300 text-[10px] font-bold">
                    Alternative: {runner.match_score}% Match
                  </span>
                  <span className="text-sm font-bold text-zinc-200">
                    ₹{runner.price?.toLocaleString('en-IN')}
                  </span>
                </div>
                <div>
                  <h4 className="font-bold text-sm text-white">{runner.title}</h4>
                  <p className="text-xs text-zinc-400 mt-1 leading-relaxed">{runner.reasoning}</p>
                </div>
                <div className="space-y-1.5 pt-1 border-t border-zinc-800">
                  {runner.strengths?.map((str: string, i: number) => (
                    <div key={i} className="flex items-start gap-2 text-xs text-zinc-400">
                      <Check className="w-3.5 h-3.5 text-zinc-500 shrink-0 mt-0.5" />
                      <span>{str}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
