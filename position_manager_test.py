#!/usr/bin/env python3
"""
Position Manager Backend API Tests
Tests the specific Position Manager functionality for Phase TT2
"""

import requests
import sys
import json
from datetime import datetime

class PositionManagerTester:
    def __init__(self, base_url="https://repo-study-4.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.errors = []
        self.test_position_id = None

    def log_test(self, name, success, details=""):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name}")
            if details:
                print(f"   {details}")
        else:
            print(f"❌ {name} - {details}")
            self.errors.append(f"{name}: {details}")

    def test_positions_health(self):
        """Test positions module health endpoint"""
        try:
            response = requests.get(f"{self.base_url}/api/terminal/positions/health", timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                success = data.get("ok") == True and data.get("module") == "position_manager"
                details = f"Module: {data.get('module')}, Version: {data.get('version')}"
            else:
                details = f"Status: {response.status_code}"
                
            self.log_test("Positions Health Check", success, details)
            return success
            
        except Exception as e:
            self.log_test("Positions Health Check", False, f"Error: {str(e)}")
            return False

    def test_get_positions_list(self):
        """Test GET /api/terminal/positions - returns positions list"""
        try:
            response = requests.get(f"{self.base_url}/api/terminal/positions", timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                success = (
                    data.get("ok") == True and
                    "data" in data and
                    "positions" in data["data"] and
                    isinstance(data["data"]["positions"], list)
                )
                positions = data.get("data", {}).get("positions", [])
                summary = data.get("data", {}).get("summary", {})
                details = f"Positions: {len(positions)}, Total PnL: {summary.get('total_pnl_usd', 0)}"
            else:
                details = f"Status: {response.status_code}"
                
            self.log_test("GET Positions List", success, details)
            return success, response.json() if success else {}
            
        except Exception as e:
            self.log_test("GET Positions List", False, f"Error: {str(e)}")
            return False, {}

    def test_get_open_positions(self):
        """Test GET /api/terminal/positions/open - returns only open positions"""
        try:
            response = requests.get(f"{self.base_url}/api/terminal/positions/open", timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                success = (
                    data.get("ok") == True and
                    "count" in data and
                    "positions" in data and
                    isinstance(data["positions"], list)
                )
                
                # Validate that all returned positions are open
                if success and data["positions"]:
                    for pos in data["positions"]:
                        if pos.get("status") not in ["OPEN", "OPENING", "SCALING", "REDUCING", "ACTIVE"]:
                            success = False
                            break
                
                details = f"Open positions: {data.get('count')}"
            else:
                details = f"Status: {response.status_code}"
                
            self.log_test("GET Open Positions", success, details)
            return success, response.json() if success else {}
            
        except Exception as e:
            self.log_test("GET Open Positions", False, f"Error: {str(e)}")
            return False, {}

    def test_get_position_summary(self, symbol="BTCUSDT"):
        """Test GET /api/terminal/positions/summary/BTCUSDT - returns position summary"""
        try:
            response = requests.get(f"{self.base_url}/api/terminal/positions/summary/{symbol}", timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                success = (
                    data.get("ok") == True and
                    "has_position" in data and
                    "symbol" in data and
                    "timeframe" in data
                )
                
                # If has_position is True, validate position data
                if success and data.get("has_position"):
                    required_fields = ["side", "size", "entry_price", "mark_price", "unrealized_pnl", "pnl_pct", "health"]
                    success = all(field in data for field in required_fields)
                
                details = f"Has position: {data.get('has_position')}, Symbol: {data.get('symbol')}"
            else:
                details = f"Status: {response.status_code}"
                
            self.log_test(f"GET Position Summary ({symbol})", success, details)
            return success, response.json() if success else {}
            
        except Exception as e:
            self.log_test(f"GET Position Summary ({symbol})", False, f"Error: {str(e)}")
            return False, {}

    def test_simulate_open_from_order(self):
        """Test POST /api/terminal/positions/simulate-open-from-order - creates position from order"""
        try:
            # Create a test order and intent
            test_order = {
                "order_id": f"test_order_{int(datetime.now().timestamp())}",
                "symbol": "BTCUSDT",
                "side": "BUY",
                "size": 0.5,
                "filled_size": 0.5,
                "avg_fill_price": 45000.0,
                "price": 45000.0
            }
            
            test_intent = {
                "intent_id": f"test_intent_{int(datetime.now().timestamp())}",
                "timeframe": "4H",
                "planned_stop": 44000.0,
                "planned_target": 47000.0,
                "planned_rr": 1.5,
                "entry_mode": "LIMIT",
                "execution_mode": "PASSIVE_LIMIT",
                "execution_confidence": 0.8
            }
            
            payload = {
                "order": test_order,
                "intent": test_intent,
                "market_price": 45100.0
            }
            
            response = requests.post(
                f"{self.base_url}/api/terminal/positions/simulate-open-from-order",
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            success = response.status_code == 200
            
            if success:
                data = response.json()
                success = (
                    data.get("ok") == True and
                    "position" in data and
                    data["position"].get("symbol") == "BTCUSDT" and
                    data["position"].get("side") == "LONG" and
                    data["position"].get("status") == "OPEN"
                )
                
                if success:
                    position = data["position"]
                    self.test_position_id = position.get("position_id")
                    
                    # Validate PnL calculation for LONG position
                    entry_price = position.get("entry_price", 0)
                    mark_price = position.get("mark_price", 0)
                    size = position.get("size", 0)
                    unrealized_pnl = position.get("unrealized_pnl", 0)
                    
                    # For LONG: PnL = (mark - entry) * size
                    expected_pnl = (mark_price - entry_price) * size
                    pnl_correct = abs(unrealized_pnl - expected_pnl) < 0.01
                    
                    success = pnl_correct
                    details = f"Position ID: {self.test_position_id}, PnL: {unrealized_pnl} (expected: {expected_pnl})"
                else:
                    details = f"Invalid position data: {data}"
            else:
                details = f"Status: {response.status_code}"
                
            self.log_test("POST Simulate Open From Order", success, details)
            return success, response.json() if success else {}
            
        except Exception as e:
            self.log_test("POST Simulate Open From Order", False, f"Error: {str(e)}")
            return False, {}

    def test_simulate_mark_update(self):
        """Test POST /api/terminal/positions/{id}/simulate-mark - updates mark price and recalculates PnL"""
        if not self.test_position_id:
            self.log_test("POST Simulate Mark Update", False, "No test position available")
            return False, {}
        
        try:
            payload = {
                "mark_price": 46000.0  # New mark price
            }
            
            response = requests.post(
                f"{self.base_url}/api/terminal/positions/{self.test_position_id}/simulate-mark",
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            success = response.status_code == 200
            
            if success:
                data = response.json()
                success = (
                    data.get("ok") == True and
                    "position" in data and
                    data["position"].get("mark_price") == 46000.0
                )
                
                if success:
                    position = data["position"]
                    
                    # Validate PnL recalculation
                    entry_price = position.get("entry_price", 0)
                    mark_price = position.get("mark_price", 0)
                    size = position.get("size", 0)
                    unrealized_pnl = position.get("unrealized_pnl", 0)
                    
                    # For LONG: PnL = (mark - entry) * size
                    expected_pnl = (mark_price - entry_price) * size
                    pnl_correct = abs(unrealized_pnl - expected_pnl) < 0.01
                    
                    # Validate health calculation
                    health = position.get("health")
                    health_valid = health in ["GOOD", "WARNING", "CRITICAL"]
                    
                    success = pnl_correct and health_valid
                    details = f"Mark: {mark_price}, PnL: {unrealized_pnl}, Health: {health}"
                else:
                    details = f"Invalid response: {data}"
            else:
                details = f"Status: {response.status_code}"
                
            self.log_test("POST Simulate Mark Update", success, details)
            return success, response.json() if success else {}
            
        except Exception as e:
            self.log_test("POST Simulate Mark Update", False, f"Error: {str(e)}")
            return False, {}

    def test_simulate_close_position(self):
        """Test POST /api/terminal/positions/{id}/simulate-close - closes position"""
        if not self.test_position_id:
            self.log_test("POST Simulate Close Position", False, "No test position available")
            return False, {}
        
        try:
            payload = {
                "close_price": 46500.0,
                "reason": "test_close"
            }
            
            response = requests.post(
                f"{self.base_url}/api/terminal/positions/{self.test_position_id}/simulate-close",
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            success = response.status_code == 200
            
            if success:
                data = response.json()
                success = (
                    data.get("ok") == True and
                    "position" in data and
                    data["position"].get("status") == "CLOSED" and
                    data["position"].get("close_reason") == "test_close"
                )
                
                if success:
                    position = data["position"]
                    
                    # Validate realized PnL calculation
                    realized_pnl = position.get("realized_pnl", 0)
                    unrealized_pnl = position.get("unrealized_pnl", 0)
                    
                    # After closing, realized_pnl should equal unrealized_pnl
                    pnl_correct = abs(realized_pnl - unrealized_pnl) < 0.01
                    
                    # Validate closed_at timestamp exists
                    closed_at = position.get("closed_at")
                    has_closed_at = closed_at is not None
                    
                    success = pnl_correct and has_closed_at
                    details = f"Realized PnL: {realized_pnl}, Closed at: {closed_at}"
                else:
                    details = f"Invalid response: {data}"
            else:
                details = f"Status: {response.status_code}"
                
            self.log_test("POST Simulate Close Position", success, details)
            return success, response.json() if success else {}
            
        except Exception as e:
            self.log_test("POST Simulate Close Position", False, f"Error: {str(e)}")
            return False, {}

    def test_terminal_state_position_integration(self, symbol="BTCUSDT", timeframe="4H"):
        """Test that terminal state includes position with has_position, side, PnL, health"""
        try:
            response = requests.get(f"{self.base_url}/api/terminal/state/{symbol}?timeframe={timeframe}", timeout=15)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                success = (
                    data.get("ok") == True and
                    "data" in data and
                    "position" in data["data"]
                )
                
                if success:
                    position = data["data"]["position"]
                    
                    # Validate position structure
                    required_fields = ["has_position", "symbol", "status"]
                    success = all(field in position for field in required_fields)
                    
                    # If has_position is True, validate additional fields
                    if success and position.get("has_position"):
                        position_fields = ["side", "unrealized_pnl", "pnl_pct", "health"]
                        success = all(field in position for field in position_fields)
                        
                        # Validate health values
                        health = position.get("health")
                        health_valid = health in ["GOOD", "WARNING", "CRITICAL"]
                        
                        # Validate side values
                        side = position.get("side")
                        side_valid = side in ["LONG", "SHORT"]
                        
                        # Validate status values (including ACTIVE which is used in the API)
                        status = position.get("status")
                        status_valid = status in ["OPEN", "OPENING", "SCALING", "REDUCING", "CLOSING", "CLOSED", "FLAT", "ACTIVE"]
                        
                        success = success and health_valid and side_valid and status_valid
                        details = f"Has position: {position.get('has_position')}, Side: {side}, Health: {health}, Status: {status}"
                    else:
                        details = f"Has position: {position.get('has_position')}, Status: {position.get('status')}"
                else:
                    details = f"Missing position data in response"
            else:
                details = f"Status: {response.status_code}"
                
            self.log_test(f"Terminal State Position Integration ({symbol})", success, details)
            return success
            
        except Exception as e:
            self.log_test(f"Terminal State Position Integration ({symbol})", False, f"Error: {str(e)}")
            return False

    def test_pnl_calculation_logic(self):
        """Test PnL calculation: LONG profit when mark > entry"""
        try:
            # Test LONG position with profit scenario
            test_order = {
                "order_id": f"pnl_test_{int(datetime.now().timestamp())}",
                "symbol": "BTCUSDT",
                "side": "BUY",
                "size": 1.0,
                "filled_size": 1.0,
                "avg_fill_price": 50000.0,
                "price": 50000.0
            }
            
            test_intent = {
                "intent_id": f"pnl_intent_{int(datetime.now().timestamp())}",
                "timeframe": "4H",
                "planned_stop": 49000.0,
                "planned_target": 52000.0,
                "planned_rr": 2.0,
                "entry_mode": "LIMIT",
                "execution_mode": "PASSIVE_LIMIT"
            }
            
            # Create position with mark > entry (profit scenario)
            payload = {
                "order": test_order,
                "intent": test_intent,
                "market_price": 51000.0  # Mark price higher than entry = profit for LONG
            }
            
            response = requests.post(
                f"{self.base_url}/api/terminal/positions/simulate-open-from-order",
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            success = response.status_code == 200
            
            if success:
                data = response.json()
                position = data.get("position", {})
                
                entry_price = position.get("entry_price", 0)
                mark_price = position.get("mark_price", 0)
                size = position.get("size", 0)
                unrealized_pnl = position.get("unrealized_pnl", 0)
                pnl_pct = position.get("pnl_pct", 0)
                
                # For LONG: profit when mark > entry
                # Expected PnL = (51000 - 50000) * 1.0 = 1000
                expected_pnl = (mark_price - entry_price) * size
                expected_pnl_pct = ((mark_price - entry_price) / entry_price) * 100
                
                pnl_correct = abs(unrealized_pnl - expected_pnl) < 0.01
                pnl_pct_correct = abs(pnl_pct - expected_pnl_pct) < 0.01
                is_profit = unrealized_pnl > 0
                
                success = pnl_correct and pnl_pct_correct and is_profit
                details = f"Entry: {entry_price}, Mark: {mark_price}, PnL: {unrealized_pnl} ({pnl_pct}%), Expected: {expected_pnl}"
                
                # Clean up test position
                if position.get("position_id"):
                    requests.post(
                        f"{self.base_url}/api/terminal/positions/{position['position_id']}/simulate-close",
                        json={"close_price": mark_price, "reason": "test_cleanup"},
                        headers={'Content-Type': 'application/json'},
                        timeout=5
                    )
            else:
                details = f"Status: {response.status_code}"
                
            self.log_test("PnL Calculation Logic (LONG Profit)", success, details)
            return success
            
        except Exception as e:
            self.log_test("PnL Calculation Logic (LONG Profit)", False, f"Error: {str(e)}")
            return False

    def run_all_tests(self):
        """Run all position manager tests"""
        print("🚀 Starting Position Manager Backend Tests")
        print(f"Testing against: {self.base_url}")
        print("=" * 60)
        
        # Test positions module health
        self.test_positions_health()
        
        print("\n📊 POSITION LIFECYCLE TESTS")
        print("-" * 40)
        
        # Test position CRUD operations
        self.test_get_positions_list()
        self.test_get_open_positions()
        self.test_get_position_summary("BTCUSDT")
        
        # Test position lifecycle: order filled -> position created -> mark update -> close
        self.test_simulate_open_from_order()
        self.test_simulate_mark_update()
        self.test_simulate_close_position()
        
        print("\n🎯 INTEGRATION TESTS")
        print("-" * 40)
        
        # Test terminal state integration
        self.test_terminal_state_position_integration("BTCUSDT", "4H")
        
        # Test PnL calculation logic
        self.test_pnl_calculation_logic()
        
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
    tester = PositionManagerTester()
    success = tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())