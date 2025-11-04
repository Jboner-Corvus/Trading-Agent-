#!/usr/bin/env node
/**
 * Test System - NOVAQUOTE Trading System
 * Tests basiques pour vérifier le fonctionnement du système
 */

const http = require('http');

console.log('🧪 NOVAQUOTE Trading System - Test Suite');
console.log('=' .repeat(50));

// Test 1: Vérifier que le backend répond
function testBackendHealth() {
  return new Promise((resolve) => {
    const options = {
      hostname: 'localhost',
      port: 7000,
      path: '/api/health',
      method: 'GET',
      timeout: 5000
    };

    const req = http.request(options, (res) => {
      let data = '';
      res.on('data', (chunk) => data += chunk);
      res.on('end', () => {
        try {
          const response = JSON.parse(data);
          if (response.status === 'ok') {
            console.log('✅ Backend Health Check: PASS');
            resolve(true);
          } else {
            console.log('❌ Backend Health Check: FAIL - Invalid response');
            resolve(false);
          }
        } catch (e) {
          console.log('❌ Backend Health Check: FAIL - Parse error');
          resolve(false);
        }
      });
    });

    req.on('error', () => {
      console.log('❌ Backend Health Check: FAIL - Connection refused');
      resolve(false);
    });

    req.on('timeout', () => {
      req.destroy();
      console.log('❌ Backend Health Check: FAIL - Timeout');
      resolve(false);
    });

    req.end();
  });
}

// Test 2: Vérifier que le frontend répond
function testFrontendHealth() {
  return new Promise((resolve) => {
    const options = {
      hostname: 'localhost',
      port: 9001,
      path: '/',
      method: 'GET',
      timeout: 5000
    };

    const req = http.request(options, (res) => {
      if (res.statusCode === 200) {
        console.log('✅ Frontend Health Check: PASS');
        resolve(true);
      } else {
        console.log(`❌ Frontend Health Check: FAIL - Status ${res.statusCode}`);
        resolve(false);
      }
    });

    req.on('error', () => {
      console.log('❌ Frontend Health Check: FAIL - Connection refused');
      resolve(false);
    });

    req.on('timeout', () => {
      req.destroy();
      console.log('❌ Frontend Health Check: FAIL - Timeout');
      resolve(false);
    });

    req.end();
  });
}

// Test 3: Vérifier les backtests
function testBacktests() {
  return new Promise((resolve) => {
    const options = {
      hostname: 'localhost',
      port: 7000,
      path: '/api/backtests',
      method: 'GET',
      timeout: 10000
    };

    const req = http.request(options, (res) => {
      let data = '';
      res.on('data', (chunk) => data += chunk);
      res.on('end', () => {
        try {
          const response = JSON.parse(data);
          if (response.success && response.backtests && response.backtests.length > 0) {
            console.log(`✅ Backtests API: PASS - ${response.backtests.length} stratégies chargées`);
            resolve(true);
          } else {
            console.log('❌ Backtests API: FAIL - Aucune stratégie trouvée');
            resolve(false);
          }
        } catch (e) {
          console.log('❌ Backtests API: FAIL - Parse error');
          resolve(false);
        }
      });
    });

    req.on('error', () => {
      console.log('❌ Backtests API: FAIL - Connection refused');
      resolve(false);
    });

    req.on('timeout', () => {
      req.destroy();
      console.log('❌ Backtests API: FAIL - Timeout');
      resolve(false);
    });

    req.end();
  });
}

// Fonction principale
async function runTests() {
  console.log('🔍 Running system tests...\n');

  const results = [];

  // Test du backend
  console.log('1. Testing Backend...');
  results.push(await testBackendHealth());

  // Test du frontend
  console.log('2. Testing Frontend...');
  results.push(await testFrontendHealth());

  // Test des backtests
  console.log('3. Testing Backtests API...');
  results.push(await testBacktests());

  console.log('\n' + '='.repeat(50));

  const passed = results.filter(r => r).length;
  const total = results.length;

  if (passed === total) {
    console.log(`🎉 ALL TESTS PASSED (${passed}/${total})`);
    console.log('✅ System is ready for trading!');
    process.exit(0);
  } else {
    console.log(`⚠️  SOME TESTS FAILED (${passed}/${total})`);
    console.log('❌ Please check system configuration');
    process.exit(1);
  }
}

// Vérifier si les services sont démarrés
function checkServices() {
  return new Promise((resolve) => {
    console.log('🔍 Checking if services are running...');

    // Vérifier les processus Node.js
    const { spawn } = require('child_process');
    const ps = spawn('tasklist', ['/FI', 'IMAGENAME eq node.exe', '/FO', 'CSV']);

    let output = '';
    ps.stdout.on('data', (data) => output += data.toString());

    ps.on('close', () => {
      const nodeProcesses = output.split('\n').filter(line =>
        line.includes('node.exe') && !line.includes('tasklist')
      ).length;

      if (nodeProcesses >= 2) {
        console.log(`✅ Found ${nodeProcesses} Node.js processes (expected: 2+)`);
        resolve(true);
      } else {
        console.log(`⚠️  Found ${nodeProcesses} Node.js processes (expected: 2+)`);
        console.log('💡 Make sure to run: node run.js start');
        resolve(false);
      }
    });

    ps.on('error', () => {
      console.log('⚠️  Could not check running processes');
      resolve(false);
    });
  });
}

// Lancer les tests
async function main() {
  await checkServices();
  console.log('');
  await runTests();
}

if (require.main === module) {
  main().catch(console.error);
}

module.exports = { testBackendHealth, testFrontendHealth, testBacktests };
