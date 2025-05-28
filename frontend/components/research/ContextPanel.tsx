'use client';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import {
  Target,
  Users,
  Lightbulb,
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
            <Target className="h-5 w-5 text-blue-600" />
            Research Progress
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Completion</span>
              <span className="text-sm font-medium">{completionPercentage}%</span>
            </div>
            <Progress value={completionPercentage} className="h-2" />

            <div className="space-y-2 mt-4">
              <div className="flex items-center gap-2">
                <CheckCircle className={`h-4 w-4 ${context.businessIdea ? 'text-green-600' : 'text-gray-300'}`} />
                <span className={`text-sm ${context.businessIdea ? 'text-green-600' : 'text-gray-500'}`}>
                  Business idea defined
                </span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle className={`h-4 w-4 ${context.targetCustomer ? 'text-green-600' : 'text-gray-300'}`} />
                <span className={`text-sm ${context.targetCustomer ? 'text-green-600' : 'text-gray-500'}`}>
                  Potential Target customer identified
                </span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle className={`h-4 w-4 ${context.problem ? 'text-green-600' : 'text-gray-300'}`} />
                <span className={`text-sm ${context.problem ? 'text-green-600' : 'text-gray-500'}`}>
                  Problem understood
                </span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle className={`h-4 w-4 ${context.questionsGenerated ? 'text-green-600' : 'text-gray-300'}`} />
                <span className={`text-sm ${context.questionsGenerated ? 'text-green-600' : 'text-gray-500'}`}>
                  Questions generated
                </span>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Context Summary */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-lg flex items-center gap-2">
            <Lightbulb className="h-5 w-5 text-yellow-600" />
            Your Research Context
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <CheckCircle className={`h-4 w-4 ${context.businessIdea ? 'text-green-600' : 'text-gray-300'}`} />
              <Badge variant="outline" className={context.businessIdea ? 'border-green-600 text-green-600' : ''}>
                Business idea defined
              </Badge>
            </div>
            {context.businessIdea && (
              <p className="text-sm text-gray-700 ml-6">{context.businessIdea}</p>
            )}
          </div>

          <div>
            <div className="flex items-center gap-2 mb-2">
              <CheckCircle className={`h-4 w-4 ${context.targetCustomer ? 'text-green-600' : 'text-gray-300'}`} />
              <Badge variant="outline" className={context.targetCustomer ? 'border-green-600 text-green-600' : ''}>
                Potential Target customer identified
              </Badge>
            </div>
            {context.targetCustomer && (
              <p className="text-sm text-gray-700 ml-6">{context.targetCustomer}</p>
            )}
          </div>

          <div>
            <div className="flex items-center gap-2 mb-2">
              <CheckCircle className={`h-4 w-4 ${context.problem ? 'text-green-600' : 'text-gray-300'}`} />
              <Badge variant="outline" className={context.problem ? 'border-green-600 text-green-600' : ''}>
                Problem understood
              </Badge>
            </div>
            {context.problem && (
              <p className="text-sm text-gray-700 ml-6">{context.problem}</p>
            )}
          </div>

          <div>
            <div className="flex items-center gap-2 mb-2">
              <CheckCircle className={`h-4 w-4 ${context.questionsGenerated ? 'text-green-600' : 'text-gray-300'}`} />
              <Badge variant="outline" className={context.questionsGenerated ? 'border-green-600 text-green-600' : ''}>
                Questions generated
              </Badge>
            </div>
            {context.questionsGenerated && (
              <p className="text-sm text-gray-700 ml-6">Research questions have been generated and confirmed in chat</p>
            )}
          </div>

          <div>
            <div className="flex items-center gap-2 mb-2">
              <CheckCircle className={`h-4 w-4 ${context.multiStakeholderConsidered ? 'text-green-600' : 'text-gray-300'}`} />
              <Badge variant="outline" className={context.multiStakeholderConsidered ? 'border-green-600 text-green-600' : ''}>
                Multi-stakeholder approach considered
              </Badge>
            </div>
            {context.multiStakeholderConsidered && (
              <p className="text-sm text-gray-700 ml-6">Strategic research approach for multiple user groups reviewed</p>
            )}
          </div>
        </CardContent>
      </Card>




    </div>
  );
}
