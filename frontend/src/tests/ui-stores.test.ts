import { describe, it, expect, vi, beforeEach } from 'vitest';
import { get } from 'svelte/store';
import { loading, setLoading, errors, addError, removeError, clearErrors } from '../stores/ui.js';

describe('UI Stores', () => {
  beforeEach(() => {
    // Reset stores
    loading.set({});
    errors.set([]);
    vi.clearAllTimers();
    vi.useFakeTimers();
  });

  describe('Loading Store', () => {
    it('should manage loading states', () => {
      setLoading('test', true);
      expect(get(loading)).toEqual({ test: true });

      setLoading('test', false);
      expect(get(loading)).toEqual({ test: false });

      setLoading('another', true);
      expect(get(loading)).toEqual({ test: false, another: true });
    });
  });

  describe('Error Store', () => {
    it('should add errors with auto-generated id and timestamp', () => {
      addError({
        code: 'TEST_ERROR',
        message: 'Test error message'
      });

      const currentErrors = get(errors);
      expect(currentErrors).toHaveLength(1);
      expect(currentErrors[0]).toMatchObject({
        code: 'TEST_ERROR',
        message: 'Test error message'
      });
      expect(currentErrors[0].id).toBeDefined();
      expect(currentErrors[0].timestamp).toBeDefined();
    });

    it('should remove specific errors', () => {
      addError({
        code: 'ERROR_1',
        message: 'First error'
      });
      addError({
        code: 'ERROR_2',
        message: 'Second error'
      });

      let currentErrors = get(errors);
      expect(currentErrors).toHaveLength(2);

      removeError(currentErrors[0].id);
      currentErrors = get(errors);
      expect(currentErrors).toHaveLength(1);
      expect(currentErrors[0].code).toBe('ERROR_2');
    });

    it('should clear all errors', () => {
      addError({ code: 'ERROR_1', message: 'First error' });
      addError({ code: 'ERROR_2', message: 'Second error' });

      expect(get(errors)).toHaveLength(2);

      clearErrors();
      expect(get(errors)).toHaveLength(0);
    });

    it('should auto-remove errors after 5 seconds', () => {
      addError({
        code: 'AUTO_REMOVE',
        message: 'This should auto-remove'
      });

      expect(get(errors)).toHaveLength(1);

      // Fast-forward 5 seconds
      vi.advanceTimersByTime(5000);

      expect(get(errors)).toHaveLength(0);
    });
  });
});