'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import {
  Target,
  CheckCircle,
  Download,
  FileText,
  ArrowRight
} from 'lucide-react';

interface ResearchContext {
  businessIdea?: string;
  targetCustomer?: string;
  problem?: string;
  stage?: string;
  questionsGenerated?: boolean;
  completionPercentage?: number;
  multiStakeholderConsidered?: boolean;
  multiStakeholderDetected?: boolean;
  detectedStakeholders?: {
    primary: (string | { name: string; description: string })[];
    secondary: (string | { name: string; description: string })[];
    industry?: string;
  };
}

interface GeneratedQuestions {
  problemDiscovery?: string[];
  solutionValidation?: string[];
  followUp?: string[];
}

interface ContextPanelProps {
  context: ResearchContext;
  questions?: GeneratedQuestions;
  onExport?: () => void;
  onContinueToAnalysis?: () => void;
}

export function ContextPanel({
  context,
  questions,
  onExport,
  onContinueToAnalysis
}: ContextPanelProps) {
  const getCompletionPercentage = () => {
    let completed = 0;
    const total = 4;

    if (context.businessIdea) completed++;
    if (context.targetCustomer) completed++;
    if (context.problem) completed++;
    if (context.questionsGenerated) completed++;

    return Math.round((completed / total) * 100);
  };

  const completionPercentage = getCompletionPercentage();

  return (
    <div className="space-y-4">
      {/* Progress Card */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-lg flex items-center gap-2">
            <Target className="h-5 w-5 text-primary" />
            Research Progress
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">Completion</span>
              <span className="text-sm font-medium">{completionPercentage}%</span>
            </div>
            <Progress value={completionPercentage} className="h-2" />

            <div className="space-y-3 mt-4">
              <div>
                <div className="flex items-center gap-2 mb-2">
                  <CheckCircle className={`h-4 w-4 ${context.businessIdea ? 'text-green-600 dark:text-green-400' : 'text-muted-foreground'}`} />
                  <span className={`text-sm ${context.businessIdea ? 'text-green-600 dark:text-green-400' : 'text-muted-foreground'}`}>
                    Business idea defined
                  </span>
                </div>
                {context.businessIdea && (
                  <p className="text-xs text-muted-foreground ml-6 bg-muted/50 p-2 rounded">{context.businessIdea}</p>
                )}
              </div>

              <div>
                <div className="flex items-center gap-2 mb-2">
                  <CheckCircle className={`h-4 w-4 ${context.targetCustomer ? 'text-green-600 dark:text-green-400' : 'text-muted-foreground'}`} />
                  <span className={`text-sm ${context.targetCustomer ? 'text-green-600 dark:text-green-400' : 'text-muted-foreground'}`}>
                    Target customer identified
                  </span>
                </div>
                {context.targetCustomer && (
                  <p className="text-xs text-muted-foreground ml-6 bg-muted/50 p-2 rounded">{context.targetCustomer}</p>
                )}
              </div>

              <div>
                <div className="flex items-center gap-2 mb-2">
                  <CheckCircle className={`h-4 w-4 ${context.problem ? 'text-green-600 dark:text-green-400' : 'text-muted-foreground'}`} />
                  <span className={`text-sm ${context.problem ? 'text-green-600 dark:text-green-400' : 'text-muted-foreground'}`}>
                    Problem understood
                  </span>
                </div>
                {context.problem && (
                  <p className="text-xs text-muted-foreground ml-6 bg-muted/50 p-2 rounded">{context.problem}</p>
                )}
              </div>

              <div>
                <div className="flex items-center gap-2 mb-2">
                  <CheckCircle className={`h-4 w-4 ${context.questionsGenerated ? 'text-green-600 dark:text-green-400' : 'text-muted-foreground'}`} />
                  <span className={`text-sm ${context.questionsGenerated ? 'text-green-600 dark:text-green-400' : 'text-muted-foreground'}`}>
                    Questions generated
                  </span>
                </div>
                {context.questionsGenerated && (
                  <p className="text-xs text-muted-foreground ml-6 bg-muted/50 p-2 rounded">Research questions have been generated and confirmed in chat</p>
                )}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Questions Summary */}
      {questions && (
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-lg flex items-center gap-2">
              <FileText className="h-5 w-5 text-green-600 dark:text-green-400" />
              Generated Questions
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid gap-3">
              <div>
                <Badge variant="outline" className="mb-2">Problem Discovery</Badge>
                <p className="text-sm text-muted-foreground">
                  {questions.problemDiscovery?.length || 0} questions to understand current challenges
                </p>
              </div>
              <div>
                <Badge variant="outline" className="mb-2">Solution Validation</Badge>
                <p className="text-sm text-muted-foreground">
                  {questions.solutionValidation?.length || 0} questions to validate your solution approach
                </p>
              </div>
              <div>
                <Badge variant="outline" className="mb-2">Follow-up</Badge>
                <p className="text-sm text-muted-foreground">
                  {questions.followUp?.length || 0} questions for deeper insights
                </p>
              </div>
            </div>

            <div className="flex gap-2 pt-2">
              {onExport && (
                <Button variant="outline" size="sm" onClick={onExport} className="flex-1">
                  <Download className="h-4 w-4 mr-2" />
                  Export
                </Button>
              )}
              {onContinueToAnalysis && (
                <Button size="sm" onClick={onContinueToAnalysis} className="flex-1">
                  <ArrowRight className="h-4 w-4 mr-2" />
                  Continue
                </Button>
              )}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
