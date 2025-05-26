'use client';

import React from 'react';
import { RoadmapPhase } from '@/lib/roadmapData';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { ArrowRight, Calendar, Target } from 'lucide-react';

interface PhaseTimelineProps {
  phases: RoadmapPhase[];
  onPhaseSelect: (phaseIndex: number) => void;
}

export const PhaseTimeline: React.FC<PhaseTimelineProps> = ({ phases, onPhaseSelect }) => {
  return (
    <div className="p-6">
      <div className="space-y-8">
        {phases.map((phase, index) => (
          <div key={index} className="relative">
            {/* Timeline connector */}
            {index < phases.length - 1 && (
              <div className="absolute left-6 top-16 w-0.5 h-24 bg-primary/20"></div>
            )}

            <div className="flex items-start gap-6">
              {/* Phase indicator */}
              <div className="flex-shrink-0 w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center border-2 border-primary/20">
                <span className="text-sm font-bold text-primary">{index + 1}</span>
              </div>

              {/* Phase content */}
              <div className="flex-1 bg-muted/30 rounded-lg p-6 hover:bg-muted/50 transition-colors">
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <h3 className="text-xl font-semibold text-foreground mb-2">{phase.title}</h3>
                    <div className="flex items-center gap-4 text-sm text-muted-foreground">
                      <div className="flex items-center gap-1">
                        <Calendar className="w-4 h-4" />
                        <span>{phase.timeframe}</span>
                      </div>
                    </div>
                  </div>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => onPhaseSelect(index)}
                    className="flex items-center gap-2"
                  >
                    View Details
                    <ArrowRight className="w-4 h-4" />
                  </Button>
                </div>

                <p className="text-muted-foreground mb-4 line-clamp-3">
                  {phase.narrative}
                </p>

                <div className="mb-4">
                  <h4 className="font-medium text-foreground mb-2 flex items-center gap-2">
                    <Target className="w-4 h-4" />
                    Key Goals
                  </h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                    {phase.keyGoals.slice(0, 4).map((goal, goalIndex) => (
                      <div key={goalIndex} className="flex items-start gap-2 text-sm">
                        <div className="w-1.5 h-1.5 rounded-full bg-primary mt-2 flex-shrink-0"></div>
                        <span className="text-muted-foreground">{goal}</span>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <Badge variant="secondary" className="text-xs">
                    {phase.cashFlowContext.includes('100K') ? '€100K Pre-seed' :
                     phase.cashFlowContext.includes('750K') ? '€750K Seed' :
                     'Growth Phase'}
                  </Badge>
                  <Badge variant="outline" className="text-xs">
                    {phase.monthlyEpics.length} monthly epics planned
                  </Badge>
                </div>
              </div>
            </div>
          </div>
        ))}

        {/* Roadmap Continuation Indicator */}
        <div className="relative">
          <div className="absolute left-6 top-0 w-0.5 h-8 bg-primary/20"></div>
          <div className="flex items-start gap-6">
            <div className="flex-shrink-0 w-12 h-12 rounded-full bg-gradient-to-r from-primary/20 to-accent/20 flex items-center justify-center border-2 border-dashed border-primary/30">
              <Target className="w-5 h-5 text-primary/60" />
            </div>
            <div className="flex-1 bg-gradient-to-r from-muted/20 to-muted/10 rounded-lg p-6 border border-dashed border-primary/20">
              <div className="text-center">
                <h3 className="text-lg font-semibold text-foreground mb-2">Roadmap Continues...</h3>
                <p className="text-sm text-muted-foreground mb-3">
                  Our development roadmap extends beyond these phases, with continuous innovation
                  and feature development planned as we scale towards market leadership.
                </p>
                <div className="flex items-center justify-center gap-2 text-xs text-muted-foreground">
                  <span>Future phases include Series A funding, international expansion, and advanced AI features</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
