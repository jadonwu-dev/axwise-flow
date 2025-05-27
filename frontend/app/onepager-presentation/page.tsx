/**
 * AxWise Onepager Presentation
 *
 * Serves the original HTML onepager presentation via API route
 * to ensure all assets (CSS, images, JS) load correctly.
 */
export default function OnepagerPresentationPage() {
  return (
    <div style={{ width: '100%', height: '100vh', margin: 0, padding: 0 }}>
      <iframe
        src="/api/onepager-presentation"
        style={{
          width: '100%',
          height: '100%',
          border: 'none',
          margin: 0,
          padding: 0,
        }}
        title="AxWise Onepager Presentation"
        allowFullScreen
      />
    </div>
  );
}

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
