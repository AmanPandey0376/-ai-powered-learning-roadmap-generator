#!/usr/bin/env node

/**
 * Development Setup Script
 * Ensures the application is ready to run in development mode
 */

import { existsSync, copyFileSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const projectRoot = join(__dirname, '..');

console.log('🚀 Setting up development environment...');

// Check if .env.development exists, if not copy from example
const envDevPath = join(projectRoot, '.env.development');
const envExamplePath = join(projectRoot, '.env.example');

if (!existsSync(envDevPath)) {
  if (existsSync(envExamplePath)) {
    copyFileSync(envExamplePath, envDevPath);
    console.log('✅ Created .env.development from .env.example');
  } else {
    console.log('⚠️  No .env.example found, please create .env.development manually');
  }
} else {
  console.log('✅ .env.development already exists');
}

// Check if node_modules exists
const nodeModulesPath = join(projectRoot, 'node_modules');
if (!existsSync(nodeModulesPath)) {
  console.log('⚠️  node_modules not found. Please run: npm install');
} else {
  console.log('✅ Dependencies are installed');
}

console.log('\n🎉 Development environment setup complete!');
console.log('\nTo start the development server:');
console.log('  npm run dev');
console.log('\nTo run tests:');
console.log('  npm test');
console.log('\nAPI Configuration:');
console.log('  Base URL: http://localhost:8000/api');
console.log('  Frontend: http://localhost:3000');