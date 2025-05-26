/**
 * AxWise Onepager Presentation
 *
 * Modern Next.js version of the onepager presentation with the same design
 * but using React components and Tailwind CSS for better compatibility.
 */
export default function OnepagerPresentationPage() {
  return (
    <div className="min-h-screen bg-white">
      {/* Header Section */}
      <header className="bg-gradient-to-br from-purple-500 to-pink-500 text-white py-16">
        <div className="max-w-6xl mx-auto px-6 text-center">
          <div className="mb-6">
            <div className="flex items-center justify-center mb-6">
              <svg className="w-12 h-12 mr-3" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 2L13.09 8.26L22 9L13.09 9.74L12 16L10.91 9.74L2 9L10.91 8.26L12 2Z" fill="white"/>
                <circle cx="12" cy="12" r="3" fill="rgba(255,255,255,0.3)"/>
              </svg>
              <div className="text-4xl font-bold text-white">AxWise</div>
            </div>
          </div>
          <h2 className="text-2xl md:text-3xl font-semibold mb-4">
            Focus on building products, not analyzing what users said
          </h2>
          <p className="text-lg md:text-xl mb-8 opacity-90">
            Empowering every team to build better products by making customer understanding actionable.
          </p>
          <a
            href="#cta"
            className="inline-block bg-white text-purple-600 px-8 py-3 rounded-full font-semibold hover:bg-gray-100 transition-colors"
          >
            Join Us
          </a>
        </div>
      </header>

      {/* Preamble Section */}
      <section className="py-16 bg-gray-50">
        <div className="max-w-4xl mx-auto px-6">
          <h2 className="text-3xl font-bold text-gray-900 mb-8 text-center">Preamble</h2>
          <blockquote className="text-lg text-gray-700 italic border-l-4 border-purple-500 pl-6 mb-4">
            <p className="mb-4">
              9 of 10 Senior Product Designers and UX researchers with 8-20 years of experience I interviewed are telling they don't need more tools.
            </p>
            <p className="mb-4">
              Actually, it's quite the opposite — they want fewer tools or to maintain their current toolkit.
            </p>
            <p>
              The same goes for startup founders, Product Managers at companies like VMWare and Volkswagen, educational facilities, and others.
            </p>
          </blockquote>
          <p className="text-right text-purple-600 font-semibold">— Vitalijs Visnevskis</p>
        </div>
      </section>

      {/* Problem Section */}
      <section className="py-16 bg-gradient-to-br from-red-50 to-pink-50">
        <div className="max-w-6xl mx-auto px-6">
          <h2 className="text-4xl font-bold text-gray-900 mb-12 text-center">
            The Bottleneck Between Conversation and Code
          </h2>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            <div className="bg-white p-6 rounded-2xl shadow-lg">
              <h3 className="text-xl font-semibold text-gray-900 mb-3">User Research is Hard and Costly</h3>
              <p className="text-gray-700 mb-3">
                Teams lack dedicated researchers, and it takes 3-5 years of hands-on experience to gain expertise.
              </p>
              <p className="text-sm text-gray-500">
                Manual coding, spreadsheets, $50K-100K/year researchers.
              </p>
            </div>

            <div className="bg-white p-6 rounded-2xl shadow-lg">
              <h3 className="text-xl font-semibold text-gray-900 mb-3">Insight-to-Action Gap</h3>
              <p className="text-gray-700">
                Valuable insights remain trapped in static reports, unable to directly influence development.
              </p>
            </div>

            <div className="bg-white p-6 rounded-2xl shadow-lg">
              <h3 className="text-xl font-semibold text-gray-900 mb-3">Stakeholder Buy-in Challenges</h3>
              <p className="text-gray-700">
                Difficult to secure commitment from management for research-based decisions.
              </p>
            </div>

            <div className="bg-white p-6 rounded-2xl shadow-lg">
              <h3 className="text-xl font-semibold text-gray-900 mb-3">Guesswork Leads to Waste</h3>
              <p className="text-gray-700 mb-3">
                Resources spent on unvalidated features nobody needs.
              </p>
              <p className="text-sm text-gray-500">
                65-80% of startup failures trace to building the wrong product → $260B/year wasted.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Solution Section */}
      <section className="py-16 bg-gradient-to-br from-green-50 to-blue-50">
        <div className="max-w-6xl mx-auto px-6">
          <h2 className="text-4xl font-bold text-gray-900 mb-6 text-center">The Solution</h2>
          <p className="text-xl text-gray-700 mb-4 text-center">
            Bridging the Gap Between Users and Actionable Insights
          </p>
          <p className="text-lg text-gray-600 mb-12 text-center max-w-4xl mx-auto">
            AxWise transforms raw user interviews into actionable development tasks, eliminating the costly gap between customer feedback and product decisions.
          </p>

          {/* Data Extraction Visual */}
          <div className="mb-12">
            <h3 className="text-2xl font-semibold text-gray-900 mb-6 text-center">
              Transforming Conversations into Actionable Product Insights
            </h3>
            <div className="flex flex-wrap justify-center gap-4 mb-6">
              {[
                'User Pain Points',
                'Feature Requests',
                'Behavioral Patterns',
                'Usability Issues',
                'Workflow Blockers',
                'Mental Models',
                '+Many More'
              ].map((item, index) => (
                <span
                  key={index}
                  className="bg-purple-100 text-purple-800 px-4 py-2 rounded-full font-medium"
                >
                  {item}
                </span>
              ))}
            </div>
            <p className="text-center text-lg font-semibold text-green-600">
              All extracted automatically from a single 45-minute user interview — delivering 10x ROI on research time.
            </p>
          </div>

          {/* Features */}
          <div className="grid md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-purple-600" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">Advanced AI</h3>
              <p className="text-gray-700">
                Proprietary NLP models extract actionable insights from unstructured conversations with 85% accuracy.
              </p>
            </div>

            <div className="text-center">
              <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-blue-600" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">Intuitive UI</h3>
              <p className="text-gray-700">
                Zero learning curve for non-researchers, reducing time-to-insight by 70% compared to traditional methods.
              </p>
            </div>

            <div className="text-center">
              <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-green-600" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-5 14H7v-2h7v2zm3-4H7v-2h10v2zm0-4H7V7h10v2z"/>
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">API-First</h3>
              <p className="text-gray-700">
                Seamless integration with development workflows (Jira, Miro, GitHub) for direct insight-to-action conversion.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Screenshots Section */}
      <section className="py-16 bg-white">
        <div className="max-w-6xl mx-auto px-6">
          <h2 className="text-3xl font-bold text-gray-900 mb-12 text-center">See AxWise in Action</h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[
              'Dashboard Overview',
              'Analysis Results',
              'Insight Generation',
              'Task Creation'
            ].map((title, index) => (
              <div key={index} className="rounded-lg overflow-hidden shadow-lg bg-gradient-to-br from-purple-100 to-pink-100">
                <div className="w-full h-48 flex items-center justify-center">
                  <div className="text-center">
                    <div className="w-16 h-16 bg-purple-500 rounded-full flex items-center justify-center mx-auto mb-3">
                      <svg className="w-8 h-8 text-white" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-5 14H7v-2h7v2zm3-4H7v-2h10v2zm0-4H7V7h10v2z"/>
                      </svg>
                    </div>
                    <p className="text-purple-800 font-medium">{title}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Market Opportunity Section */}
      <section className="py-16 bg-gradient-to-br from-blue-50 to-purple-50">
        <div className="max-w-6xl mx-auto px-6">
          <h2 className="text-3xl font-bold text-gray-900 mb-6 text-center">Market Opportunity</h2>
          <p className="text-xl text-gray-700 mb-12 text-center">
            We're Chasing a Much Bigger Opportunity than Just QDA
          </p>

          {/* Market Transition Visual */}
          <div className="flex flex-col md:flex-row items-center justify-center gap-8 mb-12">
            <div className="text-center">
              <div className="w-48 h-48 bg-gray-200 rounded-full flex flex-col items-center justify-center mb-4">
                <div className="text-sm text-gray-600 mb-2">QDA Market</div>
                <div className="text-3xl font-bold text-gray-800">$2B</div>
                <div className="text-sm text-orange-600 font-semibold">MEH</div>
              </div>
            </div>

            <div className="text-4xl text-purple-600">→</div>

            <div className="text-center">
              <div className="w-48 h-48 bg-gradient-to-br from-green-400 to-blue-500 rounded-full flex flex-col items-center justify-center text-white mb-4">
                <div className="text-sm mb-2">Product Development Waste Market</div>
                <div className="text-3xl font-bold">$50-100B+</div>
                <div className="text-sm font-semibold">WOW!</div>
              </div>
            </div>
          </div>

          <div className="grid md:grid-cols-2 gap-8">
            <div className="bg-white p-6 rounded-2xl shadow-lg">
              <h3 className="text-xl font-semibold text-gray-900 mb-4">Current QDA Software Market</h3>
              <h4 className="text-lg font-medium text-gray-800 mb-3">Qualitative Data Analysis Tools</h4>
              <p className="text-gray-700 mb-4">
                The traditional QDA software market serves qualitative researchers, UX professionals, and market researchers who need to process and analyze interview data.
              </p>
              <div className="bg-gray-50 p-4 rounded-lg">
                <p className="italic text-gray-700 mb-3">"This is a niche market with limited growth potential"</p>
                <ul className="space-y-2 text-sm text-gray-600">
                  <li><span className="font-semibold">Problem:</span> Tools are complex, designed for research experts</li>
                  <li><span className="font-semibold">Size:</span> $2B addressable market</li>
                  <li><span className="font-semibold">Competition:</span> Saturated with established players</li>
                </ul>
              </div>
            </div>

            <div className="bg-white p-6 rounded-2xl shadow-lg">
              <h3 className="text-xl font-semibold text-gray-900 mb-4">Product Development Waste Market</h3>
              <h4 className="text-lg font-medium text-gray-800 mb-3">We Want to Eliminate Product Development Waste</h4>
              <p className="text-gray-700 mb-4">
                AxWise targets a much larger opportunity: the inefficiency and waste within product development stemming from inadequate or non-actionable user insights.
              </p>
              <div className="bg-green-50 p-4 rounded-lg">
                <p className="italic text-gray-700 mb-3">"We eliminate the $100B+ inefficiency of building the wrong product."</p>
                <ul className="space-y-2 text-sm text-gray-600">
                  <li><span className="font-semibold">TAM:</span> $50-100B+ – Global cost of product misalignment & wasted development</li>
                  <li><span className="font-semibold">SAM:</span> $0.5-5B – Startups/SMBs needing actionable insights (Year 2-3)</li>
                  <li><span className="font-semibold">SOM:</span> &lt;$1M – Hyper-focused on accelerators (Year 1)</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Team Section */}
      <section className="py-16 bg-white">
        <div className="max-w-6xl mx-auto px-6">
          <h2 className="text-3xl font-bold text-gray-900 mb-6 text-center">Our Team & Mentors</h2>
          <p className="text-lg text-gray-600 mb-12 text-center">
            A diverse group of experts in product development, design, and entrepreneurship
          </p>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {[
              {
                name: 'Vitalijs',
                image: 'vitalijs.jpg',
                bio: 'Founder with 14 years of experience, 2 exits in startups and Product Management, possessing deep empathy for the target user\'s challenges.'
              },
              {
                name: 'Zuzanna',
                image: 'zuzanna.jpg',
                bio: 'Senior UX/Product Designer with fine arts background and strong visual design skills. Self-taught in coding (HTML, CSS, JavaScript), with deep interest in research and testing methodologies.'
              },
              {
                name: 'Typhanie & Krists',
                image: 'KristsTyphanie.jpg',
                bio: 'Typhanie: Senior UX/UI designer with 7+ years experience across Europe and Middle East. Krists: Product Manager with expertise in cloud-native technologies and user-centric design methodologies.'
              },
              {
                name: 'Elena Sokolova',
                image: '8d13c31f-f90e-4272-adb1-281ee291baa6.png',
                bio: 'Mentor with 11+ years in marketing and innovation. Ex-Coca-Cola, worked with Google, MIT, and led entrepreneurship programs. Expertise in bridging research, technology, and business strategy.'
              }
            ].map((member, index) => (
              <div key={index} className="text-center">
                <div className="w-32 h-32 mx-auto mb-4 rounded-full bg-gradient-to-br from-purple-400 to-pink-400 flex items-center justify-center">
                  <div className="text-white text-2xl font-bold">
                    {member.name.split(' ')[0].charAt(0)}{member.name.split(' ')[1]?.charAt(0) || ''}
                  </div>
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">{member.name}</h3>
                <p className="text-sm text-gray-600">{member.bio}</p>
              </div>
            ))}
          </div>

          <p className="text-center text-gray-600 mt-8">
            The AxWise team brings relevant experience and connections through the Constructor University ecosystem, MIT entrepreneurship networks, and European innovation hubs.
          </p>
        </div>
      </section>

      {/* Competitive Positioning Section */}
      <section className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-6">
          <h2 className="text-3xl font-bold text-gray-900 mb-6 text-center">Competitive Positioning</h2>
          <h3 className="text-xl text-gray-700 mb-8 text-center">AxWise vs Others in QDA Market</h3>

          <div className="overflow-x-auto">
            <table className="w-full border-collapse bg-white shadow-lg rounded-lg overflow-hidden">
              <thead>
                <tr className="bg-gradient-to-r from-purple-500 to-pink-500 text-white">
                  <th className="p-4 text-left font-semibold">Feature Dimension</th>
                  <th className="p-4 text-left font-semibold">AxWise</th>
                  <th className="p-4 text-left font-semibold">Others (HeyMarvin, Condens, Dovetail, etc.)</th>
                </tr>
              </thead>
              <tbody>
                {[
                  {
                    dimension: "Market Approach",
                    axwise: "Solving a Distinct Workflow Problem - Addressing the much larger ($50B-$100B+) problem of product development waste caused by poor insight utilization",
                    others: "Competing solely on analysis features within the limited ($2B) QDA market"
                  },
                  {
                    dimension: "Target Segment",
                    axwise: "Underserved non-researcher startup teams - Focused on teams needing actionable insights integrated into workflows",
                    others: "Primarily serving dedicated researchers and UX professionals"
                  },
                  {
                    dimension: "Go-to-Market Strategy",
                    axwise: "Hyper-focused initial approach - Starting with accelerator niches (SOM: $10k-$100k ARR) before scaling to broader startup/SMB market (SAM: $0.5B-$5B)",
                    others: "Broad market approach without specific niche focus"
                  },
                  {
                    dimension: "Primary Target Audience",
                    axwise: "Non-researcher startup teams (Founders, PMs, Devs)",
                    others: "UX Researchers, Product Managers, Marketing"
                  },
                  {
                    dimension: "Core Value Prop Focus",
                    axwise: "Workflow Simplification + Direct Actionability",
                    others: "Repository, AI Search, Analysis, Moderation"
                  },
                  {
                    dimension: "Explicit Insight-to-Action",
                    axwise: "High (Direct Jira/Miro item generation)",
                    others: "Medium-Low (Integrations, Reports)"
                  },
                  {
                    dimension: "Perceived Ease of Use",
                    axwise: "High (Core design principle for non-experts)",
                    others: "Medium (Designed for researchers)"
                  }
                ].map((row, index) => (
                  <tr key={index} className={index % 2 === 0 ? "bg-gray-50" : "bg-white"}>
                    <td className="p-4 font-medium text-gray-900 border-b">{row.dimension}</td>
                    <td className="p-4 text-gray-700 border-b">
                      <strong className="text-green-600">{row.axwise.split(' - ')[0]}</strong>
                      {row.axwise.includes(' - ') && (
                        <>
                          <br />
                          <span className="text-sm">{row.axwise.split(' - ')[1]}</span>
                        </>
                      )}
                    </td>
                    <td className="p-4 text-gray-600 border-b">{row.others}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </section>

      {/* Go-to-Market Strategy Section */}
      <section className="py-16 bg-gradient-to-br from-blue-50 to-indigo-50">
        <div className="max-w-6xl mx-auto px-6">
          <h2 className="text-3xl font-bold text-gray-900 mb-6 text-center">Go-to-Market Strategy</h2>
          <h3 className="text-xl text-gray-700 mb-12 text-center">Targeted Approach with Validated Growth</h3>

          <div className="grid md:grid-cols-3 gap-8">
            <div className="bg-white p-6 rounded-2xl shadow-lg">
              <h4 className="text-xl font-semibold text-gray-900 mb-4">Phase 1: Accelerator Focus</h4>
              <p className="text-gray-700 mb-4">
                Target 10 key accelerators (20% of top 50) with 10-30% startup adoption rate within each program. Focus on PMF validation and referenceable customers.
              </p>
              <p className="text-sm text-gray-600">
                <strong>Target:</strong> $10K-25K ARR (~40 startup customers at $750 ARR each)
              </p>
            </div>

            <div className="bg-white p-6 rounded-2xl shadow-lg">
              <h4 className="text-xl font-semibold text-gray-900 mb-4">Phase 2: Startup Expansion</h4>
              <p className="text-gray-700 mb-4">
                Expand to 50+ accelerators while building direct acquisition channels. Implement tiered pricing and focus on increasing ARPC through higher-value plans.
              </p>
              <p className="text-sm text-gray-600">
                <strong>Target:</strong> $100K-250K ARR (~78 customers at $2,250 ARPC)
              </p>
            </div>

            <div className="bg-white p-6 rounded-2xl shadow-lg">
              <h4 className="text-xl font-semibold text-gray-900 mb-4">Phase 3: SMB & Enterprise</h4>
              <p className="text-gray-700 mb-4">
                Leverage validated success stories to enter SMB market and enterprise innovation labs. Develop enterprise-ready features and dedicated sales approach.
              </p>
              <p className="text-sm text-gray-600">
                <strong>Target:</strong> $500K-1M ARR (~25 enterprise customers at $30K+ ARPC)
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Phased Roadmap Section */}
      <section className="py-16 bg-white">
        <div className="max-w-6xl mx-auto px-6">
          <h2 className="text-3xl font-bold text-gray-900 mb-12 text-center">Phased Roadmap</h2>

          <div className="space-y-8">
            {[
              {
                title: "Phase 1: Validation",
                items: [
                  "Focus: Validate PMF with 10 accelerators (20% of top 50), targeting 20 startups per accelerator",
                  "Adoption: 10-30% of startups within partner accelerators (20% midpoint = 40 customers)",
                  "Pricing: $500-1000 ARR per startup ($750 midpoint), packaged as accelerator deals",
                  "KPI: 30% reduction in product development waste (measured via case studies)"
                ]
              },
              {
                title: "Phase 2: Growth",
                items: [
                  "Expansion: Scale to 50+ accelerators while building direct acquisition channels",
                  "Customer Growth: 40% CAGR to reach ~78 customers",
                  "Pricing Tiers: $49/mo (startup) → $149/mo (team) → $299/mo (business)",
                  "ARPC: $1,500-3,000 ($2,250 midpoint) through upselling and higher-tier adoption",
                  "Product: Integration with Jira, Miro, and GitHub to create complete workflow"
                ]
              },
              {
                title: "Phase 3: Scale",
                items: [
                  "Market Shift: Enter SMB and enterprise innovation labs segments",
                  "Target: ~25 enterprise customers at $30K+ ARPC",
                  "Enterprise Features: Advanced security, compliance (SOC 2, GDPR), dedicated support",
                  "Pricing: Custom enterprise contracts starting at $2,500/mo",
                  "Exit Path: Acquisition by Atlassian/Miro or $5M+ ARR self-sustainable business"
                ]
              }
            ].map((phase, index) => (
              <div key={index} className="bg-gradient-to-r from-purple-50 to-pink-50 p-6 rounded-2xl">
                <h3 className="text-2xl font-semibold text-gray-900 mb-4">{phase.title}</h3>
                <ul className="space-y-2">
                  {phase.items.map((item, itemIndex) => (
                    <li key={itemIndex} className="flex items-start">
                      <span className="text-purple-600 mr-2">•</span>
                      <span className="text-gray-700">
                        <strong className="text-gray-900">{item.split(':')[0]}:</strong>
                        {item.includes(':') ? item.split(':').slice(1).join(':') : item}
                      </span>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Our Vision Section */}
      <section className="py-16 bg-gradient-to-br from-green-50 to-teal-50">
        <div className="max-w-6xl mx-auto px-6">
          <h2 className="text-3xl font-bold text-gray-900 mb-6 text-center">Our Vision</h2>
          <h3 className="text-xl text-gray-700 mb-12 text-center">Empowering Every Team to Build Better Products</h3>

          <div className="grid md:grid-cols-3 gap-8 mb-12">
            <div className="text-center">
              <div className="text-4xl font-bold text-red-600 mb-2">65-80%</div>
              <p className="text-gray-700">Product Failure Rate due to misalignment with user needs</p>
            </div>
            <div className="text-center">
              <div className="text-4xl font-bold text-orange-600 mb-2">80%</div>
              <p className="text-gray-700">Startups without dedicated research resources</p>
            </div>
            <div className="text-center">
              <div className="text-4xl font-bold text-green-600 mb-2">100x</div>
              <p className="text-gray-700">ROI from proper user research</p>
            </div>
          </div>

          <div className="max-w-4xl mx-auto text-center space-y-6">
            <p className="text-lg text-gray-700">
              Our vision is to empower every team, regardless of research expertise, to build better products by making customer understanding a seamless, integrated, and actionable part of the development process.
            </p>
            <p className="text-lg text-gray-700">
              AxWise aims to significantly reduce the waste inherent in building products without clear user validation.
            </p>
          </div>
        </div>
      </section>

      {/* The Insight Economy Section */}
      <section className="py-16 bg-gray-900 text-white">
        <div className="max-w-4xl mx-auto px-6">
          <h2 className="text-3xl font-bold mb-8 text-center">The Insight Economy</h2>
          <blockquote className="text-xl italic text-center space-y-6">
            <p>
              "Users will always beg for 'faster horses.' Startup engineers will build them. And those startups will burn $1M+ doing it.
            </p>
            <p>
              Why? Because raw feedback is chaos — but the gold is in the unspoken needs. AxWise doesn't just analyze data. We turn founder-led teams into product psychics.
            </p>
            <p>
              The 'faster horses' era is over and we're the first-movers in the insight economy."
            </p>
          </blockquote>
        </div>
      </section>

      {/* Research Insights Section */}
      <section className="py-16 bg-white">
        <div className="max-w-6xl mx-auto px-6">
          <h2 className="text-3xl font-bold text-gray-900 mb-6 text-center">Research Insights</h2>
          <p className="text-lg text-green-600 mb-12 text-center">
            Key themes and pain points from our interviews with product teams at startups
          </p>

          <div className="grid md:grid-cols-3 gap-8 mb-12">
            {[
              {
                title: "Lacking UX Expertise",
                label: "Critical Challenge",
                description: "Startups struggle with conducting proper user research without dedicated UX researchers on the team.",
                quote: "We know talking to users is important, but we don't have the expertise to ask the right questions or analyze the responses correctly."
              },
              {
                title: "Interpreting User Feedback",
                label: "Major Frustration",
                description: "Understanding what users actually need versus what they say they want is a consistent challenge.",
                quote: "Users tell us what they think they want, but we struggle to identify their underlying needs and translate that to actual features."
              },
              {
                title: "From Insight to Implementation",
                label: "Major Bottleneck",
                description: "The gap between gathering insights and turning them into development tasks is significant.",
                quote: "We collect valuable user feedback, but it sits in reports and never makes it into sprint planning or backlog."
              }
            ].map((insight, index) => (
              <div key={index} className="bg-gray-50 p-6 rounded-2xl">
                <h3 className="text-xl font-semibold text-gray-900 mb-2">{insight.title}</h3>
                <span className="inline-block bg-purple-100 text-purple-800 px-3 py-1 rounded-full text-sm font-medium mb-4">
                  {insight.label}
                </span>
                <p className="text-gray-700 mb-4">{insight.description}</p>
                <blockquote className="border-l-4 border-purple-500 pl-4 italic text-gray-600">
                  "{insight.quote}"
                </blockquote>
              </div>
            ))}
          </div>

          {/* Chart Section */}
          <div className="mb-12">
            <h3 className="text-2xl font-semibold text-gray-900 mb-8 text-center">
              Most Critical User Research Challenges for Startups
            </h3>
            <div className="bg-gray-50 p-8 rounded-2xl">
              <div className="flex items-end justify-center space-x-8 h-64">
                {[
                  { label: "Asking\nRight\nQuestions", value: 90 },
                  { label: "Avoiding\nBias", value: 85 },
                  { label: "Translating\nto\nTasks", value: 80 },
                  { label: "Creating\nPersonas", value: 75 },
                  { label: "Stakeholder\nBuy-in", value: 65 }
                ].map((item, index) => (
                  <div key={index} className="flex flex-col items-center">
                    <div className="bg-purple-100 text-purple-800 px-2 py-1 rounded text-sm font-semibold mb-2">
                      {item.value}%
                    </div>
                    <div
                      className="bg-gradient-to-t from-purple-500 to-purple-300 w-12 rounded-t"
                      style={{ height: `${(item.value / 100) * 200}px` }}
                    ></div>
                    <div className="text-xs text-gray-600 mt-2 text-center whitespace-pre-line">
                      {item.label}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* How AxWise Addresses Challenges */}
          <div>
            <h3 className="text-2xl font-semibold text-gray-900 mb-8 text-center">
              How AxWise Addresses These Challenges
            </h3>
            <div className="grid md:grid-cols-2 gap-6">
              {[
                { problem: "No UX Expertise", solution: "Guided Interview Framework" },
                { problem: "Misinterpreting Feedback", solution: "AI-Powered Intent Analysis" },
                { problem: "Insight-to-Action Gap", solution: "Automated Dev Task Generation" },
                { problem: "Can't Create Personas", solution: "Automatic Persona Generation" }
              ].map((item, index) => (
                <div key={index} className="bg-white p-6 rounded-2xl shadow-lg text-center">
                  <div className="text-gray-600 font-medium mb-2">{item.problem}</div>
                  <div className="text-purple-600 text-2xl mb-2">↓</div>
                  <div className="text-green-600 font-semibold">{item.solution}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Our Target User Section */}
      <section className="py-16 bg-gradient-to-br from-purple-50 to-pink-50">
        <div className="max-w-4xl mx-auto px-6">
          <h2 className="text-3xl font-bold text-gray-900 mb-6 text-center">Our Target User</h2>
          <p className="text-lg text-gray-600 mb-12 text-center">
            Meet the professionals driving product decisions at startups and small teams without dedicated UX researchers
          </p>

          <div className="bg-white rounded-2xl shadow-lg overflow-hidden">
            {/* Header */}
            <div className="bg-gradient-to-r from-purple-500 to-pink-500 text-white p-6">
              <div className="flex items-center">
                <div className="w-12 h-12 bg-white bg-opacity-20 rounded-full flex items-center justify-center mr-4">
                  <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
                  </svg>
                </div>
                <div>
                  <h3 className="text-xl font-semibold mb-1">Pragmatic Product Decision-Maker</h3>
                  <p className="opacity-90 italic">Product Manager / Founder / Tech Lead</p>
                </div>
              </div>
            </div>

            {/* Content */}
            <div className="p-6">
              <div className="grid md:grid-cols-2 gap-8">
                <div>
                  <h4 className="text-lg font-semibold text-purple-600 mb-4">Goals</h4>
                  <ul className="space-y-2 text-gray-700">
                    <li className="flex items-start">
                      <span className="text-green-500 mr-2">•</span>
                      Make evidence-based product decisions quickly
                    </li>
                    <li className="flex items-start">
                      <span className="text-green-500 mr-2">•</span>
                      Understand what users really need vs. what they say
                    </li>
                    <li className="flex items-start">
                      <span className="text-green-500 mr-2">•</span>
                      Translate user feedback directly into development tasks
                    </li>
                    <li className="flex items-start">
                      <span className="text-green-500 mr-2">•</span>
                      Get stakeholder buy-in using tangible user data
                    </li>
                    <li className="flex items-start">
                      <span className="text-green-500 mr-2">•</span>
                      Maximize ROI on development resources
                    </li>
                  </ul>
                </div>

                <div>
                  <h4 className="text-lg font-semibold text-purple-600 mb-4">Frustrations</h4>
                  <ul className="space-y-2 text-gray-700">
                    <li className="flex items-start">
                      <span className="text-red-500 mr-2">•</span>
                      No UX researcher on the team or budget to hire one
                    </li>
                    <li className="flex items-start">
                      <span className="text-red-500 mr-2">•</span>
                      Unsure which questions to ask during user interviews
                    </li>
                    <li className="flex items-start">
                      <span className="text-red-500 mr-2">•</span>
                      Difficulty interpreting results without bias
                    </li>
                    <li className="flex items-start">
                      <span className="text-red-500 mr-2">•</span>
                      Can't distinguish between user wants and actual needs
                    </li>
                    <li className="flex items-start">
                      <span className="text-red-500 mr-2">•</span>
                      Hours wasted on manual analysis with spreadsheets
                    </li>
                    <li className="flex items-start">
                      <span className="text-red-500 mr-2">•</span>
                      Insights remain theoretical, never reaching development
                    </li>
                  </ul>
                </div>
              </div>

              <div className="mt-8 p-4 bg-gray-50 rounded-lg">
                <blockquote className="text-lg italic text-gray-700 text-center">
                  "I know user research is important, but I don't have the time, expertise, or tools to do it properly. Most insights never make it into our product."
                </blockquote>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Final CTA Section */}
      <section id="cta" className="py-16 bg-gradient-to-br from-purple-500 to-pink-500 text-white">
        <div className="max-w-4xl mx-auto px-6 text-center">
          <h2 className="text-3xl font-bold mb-6">Join Us in Transforming Product Development</h2>
          <p className="text-xl mb-4 opacity-90">
            We are seeking seed funding to build out our core engineering and design team, and execute our go-to-market strategy focused on bringing AxWise to the broader network of Accelerators and Startups.
          </p>
          <p className="text-xl mb-8 opacity-90">
            Join us in transforming how startups connect with their users and build products people truly want.
          </p>
          <a
            href="mailto:vitalijs@axwise.de"
            className="inline-block bg-white text-purple-600 px-8 py-3 rounded-full font-semibold hover:bg-gray-100 transition-colors text-lg"
          >
            Contact Us
          </a>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-8 bg-gray-900 text-white">
        <div className="max-w-6xl mx-auto px-6 text-center">
          <div className="mb-4">
            <div className="flex items-center justify-center">
              <svg className="w-8 h-8 mr-2" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 2L13.09 8.26L22 9L13.09 9.74L12 16L10.91 9.74L2 9L10.91 8.26L12 2Z" fill="white"/>
                <circle cx="12" cy="12" r="3" fill="rgba(255,255,255,0.3)"/>
              </svg>
              <div className="text-2xl font-bold text-white">AxWise</div>
            </div>
          </div>
          <p className="text-gray-400">© 2025 AxWise. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
}

/**
 * Metadata for the onepager presentation page
 */
export const metadata = {
  title: 'AxWise – Focus on building products, not analyzing what users said',
  description: 'Empowering every team to build better products by making customer understanding actionable. Transform raw user interviews into actionable development tasks.',
  keywords: 'user research, product development, UX research, startup tools, customer insights, product management',
  openGraph: {
    title: 'AxWise – Focus on building products, not analyzing what users said',
    description: 'Empowering every team to build better products by making customer understanding actionable.',
    type: 'website',
  },
  robots: {
    index: false, // Internal presentation, don't index
    follow: false,
  },
};
