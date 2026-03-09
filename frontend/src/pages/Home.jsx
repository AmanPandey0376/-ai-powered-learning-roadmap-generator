import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { generateRoadmap } from '../utils/api';
import Loader from '../components/Loader';

function Home() {
  const [skillInput, setSkillInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [isRetryable, setIsRetryable] = useState(false);
  const navigate = useNavigate();

  const handleInputChange = (e) => {
    setSkillInput(e.target.value);
    // Clear error when user starts typing
    if (error) {
      setError('');
    }
  };

  const validateInput = () => {
    const trimmedInput = skillInput.trim();
    
    if (!trimmedInput) {
      setError('Please enter a skill or job title');
      setIsRetryable(false);
      return false;
    }
    
    if (trimmedInput.length < 2) {
      setError('Please enter at least 2 characters');
      setIsRetryable(false);
      return false;
    }
    
    if (trimmedInput.length > 100) {
      setError('Please enter a shorter skill or job title (maximum 100 characters)');
      setIsRetryable(false);
      return false;
    }
    
    // Basic validation for reasonable input
    if (!/^[a-zA-Z0-9\s\-\+\#\.]+$/.test(trimmedInput)) {
      setError('Please use only letters, numbers, spaces, and common symbols');
      setIsRetryable(false);
      return false;
    }
    
    return true;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateInput()) {
      return;
    }

    setIsLoading(true);
    setError('');

    try {
      const roadmapData = await generateRoadmap({
        skill: skillInput.trim()
      });

      // Store the response in localStorage with timestamp
      // Transform resources to match Resources page expectations
      const transformedResources = {
        free: roadmapData.resources?.freeResources || roadmapData.resources?.free || [],
        paid: roadmapData.resources?.paidResources || roadmapData.resources?.paid || []
      };

      const dataToStore = {
        timestamp: Date.now(),
        skill: skillInput.trim(),
        roadmap: roadmapData.roadmap,
        resources: transformedResources
      };

      localStorage.setItem('roadmapData', JSON.stringify(dataToStore));

      // Redirect to Roadmap page on success
      navigate('/roadmap');
    } catch (err) {
      console.error('Error generating roadmap:', err);
      
      // Use the enhanced error message from API utility
      const errorMessage = err.userMessage || err.message || 'Failed to generate roadmap. Please try again.';
      const retryable = err.isRetryable !== undefined ? err.isRetryable : true;
      
      setError(errorMessage);
      setIsRetryable(retryable);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      {isLoading && <Loader />}
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-900 to-slate-800">
        <div className="container mx-auto px-4 py-12 md:py-20">
          <div className="max-w-3xl mx-auto text-center">
            {/* Hero Section */}
            <div className="mb-12">
              <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold mb-6 bg-gradient-to-r from-white via-blue-100 to-blue-200 bg-clip-text text-transparent leading-tight">
                Learning Roadmap Generator
              </h1>
              <p className="text-lg md:text-xl text-gray-300 mb-4 max-w-2xl mx-auto leading-relaxed">
                Generate a personalized learning roadmap for any skill or job title
              </p>
              <p className="text-sm text-gray-400 max-w-xl mx-auto">
                Get structured guidance with curated resources, projects, and milestones tailored to your learning goals
              </p>
            </div>
            
            {/* Form Section */}
            <form onSubmit={handleSubmit} className="bg-slate-800/80 backdrop-blur-sm p-8 md:p-10 rounded-2xl shadow-2xl border border-slate-700/50" role="form">
              <div className="mb-8">
                <label 
                  htmlFor="skill-input" 
                  className="block text-left text-base font-semibold text-gray-200 mb-3"
                >
                  Skill or job title
                </label>
                <div className="relative">
                  <input
                    id="skill-input"
                    type="text"
                    value={skillInput}
                    onChange={handleInputChange}
                    placeholder="e.g., React Developer, Data Science, Python Programming"
                    className="w-full px-6 py-4 bg-slate-700/80 border-2 border-slate-600 rounded-xl text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary focus:border-primary transition-all duration-300 text-lg"
                    disabled={isLoading}
                  />
                  <div className="absolute inset-y-0 right-0 flex items-center pr-4">
                    <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                    </svg>
                  </div>
                </div>
                {error && (
                  <div className="mt-4 text-left">
                    <div className="flex items-start space-x-3 bg-red-500/10 border border-red-500/20 rounded-lg p-4">
                      <svg
                        className="w-5 h-5 text-red-400 mt-0.5 flex-shrink-0"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                        xmlns="http://www.w3.org/2000/svg"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"
                        />
                      </svg>
                      <div className="flex-1">
                        <p className="text-red-300 font-medium">{error}</p>
                        {isRetryable && (
                          <p className="text-red-400/70 text-sm mt-1">
                            This error is temporary. Please try again.
                          </p>
                        )}
                      </div>
                    </div>
                  </div>
                )}
              </div>
              
              <button
                type="submit"
                disabled={isLoading || !skillInput.trim()}
                className="w-full bg-gradient-to-r from-primary to-blue-600 hover:from-blue-600 hover:to-blue-700 disabled:from-gray-600 disabled:to-gray-700 disabled:cursor-not-allowed text-white font-bold py-4 px-8 rounded-xl transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 focus:ring-offset-slate-800 transform hover:scale-105 disabled:hover:scale-100 shadow-lg hover:shadow-xl text-lg"
              >
                {isLoading ? (
                  <span className="flex items-center justify-center">
                    <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Generating Roadmap...
                  </span>
                ) : (
                  <span className="flex items-center justify-center">
                    Generate My Roadmap
                    <svg className="ml-2 w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                    </svg>
                  </span>
                )}
              </button>
            </form>

            {/* Features Section */}
            <div className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-8">
              <div className="text-center p-6 rounded-xl bg-slate-800/40 border border-slate-700/50">
                <div className="w-12 h-12 bg-primary/20 rounded-lg flex items-center justify-center mx-auto mb-4">
                  <svg className="w-6 h-6 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z" />
                  </svg>
                </div>
                <h3 className="font-semibold text-white mb-2">Personalized</h3>
                <p className="text-gray-400 text-sm">Tailored to your specific skill level and learning goals</p>
              </div>
              <div className="text-center p-6 rounded-xl bg-slate-800/40 border border-slate-700/50">
                <div className="w-12 h-12 bg-accent/20 rounded-lg flex items-center justify-center mx-auto mb-4">
                  <svg className="w-6 h-6 text-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                  </svg>
                </div>
                <h3 className="font-semibold text-white mb-2">Curated Resources</h3>
                <p className="text-gray-400 text-sm">Hand-picked learning materials from trusted sources</p>
              </div>
              <div className="text-center p-6 rounded-xl bg-slate-800/40 border border-slate-700/50">
                <div className="w-12 h-12 bg-purple-500/20 rounded-lg flex items-center justify-center mx-auto mb-4">
                  <svg className="w-6 h-6 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                  </svg>
                </div>
                <h3 className="font-semibold text-white mb-2">Project-Based</h3>
                <p className="text-gray-400 text-sm">Learn by building real projects that showcase your skills</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}

export default Home;