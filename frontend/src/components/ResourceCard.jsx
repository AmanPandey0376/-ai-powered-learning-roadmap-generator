import React from 'react';

const ResourceCard = ({ platform, creator, title, link, type }) => {
  const handleLinkClick = (e) => {
    e.preventDefault();
    
    // Validate link before opening
    if (!link) {
      console.error('No link provided for resource:', title);
      return;
    }
    
    try {
      // Basic URL validation
      const url = new URL(link);
      if (url.protocol !== 'http:' && url.protocol !== 'https:') {
        console.error('Invalid URL protocol:', link);
        return;
      }
      
      window.open(link, '_blank', 'noopener,noreferrer');
    } catch (error) {
      console.error('Invalid URL:', link, error);
      // Fallback: try to open anyway in case it's a relative URL
      window.open(link, '_blank', 'noopener,noreferrer');
    }
  };

  // Handle missing required props
  if (!title || !platform) {
    return (
      <div className="bg-gray-800 rounded-lg shadow-sm border border-gray-700 p-6">
        <div className="text-center text-gray-400">
          <svg
            className="mx-auto h-8 w-8 mb-2"
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
          <p className="text-sm">Resource information unavailable</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-slate-800 rounded-xl shadow-lg border border-slate-700 p-6 hover:shadow-xl hover:border-slate-600 hover:transform hover:scale-105 transition-all duration-300 group">
      {/* Platform and Type */}
      <div className="flex items-center justify-between mb-4">
        <span className="text-primary font-semibold text-sm uppercase tracking-wider bg-blue-500/10 px-3 py-1 rounded-full">
          {platform}
        </span>
        {type && (
          <span className="text-xs text-gray-400 bg-slate-700 px-3 py-1 rounded-full border border-slate-600">
            {type}
          </span>
        )}
      </div>

      {/* Title */}
      <h3 className="text-white font-bold text-lg mb-3 line-clamp-2 group-hover:text-blue-100 transition-colors duration-300">
        {title}
      </h3>

      {/* Creator */}
      <p className="text-gray-300 text-sm mb-6 flex items-center">
        <svg className="w-4 h-4 mr-2 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
        </svg>
        by <span className="font-semibold text-white ml-1">{creator}</span>
      </p>

      {/* Link Button */}
      {link ? (
        <button
          onClick={handleLinkClick}
          className="w-full bg-primary hover:bg-blue-600 text-white font-semibold py-3 px-4 rounded-lg transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 focus:ring-offset-slate-800 hover:shadow-lg transform hover:scale-105 group/button"
          aria-label={`Open ${title} on ${platform}`}
        >
          <span className="flex items-center justify-center">
            View Resource
            <svg
              className="ml-2 w-4 h-4 transition-transform duration-300 group-hover/button:translate-x-1"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"
              />
            </svg>
          </span>
        </button>
      ) : (
        <div className="w-full bg-slate-600 text-gray-400 font-medium py-3 px-4 rounded-lg text-center border border-slate-500">
          Link not available
        </div>
      )}
    </div>
  );
};

export default ResourceCard;