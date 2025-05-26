/**
 * Design Thinking Workshop Page
 *
 * This page serves the workshop content directly as an iframe
 * to ensure compatibility with Firebase App Hosting.
 */
export default function WorkshopDesignThinkingPage() {
  return (
    <div style={{ width: '100%', height: '100vh', margin: 0, padding: 0 }}>
      <iframe
        src="/api/static/workshop-designthinking"
        style={{
          width: '100%',
          height: '100%',
          border: 'none',
          margin: 0,
          padding: 0,
        }}
        title="Design Thinking & User Research Workshop"
        allowFullScreen
      />
    </div>
  );
}

/**
 * Metadata for the workshop design thinking page
 */
export const metadata = {
  title: 'Design Thinking & User Research Workshop',
  description: 'Validating for Impact: From Ideas to Actionable Insights. Expert workshop by Vitalijs Visnevskis.',
  keywords: ['design thinking', 'user research', 'workshop', 'validation', 'product development'],
  robots: {
    index: true,
    follow: true,
  },
};
