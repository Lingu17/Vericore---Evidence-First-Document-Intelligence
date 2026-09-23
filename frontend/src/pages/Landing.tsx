import { MarketingNavbar } from '../components/marketing/MarketingNavbar';
import { HeroSection } from '../components/marketing/HeroSection';
import { HowItWorks } from '../components/marketing/HowItWorks';
import { EvidenceSection } from '../components/marketing/EvidenceSection';
import { UseCases } from '../components/marketing/UseCases';
import { Features } from '../components/marketing/Features';
import { SecuritySection } from '../components/marketing/SecuritySection';
import { FinalCTA } from '../components/marketing/FinalCTA';
import { Footer } from '../components/marketing/Footer';
import { ScrollManager } from '../lib/scroll';

export function Landing() {
  return (
    <div className="flex min-h-0 flex-1 flex-col overflow-y-auto bg-white scroll-smooth">
      <ScrollManager />
      <MarketingNavbar />
      <main className="flex-1">
        <HeroSection />
        <HowItWorks />
        <EvidenceSection />
        <UseCases />
        <Features />
        <SecuritySection />
        <FinalCTA />
      </main>
      <Footer />
    </div>
  );
}