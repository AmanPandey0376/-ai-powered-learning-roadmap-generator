import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

function Roadmap() {
  const [roadmapData, setRoadmapData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    // Retrieve roadmap data from localStorage
    const storedData = localStorage.getItem('roadmapData');
    
    if (!storedData) {
      // Redirect to Home page if no data exists
      navigate('/');
      return;
    }

    try {
      const parsedData = JSON.parse(storedData);
      
      // Validate that we have the required roadmap data
      if (!parsedData.roadmap) {
        navigate('/');
        return;
      }

      if (!parsedData.roadmap.modules || parsedData.roadmap.modules.length === 0) {
        setError('The roadmap appears to be empty. Please generate a new roadmap.');
        setLoading(false);
        return;
      }

      setRoadmapData(parsedData);
    } catch (parseError) {
      console.error('Error parsing roadmap data:', parseError);
      navigate('/');
      return;
    } finally {
      setLoading(false);
    }
  }, [navigate]);

  const handleNavigateToResources = () => {
    console.log('Navigating to resources page...');
    const storedData = localStorage.getItem('roadmapData');
    console.log('Current localStorage data:', storedData ? JSON.parse(storedData) : 'No data');
    navigate('/resources');
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-900 to-slate-800 flex items-center justify-center">
        <div className="max-w-md mx-auto text-center">
          <div className="bg-slate-800/80 backdrop-blur-sm rounded-2xl p-12 border border-slate-700/50 shadow-2xl">
            <div className="relative mb-6">
              <div className="animate-spin rounded-full h-12 w-12 border-4 border-slate-600 mx-auto"></div>
              <div className="animate-spin rounded-full h-12 w-12 border-4 border-primary border-t-transparent absolute top-0 left-1/2 transform -translate-x-1/2"></div>
            </div>
            <h3 className="text-xl font-bold text-white mb-2">Loading Your Roadmap</h3>
            <p className="text-gray-300">Please wait while we prepare your learning journey...</p>
          </div>
        </div>
      </div>
    );
  }

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
            <h3 className="text-xl font-bold text-white mb-3">Roadmap Not Available</h3>
            <p className="text-gray-300 mb-8 leading-relaxed">{error}</p>
            <button
              onClick={() => navigate('/')}
              className="bg-gradient-to-r from-primary to-blue-600 hover:from-blue-600 hover:to-blue-700 text-white font-bold py-3 px-8 rounded-xl transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 focus:ring-offset-slate-900 transform hover:scale-105 shadow-lg"
            >
              Generate New Roadmap
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (!roadmapData) {
    return null;
  }

  const { roadmap, skill } = roadmapData;

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-900 to-slate-800">
      <div className="container mx-auto px-4 py-8 md:py-12">
        <div className="max-w-5xl mx-auto">
          {/* Header Section */}
          <div className="mb-12 text-center">
            <h1 className="text-3xl md:text-4xl font-bold mb-4 bg-gradient-to-r from-white to-blue-200 bg-clip-text text-transparent">
              Your Learning Roadmap
            </h1>
            <div className="bg-slate-800/60 backdrop-blur-sm rounded-xl p-6 border border-slate-700/50 inline-block">
              <p className="text-lg text-gray-300">
                Personalized roadmap for: <span className="text-primary font-bold text-xl">{skill}</span>
              </p>
            </div>
          </div>

          {/* Roadmap Title */}
          {roadmap.title && (
            <div className="mb-8 text-center">
              <h2 className="text-2xl md:text-3xl font-bold text-primary bg-primary/10 rounded-xl p-4 border border-primary/20">
                {roadmap.title}
              </h2>
            </div>
          )}

          {/* Learning Modules */}
          <div className="space-y-8 mb-12">
            {roadmap.modules && roadmap.modules.length > 0 ? roadmap.modules.map((module, index) => (
              <div key={module.id || index} className="bg-slate-800/80 backdrop-blur-sm rounded-2xl p-8 shadow-xl border border-slate-700/50 hover:border-slate-600/50 transition-all duration-300">
                {/* Module Header */}
                <div className="mb-6">
                  <div className="flex items-center mb-4">
                    <div className="bg-gradient-to-r from-primary to-blue-600 text-white rounded-full w-12 h-12 flex items-center justify-center text-lg font-bold mr-4 shadow-lg">
                      {index + 1}
                    </div>
                    <div className="flex-1">
                      <h3 className="text-xl md:text-2xl font-bold text-white mb-1">{module.name}</h3>
                      <div className="h-1 bg-gradient-to-r from-primary to-transparent rounded-full w-24"></div>
                    </div>
                  </div>
                  {module.description && (
                    <p className="text-gray-300 ml-16 text-lg leading-relaxed">{module.description}</p>
                  )}
                </div>

                {/* Mini Projects */}
                {module.miniProjects && module.miniProjects.length > 0 && (
                  <div className="ml-16">
                    <h4 className="text-lg font-bold text-gray-200 mb-4 flex items-center">
                      <svg className="w-5 h-5 mr-2 text-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                      </svg>
                      Mini Projects:
                    </h4>
                    <div className="grid gap-4 md:grid-cols-2">
                      {module.miniProjects.map((project, projectIndex) => (
                        <div key={project.id || projectIndex} className="bg-slate-700/80 rounded-xl p-6 border border-slate-600/50 hover:border-accent/50 transition-all duration-300 hover:shadow-lg">
                          <h5 className="font-bold text-white mb-2 text-lg">{project.name}</h5>
                          {project.description && (
                            <p className="text-gray-300 text-sm mb-3 leading-relaxed">{project.description}</p>
                          )}
                          {project.estimatedHours && (
                            <div className="flex items-center text-accent text-sm font-medium">
                              <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                              </svg>
                              {project.estimatedHours} hours
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )) : (
              <div className="bg-slate-800/80 backdrop-blur-sm rounded-2xl p-12 text-center border border-slate-700/50">
                <svg
                  className="mx-auto h-16 w-16 text-gray-400 mb-6"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                  />
                </svg>
                <h3 className="text-xl font-bold text-gray-300 mb-3">No Learning Modules</h3>
                <p className="text-gray-400 max-w-md mx-auto">
                  This roadmap doesn't contain any learning modules. Please generate a new roadmap.
                </p>
              </div>
            )}
          </div>

          {/* Major Project */}
          {roadmap.majorProject && (
            <div className="bg-gradient-to-br from-accent/20 via-primary/20 to-purple-500/20 rounded-2xl p-8 mb-12 border border-accent/30 shadow-2xl">
              <div className="flex items-center mb-6">
                <div className="bg-gradient-to-r from-accent to-emerald-400 text-white rounded-full w-14 h-14 flex items-center justify-center text-2xl font-bold mr-4 shadow-lg">
                  ★
                </div>
                <div>
                  <h3 className="text-2xl md:text-3xl font-bold text-white mb-1">Capstone Project</h3>
                  <p className="text-emerald-200 font-medium">Final project to showcase your skills</p>
                </div>
              </div>
              
              <div className="ml-18">
                <h4 className="text-xl md:text-2xl font-bold text-white mb-4">{roadmap.majorProject.name}</h4>
                {roadmap.majorProject.description && (
                  <p className="text-blue-100 mb-6 text-lg leading-relaxed">{roadmap.majorProject.description}</p>
                )}
                
                {roadmap.majorProject.requirements && roadmap.majorProject.requirements.length > 0 && (
                  <div className="mb-6">
                    <h5 className="font-bold text-emerald-200 mb-3 text-lg flex items-center">
                      <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z" />
                      </svg>
                      Requirements:
                    </h5>
                    <ul className="space-y-2 text-blue-100">
                      {roadmap.majorProject.requirements.map((requirement, index) => (
                        <li key={index} className="flex items-start">
                          <svg className="w-4 h-4 mr-3 mt-1 text-accent flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                          </svg>
                          {requirement}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
                
                {roadmap.majorProject.estimatedHours && (
                  <div className="flex items-center text-accent font-bold text-lg">
                    <svg className="w-6 h-6 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    Estimated time: {roadmap.majorProject.estimatedHours} hours
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Navigation to Resources */}
          <div className="text-center">
            <button
              onClick={handleNavigateToResources}
              className="bg-gradient-to-r from-primary to-blue-600 hover:from-blue-600 hover:to-blue-700 text-white font-bold py-4 px-10 rounded-xl transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 focus:ring-offset-slate-900 transform hover:scale-105 shadow-lg hover:shadow-xl text-lg"
            >
              <span className="flex items-center justify-center">
                View Learning Resources
                <svg className="ml-2 w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                </svg>
              </span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Roadmap;