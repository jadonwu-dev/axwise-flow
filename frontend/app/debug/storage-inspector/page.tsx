'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { RefreshCw, Search, Download } from 'lucide-react';

export default function StorageInspectorPage() {
  const [storageData, setStorageData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('ed7f0192');

  const inspectStorage = () => {
    try {
      setLoading(true);

      const allData: any = {
        localStorage: {},
        sessionStorage: {},
        totalKeys: 0,
        searchResults: []
      };

      // Inspect localStorage
      for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i);
        if (key) {
          try {
            const value = localStorage.getItem(key);
            allData.localStorage[key] = {
              value: value,
              size: value ? value.length : 0,
              type: 'string'
            };

            // Try to parse as JSON
            if (value) {
              try {
                const parsed = JSON.parse(value);
                allData.localStorage[key].parsed = parsed;
                allData.localStorage[key].type = Array.isArray(parsed) ? 'array' : typeof parsed;
              } catch (e) {
                // Not JSON, keep as string
              }
            }
          } catch (e) {
            allData.localStorage[key] = { error: 'Failed to read' };
          }
        }
      }

      // Inspect sessionStorage
      for (let i = 0; i < sessionStorage.length; i++) {
        const key = sessionStorage.key(i);
        if (key) {
          try {
            const value = sessionStorage.getItem(key);
            allData.sessionStorage[key] = {
              value: value,
              size: value ? value.length : 0,
              type: 'string'
            };

            // Try to parse as JSON
            if (value) {
              try {
                const parsed = JSON.parse(value);
                allData.sessionStorage[key].parsed = parsed;
                allData.sessionStorage[key].type = Array.isArray(parsed) ? 'array' : typeof parsed;
              } catch (e) {
                // Not JSON, keep as string
              }
            }
          } catch (e) {
            allData.sessionStorage[key] = { error: 'Failed to read' };
          }
        }
      }

      allData.totalKeys = Object.keys(allData.localStorage).length + Object.keys(allData.sessionStorage).length;

      // Search for the term
      if (searchTerm) {
        const searchResults: any[] = [];

        // Search in localStorage
        Object.entries(allData.localStorage).forEach(([key, data]: [string, any]) => {
          const keyMatch = key.toLowerCase().includes(searchTerm.toLowerCase());
          const valueMatch = data.value && data.value.toLowerCase().includes(searchTerm.toLowerCase());

          if (keyMatch || valueMatch) {
            searchResults.push({
              storage: 'localStorage',
              key: key,
              matchType: keyMatch ? 'key' : 'value',
              data: data,
              preview: data.value ? data.value.substring(0, 200) + (data.value.length > 200 ? '...' : '') : ''
            });
          }
        });

        // Search in sessionStorage
        Object.entries(allData.sessionStorage).forEach(([key, data]: [string, any]) => {
          const keyMatch = key.toLowerCase().includes(searchTerm.toLowerCase());
          const valueMatch = data.value && data.value.toLowerCase().includes(searchTerm.toLowerCase());

          if (keyMatch || valueMatch) {
            searchResults.push({
              storage: 'sessionStorage',
              key: key,
              matchType: keyMatch ? 'key' : 'value',
              data: data,
              preview: data.value ? data.value.substring(0, 200) + (data.value.length > 200 ? '...' : '') : ''
            });
          }
        });

        allData.searchResults = searchResults;
      }

      setStorageData(allData);
    } catch (error) {
      console.error('Error inspecting storage:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    inspectStorage();
  }, [searchTerm]);

  const downloadStorageData = () => {
    if (!storageData) return;

    const content = JSON.stringify(storageData, null, 2);
    const blob = new Blob([content], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `storage-inspection-${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const viewFullData = (storage: string, key: string) => {
    const data = storage === 'localStorage' ? 
      storageData.localStorage[key] : 
      storageData.sessionStorage[key];

    const popup = window.open('', '_blank', 'width=1000,height=700');
    if (popup) {
      popup.document.write(`
        <html>
          <head><title>${storage}: ${key}</title></head>
          <body>
            <h1>${storage}: ${key}</h1>
            <p><strong>Type:</strong> ${data.type}</p>
            <p><strong>Size:</strong> ${data.size} characters</p>
            <hr>
            <h3>Raw Value:</h3>
            <pre style="white-space: pre-wrap; background: #f5f5f5; padding: 10px; max-height: 400px; overflow-y: auto;">${data.value || 'null'}</pre>
            ${data.parsed ? `
              <hr>
              <h3>Parsed JSON:</h3>
              <pre style="white-space: pre-wrap; background: #e8f4fd; padding: 10px; max-height: 400px; overflow-y: auto;">${JSON.stringify(data.parsed, null, 2)}</pre>
            ` : ''}
          </body>
        </html>
      `);
    }
  };

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-6xl mx-auto">
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-center">
                <RefreshCw className="h-6 w-6 animate-spin mr-2" />
                Inspecting browser storage...
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-6xl mx-auto space-y-6">
        <Card>
          <CardHeader>
            <CardTitle className="text-2xl flex items-center gap-2">
              <Search className="h-6 w-6" />
              Browser Storage Inspector
            </CardTitle>
            <div className="text-sm text-muted-foreground">
              <p>Comprehensive inspection of localStorage and sessionStorage</p>
            </div>
          </CardHeader>
        </Card>

        {/* Search */}
        <Card>
          <CardHeader>
            <CardTitle>🔍 Search Storage</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex gap-2 mb-4">
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Search for keys or values..."
                className="flex-1 px-3 py-2 border rounded-md"
              />
              <Button onClick={inspectStorage} variant="outline">
                <RefreshCw className="h-4 w-4 mr-2" />
                Refresh
              </Button>
              <Button onClick={downloadStorageData} variant="outline">
                <Download className="h-4 w-4 mr-2" />
                Download
              </Button>
            </div>

            {storageData?.searchResults && storageData.searchResults.length > 0 ? (
              <div className="space-y-3">
                <h4 className="font-semibold">Search Results ({storageData.searchResults.length} found):</h4>
                {storageData.searchResults.map((result: any, index: number) => (
                  <div key={index} className="p-3 border rounded bg-yellow-50">
                    <div className="flex justify-between items-start mb-2">
                      <div>
                        <p><strong>{result.storage}:</strong> {result.key}</p>
                        <p className="text-sm text-muted-foreground">
                          Match in: {result.matchType} | Type: {result.data.type} | Size: {result.data.size}
                        </p>
                      </div>
                      <Button
                        onClick={() => viewFullData(result.storage, result.key)}
                        variant="outline"
                        size="sm"
                      >
                        View Full
                      </Button>
                    </div>
                    <div className="text-sm bg-white p-2 rounded border">
                      <strong>Preview:</strong> {result.preview}
                    </div>
                  </div>
                ))}
              </div>
            ) : searchTerm ? (
              <div className="p-4 bg-red-50 border border-red-200 rounded">
                <p className="text-red-700">No results found for "{searchTerm}"</p>
              </div>
            ) : null}
          </CardContent>
        </Card>

        {/* Storage Summary */}
        <Card>
          <CardHeader>
            <CardTitle>📊 Storage Summary</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-4">
              <div className="p-4 bg-blue-50 border border-blue-200 rounded">
                <h4 className="font-semibold text-blue-800">localStorage</h4>
                <p className="text-blue-700">{Object.keys(storageData?.localStorage || {}).length} keys</p>
                <div className="mt-2 text-sm">
                  <p>Common keys:</p>
                  <ul className="list-disc list-inside">
                    {Object.keys(storageData?.localStorage || {}).slice(0, 5).map(key => (
                      <li key={key} className="truncate">{key}</li>
                    ))}
                  </ul>
                </div>
              </div>
              
              <div className="p-4 bg-green-50 border border-green-200 rounded">
                <h4 className="font-semibold text-green-800">sessionStorage</h4>
                <p className="text-green-700">{Object.keys(storageData?.sessionStorage || {}).length} keys</p>
                <div className="mt-2 text-sm">
                  <p>Common keys:</p>
                  <ul className="list-disc list-inside">
                    {Object.keys(storageData?.sessionStorage || {}).slice(0, 5).map(key => (
                      <li key={key} className="truncate">{key}</li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Simulation-Related Keys */}
        <Card>
          <CardHeader>
            <CardTitle>🚀 Simulation-Related Storage</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {Object.entries(storageData?.localStorage || {}).filter(([key]) => 
                key.toLowerCase().includes('simulation') || 
                key.toLowerCase().includes('interview') ||
                key.toLowerCase().includes('research')
              ).map(([key, data]: [string, any]) => (
                <div key={key} className="p-3 border rounded bg-purple-50">
                  <div className="flex justify-between items-start">
                    <div>
                      <p><strong>localStorage:</strong> {key}</p>
                      <p className="text-sm text-muted-foreground">
                        Type: {data.type} | Size: {data.size} characters
                      </p>
                      {data.type === 'array' && data.parsed && (
                        <p className="text-sm text-muted-foreground">
                          Array length: {data.parsed.length}
                        </p>
                      )}
                    </div>
                    <Button
                      onClick={() => viewFullData('localStorage', key)}
                      variant="outline"
                      size="sm"
                    >
                      View Full
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Actions */}
        <Card>
          <CardHeader>
            <CardTitle>🔧 Actions</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex gap-2 flex-wrap">
              <Button onClick={() => setSearchTerm('simulation')} variant="outline">
                Search "simulation"
              </Button>
              <Button onClick={() => setSearchTerm('ed7f0192')} variant="outline">
                Search "ed7f0192"
              </Button>
              <Button onClick={() => setSearchTerm('interview')} variant="outline">
                Search "interview"
              </Button>
              <Button onClick={() => setSearchTerm('api')} variant="outline">
                Search "api"
              </Button>
              <Button onClick={() => window.open('/unified-dashboard/simulation-history', '_blank')} variant="outline">
                Open Simulation History
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
