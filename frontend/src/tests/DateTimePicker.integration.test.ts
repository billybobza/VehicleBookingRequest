import { describe, it, expect } from 'vitest';

describe('DateTimePicker Integration', () => {
  it('can import DateTimePicker component', async () => {
    const module = await import('../components/DateTimePicker.svelte');
    expect(module.default).toBeDefined();
  });

  it('component has expected structure', async () => {
    const module = await import('../components/DateTimePicker.svelte');
    const component = module.default;
    
    // Check that it's a Svelte component
    expect(component).toBeDefined();
    expect(typeof component).toBe('function');
  });

  it('component exports expected properties', async () => {
    const module = await import('../components/DateTimePicker.svelte');
    const component = module.default;
    
    // Verify the component has the expected structure for Svelte 5
    expect(component).toBeDefined();
    expect(typeof component).toBe('function');
    
    // In Svelte 5, components are functions that can be used with mount()
    // We just verify the import works without errors
    expect(component.name).toBeDefined();
  });
});