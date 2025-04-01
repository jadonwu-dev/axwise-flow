'use client';

import React, { useEffect, useCallback, useMemo, useState } from 'react'; 
import { useAnalysisHistory } from '@/store/useAnalysisStore'; 
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from '@/components/ui/dropdown-menu'; 
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'; 
import { Input } from '@/components/ui/input'; 
import { Loader2, ChevronDown, ArrowUpDown, ChevronRight, FileText, Calendar, Clock } from 'lucide-react'; 
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'; 
import { Badge } from '@/components/ui/badge';
import { DetailedAnalysisResult } from '@/types/api';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { useRouter } from 'next/navigation';
import { useToast } from '@/components/providers/toast-provider'; 

/**
 * Props interface for HistoryTabClient
 */
interface HistoryTabClientProps {
  // initialAnalyses: DetailedAnalysisResult[]; // Removed unused prop
  sortBy: 'createdAt' | 'fileName'; 
  sortDirection: 'asc' | 'desc';
  filterStatus: 'all' | 'completed' | 'pending' | 'failed';
}

/**
 * Client component for displaying analysis history 
 */
const HistoryTabClient = (props: HistoryTabClientProps) => { // Accept props object
  const router = useRouter();
  const { showToast } = useToast(); 
  
  // Get history state from the store
  const { 
    history, 
    isLoading, 
    error, 
    filters: storeFilters, 
    setFilters, 
    fetchHistory 
  } = useAnalysisHistory();
  
  // Removed unused setCurrentAnalysis
  
  // Memoize the filter change callbacks
  const toggleSortDirection = useCallback(() => {
    setFilters({ 
      sortDirection: storeFilters.sortDirection === 'asc' ? 'desc' : 'asc' 
    });
  }, [storeFilters.sortDirection, setFilters]);
  
  const changeSortBy = useCallback((field: 'createdAt' | 'fileName') => {
    setFilters({ sortBy: field });
  }, [setFilters]);
  
  const changeStatusFilter = useCallback((status: 'all' | 'completed' | 'pending' | 'failed') => {
    setFilters({ status });
  }, [setFilters]);
  
  // Memoize the handleSelectAnalysis function
  const handleSelectAnalysis = useCallback((analysis: DetailedAnalysisResult) => {
    // Removed setCurrentAnalysis call
    
    // Navigate to visualization tab with the analysis ID
    const analyzeUrl = `/unified-dashboard/visualize?analysisId=${analysis.id}&timestamp=${Date.now()}`;
    
    // Use Next.js router for navigation
    router.push(analyzeUrl);
  }, [router]); 
  
  // Fetch history only when filters change or on mount
  useEffect(() => { 
    // Set initial filters from props when component mounts or props change
    setFilters({
        sortBy: props.sortBy, // Access via props
        sortDirection: props.sortDirection, // Access via props
        status: props.filterStatus // Access via props
    });
    fetchHistory();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [props.sortBy, props.sortDirection, props.filterStatus, fetchHistory]); 
  
  // Format file size for display
  const formatFileSize = useMemo(() => (bytes: number | undefined) => {
    if (!bytes) return 'Unknown';
    const kb = bytes / 1024;
    if (kb < 1024) return `${kb.toFixed(2)} KB`;
    const mb = kb / 1024;
    return `${mb.toFixed(2)} MB`;
  }, []);
  
  // Get status badge with valid variants - Simplified to return JSX directly
  const getStatusBadge = useCallback((status: string) => { 
    switch (status) {
      case 'completed':
        return <Badge variant="secondary">Completed</Badge>;
      case 'pending': case 'processing': // Treat processing as pending
        return <Badge variant="outline">Pending</Badge>;
      case 'failed':
        return <Badge variant="destructive">Failed</Badge>;
      default:
        return <Badge variant="outline">Unknown</Badge>;
    }
  }, []); 
  
  // Loading state
  if (isLoading && history.length === 0) {
    return (
      <Card className="w-full">
        <CardContent className="flex justify-center items-center py-12">
          <div className="flex flex-col items-center space-y-4">
            <Loader2 className="h-8 w-8 animate-spin text-primary" />
            <p className="text-muted-foreground">Loading analysis history...</p>
          </div>
        </CardContent>
      </Card>
    );
  }
  
  // Error state
  if (error && history.length === 0) {
    return (
      <Alert variant="destructive">
        <AlertTitle>Error Loading History</AlertTitle>
        <AlertDescription>{error.message}</AlertDescription>
      </Alert>
    );
  }
  
  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle>Analysis History</CardTitle>
        <CardDescription>
          View and manage your previous analyses
        </CardDescription>
      </CardHeader>
      
      <CardContent>
        {/* Filters */}
        <div className="flex flex-col md:flex-row gap-4 mb-6">
          <div className="flex-1">
            <Input
              placeholder="Search analyses..."
              className="w-full"
              // Implement search functionality if needed
            />
          </div>
          
          <div className="flex gap-2">
            <Select
              value={storeFilters.status} // Use storeFilters value
              onValueChange={(value) => changeStatusFilter(value as any)}
            >
              <SelectTrigger className="w-[180px]">
                <SelectValue placeholder="Status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Statuses</SelectItem>
                <SelectItem value="completed">Completed</SelectItem>
                <SelectItem value="pending">Pending</SelectItem>
                <SelectItem value="failed">Failed</SelectItem>
              </SelectContent>
            </Select>
            
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="outline" className="ml-auto">
                  Sort By <ChevronDown className="ml-2 h-4 w-4" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuItem onClick={() => changeSortBy('createdAt')}>
                  Date {storeFilters.sortBy === 'createdAt' && '✓'}
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => changeSortBy('fileName')}>
                  File Name {storeFilters.sortBy === 'fileName' && '✓'}
                </DropdownMenuItem>
                <DropdownMenuItem onClick={toggleSortDirection}>
                  {storeFilters.sortDirection === 'desc' ? 'Newest First ✓' : 'Oldest First ✓'}
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>
        
        {/* Analysis Table */}
        {history.length > 0 ? (
          <div className="rounded-md border">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-[200px]">
                    <div className="flex items-center space-x-1">
                      <span>File Name</span>
                      <Button 
                        variant="ghost" 
                        size="sm" 
                        className="ml-1 h-8 w-8 p-0"
                        onClick={() => {
                          changeSortBy('fileName');
                          if (storeFilters.sortBy === 'fileName') { // Use storeFilters
                            toggleSortDirection();
                          }
                        }}
                      >
                        <ArrowUpDown className="h-4 w-4" />
                      </Button>
                    </div>
                  </TableHead>
                  <TableHead>
                    <div className="flex items-center space-x-1">
                      <span>Date</span>
                      <Button 
                        variant="ghost" 
                        size="sm" 
                        className="ml-1 h-8 w-8 p-0"
                        onClick={() => {
                          changeSortBy('createdAt');
                          if (storeFilters.sortBy === 'createdAt') { // Use storeFilters
                            toggleSortDirection();
                          }
                        }}
                      >
                        <ArrowUpDown className="h-4 w-4" />
                      </Button>
                    </div>
                  </TableHead>
                  <TableHead className="hidden md:table-cell">Status</TableHead>
                  <TableHead className="hidden md:table-cell">Size</TableHead>
                  <TableHead className="hidden md:table-cell">Provider</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {history.map((analysis) => (
                  <TableRow key={analysis.id}>
                    <TableCell className="font-medium">
                      {analysis.fileName.length > 20
                        ? `${analysis.fileName.substring(0, 20)}...`
                        : analysis.fileName}
                    </TableCell>
                    <TableCell>
                      {new Date(analysis.createdAt).toLocaleString()}
                    </TableCell>
                    <TableCell className="hidden md:table-cell">
                      {getStatusBadge(analysis.status)}
                    </TableCell>
                    <TableCell className="hidden md:table-cell">
                      {formatFileSize(analysis.fileSize)}
                    </TableCell>
                    <TableCell className="hidden md:table-cell">
                      {analysis.llmProvider || 'Unknown'}
                    </TableCell>
                    <TableCell className="text-right">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleSelectAnalysis(analysis)}
                        disabled={analysis.status !== 'completed'}
                      >
                        <span className="sr-only md:not-sr-only md:inline-block mr-2">
                          View
                        </span>
                        <ChevronRight className="h-4 w-4" />
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        ) : (
          <div className="text-center py-8 border rounded-md">
            <FileText className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
            <h3 className="text-lg font-medium mb-2">No analyses found</h3>
            <p className="text-muted-foreground mb-4">
              You haven&apos;t performed any analyses yet or none match your current filters. {/* Escape quote */}
            </p>
            <Button 
              onClick={() => {
                const cacheBuster = Date.now();
                router.push(`/unified-dashboard/upload?_=${cacheBuster}`);
              }}
              variant="outline"
            >
              Start a New Analysis
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default HistoryTabClient;