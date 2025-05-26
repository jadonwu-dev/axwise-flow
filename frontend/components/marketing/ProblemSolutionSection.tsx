import React from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { TrendingDown, Clock, Users, DollarSign } from 'lucide-react';

export const ProblemSolutionSection = () => {
  const problems = [
    {
      icon: DollarSign,
      title: "Research Costs",
      description: "$50K-100K/year researchers",
      detail: "Companies spend massive amounts on user research teams and tools, yet struggle to turn insights into action."
    },
    {
      icon: TrendingDown,
      title: "Insight-to-Action Gap",
      description: "Months between research and implementation",
      detail: "Critical insights get lost in translation between research teams and product development."
    },
    {
      icon: Users,
      title: "Stakeholder Buy-in",
      description: "Difficulty convincing leadership",
      detail: "Research findings often lack the compelling narrative needed to secure resources and alignment."
    },
    {
      icon: Clock,
      title: "Wasted Development",
      description: "$260B/year wasted globally",
      detail: "Products built without proper user validation lead to massive waste in development resources."
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

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-16">
          {problems.map((problem, index) => (
            <Card key={index} className="border-destructive/20 hover:border-destructive/40 transition-colors">
              <CardContent className="p-6 text-center">
                <div className="w-12 h-12 mx-auto mb-4 rounded-full bg-destructive/10 flex items-center justify-center">
                  <problem.icon className="w-6 h-6 text-destructive" />
                </div>
                <h3 className="font-semibold mb-2">{problem.title}</h3>
                <p className="text-sm font-medium text-destructive mb-2">{problem.description}</p>
                <p className="text-xs text-muted-foreground">{problem.detail}</p>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Solution Section */}
        <div className="text-center">
          <Badge variant="default" className="mb-4">The Solution</Badge>
          <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold mb-6">
            How AxWise <span className="text-primary">Simplifies</span> User Research
          </h2>
          <p className="text-lg md:text-xl text-muted-foreground max-w-3xl mx-auto mb-8">
            Transform hours of interviews into actionable insights in minutes. 
            The only input needed is your user interviews!
          </p>
          
          <div className="bg-primary/5 rounded-2xl p-8 md:p-12 border border-primary/20">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8 items-center">
              <div className="text-center">
                <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-primary/10 flex items-center justify-center">
                  <span className="text-2xl font-bold text-primary">1</span>
                </div>
                <h3 className="font-semibold mb-2">Upload Interviews</h3>
                <p className="text-sm text-muted-foreground">Drop your interview files and let AI do the heavy lifting</p>
              </div>
              
              <div className="text-center">
                <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-primary/10 flex items-center justify-center">
                  <span className="text-2xl font-bold text-primary">2</span>
                </div>
                <h3 className="font-semibold mb-2">Get Insights</h3>
                <p className="text-sm text-muted-foreground">Receive structured personas, pain points, and opportunities</p>
              </div>
              
              <div className="text-center">
                <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-primary/10 flex items-center justify-center">
                  <span className="text-2xl font-bold text-primary">3</span>
                </div>
                <h3 className="font-semibold mb-2">Build Products</h3>
                <p className="text-sm text-muted-foreground">Turn insights into PRDs and development plans</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
