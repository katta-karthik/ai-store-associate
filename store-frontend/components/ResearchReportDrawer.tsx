'use client';

import React, { useState } from 'react';
import { Sparkles, X, Check, AlertCircle, ShoppingBag, ShieldCheck, Award } from 'lucide-react';
import { useStore } from '@/store/useStore';

export const ResearchReportDrawer: React.FC = () => {
  const { isResearchReportOpen, toggleResearchReport, researchReport, addToCart } = useStore();
  const [selectedSize, setSelectedSize] = useState<string>('10');

  if (!isResearchReportOpen || !researchReport) return null;

  const top = researchReport.top_product;
  const runner = researchReport.runner_up;

  const availableSizes = ['8', '8.5', '9', '9.5', '10', '10.5', '11'];

  return (
    <div className="fixed inset-0 z-50 overflow-hidden">
      {/* Backdrop */}
      <div
        onClick={toggleResearchReport}
        className="absolute inset-0 bg-black/75 backdrop-blur-sm transition-opacity"
      />

      <div className="fixed inset-y-0 right-0 max-w-full flex pl-10">
        <div className="w-screen max-w-md glass-panel border-l border-surface-border bg-surface/95 flex flex-col shadow-2xl animate-slide-up">
          {/* Header */}
          <div className="p-5 border-b border-surface-border flex items-center justify-between">
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
              onClick={toggleResearchReport}
              className="w-8 h-8 rounded-full bg-zinc-800 hover:bg-zinc-700 text-zinc-400 hover:text-white flex items-center justify-center transition-colors"
            >
              <X className="w-4 h-4" />
            </button>
          </div>

          {/* Content */}
          <div className="flex-1 overflow-y-auto p-5 space-y-6">
            {/* Top Match Card */}
            {top && (
              <div className="glass-panel rounded-3xl p-5 border-2 border-indigo-500/40 bg-indigo-950/20 space-y-4 shadow-xl relative overflow-hidden">
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
                  <h4 className="text-base font-extrabold text-white">{top.title}</h4>
                  <span className="text-xs text-indigo-400 font-semibold">{top.brand}</span>
                </div>

                {/* Badges */}
                {top.badges && top.badges.length > 0 && (
                  <div className="flex flex-wrap gap-1.5">
                    {top.badges.map((b: string, idx: number) => (
                      <span
                        key={idx}
                        className="px-2 py-0.5 rounded-lg bg-indigo-500/20 border border-indigo-500/30 text-[10px] font-bold text-indigo-300"
                      >
                        ✓ {b}
                      </span>
                    ))}
                  </div>
                )}

                {/* Pros */}
                <div className="space-y-1.5 pt-2 border-t border-indigo-500/20 text-xs text-zinc-300">
                  <span className="font-bold text-zinc-200 block">Why it fits your goals:</span>
                  {top.pros?.map((pro: string, idx: number) => (
                    <div key={idx} className="flex items-start gap-2">
                      <Check className="w-3.5 h-3.5 text-emerald-400 flex-shrink-0 mt-0.5" />
                      <span>{pro}</span>
                    </div>
                  ))}
                </div>

                {/* Trade-offs */}
                {top.tradeoffs && top.tradeoffs.length > 0 && (
                  <div className="space-y-1.5 pt-2 border-t border-indigo-500/20 text-xs text-amber-300/90">
                    <span className="font-bold block text-amber-300">Salesperson Trade-off:</span>
                    {top.tradeoffs.map((t: string, idx: number) => (
                      <div key={idx} className="flex items-start gap-2">
                        <AlertCircle className="w-3.5 h-3.5 text-amber-400 flex-shrink-0 mt-0.5" />
                        <span>{t}</span>
                      </div>
                    ))}
                  </div>
                )}

                {/* Size Selector */}
                <div className="pt-2 border-t border-indigo-500/20 space-y-1.5">
                  <span className="text-[10px] font-semibold text-zinc-300 uppercase">Choose Your Size (UK):</span>
                  <div className="flex flex-wrap gap-1.5">
                    {availableSizes.map((s) => (
                      <button
                        key={s}
                        onClick={() => setSelectedSize(s)}
                        className={`px-2.5 py-1 rounded-lg text-xs font-bold transition-all ${
                          selectedSize === s
                            ? 'bg-primary text-white shadow-sm shadow-primary-glow border border-primary'
                            : 'bg-zinc-800 text-zinc-300 border border-zinc-700 hover:border-zinc-500'
                        }`}
                      >
                        UK {s}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* Runner-Up Card */}
            {runner && (
              <div className="glass-panel rounded-3xl p-5 border border-surface-border space-y-4">
                <div className="flex items-center justify-between">
                  <span className="px-3 py-1 rounded-full bg-zinc-800 text-zinc-300 text-[11px] font-bold">
                    Hybrid Alternative: {runner.match_score}% Match
                  </span>
                  <span className="text-sm font-bold text-white">
                    ₹{runner.price?.toLocaleString('en-IN')}
                  </span>
                </div>

                <div>
                  <h4 className="text-sm font-bold text-white">{runner.title}</h4>
                  <span className="text-xs text-zinc-400">{runner.brand}</span>
                </div>

                {/* Pros */}
                <div className="space-y-1.5 text-xs text-zinc-300">
                  {runner.pros?.map((pro: string, idx: number) => (
                    <div key={idx} className="flex items-start gap-2">
                      <Check className="w-3.5 h-3.5 text-indigo-400 flex-shrink-0 mt-0.5" />
                      <span>{pro}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Action Footer */}
          {top && (
            <div className="p-5 border-t border-surface-border bg-surface/90">
              <button
                onClick={() => {
                  addToCart(top.product_id, `var_${top.product_id}_size_${selectedSize}`);
                  toggleResearchReport();
                }}
                className="w-full py-3.5 rounded-2xl bg-gradient-to-r from-primary to-accent hover:opacity-95 text-white font-bold text-sm flex items-center justify-center gap-2 shadow-lg shadow-primary-glow active:scale-98 transition-all"
              >
                <ShoppingBag className="w-4 h-4" />
                <span>Add UK {selectedSize} Recommendation to Bag</span>
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
