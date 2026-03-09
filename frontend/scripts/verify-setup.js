#!/usr/bin/env node

/**
 * Development Verification Script
 * Verifies that the application is properly configured and ready to run
 */

import { existsSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const projectRoot = join(__dirname, '..');

console.log('🔍 Verifying development setup...\n');

const checks = [
  {
    name: 'Node modules installed',
    check: () => existsSync(join(projectRoot, 'node_modules')),
    fix: 'Run: npm install'
  },
  {
    name: 'Environment file exists',
    check: () => existsSync(join(projectRoot, '.env.development')),
    fix: 'Run: npm run dev:setup'
  },
  {
    name: 'Package.json exists',
    check: () => existsSync(join(projectRoot, 'package.json')),
    fix: 'Package.json is missing - this is a critical error'
  },
  {
    name: 'Vite config exists',
    check: () => existsSync(join(projectRoot, 'vite.config.js')),
    fix: 'Vite configuration is missing'
  },
  {
    name: 'API utility exists',
    check: () => existsSync(join(projectRoot, 'src', 'utils', 'api.js')),
    fix: 'API utility is missing'
  },
  {
    name: 'Main entry point exists',
    check: () => existsSync(join(projectRoot, 'src', 'main.jsx')),
    fix: 'Main entry point is missing'
  }
];

let allPassed = true;

checks.forEach(({ name, check, fix }) => {
  const passed = check();
  const status = passed ? '✅' : '❌';
  console.log(`${status} ${name}`);
  
  if (!passed) {
    console.log(`   Fix: ${fix}`);
    allPassed = false;
  }
});

console.log('\n' + '='.repeat(50));

if (allPassed) {
  console.log('🎉 All checks passed! Your development environment is ready.');
  console.log('\nTo start developing:');
  console.log('  npm run dev');
  console.log('\nThe application will be available at:');
  console.log('  http://localhost:3000');
  console.log('\nAPI requests will be proxied to:');
  console.log('  http://localhost:8000/api');
} else {
  console.log('⚠️  Some checks failed. Please fix the issues above before starting development.');
  process.exit(1);
}

console.log('\n📚 For more information, see:');
console.log('  - src/utils/README.md (API documentation)');
console.log('  - .env.example (environment configuration)');