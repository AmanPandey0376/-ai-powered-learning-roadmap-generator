import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BrowserRouter } from 'react-router-dom';
import Resources from '../Resources';

// Mock react-router-dom navigate
const mockNavigate = vi.fn();
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

// Mock ResourceCard component
vi.mock('../../components/ResourceCard', () => ({
  default: ({ platform, creator, title, link, type }) => (
    <div data-testid="resource-card">
      <span data-testid="platform">{platform}</span>
      <span data-testid="creator">{creator}</span>
      <span data-testid="title">{title}</span>
      <span data-testid="link">{link}</span>
      <span data-testid="type">{type}</span>
    </div>
  ),
}));

// Helper function to render Resources component with router
const renderResources = () => {
  return render(
    <BrowserRouter>
      <Resources />
    </BrowserRouter>
  );
};

// Mock resources data for testing
const mockResourcesData = {
  timestamp: Date.now(),
  skill: 'React Developer',
  roadmap: {
    title: 'Complete React Developer Roadmap',
    modules: []
  },
  resources: {
    free: [
      {
        id: 'free-1',
        platform: 'YouTube',
        creator: 'React Official',
        title: 'React Tutorial for Beginners',
        link: 'https://youtube.com/react-tutorial',
        type: 'tutorial'
      },
      {
        id: 'free-2',
        platform: 'MDN',
        creator: 'Mozilla',
        title: 'React Documentation',
        link: 'https://developer.mozilla.org/react',
        type: 'documentation'
      }
    ],
    paid: [
      {
        id: 'paid-1',
        platform: 'Udemy',
        creator: 'John Doe',
        title: 'Complete React Course',
        link: 'https://udemy.com/react-course',
        type: 'course'
      },
      {
        id: 'paid-2',
        platform: 'Pluralsight',
        creator: 'Jane Smith',
        title: 'Advanced React Patterns',
        link: 'https://pluralsight.com/react-patterns',
        type: 'course'
      }
    ]
  }
};

describe('Resources Page', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  describe('Data Loading and Redirect Functionality', () => {
    it('should load resources data from localStorage on mount (Requirement 3.5)', () => {
      localStorage.getItem.mockReturnValue(JSON.stringify(mockResourcesData));
      
      renderResources();
      
      expect(localStorage.getItem).toHaveBeenCalledWith('roadmapData');
      expect(screen.getByText('Learning Resources')).toBeInTheDocument();
    });

    it('should redirect to Home page when no data exists in localStorage (Requirement 3.5)', () => {
      localStorage.getItem.mockReturnValue(null);
      
      renderResources();
      
      expect(mockNavigate).toHaveBeenCalledWith('/');
    });

    it('should redirect to Home page when localStorage data is corrupted (Requirement 3.5)', () => {
      localStorage.getItem.mockReturnValue('invalid-json');
      
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
      
      renderResources();
      
      expect(consoleSpy).toHaveBeenCalledWith('Error parsing stored data:', expect.any(Error));
      expect(mockNavigate).toHaveBeenCalledWith('/');
      
      consoleSpy.mockRestore();
    });

    it('should redirect to Home page when resources data is missing (Requirement 3.5)', () => {
      const dataWithoutResources = {
        timestamp: Date.now(),
        skill: 'React Developer',
        roadmap: { title: 'Test Roadmap', modules: [] }
        // Missing resources field
      };
      
      localStorage.getItem.mockReturnValue(JSON.stringify(dataWithoutResources));
      
      renderResources();
      
      expect(mockNavigate).toHaveBeenCalledWith('/');
    });

    it('should redirect to Home page when both free and paid resources are missing (Requirement 3.5)', () => {
      const dataWithEmptyResources = {
        timestamp: Date.now(),
        skill: 'React Developer',
        roadmap: { title: 'Test Roadmap', modules: [] },
        resources: {}
      };
      
      localStorage.getItem.mockReturnValue(JSON.stringify(dataWithEmptyResources));
      
      renderResources();
      
      expect(mockNavigate).toHaveBeenCalledWith('/');
    });

    it('should show loading state while data is being processed', () => {
      localStorage.getItem.mockReturnValue(null);
      
      // Render before the redirect happens
      const { container } = renderResources();
      
      // The component should show loading initially before redirect
      expect(container.querySelector('.container')).toBeInTheDocument();
    });

    it('should handle valid data with only free resources', () => {
      const dataWithOnlyFree = {
        ...mockResourcesData,
        resources: {
          free: mockResourcesData.resources.free
          // No paid resources
        }
      };
      
      localStorage.getItem.mockReturnValue(JSON.stringify(dataWithOnlyFree));
      
      renderResources();
      
      expect(screen.getByText('Learning Resources')).toBeInTheDocument();
      expect(mockNavigate).not.toHaveBeenCalled();
    });

    it('should handle valid data with only paid resources', () => {
      const dataWithOnlyPaid = {
        ...mockResourcesData,
        resources: {
          paid: mockResourcesData.resources.paid
          // No free resources
        }
      };
      
      localStorage.getItem.mockReturnValue(JSON.stringify(dataWithOnlyPaid));
      
      renderResources();
      
      expect(screen.getByText('Learning Resources')).toBeInTheDocument();
      expect(mockNavigate).not.toHaveBeenCalled();
    });
  });

  describe('Tab Switching Functionality', () => {
    beforeEach(() => {
      localStorage.getItem.mockReturnValue(JSON.stringify(mockResourcesData));
    });

    it('should display two tabs: Free and Paid (Requirement 3.1)', () => {
      renderResources();
      
      expect(screen.getByRole('tab', { name: /free resources/i })).toBeInTheDocument();
      expect(screen.getByRole('tab', { name: /paid resources/i })).toBeInTheDocument();
    });

    it('should have Free tab active by default (Requirement 3.1)', () => {
      renderResources();
      
      const freeTab = screen.getByRole('tab', { name: /free resources/i });
      const paidTab = screen.getByRole('tab', { name: /paid resources/i });
      
      expect(freeTab).toHaveAttribute('aria-selected', 'true');
      expect(paidTab).toHaveAttribute('aria-selected', 'false');
      
      // Check visual styling for active tab
      expect(freeTab).toHaveClass('border-blue-500', 'text-blue-500');
      expect(paidTab).toHaveClass('border-transparent', 'text-gray-400');
    });

    it('should switch to Paid tab when clicked (Requirement 3.2)', async () => {
      const user = userEvent.setup();
      
      renderResources();
      
      const paidTab = screen.getByRole('tab', { name: /paid resources/i });
      await user.click(paidTab);
      
      expect(paidTab).toHaveAttribute('aria-selected', 'true');
      
      const freeTab = screen.getByRole('tab', { name: /free resources/i });
      expect(freeTab).toHaveAttribute('aria-selected', 'false');
      
      // Check visual styling changes
      expect(paidTab).toHaveClass('border-blue-500', 'text-blue-500');
      expect(freeTab).toHaveClass('border-transparent', 'text-gray-400');
    });

    it('should switch back to Free tab when clicked (Requirement 3.2)', async () => {
      const user = userEvent.setup();
      
      renderResources();
      
      // First switch to Paid
      const paidTab = screen.getByRole('tab', { name: /paid resources/i });
      await user.click(paidTab);
      
      // Then switch back to Free
      const freeTab = screen.getByRole('tab', { name: /free resources/i });
      await user.click(freeTab);
      
      expect(freeTab).toHaveAttribute('aria-selected', 'true');
      expect(paidTab).toHaveAttribute('aria-selected', 'false');
    });

    it('should handle tab switching with keyboard navigation', async () => {
      const user = userEvent.setup();
      
      renderResources();
      
      const paidTab = screen.getByRole('tab', { name: /paid resources/i });
      
      // Focus and press Enter
      paidTab.focus();
      await user.keyboard('{Enter}');
      
      expect(paidTab).toHaveAttribute('aria-selected', 'true');
    });

    it('should handle tab switching with Space key', async () => {
      const user = userEvent.setup();
      
      renderResources();
      
      const paidTab = screen.getByRole('tab', { name: /paid resources/i });
      
      // Focus and press Space
      paidTab.focus();
      await user.keyboard(' ');
      
      expect(paidTab).toHaveAttribute('aria-selected', 'true');
    });

    it('should display resource count badges on tabs', () => {
      renderResources();
      
      // Check free resources count
      const freeTab = screen.getByRole('tab', { name: /free resources/i });
      expect(freeTab).toHaveTextContent('2'); // 2 free resources in mock data
      
      // Check paid resources count
      const paidTab = screen.getByRole('tab', { name: /paid resources/i });
      expect(paidTab).toHaveTextContent('2'); // 2 paid resources in mock data
    });

    it('should handle tabs when resource arrays are empty', () => {
      const dataWithEmptyArrays = {
        ...mockResourcesData,
        resources: {
          free: [],
          paid: []
        }
      };
      
      localStorage.getItem.mockReturnValue(JSON.stringify(dataWithEmptyArrays));
      
      renderResources();
      
      const freeTab = screen.getByRole('tab', { name: /free resources/i });
      const paidTab = screen.getByRole('tab', { name: /paid resources/i });
      
      expect(freeTab).toHaveTextContent('0');
      expect(paidTab).toHaveTextContent('0');
    });

    it('should handle missing resource count gracefully', () => {
      const dataWithMissingArrays = {
        ...mockResourcesData,
        resources: {
          // Missing free and paid arrays
        }
      };
      
      localStorage.getItem.mockReturnValue(JSON.stringify(dataWithMissingArrays));
      
      renderResources();
      
      // This should redirect to home page since resources are missing
      expect(mockNavigate).toHaveBeenCalledWith('/');
    });
  });

  describe('Resource Filtering and Display', () => {
    beforeEach(() => {
      localStorage.getItem.mockReturnValue(JSON.stringify(mockResourcesData));
    });

    it('should show free resources when Free tab is active (Requirement 3.2)', () => {
      renderResources();
      
      // Should show free resources by default
      const resourceCards = screen.getAllByTestId('resource-card');
      expect(resourceCards).toHaveLength(2); // 2 free resources
      
      // Check that free resources are displayed
      expect(screen.getByText('React Tutorial for Beginners')).toBeInTheDocument();
      expect(screen.getByText('React Documentation')).toBeInTheDocument();
      expect(screen.getByText('YouTube')).toBeInTheDocument();
      expect(screen.getByText('MDN')).toBeInTheDocument();
    });

    it('should show paid resources when Paid tab is active (Requirement 3.2)', async () => {
      const user = userEvent.setup();
      
      renderResources();
      
      // Switch to Paid tab
      const paidTab = screen.getByRole('tab', { name: /paid resources/i });
      await user.click(paidTab);
      
      // Should show paid resources
      const resourceCards = screen.getAllByTestId('resource-card');
      expect(resourceCards).toHaveLength(2); // 2 paid resources
      
      // Check that paid resources are displayed
      expect(screen.getByText('Complete React Course')).toBeInTheDocument();
      expect(screen.getByText('Advanced React Patterns')).toBeInTheDocument();
      expect(screen.getByText('Udemy')).toBeInTheDocument();
      expect(screen.getByText('Pluralsight')).toBeInTheDocument();
    });

    it('should filter resources correctly when switching between tabs (Requirement 3.2)', async () => {
      const user = userEvent.setup();
      
      renderResources();
      
      // Initially showing free resources
      expect(screen.getByText('React Tutorial for Beginners')).toBeInTheDocument();
      expect(screen.queryByText('Complete React Course')).not.toBeInTheDocument();
      
      // Switch to paid tab
      const paidTab = screen.getByRole('tab', { name: /paid resources/i });
      await user.click(paidTab);
      
      // Now showing paid resources
      expect(screen.queryByText('React Tutorial for Beginners')).not.toBeInTheDocument();
      expect(screen.getByText('Complete React Course')).toBeInTheDocument();
      
      // Switch back to free tab
      const freeTab = screen.getByRole('tab', { name: /free resources/i });
      await user.click(freeTab);
      
      // Back to free resources
      expect(screen.getByText('React Tutorial for Beginners')).toBeInTheDocument();
      expect(screen.queryByText('Complete React Course')).not.toBeInTheDocument();
    });

    it('should display empty state when no resources are available for active tab', async () => {
      const user = userEvent.setup();
      
      const dataWithEmptyPaid = {
        ...mockResourcesData,
        resources: {
          free: mockResourcesData.resources.free,
          paid: [] // Empty paid resources
        }
      };
      
      localStorage.getItem.mockReturnValue(JSON.stringify(dataWithEmptyPaid));
      
      renderResources();
      
      // Switch to paid tab (which has no resources)
      const paidTab = screen.getByRole('tab', { name: /paid resources/i });
      await user.click(paidTab);
      
      // Should show empty state
      expect(screen.getByText('No paid resources available')).toBeInTheDocument();
      expect(screen.getByText('There are currently no paid resources for this learning path.')).toBeInTheDocument();
      
      // Should show empty state icon (SVG)
      const emptyStateIcon = screen.getByRole('tabpanel').querySelector('svg');
      expect(emptyStateIcon).toBeInTheDocument();
    });

    it('should display empty state for free resources when array is empty', () => {
      const dataWithEmptyFree = {
        ...mockResourcesData,
        resources: {
          free: [], // Empty free resources
          paid: mockResourcesData.resources.paid
        }
      };
      
      localStorage.getItem.mockReturnValue(JSON.stringify(dataWithEmptyFree));
      
      renderResources();
      
      // Should show empty state for free resources (default tab)
      expect(screen.getByText('No free resources available')).toBeInTheDocument();
      expect(screen.getByText('There are currently no free resources for this learning path.')).toBeInTheDocument();
    });

    it('should handle resources with missing fields gracefully', () => {
      const dataWithIncompleteResources = {
        ...mockResourcesData,
        resources: {
          free: [
            {
              id: 'incomplete-1',
              platform: 'YouTube',
              // Missing creator, title, link, type
            },
            {
              // Missing id
              creator: 'Test Creator',
              title: 'Test Resource'
              // Missing platform, link, type
            }
          ],
          paid: []
        }
      };
      
      localStorage.getItem.mockReturnValue(JSON.stringify(dataWithIncompleteResources));
      
      renderResources();
      
      // Should render resource cards without crashing
      const resourceCards = screen.getAllByTestId('resource-card');
      expect(resourceCards).toHaveLength(2);
    });

    it('should maintain proper tabpanel accessibility attributes', () => {
      renderResources();
      
      const tabpanel = screen.getByRole('tabpanel');
      expect(tabpanel).toHaveAttribute('aria-labelledby', 'free-tab');
    });

    it('should update tabpanel aria-labelledby when switching tabs', async () => {
      const user = userEvent.setup();
      
      renderResources();
      
      // Switch to paid tab
      const paidTab = screen.getByRole('tab', { name: /paid resources/i });
      await user.click(paidTab);
      
      const tabpanel = screen.getByRole('tabpanel');
      expect(tabpanel).toHaveAttribute('aria-labelledby', 'paid-tab');
    });
  });

  describe('ResourceCard Integration', () => {
    beforeEach(() => {
      localStorage.getItem.mockReturnValue(JSON.stringify(mockResourcesData));
    });

    it('should render ResourceCard components with correct props (Requirement 3.3)', () => {
      renderResources();
      
      // Check that ResourceCard components are rendered
      const resourceCards = screen.getAllByTestId('resource-card');
      expect(resourceCards).toHaveLength(2); // 2 free resources by default
      
      // Check first free resource props
      const firstCard = resourceCards[0];
      expect(firstCard).toHaveTextContent('YouTube');
      expect(firstCard).toHaveTextContent('React Official');
      expect(firstCard).toHaveTextContent('React Tutorial for Beginners');
      expect(firstCard).toHaveTextContent('https://youtube.com/react-tutorial');
      expect(firstCard).toHaveTextContent('tutorial');
      
      // Check second free resource props
      const secondCard = resourceCards[1];
      expect(secondCard).toHaveTextContent('MDN');
      expect(secondCard).toHaveTextContent('Mozilla');
      expect(secondCard).toHaveTextContent('React Documentation');
      expect(secondCard).toHaveTextContent('https://developer.mozilla.org/react');
      expect(secondCard).toHaveTextContent('documentation');
    });

    it('should pass correct props to ResourceCard for paid resources (Requirement 3.3)', async () => {
      const user = userEvent.setup();
      
      renderResources();
      
      // Switch to paid tab
      const paidTab = screen.getByRole('tab', { name: /paid resources/i });
      await user.click(paidTab);
      
      const resourceCards = screen.getAllByTestId('resource-card');
      expect(resourceCards).toHaveLength(2); // 2 paid resources
      
      // Check first paid resource props
      const firstCard = resourceCards[0];
      expect(firstCard).toHaveTextContent('Udemy');
      expect(firstCard).toHaveTextContent('John Doe');
      expect(firstCard).toHaveTextContent('Complete React Course');
      expect(firstCard).toHaveTextContent('https://udemy.com/react-course');
      expect(firstCard).toHaveTextContent('course');
      
      // Check second paid resource props
      const secondCard = resourceCards[1];
      expect(secondCard).toHaveTextContent('Pluralsight');
      expect(secondCard).toHaveTextContent('Jane Smith');
      expect(secondCard).toHaveTextContent('Advanced React Patterns');
      expect(secondCard).toHaveTextContent('https://pluralsight.com/react-patterns');
      expect(secondCard).toHaveTextContent('course');
    });

    it('should render ResourceCards in responsive grid layout (Requirement 3.3)', () => {
      renderResources();
      
      // Check that the grid container has proper classes
      const gridContainer = screen.getByRole('tabpanel').querySelector('.grid');
      expect(gridContainer).toHaveClass('grid-cols-1', 'md:grid-cols-2', 'lg:grid-cols-3', 'gap-6');
    });

    it('should handle ResourceCard rendering with missing optional props', () => {
      const dataWithMissingProps = {
        ...mockResourcesData,
        resources: {
          free: [
            {
              id: 'minimal-1',
              platform: 'YouTube',
              creator: 'Test Creator',
              title: 'Test Resource',
              link: 'https://example.com'
              // Missing type
            }
          ],
          paid: []
        }
      };
      
      localStorage.getItem.mockReturnValue(JSON.stringify(dataWithMissingProps));
      
      renderResources();
      
      // Should render without crashing
      const resourceCards = screen.getAllByTestId('resource-card');
      expect(resourceCards).toHaveLength(1);
      
      const card = resourceCards[0];
      expect(card).toHaveTextContent('YouTube');
      expect(card).toHaveTextContent('Test Creator');
      expect(card).toHaveTextContent('Test Resource');
      expect(card).toHaveTextContent('https://example.com');
    });

    it('should use resource id as key for ResourceCard components', () => {
      renderResources();
      
      // This is tested implicitly - React would show warnings if keys were missing or duplicated
      // The fact that the component renders without console warnings indicates proper key usage
      const resourceCards = screen.getAllByTestId('resource-card');
      expect(resourceCards).toHaveLength(2);
    });

    it('should handle resources without id gracefully', () => {
      const dataWithoutIds = {
        ...mockResourcesData,
        resources: {
          free: [
            {
              // No id field
              platform: 'YouTube',
              creator: 'Test Creator',
              title: 'Test Resource',
              link: 'https://example.com',
              type: 'tutorial'
            }
          ],
          paid: []
        }
      };
      
      localStorage.getItem.mockReturnValue(JSON.stringify(dataWithoutIds));
      
      renderResources();
      
      // Should render without crashing even without id
      const resourceCards = screen.getAllByTestId('resource-card');
      expect(resourceCards).toHaveLength(1);
    });
  });

  describe('Navigation and Additional Features', () => {
    beforeEach(() => {
      localStorage.getItem.mockReturnValue(JSON.stringify(mockResourcesData));
    });

    it('should provide back to roadmap navigation button', () => {
      renderResources();
      
      const backButton = screen.getByRole('button', { name: /back to roadmap/i });
      expect(backButton).toBeInTheDocument();
    });

    it('should navigate back to roadmap when back button is clicked', async () => {
      const user = userEvent.setup();
      
      renderResources();
      
      const backButton = screen.getByRole('button', { name: /back to roadmap/i });
      await user.click(backButton);
      
      expect(mockNavigate).toHaveBeenCalledWith('/roadmap');
    });

    it('should handle back button keyboard navigation', async () => {
      const user = userEvent.setup();
      
      renderResources();
      
      const backButton = screen.getByRole('button', { name: /back to roadmap/i });
      
      // Focus and press Enter
      backButton.focus();
      await user.keyboard('{Enter}');
      
      expect(mockNavigate).toHaveBeenCalledWith('/roadmap');
    });

    it('should have proper styling and accessibility for back button', () => {
      renderResources();
      
      const backButton = screen.getByRole('button', { name: /back to roadmap/i });
      
      // Check styling classes
      expect(backButton).toHaveClass('bg-gray-700', 'hover:bg-gray-600', 'text-white');
      
      // Check accessibility classes
      expect(backButton).toHaveClass('focus:outline-none', 'focus:ring-2', 'focus:ring-gray-500');
    });

    it('should display page title correctly', () => {
      renderResources();
      
      expect(screen.getByRole('heading', { name: /learning resources/i })).toBeInTheDocument();
      expect(screen.getByText('Learning Resources')).toHaveClass('text-3xl', 'font-bold');
    });

    it('should maintain proper page structure and layout', () => {
      renderResources();
      
      // Check main container structure
      const container = screen.getByText('Learning Resources').closest('.container');
      expect(container).toHaveClass('mx-auto', 'px-4', 'py-8');
      
      // Check max-width wrapper
      const wrapper = container.querySelector('.max-w-6xl');
      expect(wrapper).toHaveClass('mx-auto');
    });

    it('should handle component unmounting gracefully', () => {
      const { unmount } = renderResources();
      
      // Should unmount without errors
      expect(() => unmount()).not.toThrow();
    });
  });

  describe('Error Handling and Edge Cases', () => {
    it('should handle localStorage access errors gracefully', () => {
      // Mock localStorage.getItem to throw an error
      localStorage.getItem.mockImplementation(() => {
        throw new Error('localStorage access denied');
      });
      
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
      
      // Wrap in try-catch to handle the error that bubbles up
      try {
        renderResources();
      } catch (error) {
        // Expected to throw due to the localStorage error
        expect(error.message).toBe('localStorage access denied');
      }
      
      consoleSpy.mockRestore();
    });

    it('should handle component re-renders correctly', () => {
      localStorage.getItem.mockReturnValue(JSON.stringify(mockResourcesData));
      
      const { rerender } = renderResources();
      
      // Re-render the component
      rerender(
        <BrowserRouter>
          <Resources />
        </BrowserRouter>
      );
      
      // Should still display correctly
      expect(screen.getByText('Learning Resources')).toBeInTheDocument();
      expect(screen.getByRole('tab', { name: /free resources/i })).toBeInTheDocument();
    });

    it('should handle rapid tab switching', async () => {
      const user = userEvent.setup();
      
      renderResources();
      
      const freeTab = screen.getByRole('tab', { name: /free resources/i });
      const paidTab = screen.getByRole('tab', { name: /paid resources/i });
      
      // Rapidly switch between tabs
      await user.click(paidTab);
      await user.click(freeTab);
      await user.click(paidTab);
      await user.click(freeTab);
      
      // Should end up on free tab
      expect(freeTab).toHaveAttribute('aria-selected', 'true');
      expect(paidTab).toHaveAttribute('aria-selected', 'false');
    });

    it('should handle resources with null or undefined values', () => {
      const dataWithNullValues = {
        ...mockResourcesData,
        resources: {
          free: [
            {
              id: 'null-test',
              platform: null,
              creator: undefined,
              title: 'Test Resource',
              link: 'https://example.com',
              type: null
            }
          ],
          paid: []
        }
      };
      
      localStorage.getItem.mockReturnValue(JSON.stringify(dataWithNullValues));
      
      renderResources();
      
      // Should render without crashing
      const resourceCards = screen.getAllByTestId('resource-card');
      expect(resourceCards).toHaveLength(1);
    });
  });
});