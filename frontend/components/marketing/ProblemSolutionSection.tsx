import React from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { TrendingDown, Clock, Users, DollarSign } from 'lucide-react';

export const ProblemSolutionSection = () => {
  const challenges = [
    {
      icon: DollarSign,
      title: "Expensive Research",
      description: "Traditional research costs $50K-100K/year",
      detail: "Most teams can't afford dedicated researchers, leaving them guessing about user needs."
    },
    {
      icon: TrendingDown,
      title: "Slow Validation",
      description: "Months to validate simple assumptions",
      detail: "By the time insights reach development, opportunities are missed and markets have shifted."
    },
    {
      icon: Clock,
      title: "Failed Products",
      description: "$260B/year wasted on unwanted features",
      detail: "Without proper customer validation, teams build products that solve problems nobody has."
    }
  ];

  return (
    <section className="py-16 md:py-24 bg-muted/30">
      <div className="container px-4 md:px-6 mx-auto">
        {/* Problem Section */}
        <div className="text-center mb-16">
          <Badge variant="destructive" className="mb-4">The Problem</Badge>
          <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold mb-6">
            The Bottleneck Between <span className="text-destructive">Conversation</span> and <span className="text-primary">Code</span>
          </h2>
          <p className="text-lg md:text-xl text-muted-foreground max-w-3xl mx-auto">
            Product teams are drowning in user feedback but starving for actionable insights.
            The gap between what users say and what developers build is costing companies billions.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-16">
          {challenges.map((challenge, index) => (
            <Card key={index} className="border-destructive/20 hover:border-destructive/40 transition-colors">
              <CardContent className="p-6 text-center">
                <div className="w-12 h-12 mx-auto mb-4 rounded-full bg-destructive/10 flex items-center justify-center">
                  <challenge.icon className="w-6 h-6 text-destructive" />
                </div>
                <h3 className="font-semibold mb-2">{challenge.title}</h3>
                <p className="text-sm font-medium text-destructive mb-2">{challenge.description}</p>
                <p className="text-xs text-muted-foreground">{challenge.detail}</p>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Solution Section */}
        <div className="text-center">
          <Badge variant="default" className="mb-4">The Solution</Badge>
          <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold mb-6">
            Complete Research & Development Platform in <span className="text-primary">One Place</span>
          </h2>
          <p className="text-lg md:text-xl text-muted-foreground max-w-3xl mx-auto mb-8">
            From idea validation to product launch: Generate research questions, analyze customer interviews,
            and create comprehensive PRDs—all powered by AI.
          </p>

          <div className="bg-primary/5 rounded-2xl p-8 md:p-12 border border-primary/20">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 items-center">
              <div className="text-center">
                <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-primary/10 flex items-center justify-center">
                  <span className="text-2xl font-bold text-primary">1</span>
                </div>
                <h3 className="font-semibold mb-2">Generate Research Questions</h3>
                <p className="text-sm text-muted-foreground">AI creates custom questions for your idea</p>
              </div>

              <div className="text-center">
                <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-primary/10 flex items-center justify-center">
                  <span className="text-2xl font-bold text-primary">2</span>
                </div>
                <h3 className="font-semibold mb-2">Conduct Research / Get AI Personas</h3>
                <p className="text-sm text-muted-foreground">Real interviews or AI-generated responses</p>
              </div>

              <div className="text-center">
                <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-primary/10 flex items-center justify-center">
                  <span className="text-2xl font-bold text-primary">3</span>
                </div>
                <h3 className="font-semibold mb-2">Automatic Interview Analysis</h3>
                <p className="text-sm text-muted-foreground">AI extracts insights & patterns</p>
              </div>

              <div className="text-center">
                <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-primary/10 flex items-center justify-center">
                  <span className="text-2xl font-bold text-primary">4</span>
                </div>
                <h3 className="font-semibold mb-2">Get Fully-Fledged PRDs</h3>
                <p className="text-sm text-muted-foreground">Complete product requirements ready to build</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
