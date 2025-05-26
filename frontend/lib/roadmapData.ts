export interface MonthlyObjective {
  type: 'SaaS Product Development' | 'Open-Source Core Development' | 'Marketing & Community';
  description: string;
}

export interface MonthlyEpic {
  month: string; // e.g., "Month 6 (June 2025)"
  epic: string; // High-level theme/focus for the month
  objectives: MonthlyObjective[];
}

export interface RoadmapPhase {
  title: string;
  timeframe: string;
  cashFlowContext: string;
  narrative: string;
  keyGoals: string[];
  monthlyEpics: MonthlyEpic[];
}

export interface RoadmapData {
  phases: RoadmapPhase[];
}

export const roadmapData: RoadmapData = {
  phases: [
    {
      title: "Foundation & Initial Traction",
      timeframe: "Months 6-8",
      cashFlowContext: "Securing crucial pre-seed funding of 100K to support initial growth and development.",
      narrative: "Launching our Open-Source Core and gaining initial user traction. With our powerful API-driven features already developed, we'll release the Open-Source Core in Month 6 (June 2025) and focus on attracting our first 100-200 users by Month 8 (August 2025). This phase is critical for demonstrating market validation and securing the pre-seed funding needed for further development.",
      keyGoals: [
        "Release robust Open-Source Core with our existing API-driven features",
        "Attract first 100-200 users to validate market fit",
        "Secure crucial pre-seed funding of 100K"
      ],
      monthlyEpics: [
        {
          month: "Month 5 (May 2025)",
          epic: "Problem Validation & Foundation Preparation",
          objectives: [
            {
              type: "Marketing & Community",
              description: "✅ Conduct interviews with product designers and UX researchers to validate the problem"
            }
          ]
        },
        {
          month: "Month 6 (June 2025)",
          epic: "Foundation Development for Product Development E2E Automation",
          objectives: [
            {
              type: "SaaS Product Development",
              description: "Design SaaS UI mockups & prototypes for E2E flow"
            },
            {
              type: "SaaS Product Development",
              description: "Basic user onboarding flow design"
            },
            {
              type: "SaaS Product Development",
              description: "Develop Interview Script Generator"
            },
            {
              type: "SaaS Product Development",
              description: "Develop LLM-generated answers to showcase script-to-analysis flow"
            },
            {
              type: "SaaS Product Development",
              description: "Develop Chat with more insights (initial version)"
            },
            {
              type: "SaaS Product Development",
              description: "Develop Share interview insights as cards in social networks"
            },
            {
              type: "Open-Source Core Development",
              description: "Finalize API for core features (Analysis, Themes, Patterns, Sentiment, Personas, Insights)"
            },
            {
              type: "Open-Source Core Development",
              description: "API Documentation (Initial Draft)"
            },
            {
              type: "Open-Source Core Development",
              description: "Prepare core engine for packaging"
            },
            {
              type: "Open-Source Core Development",
              description: "Implement PII Redaction"
            },
            {
              type: "Open-Source Core Development",
              description: "Begin Integrate DSPy (if feasible quickly)"
            },
            {
              type: "Marketing & Community",
              description: "Announce Active Development & Open-Source Coming Soon"
            },
            {
              type: "Marketing & Community",
              description: "Drive waitlist sign-ups"
            },
            {
              type: "Marketing & Community",
              description: "Initial content pieces on the problem/solution"
            },
            {
              type: "Marketing & Community",
              description: "Tease upcoming SaaS features (script gen, social sharing)"
            }
          ]
        },
        {
          month: "Month 7 (July 2025)",
          epic: "Open-Source Core Launch & SaaS MVP Development",
          objectives: [
            {
              type: "SaaS Product Development",
              description: "SaaS MVP UI Development (Focus on data ingest, analysis trigger, results display for core features + new quick wins)"
            },
            {
              type: "SaaS Product Development",
              description: "Implement Multi-File Upload"
            },
            {
              type: "SaaS Product Development",
              description: "Implement Basic User Guidance"
            },
            {
              type: "SaaS Product Development",
              description: "Implement Export to Miro"
            },
            {
              type: "SaaS Product Development",
              description: "Implement Export to Figma"
            },
            {
              type: "SaaS Product Development",
              description: "Begin Parse YouTube videos and podcasts"
            },
            {
              type: "SaaS Product Development",
              description: "Begin Create backlog items out of prioritised insights (User Story Generation)"
            },
            {
              type: "Open-Source Core Development",
              description: "Full Open-Source Core Release (v0.1): Packaged, documented, self-hosting. Includes stable Analysis History, User Management (Clerk), Core Batch Analysis & Synthesis, PII Redaction, performance optimizations"
            },
            {
              type: "Open-Source Core Development",
              description: "Finalize Integrate DSPy if started"
            },
            {
              type: "Open-Source Core Development",
              description: "Establish GitHub contribution guidelines (CONTRIBUTING.md, CLA)"
            },
            {
              type: "Marketing & Community",
              description: "Launch Open-Source Core! Promote on relevant channels"
            },
            {
              type: "Marketing & Community",
              description: "Share conceptual API usage examples"
            },
            {
              type: "Marketing & Community",
              description: "Start engaging with early OS contributors/issues"
            },
            {
              type: "Marketing & Community",
              description: "Highlight SaaS features being built on this core"
            }
          ]
        },
        {
          month: "Month 8 (August 2025)",
          epic: "SaaS MVP Refinement & Investor Preparation",
          objectives: [
            {
              type: "SaaS Product Development",
              description: "Refine SaaS MVP based on internal testing"
            },
            {
              type: "SaaS Product Development",
              description: "Polish UI for Analysis History & User Management (Clerk)"
            },
            {
              type: "SaaS Product Development",
              description: "Complete & Polish Parse YouTube videos and podcasts"
            },
            {
              type: "SaaS Product Development",
              description: "Complete & Polish Create backlog items out of prioritised insights (User Story Generation)"
            },
            {
              type: "SaaS Product Development",
              description: "Begin elements of Deeper automation of the Define → Gather → Process → Draft → Generate workflow in UI"
            },
            {
              type: "SaaS Product Development",
              description: "Prepare SaaS MVP for investor demos (showcasing the full, richer flow)"
            },
            {
              type: "Open-Source Core Development",
              description: "Address initial bugs/feedback on Open-Source Core"
            },
            {
              type: "Open-Source Core Development",
              description: "Plan v0.2 features based on early community input and SaaS needs"
            },
            {
              type: "Marketing & Community",
              description: "Actively engage with potential seed investors"
            },
            {
              type: "Marketing & Community",
              description: "Showcase Open-Source traction & the significantly more advanced SaaS MVP"
            },
            {
              type: "Marketing & Community",
              description: "✅ Refine pitch deck with validated insights (using AxWise itself!)"
            }
          ]
        }
      ]
    },
    {
      title: "Seed Funding & Rapid Growth",
      timeframe: "Months 9-14",
      cashFlowContext: "Securing 750K seed funding by Month 12 (December 2025) to accelerate growth.",
      narrative: "Building on our initial traction to rapidly grow our user base and secure substantial seed funding. During this phase (September 2025 - February 2026), we'll focus on enhancing our SaaS offering, expanding marketing efforts, and demonstrating strong growth metrics to investors. By the end of this phase, we aim to reach 1,000 users and secure 750K in seed funding by December 2025.",
      keyGoals: [
        "Grow user base to 1,000 users",
        "Secure 750K seed funding by December 2025",
        "Enhance SaaS offering with additional features and integrations"
      ],
      monthlyEpics: [
        {
          month: "Months 9-10 (Sept-Oct 2025)",
          epic: "SaaS Platform Launch & User Onboarding",
          objectives: [
            {
              type: "SaaS Product Development",
              description: "SaaS Platform Launch (v1.0)!"
            },
            {
              type: "SaaS Product Development",
              description: "Onboard waitlist users"
            },
            {
              type: "SaaS Product Development",
              description: "Implement robust feedback collection mechanisms"
            },
            {
              type: "SaaS Product Development",
              description: "Refine existing features (Script Gen, Chat, Exports, Parsing, User Stories) based on initial user feedback"
            },
            {
              type: "SaaS Product Development",
              description: "Continue enhancing Deeper automation of the Define → Gather → Process → Draft → Generate workflow"
            },
            {
              type: "Open-Source Core Development",
              description: "OS Core v0.2: Stability improvements, enhanced API docs. Further DSPy refinements. API support for any new nuances from SaaS launch"
            },
            {
              type: "Marketing & Community",
              description: "Public SaaS Launch Campaign!"
            },
            {
              type: "Marketing & Community",
              description: "Targeted outreach to PMs, UXRs, Founders"
            },
            {
              type: "Marketing & Community",
              description: "Collect testimonials from early users"
            },
            {
              type: "Marketing & Community",
              description: "Start regular content (blog, case studies on SaaS usage, highlighting the advanced workflow)"
            }
          ]
        },
        {
          month: "Months 11-12 (Nov-Dec 2025)",
          epic: "Feature Enhancement & Seed Funding Completion",
          objectives: [
            {
              type: "SaaS Product Development",
              description: "Iterate on SaaS UI/UX"
            },
            {
              type: "SaaS Product Development",
              description: "Enhance Centralized Insight Repository features"
            },
            {
              type: "SaaS Product Development",
              description: "Begin Report & Presentation Builder (initial version)"
            },
            {
              type: "SaaS Product Development",
              description: "Begin Feature: Assist non-researchers during interviews (guidance/prompts within SaaS)"
            },
            {
              type: "Open-Source Core Development",
              description: "OS Core v0.3: Performance optimizations. API support for repository features. Initial groundwork/exploration for Plugin Architecture"
            },
            {
              type: "Marketing & Community",
              description: "Highlight new features and user success stories"
            },
            {
              type: "Marketing & Community",
              description: "Host first webinar/demo showcasing the E2E automated flow"
            },
            {
              type: "Marketing & Community",
              description: "Build out FAQ and support documentation"
            }
          ]
        },
        {
          month: "Months 13-14 (Jan-Feb 2026)",
          epic: "Advanced Features & Market Expansion",
          objectives: [
            {
              type: "SaaS Product Development",
              description: "Export to Jira (linking user stories)"
            },
            {
              type: "SaaS Product Development",
              description: "Complete/Refine Feature: Assist non-researchers during interviews"
            },
            {
              type: "SaaS Product Development",
              description: "Mature Report & Presentation Builder"
            },
            {
              type: "SaaS Product Development",
              description: "Begin Automated Market & Competitor Insights (v1 using LLM)"
            },
            {
              type: "Open-Source Core Development",
              description: "OS Core v0.4: Solidify Plugin Architecture groundwork. API for market insights. Experiment with CamelOwl"
            },
            {
              type: "Marketing & Community",
              description: "Partnership announcements (e.g., Vexa.ai more prominently)"
            },
            {
              type: "Marketing & Community",
              description: "Grow social media presence"
            },
            {
              type: "Marketing & Community",
              description: "Start building a more formal community forum/Discord for both SaaS and OS users"
            },
            {
              type: "Marketing & Community",
              description: "Content on specific use cases like From YouTube to User Story in Minutes"
            }
          ]
        }
      ]
    },
    {
      title: "Scale & Ecosystem Expansion",
      timeframe: "Months 15-27",
      cashFlowContext: "Leveraging seed funding to drive significant growth and prepare for potential Series A.",
      narrative: "Scaling our user base and expanding our ecosystem with advanced features. During this phase (March 2026 - March 2027), we'll focus on rapid user acquisition, platform extensibility through a plugin architecture, and delivering more sophisticated AI-driven strategic insights. We aim to grow from 1,000 to 3,000-10,000 users during this period, laying the groundwork for our €1 million monthly revenue milestone.",
      keyGoals: [
        "Grow user base to 3,000-10,000 users",
        "Launch Plugin Architecture for platform extensibility",
        "Develop advanced AI features that demonstrate clear ROI"
      ],
      monthlyEpics: [
        {
          month: "Months 15-20 (Mar-Aug 2026)",
          epic: "Platform Expansion & Plugin Architecture",
          objectives: [
            {
              type: "SaaS Product Development",
              description: "Advanced collaboration features for teams"
            },
            {
              type: "SaaS Product Development",
              description: "Mature Report & Presentation Builder (v2)"
            },
            {
              type: "SaaS Product Development",
              description: "Develop and release initial Plugin Architecture for SaaS"
            },
            {
              type: "SaaS Product Development",
              description: "Mature Automated Market & Competitor Insights (v2 or broader)"
            },
            {
              type: "SaaS Product Development",
              description: "Begin Strategic Recommendations (AI-generated based on insights)"
            },
            {
              type: "Open-Source Core Development",
              description: "OS Core v0.5/0.6: Robust Plugin Architecture support in API, SDK for plugin developers"
            },
            {
              type: "Open-Source Core Development",
              description: "Update openwebUI with additional plugins (if OpenWebUI is part of your OS stack)"
            },
            {
              type: "Open-Source Core Development",
              description: "More advanced LLM configurations and fine-tuning options via API"
            },
            {
              type: "Marketing & Community",
              description: "Launch Plugin Developer Program"
            },
            {
              type: "Marketing & Community",
              description: "Showcase community/partner plugins"
            },
            {
              type: "Marketing & Community",
              description: "Content marketing focused on advanced use cases and strategic product development"
            },
            {
              type: "Marketing & Community",
              description: "Explore OASIS for marketing simulations/insights"
            }
          ]
        },
        {
          month: "Months 21-27 (Sept 2026-Mar 2027)",
          epic: "Strategic AI & Enterprise Features",
          objectives: [
            {
              type: "SaaS Product Development",
              description: "Complete and refine Strategic Recommendations"
            },
            {
              type: "SaaS Product Development",
              description: "Deeper integration with CamelOwl for enhanced backlog item creation"
            },
            {
              type: "SaaS Product Development",
              description: "Enhanced Validation Framework guidance within SaaS"
            },
            {
              type: "SaaS Product Development",
              description: "Initial enterprise-focused features (e.g., team roles/permissions, audit logs)"
            },
            {
              type: "Open-Source Core Development",
              description: "OS Core v0.7/0.8: APIs for strategic recommendations, enhanced data export/import capabilities"
            },
            {
              type: "Open-Source Core Development",
              description: "Continued refinement of DSPy/structured LLM usage"
            },
            {
              type: "Open-Source Core Development",
              description: "Documentation for enterprise self-hosting scenarios"
            },
            {
              type: "Marketing & Community",
              description: "Target enterprise clients with case studies demonstrating ROI"
            },
            {
              type: "Marketing & Community",
              description: "Develop content around AI in Product Strategy and Enterprise-Grade Qualitative Analysis"
            },
            {
              type: "Marketing & Community",
              description: "Host user conferences or participate in major industry events"
            },
            {
              type: "Marketing & Community",
              description: "Grow international user base"
            }
          ]
        }
      ]
    },
    {
      title: "Market Leadership & Revenue Milestone",
      timeframe: "Months 28-33",
      cashFlowContext: "Achieving €1 million in monthly revenue, potentially exploring Series A funding.",
      narrative: "Solidifying our market leadership and reaching our ambitious revenue milestone. During this phase (April 2027 - September 2027), we'll focus on optimizing our platform, expanding enterprise adoption, and introducing next-generation AI features. By the end of this phase, we aim to exceed 10,000 users and achieve our target of €1 million in monthly revenue, establishing AxWise as the clear market leader in AI-powered product development tools.",
      keyGoals: [
        "Exceed 10,000 users",
        "Achieve €1 million in monthly revenue",
        "Solidify market leadership with next-generation AI features"
      ],
      monthlyEpics: [
        {
          month: "Months 28-33 (Apr-Sept 2027)",
          epic: "Market Leadership & Revenue Excellence",
          objectives: [
            {
              type: "SaaS Product Development",
              description: "Highly personalized AI guidance throughout the E2E workflow"
            },
            {
              type: "SaaS Product Development",
              description: "Predictive analytics for product success based on initial data (exploratory)"
            },
            {
              type: "SaaS Product Development",
              description: "Advanced enterprise security & compliance features"
            },
            {
              type: "SaaS Product Development",
              description: "Full Flexible LLM Integration (UI to connect custom/local LLMs easily)"
            },
            {
              type: "Open-Source Core Development",
              description: "OS Core v1.0 and beyond: Focus on stability, scalability, cutting-edge LLM integration"
            },
            {
              type: "Open-Source Core Development",
              description: "Support for new data modalities or analysis types"
            },
            {
              type: "Open-Source Core Development",
              description: "Long-term maintenance and governance of the OS project"
            },
            {
              type: "Marketing & Community",
              description: "Thought leadership content (whitepapers, research reports)"
            },
            {
              type: "Marketing & Community",
              description: "Strategic partnerships with major players"
            },
            {
              type: "Marketing & Community",
              description: "Global marketing campaigns"
            },
            {
              type: "Marketing & Community",
              description: "Expanding the community to include more researchers and AI developers"
            },
            {
              type: "Marketing & Community",
              description: "Review jeda.ai/plans for competitive insights"
            }
          ]
        }
      ]
    }
  ]
};
