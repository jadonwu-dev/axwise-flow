/**
 * Simple test file that should pass in both CI and local environments
 */

import { describe, it, expect } from 'vitest';

describe('Simple test', () => {
  it('should pass', () => {
    expect(true).toBe(true);
  });

  it('should handle basic math', () => {
    expect(1 + 1).toBe(2);
  });

  it('should handle string operations', () => {
    expect('hello ' + 'world').toBe('hello world');
  });
});