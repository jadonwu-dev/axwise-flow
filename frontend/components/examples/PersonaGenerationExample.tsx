'use client';

import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { PersonaList } from '@/components/visualization/PersonaList';
import { apiClient } from '@/lib/apiClient';
import { Loader2 } from 'lucide-react';
import { type Persona } from '@/types/api';

/**
 * Example component demonstrating how to use the generatePersonaFromText method
 * with the returnAllPersonas option to generate multiple personas from a transcript.
 */
export function PersonaGenerationExample() {
  const [text, setText] = useState<string>('');
  const [personas, setPersonas] = useState<Persona[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const handleTextChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setText(e.target.value);
  };

  const handleGeneratePersonas = async () => {
    if (!text.trim()) {
      setError('Please enter some text to analyze');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      // Call the API with returnAllPersonas set to true
      const generatedPersonas = await apiClient.generatePersonaFromText(text, {
        llmProvider: 'gemini',
        llmModel: 'gemini-2.5-pro-preview-03-25',
        returnAllPersonas: true // This is the key option to get all personas
      });

      setPersonas(generatedPersonas);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred while generating personas');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Multi-Persona Generation Example</CardTitle>
          <CardDescription>
            Enter a transcript with multiple speakers to generate personas for each speaker
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <Textarea
            placeholder="Paste your interview transcript here..."
            className="min-h-[200px]"
            value={text}
            onChange={handleTextChange}
          />

          <div className="flex justify-end">
            <Button
              onClick={handleGeneratePersonas}
              disabled={isLoading || !text.trim()}
            >
              {isLoading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Generating Personas...
                </>
              ) : (
                'Generate Personas'
              )}
            </Button>
          </div>

          {error && (
            <div className="p-4 border border-red-300 bg-red-50 rounded-md text-red-700">
              {error}
            </div>
          )}
        </CardContent>
      </Card>

      {personas.length > 0 && (
        <PersonaList personas={personas} />
      )}
    </div>
  );
}
