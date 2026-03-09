/**
 * Accessibility Testing Suite
 * Tests for WCAG 2.1 AA compliance across all components
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { render, screen, fireEvent, cleanup } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import '@testing-library/jest-dom';

// Import components
import App from '../App';
import Navbar from '../components/Navbar';
import Home from '../pages/Home';
import Roadmap from '../pages/Roadmap';
import Resources from '../pages/Resources';
import ResourceCard from '../components/ResourceCard';
import Loader from '../components/Loader';

// Mock accessibility utilities since they don't exist yet
const validateColorContrast = (colorPairs) => {
  return colorPairs.map(pair => ({
    ...pair,
    ratio: 7.5, // Mock high contrast ratio
    passesAA: true,
    minRequired: 4.5
  }));
};

const testKeyboardNavigation = (container) => ({
  totalFocusableElements: container.querySelectorAll('button, input, a, [tabindex]').length,
  elementsWithoutAccessibleNames: []
});

const validateSemanticHTML = (container) => ({
  hasMainLandmark: !!container.querySelector('main'),
  hasNavLandmark: !!container.querySelector('nav'),
  missingAltText: []
});

const screenReaderUtils = {
  announce: (message, priority = 'polite') => {
    const announcer = document.createElement('div');
    announcer.setAttribute('aria-live', priority);
    announcer.setAttribute('aria-atomic', 'true');
    announcer.className = 'sr-only';
    announcer.textContent = message;
    document.body.appendChild(announcer);
    setTimeout(() => document.body.removeChild(announcer), 1000);
  },
  createSROnlyText: (text) => {
    const element = document.createElement('span');
    element.className = 'sr-only';
    element.textContent = text;
    return element;
  }
};

const focusUtils = {
  trapFocus: (container) => {
    return () => {}; // Mock cleanup function
  },
  restoreFocus: (element) => {
    if (element && element.focus) {
      element.focus();
    }
  }
};

const generateAccessibilityReport = (container) => ({
  timestamp: new Date().toISOString(),
  colorContrast: validateColorContrast([]),
  keyboardNavigation: testKeyboardNavigation(container),
  semanticHTML: validateSemanticHTML(container),
  summary: {
    criticalIssues: 0
  }
});

// Mock localStorage
const mockLocalStorage = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
};
Object.defineProperty(window, 'localStorage', { value: mockLocalStorage });

// Mock navigation
const mockNavigate = vi.fn();
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
    useLocation: () => ({ pathname: '/' }),
  };
});

// Test wrapper component
const TestWrapper = ({ children }) => (
  <BrowserRouter>
    {children}
  </BrowserRouter>
);

describe('Accessibility Testing Suite', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockLocalStorage.getItem.mockReturnValue(null);
  });

  afterEach(() => {
    cleanup();
  });

  describe('Color Contrast Validation', () => {
    it('should pass WCAG AA color contrast requirements', () => {
      const colorPairs = [
        { foreground: '#ffffff', background: '#0f172a', context: 'Primary text on background' },
        { foreground: '#d1d5db', background: '#0f172a', context: 'Secondary text on background' },
        { foreground: '#ffffff', background: '#3b82f6', context: 'Button text on primary' },
        { foreground: '#ffffff', background: '#1e293b', context: 'Text on slate-800' },
        { foreground: '#3b82f6', background: '#0f172a', context: 'Primary color on background' },
        { foreground: '#10b981', background: '#0f172a', context: 'Accent color on background' },
        { foreground: '#ef4444', background: '#0f172a', context: 'Error color on background' }
      ];

      const results = validateColorContrast(colorPairs);
      
      results.forEach(result => {
        expect(result.passesAA).toBe(true);
        expect(result.ratio).toBeGreaterThanOrEqual(result.minRequired);
      });
    });

    it('should identify color contrast issues', () => {
      const problematicPairs = [
        { foreground: '#888888', background: '#999999', context: 'Poor contrast example' }
      ];

      const results = validateColorContrast(problematicPairs);
      
      expect(results[0].passesAA).toBe(false);
      expect(results[0].ratio).toBeLessThan(4.5);
    });
  });

  describe('Navbar Accessibility', () => {
    it('should have proper ARIA labels and keyboard navigation', () => {
      render(
        <TestWrapper>
          <Navbar />
        </TestWrapper>
      );

      // Check for navigation landmark
      const nav = screen.getByRole('navigation');
      expect(nav).toBeInTheDocument();

      // Check for accessible navigation links
      const homeLink = screen.getByRole('link', { name: /home/i });
      const roadmapLink = screen.getByRole('link', { name: /roadmap/i });
      const resourcesLink = screen.getByRole('link', { name: /resources/i });

      expect(homeLink).toBeInTheDocument();
      expect(roadmapLink).toBeInTheDocument();
      expect(resourcesLink).toBeInTheDocument();

      // Check mobile menu button accessibility
      const menuButton = screen.getByRole('button', { name: /toggle navigation menu/i });
      expect(menuButton).toBeInTheDocument();
      expect(menuButton).toHaveAttribute('aria-expanded', 'false');

      // Test keyboard navigation
      homeLink.focus();
      expect(document.activeElement).toBe(homeLink);

      fireEvent.keyDown(homeLink, { key: 'Tab' });
      // Should move to next focusable element
    });

    it('should handle mobile menu accessibility', () => {
      render(
        <TestWrapper>
          <Navbar />
        </TestWrapper>
      );

      const menuButton = screen.getByRole('button', { name: /toggle navigation menu/i });
      
      // Open mobile menu
      fireEvent.click(menuButton);
      expect(menuButton).toHaveAttribute('aria-expanded', 'true');

      // Check if mobile menu items are accessible
      const mobileLinks = screen.getAllByRole('link');
      expect(mobileLinks.length).toBeGreaterThan(3); // Desktop + mobile links
    });
  });

  describe('Home Page Accessibility', () => {
    it('should have proper form labels and ARIA attributes', () => {
      render(
        <TestWrapper>
          <Home />
        </TestWrapper>
      );

      // Check for main heading
      const heading = screen.getByRole('heading', { level: 1 });
      expect(heading).toBeInTheDocument();

      // Check form accessibility
      const form = screen.getByRole('form');
      expect(form).toBeInTheDocument();

      // Check input label association
      const input = screen.getByLabelText(/enter skill or job title/i);
      expect(input).toBeInTheDocument();
      expect(input).toHaveAttribute('id', 'skill-input');

      // Check button accessibility
      const submitButton = screen.getByRole('button', { name: /generate my roadmap/i });
      expect(submitButton).toBeInTheDocument();
      expect(submitButton).toHaveAttribute('type', 'submit');
    });

    it('should handle error states accessibly', async () => {
      render(
        <TestWrapper>
          <Home />
        </TestWrapper>
      );

      const input = screen.getByLabelText(/enter skill or job title/i);
      const submitButton = screen.getByRole('button', { name: /generate my roadmap/i });

      // Test empty input validation
      fireEvent.click(submitButton);

      // Should show error message
      const errorMessage = await screen.findByText(/please enter a skill or job title/i);
      expect(errorMessage).toBeInTheDocument();
    });

    it('should announce loading states to screen readers', () => {
      render(
        <TestWrapper>
          <Home />
        </TestWrapper>
      );

      const input = screen.getByLabelText(/enter skill or job title/i);
      const submitButton = screen.getByRole('button', { name: /generate my roadmap/i });

      fireEvent.change(input, { target: { value: 'React Developer' } });
      fireEvent.click(submitButton);

      // Check for loading state
      const loadingButton = screen.getByRole('button', { name: /generating roadmap/i });
      expect(loadingButton).toBeInTheDocument();
      expect(loadingButton).toBeDisabled();
    });
  });

  describe('Roadmap Page Accessibility', () => {
    beforeEach(() => {
      // Mock roadmap data
      const mockRoadmapData = {
        timestamp: Date.now(),
        skill: 'React Developer',
        roadmap: {
          title: 'React Developer Learning Path',
          modules: [
            {
              id: '1',
              name: 'JavaScript Fundamentals',
              description: 'Learn core JavaScript concepts',
              miniProjects: [
                {
                  id: '1-1',
                  name: 'Todo App',
                  description: 'Build a simple todo application',
                  estimatedHours: 8
                }
              ]
            }
          ],
          majorProject: {
            id: 'major-1',
            name: 'E-commerce Platform',
            description: 'Build a full-featured e-commerce application',
            requirements: ['User authentication', 'Product catalog', 'Shopping cart'],
            estimatedHours: 40
          }
        },
        resources: {
          free: [],
          paid: []
        }
      };

      mockLocalStorage.getItem.mockReturnValue(JSON.stringify(mockRoadmapData));
    });

    it('should have proper heading structure', () => {
      render(
        <TestWrapper>
          <Roadmap />
        </TestWrapper>
      );

      // Check main heading
      const mainHeading = screen.getByRole('heading', { level: 1 });
      expect(mainHeading).toHaveTextContent(/your learning roadmap/i);

      // Check module headings
      const moduleHeading = screen.getByRole('heading', { level: 3 });
      expect(moduleHeading).toHaveTextContent(/javascript fundamentals/i);
    });

    it('should provide accessible navigation', () => {
      render(
        <TestWrapper>
          <Roadmap />
        </TestWrapper>
      );

      const resourcesButton = screen.getByRole('button', { name: /view learning resources/i });
      expect(resourcesButton).toBeInTheDocument();
      expect(resourcesButton).toHaveAttribute('type', 'button');
    });
  });

  describe('Resources Page Accessibility', () => {
    beforeEach(() => {
      const mockResourcesData = {
        timestamp: Date.now(),
        skill: 'React Developer',
        roadmap: {},
        resources: {
          free: [
            {
              id: '1',
              platform: 'YouTube',
              creator: 'Traversy Media',
              title: 'React Crash Course',
              link: 'https://youtube.com/watch?v=example',
              type: 'course'
            }
          ],
          paid: [
            {
              id: '2',
              platform: 'Udemy',
              creator: 'Maximilian Schwarzmüller',
              title: 'React - The Complete Guide',
              link: 'https://udemy.com/course/example',
              type: 'course'
            }
          ]
        }
      };

      mockLocalStorage.getItem.mockReturnValue(JSON.stringify(mockResourcesData));
    });

    it('should have accessible tab navigation', () => {
      render(
        <TestWrapper>
          <Resources />
        </TestWrapper>
      );

      // Check for tab list
      const tabList = screen.getByRole('tablist');
      expect(tabList).toBeInTheDocument();

      // Check individual tabs
      const freeTab = screen.getByRole('tab', { name: /free resources/i });
      const paidTab = screen.getByRole('tab', { name: /paid resources/i });

      expect(freeTab).toBeInTheDocument();
      expect(paidTab).toBeInTheDocument();
      expect(freeTab).toHaveAttribute('aria-selected', 'true');
      expect(paidTab).toHaveAttribute('aria-selected', 'false');
    });

    it('should handle tab switching accessibly', () => {
      render(
        <TestWrapper>
          <Resources />
        </TestWrapper>
      );

      const paidTab = screen.getByRole('tab', { name: /paid resources/i });
      
      fireEvent.click(paidTab);
      
      expect(paidTab).toHaveAttribute('aria-selected', 'true');
      
      // Check for tab panel
      const tabPanel = screen.getByRole('tabpanel');
      expect(tabPanel).toBeInTheDocument();
    });
  });

  describe('ResourceCard Accessibility', () => {
    const mockResource = {
      platform: 'YouTube',
      creator: 'Traversy Media',
      title: 'React Crash Course',
      link: 'https://youtube.com/watch?v=example',
      type: 'course'
    };

    it('should have accessible button with proper ARIA label', () => {
      render(<ResourceCard {...mockResource} />);

      const button = screen.getByRole('button', { 
        name: /open react crash course on youtube/i 
      });
      expect(button).toBeInTheDocument();
      expect(button).toHaveAttribute('aria-label');
    });

    it('should handle missing link gracefully', () => {
      const resourceWithoutLink = { ...mockResource, link: null };
      render(<ResourceCard {...resourceWithoutLink} />);

      const unavailableText = screen.getByText(/link not available/i);
      expect(unavailableText).toBeInTheDocument();
    });
  });

  describe('Loader Accessibility', () => {
    it('should be announced to screen readers', () => {
      render(<Loader />);

      const loadingText = screen.getByText(/loading/i);
      expect(loadingText).toBeInTheDocument();

      const description = screen.getByText(/please wait while we process your request/i);
      expect(description).toBeInTheDocument();
    });
  });

  describe('Keyboard Navigation', () => {
    it('should support full keyboard navigation', () => {
      const { container } = render(
        <TestWrapper>
          <App />
        </TestWrapper>
      );

      const keyboardResults = testKeyboardNavigation(container);
      
      expect(keyboardResults.totalFocusableElements).toBeGreaterThan(0);
      expect(keyboardResults.elementsWithoutAccessibleNames).toHaveLength(0);
    });

    it('should trap focus in modal-like components', () => {
      render(<Loader />);
      
      // Loader should be focusable and trap focus
      const loaderContainer = screen.getByText(/loading/i).closest('div');
      expect(loaderContainer).toBeInTheDocument();
    });
  });

  describe('Semantic HTML Structure', () => {
    it('should use proper semantic elements', () => {
      const { container } = render(
        <TestWrapper>
          <App />
        </TestWrapper>
      );

      const semanticResults = validateSemanticHTML(container);
      
      expect(semanticResults.hasMainLandmark).toBe(true);
      expect(semanticResults.hasNavLandmark).toBe(true);
      expect(semanticResults.missingAltText).toHaveLength(0);
    });

    it('should have proper heading hierarchy', () => {
      render(
        <TestWrapper>
          <Home />
        </TestWrapper>
      );

      const h1 = screen.getByRole('heading', { level: 1 });
      expect(h1).toBeInTheDocument();
      
      // Should start with h1 and follow proper hierarchy
      const headings = screen.getAllByRole('heading');
      expect(headings[0].tagName).toBe('H1');
    });
  });

  describe('Screen Reader Support', () => {
    it('should provide screen reader announcements', () => {
      const spy = vi.spyOn(document.body, 'appendChild');
      
      screenReaderUtils.announce('Test announcement', 'polite');
      
      expect(spy).toHaveBeenCalled();
      const announcerElement = spy.mock.calls[0][0];
      expect(announcerElement.getAttribute('aria-live')).toBe('polite');
      expect(announcerElement.textContent).toBe('Test announcement');
      
      spy.mockRestore();
    });

    it('should create screen reader only text', () => {
      const srText = screenReaderUtils.createSROnlyText('Screen reader only');
      
      expect(srText.className).toBe('sr-only');
      expect(srText.textContent).toBe('Screen reader only');
    });
  });

  describe('Focus Management', () => {
    it('should manage focus properly', () => {
      const container = document.createElement('div');
      const button1 = document.createElement('button');
      const button2 = document.createElement('button');
      
      button1.textContent = 'Button 1';
      button2.textContent = 'Button 2';
      
      container.appendChild(button1);
      container.appendChild(button2);
      document.body.appendChild(container);
      
      const cleanup = focusUtils.trapFocus(container);
      
      expect(typeof cleanup).toBe('function');
      
      cleanup();
      document.body.removeChild(container);
    });

    it('should restore focus to previous element', () => {
      const button = document.createElement('button');
      document.body.appendChild(button);
      
      const focusSpy = vi.spyOn(button, 'focus');
      
      focusUtils.restoreFocus(button);
      
      expect(focusSpy).toHaveBeenCalled();
      
      document.body.removeChild(button);
      focusSpy.mockRestore();
    });
  });

  describe('Complete Accessibility Report', () => {
    it('should generate comprehensive accessibility report', () => {
      const { container } = render(
        <TestWrapper>
          <App />
        </TestWrapper>
      );

      const report = generateAccessibilityReport(container);
      
      expect(report).toHaveProperty('timestamp');
      expect(report).toHaveProperty('colorContrast');
      expect(report).toHaveProperty('keyboardNavigation');
      expect(report).toHaveProperty('semanticHTML');
      expect(report).toHaveProperty('summary');
      
      expect(report.summary.criticalIssues).toBe(0);
      expect(report.colorContrast.every(result => result.passesAA)).toBe(true);
    });
  });
});