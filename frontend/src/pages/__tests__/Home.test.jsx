import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BrowserRouter } from 'react-router-dom';
import Home from '../Home';
import * as api from '../../utils/api';

// Mock the API module
vi.mock('../../utils/api', () => ({
  generateRoadmap: vi.fn(),
}));

// Mock the Loader component
vi.mock('../../components/Loader', () => ({
  default: () => <div data-testid="loader">Loading...</div>,
}));

// Mock react-router-dom navigate
const mockNavigate = vi.fn();
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

// Helper function to render Home component with router
const renderHome = () => {
  return render(
    <BrowserRouter>
      <Home />
    </BrowserRouter>
  );
};

describe('Home Page', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  describe('Form Input Validation and Submission', () => {
    it('should display input field for skill/job title (Requirement 1.1)', () => {
      renderHome();
      
      const input = screen.getByLabelText(/skill or job title/i);
      expect(input).toBeInTheDocument();
      expect(input).toHaveAttribute('placeholder', expect.stringContaining('React Developer'));
    });

    it('should enable Generate Roadmap button when user enters text (Requirement 1.2)', async () => {
      const user = userEvent.setup();
      renderHome();
      
      const input = screen.getByLabelText(/skill or job title/i);
      const button = screen.getByRole('button', { name: /generate roadmap/i });
      
      // Button should be disabled initially
      expect(button).toBeDisabled();
      
      // Type in input
      await user.type(input, 'React Developer');
      
      // Button should be enabled
      expect(button).toBeEnabled();
    });

    it('should validate input and show error for empty input', async () => {
      const user = userEvent.setup();
      renderHome();
      
      const input = screen.getByLabelText(/skill or job title/i);
      const form = screen.getByRole('form') || input.closest('form');
      
      // Try to submit empty form by triggering form submission
      fireEvent.submit(form);
      
      expect(screen.getByText(/please enter a skill or job title/i)).toBeInTheDocument();
    });

    it('should validate input and show error for input less than 2 characters', async () => {
      const user = userEvent.setup();
      renderHome();
      
      const input = screen.getByLabelText(/skill or job title/i);
      const button = screen.getByRole('button', { name: /generate roadmap/i });
      
      // Type single character
      await user.type(input, 'R');
      await user.click(button);
      
      expect(screen.getByText(/please enter at least 2 characters/i)).toBeInTheDocument();
    });

    it('should clear error when user starts typing', async () => {
      const user = userEvent.setup();
      renderHome();
      
      const input = screen.getByLabelText(/skill or job title/i);
      const form = screen.getByRole('form') || input.closest('form');
      
      // Trigger error first
      fireEvent.submit(form);
      expect(screen.getByText(/please enter a skill or job title/i)).toBeInTheDocument();
      
      // Start typing
      await user.type(input, 'React');
      
      // Error should be cleared
      expect(screen.queryByText(/please enter a skill or job title/i)).not.toBeInTheDocument();
    });

    it('should trim whitespace from input before validation', async () => {
      const user = userEvent.setup();
      renderHome();
      
      const input = screen.getByLabelText(/skill or job title/i);
      const form = screen.getByRole('form') || input.closest('form');
      
      // Type only spaces
      await user.type(input, '   ');
      fireEvent.submit(form);
      
      expect(screen.getByText(/please enter a skill or job title/i)).toBeInTheDocument();
    });
  });

  describe('Loading States and API Integration', () => {
    it('should show loading spinner when Generate Roadmap is clicked (Requirement 1.3)', async () => {
      const user = userEvent.setup();
      
      // Mock API to return a pending promise
      const mockPromise = new Promise(() => {}); // Never resolves
      api.generateRoadmap.mockReturnValue(mockPromise);
      
      renderHome();
      
      const input = screen.getByLabelText(/skill or job title/i);
      const button = screen.getByRole('button', { name: /generate roadmap/i });
      
      await user.type(input, 'React Developer');
      await user.click(button);
      
      // Should show loader
      expect(screen.getByTestId('loader')).toBeInTheDocument();
      
      // Button text should change
      expect(screen.getByText(/generating roadmap.../i)).toBeInTheDocument();
      
      // Input should be disabled
      expect(input).toBeDisabled();
    });

    it('should make POST request to /api/roadmap endpoint (Requirement 1.4)', async () => {
      const user = userEvent.setup();
      
      const mockResponse = {
        roadmap: { title: 'React Developer Roadmap', modules: [] },
        resources: { free: [], paid: [] }
      };
      
      api.generateRoadmap.mockResolvedValue(mockResponse);
      
      renderHome();
      
      const input = screen.getByLabelText(/skill or job title/i);
      const button = screen.getByRole('button', { name: /generate roadmap/i });
      
      await user.type(input, 'React Developer');
      await user.click(button);
      
      expect(api.generateRoadmap).toHaveBeenCalledWith({
        skill: 'React Developer'
      });
    });

    it('should handle API errors gracefully', async () => {
      const user = userEvent.setup();
      
      api.generateRoadmap.mockRejectedValue(new Error('Network error'));
      
      renderHome();
      
      const input = screen.getByLabelText(/skill or job title/i);
      const button = screen.getByRole('button', { name: /generate roadmap/i });
      
      await user.type(input, 'React Developer');
      await user.click(button);
      
      await waitFor(() => {
        expect(screen.getByText(/network error/i)).toBeInTheDocument();
      });
      
      // Loading should stop
      expect(screen.queryByTestId('loader')).not.toBeInTheDocument();
    });

    it('should show generic error message when API error has no message', async () => {
      const user = userEvent.setup();
      
      api.generateRoadmap.mockRejectedValue(new Error());
      
      renderHome();
      
      const input = screen.getByLabelText(/skill or job title/i);
      const button = screen.getByRole('button', { name: /generate roadmap/i });
      
      await user.type(input, 'React Developer');
      await user.click(button);
      
      await waitFor(() => {
        expect(screen.getByText(/failed to generate roadmap/i)).toBeInTheDocument();
      });
    });
  });

  describe('localStorage Integration and Navigation', () => {
    it('should store API response in localStorage (Requirement 1.5)', async () => {
      const user = userEvent.setup();
      
      const mockResponse = {
        roadmap: { 
          title: 'React Developer Roadmap', 
          modules: [{ id: '1', name: 'Basics' }] 
        },
        resources: { 
          free: [{ id: '1', platform: 'YouTube' }], 
          paid: [{ id: '2', platform: 'Udemy' }] 
        }
      };
      
      api.generateRoadmap.mockResolvedValue(mockResponse);
      
      // Mock Date.now for consistent timestamp
      const mockTimestamp = 1234567890;
      vi.spyOn(Date, 'now').mockReturnValue(mockTimestamp);
      
      renderHome();
      
      const input = screen.getByLabelText(/skill or job title/i);
      const button = screen.getByRole('button', { name: /generate roadmap/i });
      
      await user.type(input, 'React Developer');
      await user.click(button);
      
      await waitFor(() => {
        expect(localStorage.setItem).toHaveBeenCalledWith(
          'roadmapData',
          JSON.stringify({
            timestamp: mockTimestamp,
            skill: 'React Developer',
            roadmap: mockResponse.roadmap,
            resources: mockResponse.resources
          })
        );
      });
      
      Date.now.mockRestore();
    });

    it('should redirect to Roadmap page on successful API response (Requirement 1.6)', async () => {
      const user = userEvent.setup();
      
      const mockResponse = {
        roadmap: { title: 'React Developer Roadmap', modules: [] },
        resources: { free: [], paid: [] }
      };
      
      api.generateRoadmap.mockResolvedValue(mockResponse);
      
      renderHome();
      
      const input = screen.getByLabelText(/skill or job title/i);
      const button = screen.getByRole('button', { name: /generate roadmap/i });
      
      await user.type(input, 'React Developer');
      await user.click(button);
      
      await waitFor(() => {
        expect(mockNavigate).toHaveBeenCalledWith('/roadmap');
      });
    });

    it('should store trimmed skill input in localStorage', async () => {
      const user = userEvent.setup();
      
      const mockResponse = {
        roadmap: { title: 'React Developer Roadmap', modules: [] },
        resources: { free: [], paid: [] }
      };
      
      api.generateRoadmap.mockResolvedValue(mockResponse);
      
      renderHome();
      
      const input = screen.getByLabelText(/skill or job title/i);
      const button = screen.getByRole('button', { name: /generate roadmap/i });
      
      // Type with extra spaces
      await user.type(input, '  React Developer  ');
      await user.click(button);
      
      await waitFor(() => {
        const setItemCall = localStorage.setItem.mock.calls[0];
        const storedData = JSON.parse(setItemCall[1]);
        expect(storedData.skill).toBe('React Developer');
      });
    });

    it('should not redirect on API error', async () => {
      const user = userEvent.setup();
      
      api.generateRoadmap.mockRejectedValue(new Error('API Error'));
      
      renderHome();
      
      const input = screen.getByLabelText(/skill or job title/i);
      const button = screen.getByRole('button', { name: /generate roadmap/i });
      
      await user.type(input, 'React Developer');
      await user.click(button);
      
      await waitFor(() => {
        expect(screen.getByText(/api error/i)).toBeInTheDocument();
      });
      
      expect(mockNavigate).not.toHaveBeenCalled();
      expect(localStorage.setItem).not.toHaveBeenCalled();
    });
  });

  describe('Form Accessibility and User Experience', () => {
    it('should have proper form labels and accessibility attributes', () => {
      renderHome();
      
      const input = screen.getByLabelText(/skill or job title/i);
      expect(input).toHaveAttribute('id', 'skill-input');
      
      const label = screen.getByLabelText(/skill or job title/i).closest('div').querySelector('label');
      expect(label).toHaveAttribute('for', 'skill-input');
      expect(label).toHaveTextContent('Skill or Job Title');
    });

    it('should handle form submission with Enter key', async () => {
      const user = userEvent.setup();
      
      const mockResponse = {
        roadmap: { title: 'React Developer Roadmap', modules: [] },
        resources: { free: [], paid: [] }
      };
      
      api.generateRoadmap.mockResolvedValue(mockResponse);
      
      renderHome();
      
      const input = screen.getByLabelText(/skill or job title/i);
      
      await user.type(input, 'React Developer');
      await user.keyboard('{Enter}');
      
      expect(api.generateRoadmap).toHaveBeenCalledWith({
        skill: 'React Developer'
      });
    });

    it('should prevent form submission when loading', async () => {
      const user = userEvent.setup();
      
      // Mock API to return a pending promise
      const mockPromise = new Promise(() => {});
      api.generateRoadmap.mockReturnValue(mockPromise);
      
      renderHome();
      
      const input = screen.getByLabelText(/skill or job title/i);
      const button = screen.getByRole('button', { name: /generate roadmap/i });
      
      await user.type(input, 'React Developer');
      await user.click(button);
      
      // Try to click again while loading
      await user.click(button);
      
      // API should only be called once
      expect(api.generateRoadmap).toHaveBeenCalledTimes(1);
    });
  });
});