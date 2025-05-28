'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Lightbulb, ArrowRight } from 'lucide-react';

interface AutoSuggestion {
  id: string;
  text: string;
  category: 'business_type' | 'target_customer' | 'problem' | 'solution' | 'stage';
  context?: string;
}

interface AutoSuggestionsProps {
  conversationContext: string;
  currentStage: 'initial' | 'business_idea' | 'target_customer' | 'problem_validation' | 'solution_validation';
  onSuggestionClick: (suggestion: string) => void;
  className?: string;
}

const SUGGESTION_TEMPLATES = {
  initial: [
    { id: '1', text: 'I have a business idea', category: 'business_type' as const },
    { id: '2', text: 'I want to decide about one feature', category: 'business_type' as const },
    { id: '3', text: 'I have a mobile app idea', category: 'business_type' as const },
    { id: '4', text: 'I have a SaaS product idea', category: 'business_type' as const },
    { id: '5', text: 'I want to start a service business', category: 'business_type' as const },
    { id: '6', text: 'I have a physical product idea', category: 'business_type' as const },
    { id: '7', text: 'I need help with customer research', category: 'business_type' as const },
    { id: '8', text: 'I want to validate my idea', category: 'business_type' as const },
  ],
  business_idea: [
    { id: '5', text: 'Small business owners', category: 'target_customer' as const },
    { id: '6', text: 'Busy professionals', category: 'target_customer' as const },
    { id: '7', text: 'Students and educators', category: 'target_customer' as const },
    { id: '8', text: 'Parents with young children', category: 'target_customer' as const },
    { id: '9', text: 'Healthcare professionals', category: 'target_customer' as const },
  ],
  target_customer: [
    { id: '10', text: 'They waste too much time on manual tasks', category: 'problem' as const },
    { id: '11', text: 'Current solutions are too expensive', category: 'problem' as const },
    { id: '12', text: 'They struggle with organization', category: 'problem' as const },
    { id: '13', text: 'Communication between teams is difficult', category: 'problem' as const },
  ],
  problem_validation: [
    { id: '14', text: 'Yes, I\'ve talked to a few people', category: 'stage' as const },
    { id: '15', text: 'No, I haven\'t done any research yet', category: 'stage' as const },
    { id: '16', text: 'I\'ve done some online research', category: 'stage' as const },
  ],
  solution_validation: [
    { id: '17', text: 'I have a working prototype', category: 'stage' as const },
    { id: '18', text: 'I have detailed mockups', category: 'stage' as const },
    { id: '19', text: 'It\'s still just an idea', category: 'stage' as const },
  ],
};

const DYNAMIC_SUGGESTIONS = {
  business_types: [
    'mobile app', 'web application', 'SaaS platform', 'e-commerce store',
    'consulting service', 'online course', 'subscription service', 'marketplace'
  ],
  industries: [
    'healthcare', 'education', 'finance', 'retail', 'manufacturing',
    'real estate', 'food & beverage', 'fitness', 'travel', 'entertainment'
  ],
  customer_types: [
    'small business owners', 'enterprise companies', 'freelancers', 'students',
    'parents', 'seniors', 'professionals', 'entrepreneurs', 'developers'
  ],
  problems: [
    'save time', 'reduce costs', 'improve communication', 'increase productivity',
    'better organization', 'automate processes', 'improve customer service'
  ]
};

export function AutoSuggestions({
  conversationContext,
  currentStage,
  onSuggestionClick,
  className = ''
}: AutoSuggestionsProps) {
  const [suggestions, setSuggestions] = useState<AutoSuggestion[]>([]);
  const [isVisible, setIsVisible] = useState(true);

  useEffect(() => {
    generateSuggestions();
  }, [conversationContext, currentStage]);

  const generateSuggestions = () => {
    let newSuggestions: AutoSuggestion[] = [];

    // Get base suggestions for current stage
    const baseSuggestions = SUGGESTION_TEMPLATES[currentStage] || [];
    newSuggestions = [...baseSuggestions];

    // Add dynamic suggestions based on context
    const contextLower = conversationContext.toLowerCase();

    // If they mentioned an industry, suggest related customer types
    Object.entries(DYNAMIC_SUGGESTIONS.industries).forEach(([_, industry]) => {
      if (contextLower.includes(industry)) {
        newSuggestions.push({
          id: `dynamic_${industry}`,
          text: `${industry} professionals`,
          category: 'target_customer',
          context: `Based on your ${industry} focus`
        });
      }
    });

    // If they mentioned a business type, suggest common problems
    if (contextLower.includes('app') || contextLower.includes('software')) {
      newSuggestions.push(
        {
          id: 'dynamic_app_1',
          text: 'Current apps are too complicated to use',
          category: 'problem',
          context: 'Common app-related problem'
        },
        {
          id: 'dynamic_app_2',
          text: 'Existing solutions don\'t integrate well',
          category: 'problem',
          context: 'Common integration issue'
        }
      );
    }

    // Limit to 6 suggestions and shuffle
    const shuffled = newSuggestions.sort(() => 0.5 - Math.random());
    setSuggestions(shuffled.slice(0, 6));
  };

  const handleSuggestionClick = (suggestion: AutoSuggestion) => {
    onSuggestionClick(suggestion.text);
    // Hide suggestions briefly after click
    setIsVisible(false);
    setTimeout(() => setIsVisible(true), 1000);
  };

  if (!isVisible || suggestions.length === 0) {
    return null;
  }

  const getCategoryColor = (category: string) => {
    switch (category) {
      case 'business_type': return 'bg-blue-100 text-blue-800';
      case 'target_customer': return 'bg-green-100 text-green-800';
      case 'problem': return 'bg-orange-100 text-orange-800';
      case 'solution': return 'bg-purple-100 text-purple-800';
      case 'stage': return 'bg-gray-100 text-gray-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  // Check if this is inline suggestions
  const isInline = className?.includes('inline-suggestions');

  if (isInline) {
    return (
      <div className="mt-2">
        <div className="flex items-center gap-2 mb-2">
          <Lightbulb className="h-3 w-3 text-yellow-600" />
          <span className="text-xs text-gray-600">Quick replies:</span>
        </div>
        <div className="flex flex-wrap gap-2">
          {suggestions.slice(0, 3).map((suggestion) => (
            <Button
              key={suggestion.id}
              variant="outline"
              size="sm"
              className="h-auto py-1 px-2 text-xs hover:bg-blue-50 hover:border-blue-300"
              onClick={() => handleSuggestionClick(suggestion)}
            >
              {suggestion.text}
            </Button>
          ))}
        </div>
      </div>
    );
  }

  return (
    <Card className={`p-4 ${className}`}>
      <div className="flex items-center gap-2 mb-3">
        <Lightbulb className="h-4 w-4 text-yellow-600" />
        <span className="text-sm font-medium text-gray-700">Quick suggestions</span>
      </div>

      <div className="grid grid-cols-1 gap-2">
        {suggestions.map((suggestion) => (
          <Button
            key={suggestion.id}
            variant="ghost"
            className="justify-start h-auto p-3 text-left hover:bg-gray-50"
            onClick={() => handleSuggestionClick(suggestion)}
          >
            <div className="flex items-center justify-between w-full">
              <div className="flex-1">
                <div className="text-sm">{suggestion.text}</div>
                {suggestion.context && (
                  <div className="text-xs text-gray-500 mt-1">{suggestion.context}</div>
                )}
              </div>
              <div className="flex items-center gap-2 ml-2">
                <Badge
                  variant="secondary"
                  className={`text-xs ${getCategoryColor(suggestion.category)}`}
                >
                  {suggestion.category.replace('_', ' ')}
                </Badge>
                <ArrowRight className="h-3 w-3 text-gray-400" />
              </div>
            </div>
          </Button>
        ))}
      </div>

      <div className="mt-3 pt-3 border-t">
        <p className="text-xs text-gray-500">
          💡 Click any suggestion to use it, or type your own response
        </p>
      </div>
    </Card>
  );
}
