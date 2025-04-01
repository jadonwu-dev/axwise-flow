'use client';

import { Card, CardContent } from '@/components/ui/card';
import { FileQuestion } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useRouter } from 'next/navigation';

/**
 * Component displayed when no analysis results are available
 */
const NoResultsView = (): JSX.Element => { // Add return type
  const router = useRouter();
  
  return (
    <Card className="w-full">
      <CardContent className="flex flex-col items-center justify-center py-12">
        <FileQuestion className="h-16 w-16 text-muted-foreground mb-4" />
        <h3 className="text-xl font-medium mb-2">No Analysis Results</h3>
        <p className="text-center text-muted-foreground mb-6 max-w-md">
          You haven&apos;t analyzed any interview data yet or no results are available.
 {/* Escape quote */}
          Upload your interview data and start analysis to see results here.
        </p>
        <Button 
          onClick={() => router.push('/unified-dashboard?tab=upload')}
          variant="outline"
        >
          Go to Upload
        </Button>
      </CardContent>
    </Card>
  );
};

export default NoResultsView;
