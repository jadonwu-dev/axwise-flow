'use client';

import React from 'react';
import { RoadmapPhase } from '@/lib/roadmapData';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ArrowLeft, ArrowRight, Calendar, DollarSign, Target, TrendingUp, CheckCircle } from 'lucide-react';

interface PhaseDetailProps {
  phase: RoadmapPhase;
  phaseIndex: number;
  onBack: () => void;
  onNavigate: (direction: 'prev' | 'next') => void;
  hasNext: boolean;
  hasPrev: boolean;
}

export const PhaseDetail: React.FC<PhaseDetailProps> = ({
  phase,
  phaseIndex,
  onBack,
  onNavigate,
  hasNext,
  hasPrev
}) => {
  return (
    <div className="p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <Button variant="outline" onClick={onBack} className="flex items-center gap-2">
          <ArrowLeft className="w-4 h-4" />
          Back to Timeline
        </Button>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <span>Phase {phaseIndex + 1} of 4</span>
            <div className="flex gap-1">
              {[0, 1, 2, 3].map((index) => (
                <div
                  key={index}
                  className={`w-2 h-2 rounded-full ${
                    index === phaseIndex
                      ? 'bg-primary'
                      : index < phaseIndex
                        ? 'bg-primary/50'
                        : 'bg-muted'
                  }`}
                />
              ))}
            </div>
          </div>
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => onNavigate('prev')}
              disabled={!hasPrev}
              className="flex items-center gap-1"
            >
              <ArrowLeft className="w-3 h-3" />
              Previous
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => onNavigate('next')}
              disabled={!hasNext}
              className="flex items-center gap-1"
            >
              Next
              <ArrowRight className="w-3 h-3" />
            </Button>
          </div>
        </div>
      </div>

      {/* Phase Overview */}
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center border-2 border-primary/20">
            <span className="font-bold text-primary">{phaseIndex + 1}</span>
          </div>
          <div>
            <h1 className="text-3xl font-bold text-foreground">{phase.title}</h1>
            <div className="flex items-center gap-4 mt-2">
              <Badge variant="secondary" className="flex items-center gap-1">
                <Calendar className="w-3 h-3" />
                {phase.timeframe}
              </Badge>
              <Badge variant="outline" className="flex items-center gap-1">
                <DollarSign className="w-3 h-3" />
                Funding Phase
              </Badge>
            </div>
          </div>
        </div>

        <p className="text-lg text-muted-foreground mb-4">{phase.narrative}</p>

        <div className="bg-primary/5 border border-primary/20 rounded-lg p-4">
          <h3 className="font-semibold text-primary mb-2 flex items-center gap-2">
            <DollarSign className="w-4 h-4" />
            Cash Flow Context
          </h3>
          <p className="text-sm text-muted-foreground">{phase.cashFlowContext}</p>
        </div>
      </div>

      {/* Key Goals */}
      <Card className="mb-8">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Target className="w-5 h-5" />
            Key Goals
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {phase.keyGoals.map((goal, index) => (
              <div key={index} className="flex items-start gap-3 p-3 bg-muted/30 rounded-lg">
                <CheckCircle className="w-5 h-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-sm">{goal}</span>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Monthly Epics & Objectives */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="w-5 h-5" />
            Monthly Epics & Objectives
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-8">
            {phase.monthlyEpics.map((monthlyEpic, index) => (
              <div key={index} className="border-l-2 border-primary/20 pl-6 relative">
                <div className="absolute -left-2 top-0 w-4 h-4 rounded-full bg-primary/20 border-2 border-background"></div>

                <div className="mb-6">
                  <h3 className="text-xl font-bold text-foreground mb-2">{monthlyEpic.month}</h3>
                  <div className="bg-primary/10 rounded-lg p-4 mb-4">
                    <h4 className="font-semibold text-primary mb-2">Epic:</h4>
                    <p className="text-foreground">{monthlyEpic.epic}</p>
                  </div>
                  <Badge variant="outline" className="text-xs">{monthlyEpic.objectives.length} objectives</Badge>
                </div>

                <div className="space-y-3">
                  {monthlyEpic.objectives.map((objective, objIndex) => (
                    <div key={objIndex} className="bg-muted/30 rounded-lg p-4">
                      <div className="flex items-start justify-between mb-2">
                        <Badge
                          variant="secondary"
                          className={`text-xs ${
                            objective.type === 'SaaS Product Development' ? 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200' :
                            objective.type === 'Open-Source Core Development' ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' :
                            'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200'
                          }`}
                        >
                          {objective.type}
                        </Badge>
                      </div>
                      <p className="text-sm text-muted-foreground">{objective.description}</p>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
