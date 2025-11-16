#!/usr/bin/env node

/**
 * Zero-Simulation AST Checker
 * 
 * This script performs structural analysis of code files to detect and ban
 * non-deterministic constructs that violate the Zero-Simulation mandate.
 * 
 * It uses AST (Abstract Syntax Tree) parsing to structurally identify:
 * - Math.random, Date.now, and other non-deterministic functions
 * - Floating-point literals and operations
 * - setTimeout, setInterval, and other time-based functions
 * - Native crypto functions
 * 
 * Usage: node zero-sim-ast.js --file <filepath>
 */

const fs = require('fs');
const path = require('path');
const acorn = require('acorn');
const walk = require('acorn-walk');

// List of forbidden constructs
const FORBIDDEN_NODES = {
  // Non-deterministic functions
  'Math.random': 'Use of Math.random is forbidden - violates Zero-Simulation mandate',
  'Date.now': 'Use of Date.now is forbidden - use DRV_ClockService instead',
  'new Date()': 'Use of new Date() is forbidden - use DRV_ClockService instead',
  'process.hrtime': 'Use of process.hrtime is forbidden - use DRV_ClockService instead',
  'crypto.random': 'Use of crypto.random is forbidden - violates Zero-Simulation mandate',
  
  // Time-based functions
  'setTimeout': 'Use of setTimeout is forbidden - violates Zero-Simulation mandate',
  'setInterval': 'Use of setInterval is forbidden - violates Zero-Simulation mandate',
  'setImmediate': 'Use of setImmediate is forbidden - violates Zero-Simulation mandate',
  
  // Native crypto functions
  'crypto.getRandomValues': 'Use of crypto.getRandomValues is forbidden - violates Zero-Simulation mandate',
  'crypto.createHash': 'Use of crypto.createHash is forbidden - use PQC_Verifier instead',
  'crypto.createSign': 'Use of crypto.createSign is forbidden - use PQC_Verifier instead',
  'crypto.createVerify': 'Use of crypto.createVerify is forbidden - use PQC_Verifier instead',
};

// Floating-point detection
const FLOAT_REGEX = /\d+\.\d+/;

class ZeroSimChecker {
  constructor() {
    this.violations = [];
    this.file = '';
  }

  /**
   * Check a file for Zero-Simulation violations
   * @param {string} filepath - Path to the file to check
   * @returns {Array} List of violations found
   */
  checkFile(filepath) {
    this.file = filepath;
    this.violations = [];
    
    try {
      const code = fs.readFileSync(filepath, 'utf8');
      const ast = acorn.parse(code, { 
        ecmaVersion: 2020, 
        sourceType: 'module',
        allowReturnOutsideFunction: true,
        allowImportExportEverywhere: true
      });
      
      // Walk the AST and check for violations
      walk.simple(ast, {
        CallExpression: (node) => this.checkCallExpression(node),
        Literal: (node) => this.checkLiteral(node),
        Identifier: (node) => this.checkIdentifier(node),
      });
      
      return this.violations;
    } catch (error) {
      this.violations.push({
        type: 'PARSE_ERROR',
        message: `Failed to parse file: ${error.message}`,
        line: 0,
        column: 0
      });
      return this.violations;
    }
  }

  /**
   * Check CallExpression nodes for forbidden function calls
   * @param {Object} node - AST node
   */
  checkCallExpression(node) {
    if (node.callee) {
      let functionName = '';
      
      // Handle MemberExpression (e.g., Math.random)
      if (node.callee.type === 'MemberExpression') {
        const objectName = node.callee.object.name || '';
        const propertyName = node.callee.property.name || '';
        functionName = `${objectName}.${propertyName}`;
      }
      // Handle Identifier (e.g., setTimeout)
      else if (node.callee.type === 'Identifier') {
        functionName = node.callee.name;
      }
      
      // Check if function is forbidden
      if (FORBIDDEN_NODES[functionName]) {
        this.violations.push({
          type: 'FORBIDDEN_FUNCTION',
          message: FORBIDDEN_NODES[functionName],
          line: node.loc ? node.loc.start.line : 0,
          column: node.loc ? node.loc.start.column : 0,
          function: functionName
        });
      }
    }
  }

  /**
   * Check Literal nodes for floating-point numbers
   * @param {Object} node - AST node
   */
  checkLiteral(node) {
    // Check for floating-point literals
    if (typeof node.value === 'number' && !Number.isInteger(node.value)) {
      this.violations.push({
        type: 'FLOATING_POINT',
        message: 'Use of floating-point literals is forbidden - use CertifiedMath fixed-point instead',
        line: node.loc ? node.loc.start.line : 0,
        column: node.loc ? node.loc.start.column : 0,
        value: node.value
      });
    }
  }

  /**
   * Check Identifier nodes for forbidden identifiers
   * @param {Object} node - AST node
   */
  checkIdentifier(node) {
    // Check for forbidden identifiers
    if (FORBIDDEN_NODES[node.name]) {
      this.violations.push({
        type: 'FORBIDDEN_IDENTIFIER',
        message: FORBIDDEN_NODES[node.name],
        line: node.loc ? node.loc.start.line : 0,
        column: node.loc ? node.loc.start.column : 0,
        identifier: node.name
      });
    }
  }

  /**
   * Print violations in a structured format
   * @param {Array} violations - List of violations
   */
  printViolations(violations) {
    if (violations.length === 0) {
      console.log(`✅ No Zero-Simulation violations found in ${this.file}`);
      return;
    }

    console.log(`❌ ${violations.length} Zero-Simulation violations found in ${this.file}:`);
    violations.forEach((violation, index) => {
      console.log(`  ${index + 1}. ${violation.type}: ${violation.message}`);
      if (violation.line > 0) {
        console.log(`     Location: Line ${violation.line}, Column ${violation.column}`);
      }
      if (violation.function) {
        console.log(`     Function: ${violation.function}`);
      }
      if (violation.identifier) {
        console.log(`     Identifier: ${violation.identifier}`);
      }
      if (violation.value !== undefined) {
        console.log(`     Value: ${violation.value}`);
      }
      console.log();
    });
  }

  /**
   * Generate machine-readable report
   * @param {Array} violations - List of violations
   * @returns {Object} Report object
   */
  generateReport(violations) {
    return {
      timestamp: new Date().toISOString(),
      file: this.file,
      violations: violations,
      passed: violations.length === 0
    };
  }
}

// Main execution
function main() {
  const args = process.argv.slice(2);
  let filepath = '';

  // Parse command line arguments
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--file' && i + 1 < args.length) {
      filepath = args[i + 1];
      break;
    }
  }

  if (!filepath) {
    console.error('Usage: node zero-sim-ast.js --file <filepath>');
    process.exit(1);
  }

  // Check if file exists
  if (!fs.existsSync(filepath)) {
    console.error(`Error: File ${filepath} does not exist`);
    process.exit(1);
  }

  // Run the checker
  const checker = new ZeroSimChecker();
  const violations = checker.checkFile(filepath);
  
  // Print results
  checker.printViolations(violations);
  
  // Generate report
  const report = checker.generateReport(violations);
  
  // Write report to file
  const reportFile = filepath.replace(/\.[^/.]+$/, '') + '_zero_sim_report.json';
  fs.writeFileSync(reportFile, JSON.stringify(report, null, 2));
  console.log(`Report saved to: ${reportFile}`);
  
  // Exit with appropriate code
  process.exit(violations.length > 0 ? 1 : 0);
}

// Run main if script is executed directly
if (require.main === module) {
  main();
}

module.exports = ZeroSimChecker;