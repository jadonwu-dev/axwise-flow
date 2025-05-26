import React from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Star, Quote } from 'lucide-react';

export const TestimonialsSection = () => {
  const testimonials = [
    {
      name: "Sarah Chen",
      role: "Senior Product Manager",
      company: "TechFlow Inc.",
      avatar: "SC",
      rating: 5,
      quote: "AxWise transformed how we handle user research. What used to take our team 3 weeks now takes 3 hours. The insights are deeper and more actionable than anything we've produced manually.",
      highlight: "3 weeks → 3 hours"
    },
    {
      name: "Marcus Rodriguez",
      role: "UX Research Lead",
      company: "InnovateLabs",
      avatar: "MR",
      rating: 5,
      quote: "The AI catches patterns across interviews that we completely missed. Our stakeholder buy-in has increased dramatically because the insights are so clear and compelling.",
      highlight: "Patterns we missed"
    },
    {
      name: "Emily Watson",
      role: "Founder & CEO",
      company: "StartupXYZ",
      avatar: "EW",
      rating: 5,
      quote: "As a startup, we can't afford a full research team. AxWise gives us enterprise-level insights with a fraction of the cost and time investment.",
      highlight: "Enterprise insights, startup budget"
    },
    {
      name: "David Kim",
      role: "Head of Product",
      company: "ScaleUp Co.",
      avatar: "DK",
      rating: 5,
      quote: "The PRD generation feature is a game-changer. We go from user interviews directly to development plans. Our time-to-market has improved by 40%.",
      highlight: "40% faster time-to-market"
    },
    {
      name: "Lisa Thompson",
      role: "Design Director",
      company: "CreativeStudio",
      avatar: "LT",
      rating: 5,
      quote: "The persona generation is incredibly detailed and accurate. It's like having a senior researcher analyze every interview with perfect consistency.",
      highlight: "Perfect consistency"
    },
    {
      name: "Alex Johnson",
      role: "VP of Product",
      company: "GrowthTech",
      avatar: "AJ",
      rating: 5,
      quote: "AxWise has become essential to our product development process. The insights drive our roadmap decisions and the team alignment is unprecedented.",
      highlight: "Drives our roadmap"
    }
  ];

  const stats = [
    { value: "95%", label: "Time Reduction" },
    { value: "3x", label: "More Insights" },
    { value: "90%", label: "Stakeholder Buy-in" },
    { value: "40%", label: "Faster Time-to-Market" }
  ];

  return (
    <section className="py-16 md:py-24 bg-muted/30">
      <div className="container px-4 md:px-6 mx-auto">
        <div className="text-center mb-16">
          <Badge variant="default" className="mb-4">Testimonials</Badge>
          <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold mb-6">
            What Product Teams Are <span className="text-primary">Saying</span>
          </h2>
          <p className="text-lg md:text-xl text-muted-foreground max-w-3xl mx-auto">
            Don't just take our word for it. See how AxWise is transforming 
            product development for teams around the world.
          </p>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-16">
          {stats.map((stat, index) => (
            <div key={index} className="text-center">
              <div className="text-3xl md:text-4xl font-bold text-primary mb-2">{stat.value}</div>
              <div className="text-sm text-muted-foreground">{stat.label}</div>
            </div>
          ))}
        </div>

        {/* Testimonials Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-16">
          {testimonials.map((testimonial, index) => (
            <Card key={index} className="border-primary/20 hover:border-primary/40 transition-colors">
              <CardContent className="p-6">
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center font-semibold text-primary">
                    {testimonial.avatar}
                  </div>
                  <div className="flex-1">
                    <h4 className="font-semibold text-sm">{testimonial.name}</h4>
                    <p className="text-xs text-muted-foreground">{testimonial.role}</p>
                    <p className="text-xs text-muted-foreground">{testimonial.company}</p>
                  </div>
                  <div className="flex">
                    {[...Array(testimonial.rating)].map((_, i) => (
                      <Star key={i} className="w-4 h-4 fill-yellow-400 text-yellow-400" />
                    ))}
                  </div>
                </div>
                
                <div className="relative">
                  <Quote className="w-6 h-6 text-primary/20 absolute -top-2 -left-2" />
                  <p className="text-sm text-muted-foreground mb-3 pl-4">
                    {testimonial.quote}
                  </p>
                </div>
                
                <Badge variant="secondary" className="text-xs">
                  {testimonial.highlight}
                </Badge>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Social Proof */}
        <div className="text-center">
          <div className="bg-gradient-to-r from-primary/10 to-accent/10 rounded-2xl p-8 md:p-12 border border-primary/20">
            <h3 className="text-2xl md:text-3xl font-bold mb-4">
              Join 500+ Product Teams Already Using AxWise
            </h3>
            <p className="text-lg text-muted-foreground mb-6">
              From startups to enterprises, product teams worldwide trust AxWise 
              to transform their user research process.
            </p>
            <div className="flex flex-wrap justify-center gap-4">
              <Badge variant="outline" className="text-sm px-4 py-2">
                🚀 Startups
              </Badge>
              <Badge variant="outline" className="text-sm px-4 py-2">
                🏢 Enterprises
              </Badge>
              <Badge variant="outline" className="text-sm px-4 py-2">
                🎨 Design Agencies
              </Badge>
              <Badge variant="outline" className="text-sm px-4 py-2">
                📊 Research Teams
              </Badge>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
