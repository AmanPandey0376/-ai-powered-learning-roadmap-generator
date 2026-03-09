import React, { useState } from 'react'
import { Link, useLocation } from 'react-router-dom'

const Navbar = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false)
  const location = useLocation()

  const isActive = (path) => {
    return location.pathname === path
  }

  const toggleMenu = () => {
    setIsMenuOpen(!isMenuOpen)
  }

  return (
    <nav className="bg-slate-900 border-b border-slate-700 shadow-lg sticky top-0 z-50" role="navigation" aria-label="Main navigation">
      <div className="max-w-6xl mx-auto px-4 md:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <div className="flex-shrink-0">
            <Link 
              to="/" 
              className="text-xl font-bold text-primary hover:text-blue-400 transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 focus:ring-offset-slate-900 rounded-md px-2 py-1"
              aria-label="Learning Roadmap Generator - Home"
            >
              Learning Roadmap
            </Link>
          </div>

          {/* Desktop Navigation */}
          <div className="hidden md:block">
            <div className="ml-10 flex items-baseline space-x-2">
              <Link
                to="/"
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 focus:ring-offset-slate-900 ${
                  isActive('/')
                    ? 'bg-primary text-white shadow-md transform scale-105'
                    : 'text-gray-300 hover:bg-slate-700 hover:text-white hover:shadow-md hover:transform hover:scale-105'
                }`}
              >
                Home
              </Link>
              <Link
                to="/roadmap"
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 focus:ring-offset-slate-900 ${
                  isActive('/roadmap')
                    ? 'bg-primary text-white shadow-md transform scale-105'
                    : 'text-gray-300 hover:bg-slate-700 hover:text-white hover:shadow-md hover:transform hover:scale-105'
                }`}
              >
                Roadmap
              </Link>
              <Link
                to="/resources"
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 focus:ring-offset-slate-900 ${
                  isActive('/resources')
                    ? 'bg-primary text-white shadow-md transform scale-105'
                    : 'text-gray-300 hover:bg-slate-700 hover:text-white hover:shadow-md hover:transform hover:scale-105'
                }`}
              >
                Resources
              </Link>
            </div>
          </div>

          {/* Mobile menu button */}
          <div className="md:hidden">
            <button
              onClick={toggleMenu}
              className="inline-flex items-center justify-center p-2 rounded-lg text-gray-300 hover:text-white hover:bg-slate-700 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-primary transition-all duration-300"
              aria-expanded={isMenuOpen}
              aria-label="Toggle navigation menu"
              aria-controls="mobile-menu"
              id="mobile-menu-button"
            >
              <span className="sr-only">Open main menu</span>
              {/* Hamburger icon */}
              <svg
                className={`${isMenuOpen ? 'hidden' : 'block'} h-6 w-6 transition-transform duration-300`}
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                aria-hidden="true"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  d="M4 6h16M4 12h16M4 18h16"
                />
              </svg>
              {/* Close icon */}
              <svg
                className={`${isMenuOpen ? 'block' : 'hidden'} h-6 w-6 transition-transform duration-300 rotate-180`}
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                aria-hidden="true"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Navigation Menu */}
      <div 
        className={`${isMenuOpen ? 'block animate-fadeIn' : 'hidden'} md:hidden bg-slate-800 border-t border-slate-700`}
        id="mobile-menu"
        aria-labelledby="mobile-menu-button"
      >
        <div className="px-4 pt-2 pb-3 space-y-1" role="menu">
          <Link
            to="/"
            onClick={() => setIsMenuOpen(false)}
            className={`block px-4 py-3 rounded-lg text-base font-medium transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 focus:ring-offset-slate-800 ${
              isActive('/')
                ? 'bg-primary text-white shadow-md'
                : 'text-gray-300 hover:bg-slate-700 hover:text-white hover:shadow-md'
            }`}
            role="menuitem"
          >
            Home
          </Link>
          <Link
            to="/roadmap"
            onClick={() => setIsMenuOpen(false)}
            className={`block px-4 py-3 rounded-lg text-base font-medium transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 focus:ring-offset-slate-800 ${
              isActive('/roadmap')
                ? 'bg-primary text-white shadow-md'
                : 'text-gray-300 hover:bg-slate-700 hover:text-white hover:shadow-md'
            }`}
            role="menuitem"
          >
            Roadmap
          </Link>
          <Link
            to="/resources"
            onClick={() => setIsMenuOpen(false)}
            className={`block px-4 py-3 rounded-lg text-base font-medium transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 focus:ring-offset-slate-800 ${
              isActive('/resources')
                ? 'bg-primary text-white shadow-md'
                : 'text-gray-300 hover:bg-slate-700 hover:text-white hover:shadow-md'
            }`}
            role="menuitem"
          >
            Resources
          </Link>
        </div>
      </div>
    </nav>
  )
}

export default Navbar