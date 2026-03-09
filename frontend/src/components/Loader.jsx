import React from 'react';

const Loader = () => {
  return (
    <div className="fixed inset-0 bg-slate-900 bg-opacity-90 backdrop-blur-sm flex items-center justify-center z-50">
      <div className="bg-slate-800 rounded-xl p-8 shadow-2xl border border-slate-700">
        <div className="flex flex-col items-center space-y-4">
          <div className="relative">
            <div className="animate-spin rounded-full h-12 w-12 border-4 border-slate-600"></div>
            <div className="animate-spin rounded-full h-12 w-12 border-4 border-primary border-t-transparent absolute top-0 left-0"></div>
          </div>
          <div className="text-center">
            <p className="text-white font-medium">Loading...</p>
            <p className="text-gray-400 text-sm mt-1">Please wait while we process your request</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Loader;