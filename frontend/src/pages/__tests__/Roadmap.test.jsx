import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BrowserRouter } from 'react-router-dom';
import Roadmap from '../Roadmap';

// Mock react-router-dom navigate
const mockNavigate = vi.fn();
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

// Helper function to render Roadmap component with router
const renderRoadmap = () => {
  return render(
    <BrowserRouter>
      <Roadmap />
    </BrowserRouter>
  );
};

// Mock roadmap data for testing
const mockRoadmapData = {
  timestamp: Date.now(),
  skill: 'React Developer',
  roadmap: {
    title: 'Complete React Developer Roadmap',
    modules: [
      {
        id: 'module-1',
        name: 'React Fundamentals',
        description: 'Learn the basics of React including components, props, and state',
        miniProjects: [
          {
            id: 'project-1',
            name: 'Todo App',
            description: 'Build a simple todo application',
            estimatedHours: 8
          },
          {
            id: 'project-2',
            name: 'Weather Widget',
            description: 'Create a weather display component',
            estimatedHours: 6
          }
        ]
      },
      {
        id: 'module-2',
        name: 'Advanced React',
        description: 'Advanced concepts like hooks, context, and performance optimization',
        miniProjects: [
          {
            id: 'project-3',
            name: 'Shopping Cart',
            description: 'Build a shopping cart with context API',
            estimatedHours: 12
          }
        ]
      }
    ],
    majorProject: {
      id: 'major-1',
      name: 'Full-Stack E-commerce Platform',
      description: 'Build a complete e-commerce application with React frontend',
      requirements: [
        'User authentication and authorization',
        'Product catalog with search and filtering',
        'Shopping cart and checkout process',
        'Admin dashboard for product management'
      ],
      estimatedHours: 80
    }
  },
  resources: {
    free: [
      {
        id: 'free-1',
        platform: 'YouTube',
        creator: 'React Official',
        title: 'React Tutorial',
        link: 'https://youtube.com/react-tutorial'
      }
    ],
    paid: [
      {
        id: 'paid-1',
        platform: 'Udemy',
        creator: 'John Doe',
        title: 'Complete React Course',
        link: 'https://udemy.com/react-course'
      }
    ]
  }
};

describe('Roadmap Page', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  describe('Data Loading from localStorage', () => {
    it('should load and display roadmap data from localStorage (Requirement 2.1)', () => {
      localStorage.getItem.mockReturnValue(JSON.stringify(mockRoadmapData));
      
      renderRoadmap();
      
      expect(localStorage.getItem).toHaveBeenCalledWith('roadmapData');
      expect(screen.getByText('Your Learning Roadmap')).toBeInTheDocument();
      expect(screen.getByText('Personalized roadmap for:')).toBeInTheDocument();
      expect(screen.getByText('React Developer')).toBeInTheDocument();
    });

    it('should redirect to Home page when no data exists in localStorage (Requirement 2.5)', () => {
      localStorage.getItem.mockReturnValue(null);
      
      renderRoadmap();
      
      expect(mockNavigate).toHaveBeenCalledWith('/');
    });

    it('should redirect to Home page when localStorage data is corrupted (Requirement 2.5)', () => {
      localStorage.getItem.mockReturnValue('invalid-json');
      
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
      
      renderRoadmap();
      
      expect(consoleSpy).toHaveBeenCalledWith('Error parsing roadmap data:', expect.any(Error));
      expect(mockNavigate).toHaveBeenCalledWith('/');
      
      consoleSpy.mockRestore();
    });

    it('should redirect to Home page when roadmap data is missing required fields (Requirement 2.5)', () => {
      const invalidData = {
        timestamp: Date.now(),
        skill: 'React Developer',
        roadmap: {} // Missing modules
      };
      
      localStorage.getItem.mockReturnValue(JSON.stringify(invalidData));
      
      renderRoadmap();
      
      expect(mockNavigate).toHaveBeenCalledWith('/');
    });

    it('should redirect to Home page when roadmap modules are missing (Requirement 2.5)', () => {
      const invalidData = {
        timestamp: Date.now(),
        skill: 'React Developer',
        roadmap: {
          title: 'Test Roadmap'
          // Missing modules array
        }
      };
      
      localStorage.getItem.mockReturnValue(JSON.stringify(invalidData));
      
      renderRoadmap();
      
      expect(mockNavigate).toHaveBeenCalledWith('/');
    });

    it('should handle component mounting and data loading process', () => {
      localStorage.getItem.mockReturnValue(JSON.stringify(mockRoadmapData));
      
      renderRoadmap();
      
      // Should successfully load and display the roadmap data
      expect(localStorage.getItem).toHaveBeenCalledWith('roadmapData');
      expect(screen.getByText('Your Learning Roadmap')).toBeInTheDocument();
      expect(mockNavigate).not.toHaveBeenCalled();
    });
  });

  describe('Module and Project Rendering', () => {
    beforeEach(() => {
      localStorage.getItem.mockReturnValue(JSON.stringify(mockRoadmapData));
    });

    it('should display roadmap modules in vertical list format (Requirement 2.1)', () => {
      renderRoadmap();
      
      // Check that modules are displayed
      expect(screen.getByText('React Fundamentals')).toBeInTheDocument();
      expect(screen.getByText('Advanced React')).toBeInTheDocument();
      
      // Check module descriptions
      expect(screen.getByText('Learn the basics of React including components, props, and state')).toBeInTheDocument();
      expect(screen.getByText('Advanced concepts like hooks, context, and performance optimization')).toBeInTheDocument();
      
      // Check module numbering
      expect(screen.getByText('1')).toBeInTheDocument();
      expect(screen.getByText('2')).toBeInTheDocument();
    });

    it('should show mini projects under each module (Requirement 2.2)', () => {
      renderRoadmap();
      
      // Check mini projects section headers
      const miniProjectHeaders = screen.getAllByText('Mini Projects:');
      expect(miniProjectHeaders).toHaveLength(2);
      
      // Check individual mini projects
      expect(screen.getByText('Todo App')).toBeInTheDocument();
      expect(screen.getByText('Weather Widget')).toBeInTheDocument();
      expect(screen.getByText('Shopping Cart')).toBeInTheDocument();
      
      // Check project descriptions
      expect(screen.getByText('Build a simple todo application')).toBeInTheDocument();
      expect(screen.getByText('Create a weather display component')).toBeInTheDocument();
      expect(screen.getByText('Build a shopping cart with context API')).toBeInTheDocument();
      
      // Check estimated hours
      expect(screen.getByText('Estimated time: 8 hours')).toBeInTheDocument();
      expect(screen.getByText('Estimated time: 6 hours')).toBeInTheDocument();
      expect(screen.getByText('Estimated time: 12 hours')).toBeInTheDocument();
    });

    it('should show major project at the end (Requirement 2.3)', () => {
      renderRoadmap();
      
      // Check capstone project section
      expect(screen.getByText('Capstone Project')).toBeInTheDocument();
      expect(screen.getByText('Final project to showcase your skills')).toBeInTheDocument();
      
      // Check major project details
      expect(screen.getByText('Full-Stack E-commerce Platform')).toBeInTheDocument();
      expect(screen.getByText('Build a complete e-commerce application with React frontend')).toBeInTheDocument();
      
      // Check requirements list
      expect(screen.getByText('Requirements:')).toBeInTheDocument();
      expect(screen.getByText('User authentication and authorization')).toBeInTheDocument();
      expect(screen.getByText('Product catalog with search and filtering')).toBeInTheDocument();
      expect(screen.getByText('Shopping cart and checkout process')).toBeInTheDocument();
      expect(screen.getByText('Admin dashboard for product management')).toBeInTheDocument();
      
      // Check estimated hours for major project
      expect(screen.getByText('Estimated time: 80 hours')).toBeInTheDocument();
    });

    it('should display roadmap title when available', () => {
      renderRoadmap();
      
      expect(screen.getByText('Complete React Developer Roadmap')).toBeInTheDocument();
    });

    it('should handle modules without mini projects gracefully', () => {
      const dataWithoutMiniProjects = {
        ...mockRoadmapData,
        roadmap: {
          ...mockRoadmapData.roadmap,
          modules: [
            {
              id: 'module-1',
              name: 'Basic Module',
              description: 'A module without mini projects'
              // No miniProjects array
            }
          ]
        }
      };
      
      localStorage.getItem.mockReturnValue(JSON.stringify(dataWithoutMiniProjects));
      
      renderRoadmap();
      
      expect(screen.getByText('Basic Module')).toBeInTheDocument();
      expect(screen.getByText('A module without mini projects')).toBeInTheDocument();
      expect(screen.queryByText('Mini Projects:')).not.toBeInTheDocument();
    });

    it('should handle modules with empty mini projects array', () => {
      const dataWithEmptyMiniProjects = {
        ...mockRoadmapData,
        roadmap: {
          ...mockRoadmapData.roadmap,
          modules: [
            {
              id: 'module-1',
              name: 'Basic Module',
              description: 'A module with empty mini projects',
              miniProjects: []
            }
          ]
        }
      };
      
      localStorage.getItem.mockReturnValue(JSON.stringify(dataWithEmptyMiniProjects));
      
      renderRoadmap();
      
      expect(screen.getByText('Basic Module')).toBeInTheDocument();
      expect(screen.queryByText('Mini Projects:')).not.toBeInTheDocument();
    });

    it('should handle roadmap without major project', () => {
      const dataWithoutMajorProject = {
        ...mockRoadmapData,
        roadmap: {
          ...mockRoadmapData.roadmap,
          majorProject: null
        }
      };
      
      localStorage.getItem.mockReturnValue(JSON.stringify(dataWithoutMajorProject));
      
      renderRoadmap();
      
      expect(screen.queryByText('Capstone Project')).not.toBeInTheDocument();
      expect(screen.queryByText('Final project to showcase your skills')).not.toBeInTheDocument();
    });

    it('should handle modules without descriptions', () => {
      const dataWithoutDescriptions = {
        ...mockRoadmapData,
        roadmap: {
          ...mockRoadmapData.roadmap,
          modules: [
            {
              id: 'module-1',
              name: 'Basic Module',
              // No description
              miniProjects: []
            }
          ]
        }
      };
      
      localStorage.getItem.mockReturnValue(JSON.stringify(dataWithoutDescriptions));
      
      renderRoadmap();
      
      expect(screen.getByText('Basic Module')).toBeInTheDocument();
    });

    it('should handle mini projects without descriptions or estimated hours', () => {
      const dataWithMinimalProjects = {
        ...mockRoadmapData,
        roadmap: {
          ...mockRoadmapData.roadmap,
          modules: [
            {
              id: 'module-1',
              name: 'Basic Module',
              description: 'Test module',
              miniProjects: [
                {
                  id: 'project-1',
                  name: 'Simple Project'
                  // No description or estimatedHours
                }
              ]
            }
          ]
        }
      };
      
      localStorage.getItem.mockReturnValue(JSON.stringify(dataWithMinimalProjects));
      
      renderRoadmap();
      
      expect(screen.getByText('Simple Project')).toBeInTheDocument();
      expect(screen.queryByText('Estimated time:')).not.toBeInTheDocument();
    });
  });

  describe('Navigation and Redirect Functionality', () => {
    beforeEach(() => {
      localStorage.getItem.mockReturnValue(JSON.stringify(mockRoadmapData));
    });

    it('should provide button to navigate to Resources page (Requirement 2.4)', () => {
      renderRoadmap();
      
      const resourcesButton = screen.getByRole('button', { name: /view learning resources/i });
      expect(resourcesButton).toBeInTheDocument();
    });

    it('should navigate to Resources page when button is clicked (Requirement 2.4)', async () => {
      const user = userEvent.setup();
      
      renderRoadmap();
      
      const resourcesButton = screen.getByRole('button', { name: /view learning resources/i });
      await user.click(resourcesButton);
      
      expect(mockNavigate).toHaveBeenCalledWith('/resources');
    });

    it('should have proper button styling and accessibility', () => {
      renderRoadmap();
      
      const resourcesButton = screen.getByRole('button', { name: /view learning resources/i });
      
      // Check that button has proper classes for styling
      expect(resourcesButton).toHaveClass('bg-blue-500');
      expect(resourcesButton).toHaveClass('hover:bg-blue-600');
      expect(resourcesButton).toHaveClass('text-white');
      
      // Check focus attributes for accessibility
      expect(resourcesButton).toHaveClass('focus:outline-none');
      expect(resourcesButton).toHaveClass('focus:ring-2');
    });

    it('should handle navigation button click with keyboard', async () => {
      const user = userEvent.setup();
      
      renderRoadmap();
      
      const resourcesButton = screen.getByRole('button', { name: /view learning resources/i });
      
      // Focus the button and press Enter
      resourcesButton.focus();
      await user.keyboard('{Enter}');
      
      expect(mockNavigate).toHaveBeenCalledWith('/resources');
    });

    it('should handle navigation button click with Space key', async () => {
      const user = userEvent.setup();
      
      renderRoadmap();
      
      const resourcesButton = screen.getByRole('button', { name: /view learning resources/i });
      
      // Focus the button and press Space
      resourcesButton.focus();
      await user.keyboard(' ');
      
      expect(mockNavigate).toHaveBeenCalledWith('/resources');
    });
  });

  describe('Error Handling and Edge Cases', () => {
    it('should handle modules without IDs gracefully', () => {
      const dataWithoutIds = {
        ...mockRoadmapData,
        roadmap: {
          ...mockRoadmapData.roadmap,
          modules: [
            {
              // No id field
              name: 'Module Without ID',
              description: 'Test module',
              miniProjects: [
                {
                  // No id field
                  name: 'Project Without ID',
                  description: 'Test project'
                }
              ]
            }
          ]
        }
      };
      
      localStorage.getItem.mockReturnValue(JSON.stringify(dataWithoutIds));
      
      renderRoadmap();
      
      expect(screen.getByText('Module Without ID')).toBeInTheDocument();
      expect(screen.getByText('Project Without ID')).toBeInTheDocument();
    });

    it('should handle empty modules array', () => {
      const dataWithEmptyModules = {
        ...mockRoadmapData,
        roadmap: {
          title: 'Empty Roadmap',
          modules: []
        }
      };
      
      localStorage.getItem.mockReturnValue(JSON.stringify(dataWithEmptyModules));
      
      renderRoadmap();
      
      expect(screen.getByText('Your Learning Roadmap')).toBeInTheDocument();
      expect(screen.getByText('Empty Roadmap')).toBeInTheDocument();
      
      // Should still show the resources button
      expect(screen.getByRole('button', { name: /view learning resources/i })).toBeInTheDocument();
    });

    it('should handle roadmap without title', () => {
      const dataWithoutTitle = {
        ...mockRoadmapData,
        roadmap: {
          // No title field
          modules: mockRoadmapData.roadmap.modules
        }
      };
      
      localStorage.getItem.mockReturnValue(JSON.stringify(dataWithoutTitle));
      
      renderRoadmap();
      
      expect(screen.getByText('Your Learning Roadmap')).toBeInTheDocument();
      expect(screen.getByText('React Fundamentals')).toBeInTheDocument();
    });

    it('should handle major project without requirements', () => {
      const dataWithoutRequirements = {
        ...mockRoadmapData,
        roadmap: {
          ...mockRoadmapData.roadmap,
          majorProject: {
            id: 'major-1',
            name: 'Simple Project',
            description: 'A project without requirements'
            // No requirements array
          }
        }
      };
      
      localStorage.getItem.mockReturnValue(JSON.stringify(dataWithoutRequirements));
      
      renderRoadmap();
      
      expect(screen.getByText('Simple Project')).toBeInTheDocument();
      expect(screen.getByText('A project without requirements')).toBeInTheDocument();
      expect(screen.queryByText('Requirements:')).not.toBeInTheDocument();
    });

    it('should handle major project with empty requirements array', () => {
      const dataWithEmptyRequirements = {
        ...mockRoadmapData,
        roadmap: {
          ...mockRoadmapData.roadmap,
          majorProject: {
            id: 'major-1',
            name: 'Simple Project',
            description: 'A project with empty requirements',
            requirements: []
          }
        }
      };
      
      localStorage.getItem.mockReturnValue(JSON.stringify(dataWithEmptyRequirements));
      
      renderRoadmap();
      
      expect(screen.getByText('Simple Project')).toBeInTheDocument();
      expect(screen.queryByText('Requirements:')).not.toBeInTheDocument();
    });
  });
});