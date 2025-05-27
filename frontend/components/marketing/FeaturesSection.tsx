import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Brain, Palette, Zap, Shield, BarChart3, FileText } from 'lucide-react';

export const FeaturesSection = () => {
  const features = [
    {
      icon: Brain,
      title: "Advanced AI Analysis",
      description: "Powered by cutting-edge LLMs to extract deep insights from unstructured interview data",
      benefits: ["Pattern recognition", "Sentiment analysis", "Automated categorization"]
    },
    {
      icon: Palette,
      title: "Intuitive UI",
      description: "Clean, user-friendly interface designed for product managers and researchers",
      benefits: ["Drag & drop uploads", "Visual insights", "Export capabilities"]
    },
    {
      icon: Zap,
      title: "API-First Architecture",
      description: "Seamlessly integrate with your existing workflow and tools",
      benefits: ["REST API access", "Webhook support", "Custom integrations"]
    },
    {
      icon: BarChart3,
      title: "Rich Visualizations",
      description: "Transform complex data into clear, actionable visual insights",
      benefits: ["Interactive charts", "Persona mapping", "Trend analysis"]
    },
    {
      icon: FileText,
      title: "Automated Documentation",
      description: "Generate comprehensive reports and PRDs from your research",
      benefits: ["PRD generation", "Executive summaries", "Action plans"]
    },
    {
      icon: Shield,
      title: "Enterprise Security",
      description: "Bank-grade security to protect your sensitive research data",
      benefits: ["End-to-end encryption", "SOC 2 in progress", "Data residency"]
    }
  ];

  return (
    <section className="py-16 md:py-24">
      <div className="container px-4 md:px-6 mx-auto">
        <div className="text-center mb-16">
          <Badge variant="default" className="mb-4">Features</Badge>
          <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold mb-6">
            Everything You Need to <span className="text-primary">Transform</span> Research into Results
          </h2>
          <p className="text-lg md:text-xl text-muted-foreground max-w-3xl mx-auto">
            AxWise combines powerful AI with intuitive design to make user research analysis
            faster, deeper, and more actionable than ever before.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature, index) => (
            <Card key={index} className="border-primary/20 hover:border-primary/40 transition-all duration-300 hover:shadow-lg">
              <CardHeader>
                <div className="w-12 h-12 mb-4 rounded-full bg-primary/10 flex items-center justify-center">
                  <feature.icon className="w-6 h-6 text-primary" />
                </div>
                <CardTitle className="text-xl">{feature.title}</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground mb-4">{feature.description}</p>
                <ul className="space-y-2">
                  {feature.benefits.map((benefit, benefitIndex) => (
                    <li key={benefitIndex} className="flex items-center text-sm">
                      <div className="w-1.5 h-1.5 rounded-full bg-primary mr-2"></div>
                      {benefit}
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>
          ))}
        </div>

        <div className="mt-16 text-center">
          <div className="bg-gradient-to-r from-primary/10 to-accent/10 rounded-2xl p-8 md:p-12 border border-primary/20">
            <h3 className="text-2xl md:text-3xl font-bold mb-4">
              Ready to see AxWise in action?
            </h3>
            <p className="text-lg text-muted-foreground mb-6">
              Experience the power of AI-driven user research analysis
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Badge variant="outline" className="text-sm px-4 py-2">
                🚀 Upload interviews in seconds
              </Badge>
              <Badge variant="outline" className="text-sm px-4 py-2">
                🧠 Get insights in minutes
              </Badge>
              <Badge variant="outline" className="text-sm px-4 py-2">
                📊 Build better products
              </Badge>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
