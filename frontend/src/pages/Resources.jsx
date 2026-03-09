import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import ResourceCard from '../components/ResourceCard';

function Resources() {
  const [activeTab, setActiveTab] = useState('free');
  const [resourcesData, setResourcesData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    // Load resources data from localStorage
    const storedData = localStorage.getItem('roadmapData');
    
    if (!storedData) {
      // Redirect to Home page if no data exists
      navigate('/');
      return;
    }

    try {
      const parsedData = JSON.parse(storedData);
      
      // Validate that resources data exists
      if (!parsedData.resources) {
        console.error('No resources data found in localStorage');
        navigate('/');
        return;
      }

      console.log('Raw resources data:', parsedData.resources);

      // Handle both old and new resource data formats
      let freeResources = [];
      let paidResources = [];
      
      // New format (from Groq AI): {freeResources: [...], paidResources: [...]}
      if (parsedData.resources.freeResources !== undefined) {
        freeResources = parsedData.resources.freeResources || [];
        paidResources = parsedData.resources.paidResources || [];
        console.log('Using new format (freeResources/paidResources)');
      }
      // Old format: {free: [...], paid: [...]}
      else if (parsedData.resources.free !== undefined) {
        freeResources = parsedData.resources.free || [];
        paidResources = parsedData.resources.paid || [];
        console.log('Using old format (free/paid)');
      }
      // Direct format (resources might be the array itself)
      else if (Array.isArray(parsedData.resources)) {
        freeResources = parsedData.resources;
        paidResources = [];
        console.log('Using direct array format');
      }
      
      console.log('Resources loaded:', {
        free: freeResources.length,
        paid: paidResources.length,
        freeFirst3: freeResources.slice(0, 3),
        paidFirst3: paidResources.slice(0, 3)
      });

      // Debug: Log the structure of the first resource to understand the data format
      if (freeResources.length > 0) {
        console.log('Sample free resource structure:', freeResources[0]);
      }
      if (paidResources.length > 0) {
        console.log('Sample paid resource structure:', paidResources[0]);
      }

      // If no resources found, try to fetch from API
      if (freeResources.length === 0 && paidResources.length === 0) {
        console.log('No resources in localStorage, trying to fetch from API...');
        
        // Try to get skill from stored data and fetch resources
        if (parsedData.skill) {
          fetchResourcesFromAPI(parsedData.skill);
          return;
        } else {
          console.error('No skill found and no resources available');
          setError('No learning resources available. Please generate a new roadmap.');
          setLoading(false);
          return;
        }
      }
      
      // Set resources in the expected format for the component
      setResourcesData({
        free: freeResources,
        paid: paidResources
      });
      
      setLoading(false);
    } catch (parseError) {
      console.error('Error parsing stored data:', parseError);
      navigate('/');
      return;
    } finally {
      setLoading(false);
    }
  }, [navigate]);

  // Function to fetch resources from API if not available in localStorage
  const fetchResourcesFromAPI = async (skill) => {
    try {
      console.log(`Fetching resources from API for skill: ${skill}`);
      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/resources/${encodeURIComponent(skill)}`);
      
      if (response.ok) {
        const resourcesData = await response.json();
        console.log('Fetched resources from API:', resourcesData);
        
        const freeRes = resourcesData.freeResources || [];
        const paidRes = resourcesData.paidResources || [];
        
        console.log('API fetched resources structure:', {
          freeCount: freeRes.length,
          paidCount: paidRes.length,
          sampleFree: freeRes[0],
          samplePaid: paidRes[0]
        });
        
        setResourcesData({
          free: freeRes,
          paid: paidRes
        });
        
        // Update localStorage with the fetched resources
        const storedData = localStorage.getItem('roadmapData');
        if (storedData) {
          const parsedData = JSON.parse(storedData);
          parsedData.resources = {
            free: freeRes,
            paid: paidRes
          };
          localStorage.setItem('roadmapData', JSON.stringify(parsedData));
          console.log('Updated localStorage with fetched resources');
        }
      } else {
        console.error('Failed to fetch resources:', response.status);
        setError('Failed to load learning resources. Please try generating a new roadmap.');
      }
    } catch (error) {
      console.error('Error fetching resources:', error);
      setError('Unable to load learning resources. Please check your connection and try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleTabClick = (tab) => {
    setActiveTab(tab);
  };

  // Show loading state while data is being loaded
  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-900 to-slate-800 flex items-center justify-center">
        <div className="max-w-md mx-auto text-center">
          <div className="bg-slate-800/80 backdrop-blur-sm rounded-2xl p-12 border border-slate-700/50 shadow-2xl">
            <div className="relative mb-6">
              <div className="animate-spin rounded-full h-12 w-12 border-4 border-slate-600 mx-auto"></div>
              <div className="animate-spin rounded-full h-12 w-12 border-4 border-primary border-t-transparent absolute top-0 left-1/2 transform -translate-x-1/2"></div>
            </div>
            <h3 className="text-xl font-bold text-white mb-2">Loading Resources</h3>
            <p className="text-gray-300">Gathering the best learning materials for you...</p>
          </div>
        </div>
      </div>
    );
  }

  // Show error state
  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-900 to-slate-800 flex items-center justify-center">
        <div className="max-w-md mx-auto text-center">
          <div className="bg-slate-800/80 backdrop-blur-sm rounded-2xl p-12 border border-slate-700/50 shadow-2xl">
            <div className="w-16 h-16 bg-red-500/20 rounded-full flex items-center justify-center mx-auto mb-6">
              <svg
                className="h-8 w-8 text-red-400"
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
            </div>
            <h3 className="text-xl font-bold text-white mb-3">Resources Not Available</h3>
            <p className="text-gray-300 mb-8 leading-relaxed">{error}</p>
            <div className="space-y-4">
              <button
                onClick={() => navigate('/')}
                className="w-full bg-gradient-to-r from-primary to-blue-600 hover:from-blue-600 hover:to-blue-700 text-white font-bold py-3 px-6 rounded-xl transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 focus:ring-offset-slate-900 transform hover:scale-105 shadow-lg"
              >
                Generate New Roadmap
              </button>
              <button
                onClick={() => navigate('/roadmap')}
                className="w-full bg-slate-700/80 backdrop-blur-sm hover:bg-slate-600 text-white font-semibold py-3 px-6 rounded-xl transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-slate-500 focus:ring-offset-2 focus:ring-offset-slate-900 border border-slate-600/50"
              >
                Back to Roadmap
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!resourcesData) {
    return null;
  }

  const currentResources = resourcesData[activeTab] || [];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-900 to-slate-800">
      <div className="container mx-auto px-4 py-8 md:py-12">
        <div className="max-w-7xl mx-auto">
          {/* Header Section */}
          <div className="mb-12 text-center">
            <h1 className="text-3xl md:text-4xl font-bold mb-4 bg-gradient-to-r from-white to-blue-200 bg-clip-text text-transparent">
              Learning Resources
            </h1>
            <p className="text-lg text-gray-300 max-w-2xl mx-auto">
              Curated learning materials to support your journey
            </p>
          </div>
          
          {/* Tab Navigation */}
          <div className="mb-10">
            <div className="bg-slate-800/60 backdrop-blur-sm rounded-2xl p-2 border border-slate-700/50 inline-flex mx-auto">
              <nav className="flex space-x-2" role="tablist">
                <button
                  onClick={() => handleTabClick('free')}
                  className={`py-3 px-6 rounded-xl font-semibold text-sm transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 focus:ring-offset-slate-800 ${
                    activeTab === 'free'
                      ? 'bg-gradient-to-r from-accent to-emerald-400 text-white shadow-lg transform scale-105'
                      : 'text-gray-400 hover:text-white hover:bg-slate-700/50'
                  }`}
                  aria-selected={activeTab === 'free'}
                  role="tab"
                >
                  <span className="flex items-center">
                    <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
                    </svg>
                    Free Resources
                    {resourcesData.free && (
                      <span className="ml-2 bg-white/20 text-white py-1 px-2 rounded-full text-xs font-bold">
                        {resourcesData.free.length}
                      </span>
                    )}
                  </span>
                </button>
                <button
                  onClick={() => handleTabClick('paid')}
                  className={`py-3 px-6 rounded-xl font-semibold text-sm transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 focus:ring-offset-slate-800 ${
                    activeTab === 'paid'
                      ? 'bg-gradient-to-r from-primary to-blue-600 text-white shadow-lg transform scale-105'
                      : 'text-gray-400 hover:text-white hover:bg-slate-700/50'
                  }`}
                  aria-selected={activeTab === 'paid'}
                  role="tab"
                >
                  <span className="flex items-center">
                    <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
                    </svg>
                    Paid Resources
                    {resourcesData.paid && (
                      <span className="ml-2 bg-white/20 text-white py-1 px-2 rounded-full text-xs font-bold">
                        {resourcesData.paid.length}
                      </span>
                    )}
                  </span>
                </button>
              </nav>
            </div>
          </div>

          {/* Resources Grid */}
          <div role="tabpanel" aria-labelledby={`${activeTab}-tab`}>
            {currentResources.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6 md:gap-8">
                {currentResources.map((resource, index) => (
                  <ResourceCard
                    key={resource.id || index}
                    platform={resource.platform || resource.provider || 'Learning Platform'}
                    creator={resource.creator || resource.provider || 'Various'}
                    title={resource.title || resource.name || 'Learning Resource'}
                    link={resource.link || resource.url}
                    type={resource.type || 'Course'}
                  />
                ))}
              </div>
            ) : (
              <div className="text-center py-16">
                <div className="bg-slate-800/80 backdrop-blur-sm rounded-2xl p-12 border border-slate-700/50 max-w-md mx-auto">
                  <div className="w-20 h-20 bg-slate-700/50 rounded-full flex items-center justify-center mx-auto mb-6">
                    <svg
                      className="h-10 w-10 text-gray-400"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                      xmlns="http://www.w3.org/2000/svg"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"
                      />
                    </svg>
                  </div>
                  <h3 className="text-xl font-bold text-gray-300 mb-3">
                    No {activeTab} resources available
                  </h3>
                  <p className="text-gray-400 leading-relaxed">
                    {activeTab === 'free' 
                      ? 'There are currently no free resources for this learning path. Try switching to the other tab or generate a new roadmap.'
                      : 'There are currently no paid resources for this learning path. Try switching to the other tab or generate a new roadmap.'
                    }
                  </p>
                </div>
              </div>
            )}
          </div>

          {/* Back to Roadmap Button */}
          <div className="mt-16 text-center">
            <button
              onClick={() => navigate('/roadmap')}
              className="bg-slate-700/80 backdrop-blur-sm hover:bg-slate-600 text-white font-semibold py-3 px-8 rounded-xl transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-slate-500 focus:ring-offset-2 focus:ring-offset-slate-900 border border-slate-600/50 hover:border-slate-500"
            >
              <span className="flex items-center justify-center">
                <svg className="mr-2 w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
                </svg>
                Back to Roadmap
              </span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Resources;