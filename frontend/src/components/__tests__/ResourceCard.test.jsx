import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import ResourceCard from '../ResourceCard';

// Mock window.open
const mockOpen = vi.fn();
Object.defineProperty(window, 'open', {
  value: mockOpen,
  writable: true,
});

describe('ResourceCard', () => {
  const mockProps = {
    platform: 'YouTube',
    creator: 'John Doe',
    title: 'Learn React in 30 Days',
    link: 'https://example.com/course',
    type: 'course'
  };

  beforeEach(() => {
    mockOpen.mockClear();
  });

  it('renders resource information correctly', () => {
    render(<ResourceCard {...mockProps} />);
    
    expect(screen.getByText('YouTube')).toBeInTheDocument();
    expect(screen.getByText('Learn React in 30 Days')).toBeInTheDocument();
    expect(screen.getByText('by')).toBeInTheDocument();
    expect(screen.getByText('John Doe')).toBeInTheDocument();
    expect(screen.getByText('course')).toBeInTheDocument();
  });

  it('opens link in new tab when button is clicked', () => {
    render(<ResourceCard {...mockProps} />);
    
    const button = screen.getByRole('button', { name: /open.*learn react.*youtube/i });
    fireEvent.click(button);
    
    expect(mockOpen).toHaveBeenCalledWith(
      'https://example.com/course',
      '_blank',
      'noopener,noreferrer'
    );
  });

  it('renders without type when not provided', () => {
    const propsWithoutType = { ...mockProps };
    delete propsWithoutType.type;
    
    render(<ResourceCard {...propsWithoutType} />);
    
    expect(screen.queryByText('course')).not.toBeInTheDocument();
    expect(screen.getByText('YouTube')).toBeInTheDocument();
  });

  it('has proper accessibility attributes', () => {
    render(<ResourceCard {...mockProps} />);
    
    const button = screen.getByRole('button');
    expect(button).toHaveAttribute('aria-label', 'Open Learn React in 30 Days on YouTube');
  });
});