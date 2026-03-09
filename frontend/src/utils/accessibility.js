/**
 * Accessibility Testing Utilities
 * Provides functions to test and validate accessibility compliance
 */

/**
 * Color contrast ratio calculation using WCAG 2.1 guidelines
 * @param {string} foreground - Foreground color (hex)
 * @param {string} background - Background color (hex)
 * @returns {number} Contrast ratio
 */
export function calculateContrastRatio(foreground, background) {
  // Convert hex to RGB
  const hexToRgb = (hex) => {
    const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
    return result ? {
      r: parseInt(result[1], 16),
      g: parseInt(result[2], 16),
      b: parseInt(result[3], 16)
    } : null;
  };

  // Calculate relative luminance
  const getLuminance = (rgb) => {
    const { r, g, b } = rgb;
    const [rs, gs, bs] = [r, g, b].map(c => {
      c = c / 255;
      return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
    });
    return 0.2126 * rs + 0.7152 * gs + 0.0722 * bs;
  };

  const fg = hexToRgb(foreground);
  const bg = hexToRgb(background);
  
  if (!fg || !bg) return 0;

  const fgLum = getLuminance(fg);
  const bgLum = getLuminance(bg);
  
  const lighter = Math.max(fgLum, bgLum);
  const darker = Math.min(fgLum, bgLum);
  
  return (lighter + 0.05) / (darker + 0.05);
}

/**
 * Validate color contrast ratios for WCAG AA compliance
 * @param {Array} colorPairs - Array of {foreground, background, context} objects
 * @returns {Array} Validation results
 */
export function validateColorContrast(colorPairs) {
  const results = [];
  
  colorPairs.forEach(({ foreground, background, context, isLargeText = false }) => {
    const ratio = calculateContrastRatio(foreground, background);
    const minRatio = isLargeText ? 3.0 : 4.5; // WCAG AA standards
    const minRatioAAA = isLargeText ? 4.5 : 7.0; // WCAG AAA standards
    
    results.push({
      context,
      foreground,
      background,
      ratio: Math.round(ratio * 100) / 100,
      passesAA: ratio >= minRatio,
      passesAAA: ratio >= minRatioAAA,
      minRequired: minRatio,
      isLargeText
    });
  });
  
  return results;
}

/**
 * Test keyboard navigation functionality
 * @param {HTMLElement} container - Container element to test
 * @returns {Object} Test results
 */
export function testKeyboardNavigation(container) {
  const focusableElements = container.querySelectorAll(
    'a[href], button, textarea, input[type="text"], input[type="radio"], input[type="checkbox"], select, [tabindex]:not([tabindex="-1"])'
  );
  
  const results = {
    totalFocusableElements: focusableElements.length,
    elementsWithTabIndex: 0,
    elementsWithAriaLabels: 0,
    elementsWithoutAccessibleNames: [],
    keyboardTrappable: true
  };
  
  focusableElements.forEach((element, index) => {
    // Check for tabindex
    if (element.hasAttribute('tabindex')) {
      results.elementsWithTabIndex++;
    }
    
    // Check for ARIA labels or accessible names
    const hasAriaLabel = element.hasAttribute('aria-label');
    const hasAriaLabelledBy = element.hasAttribute('aria-labelledby');
    const hasTitle = element.hasAttribute('title');
    const hasTextContent = element.textContent.trim().length > 0;
    const hasAltText = element.hasAttribute('alt');
    
    if (hasAriaLabel || hasAriaLabelledBy || hasTitle || hasTextContent || hasAltText) {
      results.elementsWithAriaLabels++;
    } else {
      results.elementsWithoutAccessibleNames.push({
        element: element.tagName.toLowerCase(),
        index,
        id: element.id || 'no-id',
        className: element.className || 'no-class'
      });
    }
  });
  
  return results;
}

/**
 * Validate semantic HTML structure
 * @param {HTMLElement} container - Container element to test
 * @returns {Object} Validation results
 */
export function validateSemanticHTML(container) {
  const results = {
    hasMainLandmark: !!container.querySelector('main'),
    hasNavLandmark: !!container.querySelector('nav'),
    headingStructure: [],
    missingAltText: [],
    formLabels: [],
    ariaRoles: []
  };
  
  // Check heading structure
  const headings = container.querySelectorAll('h1, h2, h3, h4, h5, h6');
  headings.forEach(heading => {
    results.headingStructure.push({
      level: parseInt(heading.tagName.charAt(1)),
      text: heading.textContent.trim(),
      hasId: !!heading.id
    });
  });
  
  // Check images for alt text
  const images = container.querySelectorAll('img');
  images.forEach((img, index) => {
    if (!img.hasAttribute('alt')) {
      results.missingAltText.push({
        index,
        src: img.src || 'no-src',
        id: img.id || 'no-id'
      });
    }
  });
  
  // Check form labels
  const inputs = container.querySelectorAll('input, textarea, select');
  inputs.forEach((input, index) => {
    const hasLabel = !!container.querySelector(`label[for="${input.id}"]`);
    const hasAriaLabel = input.hasAttribute('aria-label');
    const hasAriaLabelledBy = input.hasAttribute('aria-labelledby');
    
    results.formLabels.push({
      index,
      id: input.id || 'no-id',
      type: input.type || input.tagName.toLowerCase(),
      hasLabel: hasLabel || hasAriaLabel || hasAriaLabelledBy
    });
  });
  
  // Check ARIA roles
  const elementsWithRoles = container.querySelectorAll('[role]');
  elementsWithRoles.forEach(element => {
    results.ariaRoles.push({
      element: element.tagName.toLowerCase(),
      role: element.getAttribute('role'),
      id: element.id || 'no-id'
    });
  });
  
  return results;
}

/**
 * Generate accessibility report
 * @param {HTMLElement} container - Container element to test
 * @returns {Object} Complete accessibility report
 */
export function generateAccessibilityReport(container) {
  // Define color pairs used in the application
  const colorPairs = [
    { foreground: '#ffffff', background: '#0f172a', context: 'Primary text on background' },
    { foreground: '#d1d5db', background: '#0f172a', context: 'Secondary text on background' },
    { foreground: '#ffffff', background: '#3b82f6', context: 'Button text on primary' },
    { foreground: '#ffffff', background: '#1e293b', context: 'Text on slate-800' },
    { foreground: '#3b82f6', background: '#0f172a', context: 'Primary color on background' },
    { foreground: '#10b981', background: '#0f172a', context: 'Accent color on background' },
    { foreground: '#ef4444', background: '#0f172a', context: 'Error color on background' },
    { foreground: '#ffffff', background: '#475569', context: 'Text on slate-600' },
    { foreground: '#d1d5db', background: '#1e293b', context: 'Secondary text on slate-800' }
  ];
  
  const report = {
    timestamp: new Date().toISOString(),
    colorContrast: validateColorContrast(colorPairs),
    keyboardNavigation: testKeyboardNavigation(container),
    semanticHTML: validateSemanticHTML(container),
    summary: {
      totalIssues: 0,
      criticalIssues: 0,
      warnings: 0,
      passed: 0
    }
  };
  
  // Calculate summary
  report.colorContrast.forEach(result => {
    if (!result.passesAA) {
      report.summary.criticalIssues++;
      report.summary.totalIssues++;
    } else if (!result.passesAAA) {
      report.summary.warnings++;
      report.summary.totalIssues++;
    } else {
      report.summary.passed++;
    }
  });
  
  if (report.keyboardNavigation.elementsWithoutAccessibleNames.length > 0) {
    report.summary.criticalIssues += report.keyboardNavigation.elementsWithoutAccessibleNames.length;
    report.summary.totalIssues += report.keyboardNavigation.elementsWithoutAccessibleNames.length;
  }
  
  if (report.semanticHTML.missingAltText.length > 0) {
    report.summary.criticalIssues += report.semanticHTML.missingAltText.length;
    report.summary.totalIssues += report.semanticHTML.missingAltText.length;
  }
  
  report.semanticHTML.formLabels.forEach(label => {
    if (!label.hasLabel) {
      report.summary.criticalIssues++;
      report.summary.totalIssues++;
    }
  });
  
  return report;
}

/**
 * Screen reader testing utilities
 */
export const screenReaderUtils = {
  /**
   * Announce text to screen readers
   * @param {string} message - Message to announce
   * @param {string} priority - Priority level ('polite' or 'assertive')
   */
  announce(message, priority = 'polite') {
    const announcer = document.createElement('div');
    announcer.setAttribute('aria-live', priority);
    announcer.setAttribute('aria-atomic', 'true');
    announcer.className = 'sr-only';
    announcer.textContent = message;
    
    document.body.appendChild(announcer);
    
    // Remove after announcement
    setTimeout(() => {
      document.body.removeChild(announcer);
    }, 1000);
  },
  
  /**
   * Create screen reader only text
   * @param {string} text - Text for screen readers only
   * @returns {HTMLElement} Screen reader only element
   */
  createSROnlyText(text) {
    const element = document.createElement('span');
    element.className = 'sr-only';
    element.textContent = text;
    return element;
  }
};

/**
 * Focus management utilities
 */
export const focusUtils = {
  /**
   * Trap focus within a container
   * @param {HTMLElement} container - Container to trap focus within
   */
  trapFocus(container) {
    const focusableElements = container.querySelectorAll(
      'a[href], button, textarea, input[type="text"], input[type="radio"], input[type="checkbox"], select, [tabindex]:not([tabindex="-1"])'
    );
    
    if (focusableElements.length === 0) return;
    
    const firstElement = focusableElements[0];
    const lastElement = focusableElements[focusableElements.length - 1];
    
    const handleTabKey = (e) => {
      if (e.key === 'Tab') {
        if (e.shiftKey) {
          if (document.activeElement === firstElement) {
            e.preventDefault();
            lastElement.focus();
          }
        } else {
          if (document.activeElement === lastElement) {
            e.preventDefault();
            firstElement.focus();
          }
        }
      }
    };
    
    container.addEventListener('keydown', handleTabKey);
    
    // Return cleanup function
    return () => {
      container.removeEventListener('keydown', handleTabKey);
    };
  },
  
  /**
   * Restore focus to a previously focused element
   * @param {HTMLElement} element - Element to restore focus to
   */
  restoreFocus(element) {
    if (element && typeof element.focus === 'function') {
      element.focus();
    }
  }
};