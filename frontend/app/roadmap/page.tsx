import { Metadata } from 'next';
import { RoadmapComponent } from '@/components/roadmap/RoadmapComponent';

export const metadata: Metadata = {
  title: 'AxWise Product Roadmap - Strategic Development Plan',
  description: 'Explore AxWise\'s comprehensive product roadmap from foundation to market leadership, including funding milestones and growth targets.',
};

/**
 * Roadmap page showcasing AxWise's strategic development plan
 */
export default function RoadmapPage(): JSX.Element {
  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-12">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-primary mb-6">
            AxWise Product Roadmap
          </h1>
          <p className="text-lg text-muted-foreground max-w-3xl mx-auto">
            Our strategic journey from foundation to market leadership. Explore our phased approach 
            to building the future of AI-powered user research and product development.
          </p>
        </div>

        {/* Roadmap Component */}
        <RoadmapComponent />

        {/* Key Highlights */}
        <div className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="bg-card rounded-lg border p-6 text-center">
            <div className="w-12 h-12 mx-auto mb-4 rounded-full bg-primary/10 flex items-center justify-center">
              <span className="text-2xl font-bold text-primary">€850K</span>
            </div>
            <h3 className="font-semibold mb-2">Total Funding Target</h3>
            <p className="text-sm text-muted-foreground">
              Pre-seed and seed funding to accelerate growth and development
            </p>
          </div>

          <div className="bg-card rounded-lg border p-6 text-center">
            <div className="w-12 h-12 mx-auto mb-4 rounded-full bg-primary/10 flex items-center justify-center">
              <span className="text-2xl font-bold text-primary">10K+</span>
            </div>
            <h3 className="font-semibold mb-2">User Target</h3>
            <p className="text-sm text-muted-foreground">
              Growing from initial users to market leadership with 10,000+ active users
            </p>
          </div>

          <div className="bg-card rounded-lg border p-6 text-center">
            <div className="w-12 h-12 mx-auto mb-4 rounded-full bg-primary/10 flex items-center justify-center">
              <span className="text-2xl font-bold text-primary">€1M</span>
            </div>
            <h3 className="font-semibold mb-2">Revenue Milestone</h3>
            <p className="text-sm text-muted-foreground">
              Target monthly recurring revenue demonstrating strong market traction
            </p>
          </div>
        </div>

        {/* Strategic Focus Areas */}
        <div className="mt-16 bg-card rounded-lg border p-8">
          <h2 className="text-2xl font-semibold text-primary mb-6">Strategic Focus Areas</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h3 className="font-semibold mb-3">Technology Development</h3>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li>• Open-source core platform</li>
                <li>• Advanced AI analysis capabilities</li>
                <li>• API-first architecture</li>
                <li>• Enterprise-grade security</li>
              </ul>
            </div>
            <div>
              <h3 className="font-semibold mb-3">Market Expansion</h3>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li>• Community building and engagement</li>
                <li>• Strategic partnerships</li>
                <li>• International market entry</li>
                <li>• Enterprise customer acquisition</li>
              </ul>
            </div>
          </div>
        </div>

        {/* Call to Action */}
        <div className="mt-16 text-center">
          <div className="bg-gradient-to-r from-primary/10 to-accent/10 rounded-2xl p-8 md:p-12 border border-primary/20">
            <h3 className="text-2xl md:text-3xl font-bold mb-4">
              Join Our Journey
            </h3>
            <p className="text-lg text-muted-foreground mb-6 max-w-2xl mx-auto">
              Be part of the future of user research and product development. 
              Whether you're an investor, partner, or early adopter, we'd love to connect.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <a 
                href="/unified-dashboard"
                className="inline-flex items-center justify-center rounded-md bg-primary px-6 py-3 text-sm font-medium text-primary-foreground hover:bg-primary/90 transition-colors"
              >
                Try AxWise Now
              </a>
              <a 
                href="/contact"
                className="inline-flex items-center justify-center rounded-md border border-input bg-background px-6 py-3 text-sm font-medium hover:bg-accent hover:text-accent-foreground transition-colors"
              >
                Contact Us
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
