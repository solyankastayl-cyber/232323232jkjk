#!/usr/bin/env python3
"""
Terminal State Orchestrator Backend API Tests
Tests the unified terminal state endpoint and all its components
"""

import requests
import sys
import json
from datetime import datetime

class TerminalStateOrchestratorTester:
    def __init__(self, base_url="https://arch-study-5.preview.emergentagent.com"):
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

    def test_orchestrator_health(self):
        """Test /api/terminal/state/health - Orchestrator health check"""
        try:
            response = requests.get(f"{self.base_url}/api/terminal/state/health", timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                success = (
                    data.get("ok") == True and
                    data.get("module") == "terminal_state_orchestrator" and
                    "version" in data and
                    "usage" in data
                )
                details = f"Status: {response.status_code}, Module: {data.get('module')}"
            else:
                details = f"Status: {response.status_code}"
                
            self.log_test("Orchestrator Health Check", success, details)
            return success, response.json() if success else {}
            
        except Exception as e:
            self.log_test("Orchestrator Health Check", False, f"Error: {str(e)}")
            return False, {}

    def test_unified_terminal_state(self, symbol="BTCUSDT"):
        """Test /api/terminal/state/{symbol} - Returns unified state with all blocks"""
        try:
            response = requests.get(f"{self.base_url}/api/terminal/state/{symbol}", timeout=15)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                success = data.get("ok") == True and "data" in data
                
                if success:
                    state = data["data"]
                    
                    # Check all required blocks are present
                    required_blocks = [
                        "symbol", "timestamp", "decision", "execution", 
                        "micro", "position", "portfolio", "risk", 
                        "strategy", "system"
                    ]
                    
                    blocks_present = all(block in state for block in required_blocks)
                    
                    if blocks_present:
                        # Validate decision block
                        decision = state["decision"]
                        decision_valid = all(key in decision for key in ["action", "confidence", "direction", "mode", "reasons"])
                        
                        # Validate execution block
                        execution = state["execution"]
                        execution_valid = all(key in execution for key in ["mode", "size", "entry", "stop", "target", "rr"])
                        
                        # Validate micro block
                        micro = state["micro"]
                        micro_valid = all(key in micro for key in ["source", "imbalance", "spread", "liquidity", "state"])
                        
                        # Validate position block
                        position = state["position"]
                        position_valid = all(key in position for key in ["has_position", "symbol", "side", "size"])
                        
                        # Validate portfolio block
                        portfolio = state["portfolio"]
                        portfolio_valid = all(key in portfolio for key in ["equity", "exposure"])
                        
                        # Validate risk block
                        risk = state["risk"]
                        risk_valid = all(key in risk for key in ["heat", "drawdown", "status", "kill_switch"])
                        
                        # Validate system block
                        system = state["system"]
                        system_valid = all(key in system for key in ["mode", "adaptive_active", "scheduler"])
                        
                        success = all([
                            decision_valid, execution_valid, micro_valid, 
                            position_valid, portfolio_valid, risk_valid, system_valid
                        ])
                        
                        details = f"Symbol: {state['symbol']}, All blocks valid: {success}"
                    else:
                        missing_blocks = [block for block in required_blocks if block not in state]
                        details = f"Missing blocks: {missing_blocks}"
                        success = False
                else:
                    details = f"Missing 'data' field in response: {data}"
            else:
                details = f"Status: {response.status_code}"
                
            self.log_test(f"Unified Terminal State ({symbol})", success, details)
            return success, response.json() if success else {}
            
        except Exception as e:
            self.log_test(f"Unified Terminal State ({symbol})", False, f"Error: {str(e)}")
            return False, {}

    def test_decision_block_content(self, symbol="BTCUSDT"):
        """Test decision block shows action, direction, confidence, reasons"""
        try:
            response = requests.get(f"{self.base_url}/api/terminal/state/{symbol}", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("ok") and "data" in data:
                    decision = data["data"].get("decision", {})
                    
                    # Check decision content
                    action = decision.get("action")
                    direction = decision.get("direction")
                    confidence = decision.get("confidence")
                    reasons = decision.get("reasons", [])
                    
                    # Validate action is meaningful
                    valid_actions = ["GO_FULL", "GO_REDUCED", "WAIT", "WAIT_MICRO", "SKIP"]
                    action_valid = action in valid_actions or action == "WAIT"
                    
                    # Validate direction
                    valid_directions = ["LONG", "SHORT", "NEUTRAL"]
                    direction_valid = direction in valid_directions
                    
                    # Validate confidence range
                    confidence_valid = isinstance(confidence, (int, float)) and 0 <= confidence <= 1
                    
                    # Validate reasons exist
                    reasons_valid = isinstance(reasons, list) and len(reasons) > 0
                    
                    success = action_valid and direction_valid and confidence_valid and reasons_valid
                    details = f"Action: {action}, Direction: {direction}, Confidence: {confidence}, Reasons: {len(reasons)}"
                    
                    self.log_test(f"Decision Block Content ({symbol})", success, details)
                    return success
                    
        except Exception as e:
            self.log_test(f"Decision Block Content ({symbol})", False, f"Error: {str(e)}")
            return False

    def test_microstructure_block_content(self, symbol="BTCUSDT"):
        """Test microstructure block shows imbalance, spread, liquidity, state"""
        try:
            response = requests.get(f"{self.base_url}/api/terminal/state/{symbol}", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("ok") and "data" in data:
                    micro = data["data"].get("micro", {})
                    
                    # Check microstructure content
                    imbalance = micro.get("imbalance")
                    spread = micro.get("spread")
                    liquidity = micro.get("liquidity")
                    state = micro.get("state")
                    source = micro.get("source")
                    
                    # Validate imbalance range
                    imbalance_valid = isinstance(imbalance, (int, float)) and -1 <= imbalance <= 1
                    
                    # Validate spread (can be None for mock data)
                    spread_valid = spread is None or (isinstance(spread, (int, float)) and spread >= 0)
                    
                    # Validate liquidity state
                    valid_liquidity = ["strong_bid", "strong_ask", "balanced", "unknown"]
                    liquidity_valid = liquidity in valid_liquidity
                    
                    # Validate state
                    valid_states = ["favorable", "hostile", "caution", "neutral", "unknown"]
                    state_valid = state in valid_states
                    
                    # Validate source
                    source_valid = source in ["mock", "live", "offline"]
                    
                    success = all([imbalance_valid, spread_valid, liquidity_valid, state_valid, source_valid])
                    details = f"Imbalance: {imbalance}, Spread: {spread}, Liquidity: {liquidity}, State: {state}, Source: {source}"
                    
                    self.log_test(f"Microstructure Block Content ({symbol})", success, details)
                    return success
                    
        except Exception as e:
            self.log_test(f"Microstructure Block Content ({symbol})", False, f"Error: {str(e)}")
            return False

    def test_execution_panel_content(self, symbol="BTCUSDT"):
        """Test execution panel shows mode, size, entry/stop/target, R:R"""
        try:
            response = requests.get(f"{self.base_url}/api/terminal/state/{symbol}", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("ok") and "data" in data:
                    execution = data["data"].get("execution", {})
                    
                    # Check execution content
                    mode = execution.get("mode")
                    size = execution.get("size")
                    entry = execution.get("entry")
                    stop = execution.get("stop")
                    target = execution.get("target")
                    rr = execution.get("rr")
                    
                    # Validate mode
                    valid_modes = ["PASSIVE_LIMIT", "AGGRESSIVE_MARKET", "UNKNOWN"]
                    mode_valid = mode in valid_modes
                    
                    # Validate size (can be 0 for no position)
                    size_valid = isinstance(size, (int, float)) and size >= 0
                    
                    # Entry, stop, target can be None for no active trade
                    # R:R can be None for no active trade
                    
                    success = mode_valid and size_valid
                    details = f"Mode: {mode}, Size: {size}, Entry: {entry}, Stop: {stop}, Target: {target}, R:R: {rr}"
                    
                    self.log_test(f"Execution Panel Content ({symbol})", success, details)
                    return success
                    
        except Exception as e:
            self.log_test(f"Execution Panel Content ({symbol})", False, f"Error: {str(e)}")
            return False

    def test_position_block_content(self, symbol="BTCUSDT"):
        """Test position block shows current position or 'No open position'"""
        try:
            response = requests.get(f"{self.base_url}/api/terminal/state/{symbol}", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("ok") and "data" in data:
                    position = data["data"].get("position", {})
                    
                    # Check position content
                    has_position = position.get("has_position")
                    symbol_match = position.get("symbol") == symbol
                    side = position.get("side")
                    size = position.get("size")
                    status = position.get("status")
                    
                    # Validate position structure
                    has_position_valid = isinstance(has_position, bool)
                    symbol_valid = symbol_match
                    
                    if has_position:
                        # If has position, validate required fields
                        side_valid = side in ["LONG", "SHORT"]
                        size_valid = isinstance(size, (int, float)) and size > 0
                        status_valid = status is not None
                    else:
                        # If no position, side should be None and size should be 0
                        side_valid = side is None
                        size_valid = size == 0.0
                        status_valid = status == "FLAT"
                    
                    success = has_position_valid and symbol_valid and side_valid and size_valid and status_valid
                    details = f"Has Position: {has_position}, Side: {side}, Size: {size}, Status: {status}"
                    
                    self.log_test(f"Position Block Content ({symbol})", success, details)
                    return success
                    
        except Exception as e:
            self.log_test(f"Position Block Content ({symbol})", False, f"Error: {str(e)}")
            return False

    def test_portfolio_block_content(self, symbol="BTCUSDT"):
        """Test portfolio block shows equity, exposure"""
        try:
            response = requests.get(f"{self.base_url}/api/terminal/state/{symbol}", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("ok") and "data" in data:
                    portfolio = data["data"].get("portfolio", {})
                    
                    # Check portfolio content
                    equity = portfolio.get("equity")
                    exposure = portfolio.get("exposure")
                    free_capital = portfolio.get("free_capital")
                    risk_used = portfolio.get("risk_used")
                    
                    # Validate portfolio fields (can be None for mock data)
                    equity_valid = equity is None or isinstance(equity, (int, float))
                    exposure_valid = exposure is None or isinstance(exposure, (int, float))
                    free_capital_valid = free_capital is None or isinstance(free_capital, (int, float))
                    risk_used_valid = risk_used is None or isinstance(risk_used, (int, float))
                    
                    success = equity_valid and exposure_valid and free_capital_valid and risk_used_valid
                    details = f"Equity: {equity}, Exposure: {exposure}, Free: {free_capital}, Risk Used: {risk_used}"
                    
                    self.log_test(f"Portfolio Block Content ({symbol})", success, details)
                    return success
                    
        except Exception as e:
            self.log_test(f"Portfolio Block Content ({symbol})", False, f"Error: {str(e)}")
            return False

    def test_risk_metrics_content(self, symbol="BTCUSDT"):
        """Test risk metrics shows heat, drawdown, kill switch"""
        try:
            response = requests.get(f"{self.base_url}/api/terminal/state/{symbol}", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("ok") and "data" in data:
                    risk = data["data"].get("risk", {})
                    
                    # Check risk content
                    heat = risk.get("heat")
                    drawdown = risk.get("drawdown")
                    status = risk.get("status")
                    kill_switch = risk.get("kill_switch")
                    
                    # Validate risk fields
                    heat_valid = heat is None or (isinstance(heat, (int, float)) and 0 <= heat <= 1)
                    drawdown_valid = drawdown is None or (isinstance(drawdown, (int, float)) and drawdown >= 0)
                    status_valid = status in ["normal", "elevated", "critical", "unknown"]
                    kill_switch_valid = isinstance(kill_switch, bool)
                    
                    success = heat_valid and drawdown_valid and status_valid and kill_switch_valid
                    details = f"Heat: {heat}, Drawdown: {drawdown}, Status: {status}, Kill Switch: {kill_switch}"
                    
                    self.log_test(f"Risk Metrics Content ({symbol})", success, details)
                    return success
                    
        except Exception as e:
            self.log_test(f"Risk Metrics Content ({symbol})", False, f"Error: {str(e)}")
            return False

    def test_system_state_content(self, symbol="BTCUSDT"):
        """Test system state shows adaptive, scheduler, profile, risk status"""
        try:
            response = requests.get(f"{self.base_url}/api/terminal/state/{symbol}", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("ok") and "data" in data:
                    system = data["data"].get("system", {})
                    strategy = data["data"].get("strategy", {})
                    
                    # Check system content
                    mode = system.get("mode")
                    adaptive_active = system.get("adaptive_active")
                    scheduler = system.get("scheduler")
                    data_source = system.get("data_source")
                    
                    # Check strategy content
                    profile = strategy.get("profile")
                    paused = strategy.get("paused")
                    
                    # Validate system fields
                    mode_valid = mode in ["LIVE", "SIMULATION"]
                    adaptive_valid = isinstance(adaptive_active, bool)
                    scheduler_valid = scheduler in ["running", "stopped", "unknown"]
                    source_valid = data_source in ["live", "mock", "offline"]
                    
                    # Validate strategy fields
                    profile_valid = profile in ["BALANCED", "AGGRESSIVE", "CONSERVATIVE", "UNKNOWN"]
                    paused_valid = isinstance(paused, bool)
                    
                    success = all([mode_valid, adaptive_valid, scheduler_valid, source_valid, profile_valid, paused_valid])
                    details = f"Mode: {mode}, Adaptive: {adaptive_active}, Scheduler: {scheduler}, Profile: {profile}"
                    
                    self.log_test(f"System State Content ({symbol})", success, details)
                    return success
                    
        except Exception as e:
            self.log_test(f"System State Content ({symbol})", False, f"Error: {str(e)}")
            return False

    def test_symbol_input_functionality(self):
        """Test symbol input allows changing symbol"""
        symbols_to_test = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
        
        for symbol in symbols_to_test:
            try:
                response = requests.get(f"{self.base_url}/api/terminal/state/{symbol}", timeout=10)
                success = response.status_code == 200
                
                if success:
                    data = response.json()
                    if data.get("ok") and "data" in data:
                        returned_symbol = data["data"].get("symbol")
                        success = returned_symbol == symbol
                        details = f"Requested: {symbol}, Returned: {returned_symbol}"
                    else:
                        success = False
                        details = "Invalid response structure"
                else:
                    details = f"Status: {response.status_code}"
                    
                self.log_test(f"Symbol Input Functionality ({symbol})", success, details)
                
            except Exception as e:
                self.log_test(f"Symbol Input Functionality ({symbol})", False, f"Error: {str(e)}")

    def run_all_tests(self):
        """Run all terminal state orchestrator tests"""
        print("🚀 Starting Terminal State Orchestrator Tests")
        print(f"Testing against: {self.base_url}")
        print("=" * 70)
        
        # Test orchestrator health
        self.test_orchestrator_health()
        
        # Test unified terminal state for BTCUSDT
        self.test_unified_terminal_state("BTCUSDT")
        
        # Test all block contents
        self.test_decision_block_content("BTCUSDT")
        self.test_microstructure_block_content("BTCUSDT")
        self.test_execution_panel_content("BTCUSDT")
        self.test_position_block_content("BTCUSDT")
        self.test_portfolio_block_content("BTCUSDT")
        self.test_risk_metrics_content("BTCUSDT")
        self.test_system_state_content("BTCUSDT")
        
        # Test symbol input functionality
        self.test_symbol_input_functionality()
        
        # Test with ETHUSDT as well
        self.test_unified_terminal_state("ETHUSDT")
        
        # Print summary
        print("=" * 70)
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
    tester = TerminalStateOrchestratorTester()
    success = tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())