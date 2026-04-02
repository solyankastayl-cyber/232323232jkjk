#!/usr/bin/env python3
"""
Trading Terminal Backend API Tests
Tests all trading terminal endpoints for functionality and data integrity
"""

import requests
import sys
import json
from datetime import datetime

class TradingTerminalTester:
    def __init__(self, base_url="https://repo-study-4.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.errors = []

    def log_test(self, name, success, details=""):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name}")
        else:
            print(f"❌ {name} - {details}")
            self.errors.append(f"{name}: {details}")

    def test_terminal_health(self):
        """Test terminal health endpoint"""
        try:
            response = requests.get(f"{self.base_url}/api/terminal/health", timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                success = data.get("ok") == True and "module" in data
                details = f"Status: {response.status_code}, Data: {data}"
            else:
                details = f"Status: {response.status_code}"
                
            self.log_test("Terminal Health Check", success, details)
            return success, response.json() if success else {}
            
        except Exception as e:
            self.log_test("Terminal Health Check", False, f"Error: {str(e)}")
            return False, {}

    def test_terminal_auth(self):
        """Test terminal authentication"""
        try:
            # Test valid password (dev mode - any 4+ chars)
            response = requests.post(
                f"{self.base_url}/api/terminal/auth",
                json={"password": "test123"},
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            success = response.status_code == 200
            if success:
                data = response.json()
                success = data.get("ok") == True and data.get("authenticated") == True
                details = f"Auth response: {data}"
            else:
                details = f"Status: {response.status_code}"
                
            self.log_test("Terminal Auth (Valid Password)", success, details)
            
            # Test invalid password (too short)
            response = requests.post(
                f"{self.base_url}/api/terminal/auth",
                json={"password": "123"},
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            success = response.status_code == 200
            if success:
                data = response.json()
                success = data.get("ok") == False and data.get("authenticated") == False
                details = f"Invalid auth response: {data}"
            else:
                details = f"Status: {response.status_code}"
                
            self.log_test("Terminal Auth (Invalid Password)", success, details)
            return True
            
        except Exception as e:
            self.log_test("Terminal Auth", False, f"Error: {str(e)}")
            return False

    def test_decision_endpoint(self, symbol="BTCUSDT"):
        """Test decision endpoint for a symbol"""
        try:
            response = requests.get(f"{self.base_url}/api/terminal/decision/{symbol}", timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                success = (
                    data.get("ok") == True and
                    "data" in data and
                    "decision" in data["data"] and
                    "action" in data["data"]["decision"] and
                    "confidence" in data["data"]["decision"] and
                    "why" in data["data"] and
                    "execution" in data["data"] and
                    "micro" in data["data"]
                )
                
                if success:
                    decision_data = data["data"]
                    action = decision_data["decision"]["action"]
                    confidence = decision_data["decision"]["confidence"]
                    
                    # Validate action is one of expected values
                    valid_actions = ["GO_FULL", "GO_REDUCED", "WAIT", "WAIT_MICRO", "SKIP"]
                    action_valid = action in valid_actions
                    
                    # Validate confidence is between 0 and 1
                    confidence_valid = 0 <= confidence <= 1
                    
                    # Validate execution data
                    execution = decision_data["execution"]
                    execution_valid = all(key in execution for key in ["mode", "size_multiplier", "entry", "stop_loss", "take_profit", "risk_reward"])
                    
                    # Validate micro data
                    micro = decision_data["micro"]
                    micro_valid = all(key in micro for key in ["imbalance", "spread_bps", "liquidity_state", "state"])
                    
                    success = action_valid and confidence_valid and execution_valid and micro_valid
                    details = f"Action: {action}, Confidence: {confidence}, Valid: {success}"
                else:
                    details = f"Missing required fields in response: {data}"
            else:
                details = f"Status: {response.status_code}"
                
            self.log_test(f"Decision Endpoint ({symbol})", success, details)
            return success, response.json() if success else {}
            
        except Exception as e:
            self.log_test(f"Decision Endpoint ({symbol})", False, f"Error: {str(e)}")
            return False, {}

    def test_positions_endpoint(self):
        """Test positions endpoint"""
        try:
            response = requests.get(f"{self.base_url}/api/terminal/positions", timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                success = (
                    data.get("ok") == True and
                    "data" in data and
                    "positions" in data["data"] and
                    "summary" in data["data"]
                )
                
                if success:
                    positions = data["data"]["positions"]
                    summary = data["data"]["summary"]
                    
                    # Validate positions structure
                    positions_valid = True
                    if positions:  # If there are positions, validate structure
                        for pos in positions:
                            required_fields = ["id", "symbol", "side", "size", "entry_price", "current_price", "pnl_usd", "pnl_percent", "status"]
                            if not all(field in pos for field in required_fields):
                                positions_valid = False
                                break
                    
                    # Validate summary structure
                    summary_valid = all(key in summary for key in ["total_positions", "total_pnl_usd"])
                    
                    success = positions_valid and summary_valid
                    details = f"Positions count: {len(positions)}, Summary valid: {summary_valid}"
                else:
                    details = f"Missing required fields in response: {data}"
            else:
                details = f"Status: {response.status_code}"
                
            self.log_test("Positions Endpoint", success, details)
            return success, response.json() if success else {}
            
        except Exception as e:
            self.log_test("Positions Endpoint", False, f"Error: {str(e)}")
            return False, {}

    def test_micro_live_endpoint(self, symbol="BTCUSDT"):
        """Test microstructure live endpoint"""
        try:
            response = requests.get(f"{self.base_url}/api/terminal/micro/live/{symbol}", timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                success = (
                    data.get("ok") == True and
                    "data" in data
                )
                
                if success:
                    micro_data = data["data"]
                    required_fields = ["symbol", "imbalance", "spread_bps", "liquidity_state", "state", "confidence"]
                    success = all(field in micro_data for field in required_fields)
                    
                    if success:
                        # Validate data ranges
                        imbalance = micro_data["imbalance"]
                        confidence = micro_data["confidence"]
                        spread_bps = micro_data["spread_bps"]
                        
                        ranges_valid = (
                            -1 <= imbalance <= 1 and
                            0 <= confidence <= 1 and
                            spread_bps >= 0
                        )
                        success = ranges_valid
                        details = f"Imbalance: {imbalance}, Confidence: {confidence}, Spread: {spread_bps}bps"
                    else:
                        details = f"Missing required fields: {micro_data}"
                else:
                    details = f"Missing data field in response: {data}"
            else:
                details = f"Status: {response.status_code}"
                
            self.log_test(f"Micro Live Endpoint ({symbol})", success, details)
            return success, response.json() if success else {}
            
        except Exception as e:
            self.log_test(f"Micro Live Endpoint ({symbol})", False, f"Error: {str(e)}")
            return False, {}

    def test_terminal_state_endpoint(self, symbol="BTCUSDT", timeframe="4H"):
        """Test the main terminal state endpoint with validation layer"""
        try:
            response = requests.get(f"{self.base_url}/api/terminal/state/{symbol}?timeframe={timeframe}", timeout=15)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                success = (
                    data.get("ok") == True and
                    "data" in data
                )
                
                if success:
                    state_data = data["data"]
                    
                    # Check main sections exist
                    required_sections = ["symbol", "timestamp", "decision", "execution", "micro", "position", "portfolio", "risk", "strategy", "system", "validation"]
                    sections_valid = all(section in state_data for section in required_sections)
                    
                    if sections_valid:
                        # Check timeframe consistency - CRITICAL for this test
                        system_timeframe = state_data.get("timeframe")
                        execution_timeframe = state_data.get("execution", {}).get("timeframe")
                        decision_timeframe = state_data.get("decision", {}).get("timeframe")
                        
                        timeframe_consistent = (
                            system_timeframe == timeframe and
                            (execution_timeframe is None or execution_timeframe == timeframe) and
                            (decision_timeframe is None or decision_timeframe == timeframe)
                        )
                        
                        # Check validation section specifically
                        validation = state_data["validation"]
                        validation_valid = all(key in validation for key in ["is_valid", "critical_count", "warning_count", "info_count", "issues"])
                        
                        # Check decision section
                        decision = state_data["decision"]
                        decision_valid = all(key in decision for key in ["action", "confidence", "direction", "mode", "reasons"])
                        
                        # Check execution section
                        execution = state_data["execution"]
                        execution_valid = all(key in execution for key in ["mode", "size", "entry", "stop", "target", "rr"])
                        
                        # Check micro section
                        micro = state_data["micro"]
                        micro_valid = all(key in micro for key in ["source", "imbalance", "spread", "liquidity", "state", "decision", "reasons"])
                        
                        success = validation_valid and decision_valid and execution_valid and micro_valid and timeframe_consistent
                        
                        # Additional validation checks
                        if success:
                            # Check if validation shows warnings for mock data
                            has_mock_warning = any(
                                issue.get("type") == "SIMULATION_MODE" or "mock" in issue.get("message", "").lower()
                                for issue in validation.get("issues", [])
                            )
                            
                            # Check if entry price validation exists when execution has entry
                            has_entry_validation = True
                            if execution.get("entry"):
                                has_entry_validation = any(
                                    "entry" in issue.get("message", "").lower() or issue.get("type") == "ENTRY_PRICE_MISMATCH"
                                    for issue in validation.get("issues", [])
                                ) or validation.get("is_valid", True)  # Valid if no issues
                            
                            details = f"TF: {system_timeframe}, Consistent: {timeframe_consistent}, Validation: ✓, Mock warning: {has_mock_warning}"
                        else:
                            details = f"TF inconsistent: sys={system_timeframe}, exec={execution_timeframe}, dec={decision_timeframe} | Validation: {validation_valid}, Decision: {decision_valid}, Execution: {execution_valid}, Micro: {micro_valid}"
                    else:
                        missing_sections = [s for s in required_sections if s not in state_data]
                        details = f"Missing sections: {missing_sections}"
                        success = False
                else:
                    details = f"Missing data field in response: {data}"
            else:
                details = f"Status: {response.status_code}"
                
            self.log_test(f"Terminal State Endpoint ({symbol} @ {timeframe})", success, details)
            return success, response.json() if success else {}
            
        except Exception as e:
            self.log_test(f"Terminal State Endpoint ({symbol} @ {timeframe})", False, f"Error: {str(e)}")
            return False, {}

    def test_timeframe_consistency_validation(self, symbol="BTCUSDT"):
        """Test timeframe consistency validation across all timeframes"""
        timeframes = ["1H", "4H", "1D"]
        all_passed = True
        
        for tf in timeframes:
            try:
                response = requests.get(f"{self.base_url}/api/terminal/state/{symbol}?timeframe={tf}", timeout=15)
                success = response.status_code == 200
                
                if success:
                    data = response.json()
                    if data.get("ok") and "data" in data:
                        state_data = data["data"]
                        validation = state_data.get("validation", {})
                        
                        # Check for timeframe consistency issues
                        timeframe_issues = [
                            issue for issue in validation.get("issues", [])
                            if issue.get("type") == "TIMEFRAME_MISMATCH"
                        ]
                        
                        # Should have no timeframe mismatch issues
                        tf_consistent = len(timeframe_issues) == 0
                        system_tf = state_data.get("timeframe")
                        
                        if tf_consistent and system_tf == tf:
                            self.log_test(f"Timeframe Consistency ({tf})", True, f"System TF: {system_tf}")
                        else:
                            self.log_test(f"Timeframe Consistency ({tf})", False, f"System TF: {system_tf}, Issues: {timeframe_issues}")
                            all_passed = False
                    else:
                        self.log_test(f"Timeframe Consistency ({tf})", False, "Invalid response structure")
                        all_passed = False
                else:
                    self.log_test(f"Timeframe Consistency ({tf})", False, f"Status: {response.status_code}")
                    all_passed = False
                    
            except Exception as e:
                self.log_test(f"Timeframe Consistency ({tf})", False, f"Error: {str(e)}")
                all_passed = False
        
        return all_passed

    def test_coinbase_chart_data(self, symbol="BTCUSDT"):
        """Test that chart loads real Coinbase data for all timeframes"""
        timeframes = ["1H", "4H", "1D"]
        tf_mapping = {"1H": "1h", "4H": "6h", "1D": "1d"}
        all_passed = True
        
        asset = symbol.replace("USDT", "").replace("USD", "")
        
        for tf in timeframes:
            try:
                coinbase_tf = tf_mapping[tf]
                response = requests.get(f"{self.base_url}/api/provider/coinbase/candles/{asset}?timeframe={coinbase_tf}&limit=50", timeout=15)
                success = response.status_code == 200
                
                if success:
                    data = response.json()
                    if data.get("ok") and data.get("candles") and len(data["candles"]) > 0:
                        candles = data["candles"]
                        # Validate candle structure
                        first_candle = candles[0]
                        required_fields = ["timestamp", "open", "high", "low", "close", "volume"]
                        candle_valid = all(field in first_candle for field in required_fields)
                        
                        if candle_valid:
                            self.log_test(f"Coinbase Chart Data ({tf})", True, f"Got {len(candles)} candles")
                        else:
                            self.log_test(f"Coinbase Chart Data ({tf})", False, f"Invalid candle structure: {first_candle}")
                            all_passed = False
                    else:
                        self.log_test(f"Coinbase Chart Data ({tf})", False, f"No candles data: {data}")
                        all_passed = False
                else:
                    self.log_test(f"Coinbase Chart Data ({tf})", False, f"Status: {response.status_code}")
                    all_passed = False
                    
            except Exception as e:
                self.log_test(f"Coinbase Chart Data ({tf})", False, f"Error: {str(e)}")
                all_passed = False
        
        return all_passed

    def run_all_tests(self):
        """Run all trading terminal tests"""
        print("🚀 Starting Trading Terminal Backend Tests")
        print(f"Testing against: {self.base_url}")
        print("=" * 60)
        
        # Test health endpoint
        self.test_terminal_health()
        
        # Test authentication
        self.test_terminal_auth()
        
        # Test timeframe functionality - MAIN FOCUS
        print("\n🎯 TIMEFRAME FUNCTIONALITY TESTS")
        print("-" * 40)
        
        # Test timeframe consistency validation
        self.test_timeframe_consistency_validation()
        
        # Test Coinbase chart data for all timeframes
        self.test_coinbase_chart_data()
        
        # Test the main terminal state endpoint with all timeframes
        symbols = ["BTCUSDT", "ETHUSDT"]
        timeframes = ["1H", "4H", "1D"]
        
        for symbol in symbols:
            for tf in timeframes:
                self.test_terminal_state_endpoint(symbol, tf)
        
        print("\n📊 OTHER ENDPOINT TESTS")
        print("-" * 40)
        
        # Test individual endpoints
        for symbol in symbols:
            self.test_decision_endpoint(symbol)
            self.test_micro_live_endpoint(symbol)
        
        # Test positions
        self.test_positions_endpoint()
        
        # Print summary
        print("=" * 60)
        print(f"📊 Test Results: {self.tests_passed}/{self.tests_run} passed")
        
        if self.errors:
            print("\n❌ Failed Tests:")
            for error in self.errors:
                print(f"  - {error}")
        
        success_rate = (self.tests_passed / self.tests_run) * 100 if self.tests_run > 0 else 0
        print(f"Success Rate: {success_rate:.1f}%")
        
        return self.tests_passed == self.tests_run

def main():
    """Main test runner"""
    tester = TradingTerminalTester()
    success = tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())