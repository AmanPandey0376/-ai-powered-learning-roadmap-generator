/**
 * Manual Accessibility Testing Script
 * Run this in the browser console to perform accessibility checks
 */

import { generateAccessibilityReport } from '../utils/accessibility.js';

/**
 * Run comprehensive accessibility tests
 */
function runAccessibilityTests() {
  console.log('🔍 Starting Accessibility Testing...\n');
  
  const container = document.body;
  const report = generateAccessibilityReport(container);
  
  console.log('📊 ACCESSIBILITY REPORT');
  console.log('='.repeat(50));
  console.log(`Generated: ${new Date(report.timestamp).toLocaleString()}`);
  console.log(`Total Issues: ${report.summary.totalIssues}`);
  console.log(`Critical Issues: ${report.summary.criticalIssues}`);
  console.log(`Warnings: ${report.summary.warnings}`);
  console.log(`Passed: ${report.summary.passed}\n`);
  
  // Color Contrast Results
  console.log('🎨 COLOR CONTRAST ANALYSIS');
  console.log('-'.repeat(30));
  report.colorContrast.forEach(result => {
    const status = result.passesAA ? '✅' : '❌';
    const level = result.passesAAA ? 'AAA' : result.passesAA ? 'AA' : 'FAIL';
    console.log(`${status} ${result.context}`);
    console.log(`   Ratio: ${result.ratio}:1 (${level})`);
    console.log(`   Colors: ${result.foreground} on ${result.background}`);
    if (!result.passesAA) {
      console.log(`   ⚠️  Minimum required: ${result.minRequired}:1`);
    }
    console.log('');
  });
  
  // Keyboard Navigation Results
  console.log('⌨️  KEYBOARD NAVIGATION ANALYSIS');
  console.log('-'.repeat(35));
  console.log(`Total focusable elements: ${report.keyboardNavigation.totalFocusableElements}`);
  console.log(`Elements with ARIA labels: ${report.keyboardNavigation.elementsWithAriaLabels}`);
  
  if (report.keyboardNavigation.elementsWithoutAccessibleNames.length > 0) {
    console.log('❌ Elements without accessible names:');
    report.keyboardNavigation.elementsWithoutAccessibleNames.forEach(element => {
      console.log(`   - ${element.element} (${element.id || element.className})`);
    });
  } else {
    console.log('✅ All focusable elements have accessible names');
  }
  console.log('');
  
  // Semantic HTML Results
  console.log('🏗️  SEMANTIC HTML ANALYSIS');
  console.log('-'.repeat(30));
  console.log(`Has main landmark: ${report.semanticHTML.hasMainLandmark ? '✅' : '❌'}`);
  console.log(`Has nav landmark: ${report.semanticHTML.hasNavLandmark ? '✅' : '❌'}`);
  
  // Heading Structure
  if (report.semanticHTML.headingStructure.length > 0) {
    console.log('📝 Heading Structure:');
    report.semanticHTML.headingStructure.forEach((heading, index) => {
      const indent = '  '.repeat(heading.level - 1);
      console.log(`   ${indent}H${heading.level}: ${heading.text.substring(0, 50)}${heading.text.length > 50 ? '...' : ''}`);
    });
  }
  
  // Missing Alt Text
  if (report.semanticHTML.missingAltText.length > 0) {
    console.log('❌ Images missing alt text:');
    report.semanticHTML.missingAltText.forEach(img => {
      console.log(`   - Image ${img.index}: ${img.src}`);
    });
  } else {
    console.log('✅ All images have alt text');
  }
  
  // Form Labels
  const unlabeledInputs = report.semanticHTML.formLabels.filter(label => !label.hasLabel);
  if (unlabeledInputs.length > 0) {
    console.log('❌ Form inputs without labels:');
    unlabeledInputs.forEach(input => {
      console.log(`   - ${input.type} (${input.id})`);
    });
  } else {
    console.log('✅ All form inputs have proper labels');
  }
  
  // ARIA Roles
  if (report.semanticHTML.ariaRoles.length > 0) {
    console.log('🏷️  ARIA Roles:');
    report.semanticHTML.ariaRoles.forEach(role => {
      console.log(`   - ${role.element}: ${role.role}`);
    });
  }
  
  console.log('\n' + '='.repeat(50));
  
  if (report.summary.criticalIssues === 0) {
    console.log('🎉 ACCESSIBILITY TEST PASSED!');
    console.log('All critical accessibility requirements are met.');
  } else {
    console.log('⚠️  ACCESSIBILITY ISSUES FOUND');
    console.log(`Please address ${report.summary.criticalIssues} critical issue(s).`);
  }
  
  return report;
}

/**
 * Test keyboard navigation manually
 */
function testKeyboardNavigation() {
  console.log('⌨️  KEYBOARD NAVIGATION TEST');
  console.log('='.repeat(40));
  console.log('Instructions:');
  console.log('1. Press Tab to navigate through focusable elements');
  console.log('2. Press Shift+Tab to navigate backwards');
  console.log('3. Press Enter/Space on buttons and links');
  console.log('4. Use arrow keys in tab lists and menus');
  console.log('5. Press Escape to close modals/menus');
  console.log('\nFocusable elements will be highlighted as you navigate.');
  
  // Add visual focus indicator for testing
  const style = document.createElement('style');
  style.textContent = `
    *:focus {
      outline: 3px solid #ff6b6b !important;
      outline-offset: 2px !important;
      box-shadow: 0 0 0 5px rgba(255, 107, 107, 0.3) !important;
    }
  `;
  document.head.appendChild(style);
  
  // Focus the first focusable element
  const firstFocusable = document.querySelector('a, button, input, textarea, select, [tabindex]:not([tabindex="-1"])');
  if (firstFocusable) {
    firstFocusable.focus();
    console.log('✅ Started keyboard navigation test. First element focused.');
  }
  
  return () => {
    document.head.removeChild(style);
    console.log('🏁 Keyboard navigation test ended.');
  };
}

/**
 * Test screen reader announcements
 */
function testScreenReaderAnnouncements() {
  console.log('📢 SCREEN READER ANNOUNCEMENT TEST');
  console.log('='.repeat(45));
  
  // Create live region for testing
  const liveRegion = document.createElement('div');
  liveRegion.setAttribute('aria-live', 'polite');
  liveRegion.setAttribute('aria-atomic', 'true');
  liveRegion.className = 'sr-only';
  liveRegion.id = 'test-announcements';
  document.body.appendChild(liveRegion);
  
  const announcements = [
    'Screen reader test started',
    'Testing polite announcements',
    'This should be announced to screen readers',
    'Screen reader test completed'
  ];
  
  announcements.forEach((message, index) => {
    setTimeout(() => {
      liveRegion.textContent = message;
      console.log(`📢 Announced: "${message}"`);
      
      if (index === announcements.length - 1) {
        setTimeout(() => {
          document.body.removeChild(liveRegion);
          console.log('✅ Screen reader test completed');
        }, 2000);
      }
    }, index * 2000);
  });
  
  console.log('🔊 Listen for screen reader announcements...');
}

/**
 * Check color contrast for specific elements
 */
function checkElementContrast(selector) {
  const element = document.querySelector(selector);
  if (!element) {
    console.log(`❌ Element not found: ${selector}`);
    return;
  }
  
  const styles = window.getComputedStyle(element);
  const color = styles.color;
  const backgroundColor = styles.backgroundColor;
  
  console.log(`🎨 Color contrast for: ${selector}`);
  console.log(`   Text color: ${color}`);
  console.log(`   Background: ${backgroundColor}`);
  
  // Note: This is a simplified check. Full implementation would need
  // to convert computed styles to hex and calculate actual contrast ratio
}

/**
 * Export functions for manual testing
 */
window.accessibilityTest = {
  runAll: runAccessibilityTests,
  testKeyboard: testKeyboardNavigation,
  testScreenReader: testScreenReaderAnnouncements,
  checkContrast: checkElementContrast
};

console.log('🔧 Accessibility testing tools loaded!');
console.log('Available commands:');
console.log('- accessibilityTest.runAll() - Run complete accessibility audit');
console.log('- accessibilityTest.testKeyboard() - Test keyboard navigation');
console.log('- accessibilityTest.testScreenReader() - Test screen reader announcements');
console.log('- accessibilityTest.checkContrast(selector) - Check color contrast for element');

export { runAccessibilityTests, testKeyboardNavigation, testScreenReaderAnnouncements, checkElementContrast };