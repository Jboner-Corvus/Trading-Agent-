/**
 * 🔒 ROBUST BACKTEST VALIDATION SYSTEM
 * Validates integrity and consistency of production backtests
 */

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

class BacktestValidator {
  constructor() {
    this.productionPath = path.join(__dirname, '../src/data/production_backtests');
    this.requiredStrategies = 7;
    this.validationLog = [];
  }

  /**
   * Calculate SHA256 hash of data
   */
  calculateHash(data) {
    const dataString = JSON.stringify(data, Object.keys(data).sort(), (key, value) => {
      if (key === 'data_hash') return undefined; // Exclude hash from hash calculation
      if (typeof value === 'object' && value !== null) {
        return JSON.stringify(value, Object.keys(value).sort());
      }
      return value;
    });
    return crypto.createHash('sha256').update(dataString).digest('hex');
  }

  /**
   * Validate single backtest file integrity
   */
  validateBacktestFile(filepath) {
    try {
      const content = fs.readFileSync(filepath, 'utf8');
      const data = JSON.parse(content);

      // Validate required fields
      const requiredFields = ['strategy_id', 'strategy_name', 'metrics', 'metadata', 'data_hash'];
      for (const field of requiredFields) {
        if (!data[field]) {
          throw new Error(`Missing required field: ${field}`);
        }
      }

      // Validate metrics
      const requiredMetrics = ['total_return', 'sharpe_ratio', 'win_rate', 'total_trades'];
      for (const metric of requiredMetrics) {
        if (data.metrics[metric] === undefined || data.metrics[metric] === null) {
          throw new Error(`Missing required metric: ${metric}`);
        }
      }

      // Validate value ranges
      if (data.metrics.total_return < -1 || data.metrics.total_return > 10) {
        throw new Error(`Invalid total_return: ${data.metrics.total_return} (should be between -100% and 1000%)`);
      }

      if (data.metrics.win_rate < 0 || data.metrics.win_rate > 1) {
        throw new Error(`Invalid win_rate: ${data.metrics.win_rate} (should be between 0 and 1)`);
      }

      if (data.metrics.sharpe_ratio < -5 || data.metrics.sharpe_ratio > 10) {
        throw new Error(`Invalid sharpe_ratio: ${data.metrics.sharpe_ratio} (should be reasonable)`);
      }

      // Validate hash integrity
      const dataForHash = { ...data };
      delete dataForHash.data_hash;
      const calculatedHash = this.calculateHash(dataForHash);

      if (calculatedHash !== data.data_hash) {
        throw new Error(`Hash mismatch: calculated ${calculatedHash.slice(0, 16)}..., stored ${data.data_hash.slice(0, 16)}...`);
      }

      return {
        valid: true,
        strategy: data.strategy_id,
        name: data.strategy_name,
        return: data.metrics.total_return,
        sharpe: data.metrics.sharpe_ratio,
        validated_at: data.validated_at
      };

    } catch (error) {
      return {
        valid: false,
        file: path.basename(filepath),
        error: error.message
      };
    }
  }

  /**
   * Validate entire backtest system
   */
  validateSystem() {
    const results = {
      total_files: 0,
      valid_files: 0,
      invalid_files: 0,
      validation_errors: [],
      strategies: [],
      system_integrity: false,
      validated_at: new Date().toISOString()
    };

    try {
      // Check if production directory exists
      if (!fs.existsSync(this.productionPath)) {
        throw new Error(`Production directory not found: ${this.productionPath}`);
      }

      // Get all JSON files except system metadata
      const files = fs.readdirSync(this.productionPath)
        .filter(file => file.endsWith('.json') && file !== 'system_metadata.json');

      results.total_files = files.length;

      // Validate each file
      for (const file of files) {
        const filepath = path.join(this.productionPath, file);
        const validation = this.validateBacktestFile(filepath);

        if (validation.valid) {
          results.valid_files++;
          results.strategies.push(validation);
          this.validationLog.push(`✅ ${validation.name} - Valid (${(validation.return * 100).toFixed(2)}% return)`);
        } else {
          results.invalid_files++;
          results.validation_errors.push(validation);
          this.validationLog.push(`❌ ${validation.file} - Invalid: ${validation.error}`);
        }
      }

      // System integrity check
      results.system_integrity = (
        results.total_files === this.requiredStrategies &&
        results.invalid_files === 0 &&
        results.valid_files === this.requiredStrategies
      );

      // Validate system metadata if it exists
      const metadataPath = path.join(this.productionPath, 'system_metadata.json');
      if (fs.existsSync(metadataPath)) {
        try {
          const metadata = JSON.parse(fs.readFileSync(metadataPath, 'utf8'));
          if (metadata.total_strategies !== this.requiredStrategies) {
            results.validation_errors.push({
              type: 'system_metadata',
              error: `Metadata claims ${metadata.total_strategies} strategies, found ${results.total_files}`
            });
          }
        } catch (error) {
          results.validation_errors.push({
            type: 'system_metadata',
            error: `Failed to read system metadata: ${error.message}`
          });
        }
      }

    } catch (error) {
      results.validation_errors.push({
        type: 'system',
        error: error.message
      });
      this.validationLog.push(`🚨 System validation error: ${error.message}`);
    }

    return results;
  }

  /**
   * Get validation report
   */
  getValidationReport() {
    const results = this.validateSystem();

    const report = {
      summary: {
        status: results.system_integrity ? 'VALID' : 'INVALID',
        total_strategies: results.total_files,
        valid_strategies: results.valid_files,
        invalid_strategies: results.invalid_files,
        validation_rate: results.total_files > 0 ? (results.valid_files / results.total_files * 100).toFixed(1) : 0,
        validated_at: results.validated_at
      },
      strategies: results.strategies,
      errors: results.validation_errors,
      logs: this.validationLog
    };

    return report;
  }

  /**
   * Express middleware for validation
   */
  getValidationMiddleware() {
    return (req, res, next) => {
      const validation = this.validateSystem();

      if (!validation.system_integrity) {
        console.error('🚨 BACKTEST SYSTEM VALIDATION FAILED');
        console.error('Errors:', validation.validation_errors);

        return res.status(500).json({
          success: false,
          error: 'Backtest system validation failed',
          details: validation.validation_errors,
          validation_report: validation
        });
      }

      console.log('✅ Backtest system validation passed');
      req.backtest_validation = validation;
      next();
    };
  }
}

module.exports = BacktestValidator;