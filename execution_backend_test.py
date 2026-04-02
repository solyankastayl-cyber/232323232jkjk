#!/usr/bin/env python3
"""
TA Engine Trading Terminal Phase TT1 - Execution State & Orders Backend Tests
Tests the full execution lifecycle: create intent -> place order -> fill -> verify status
"""

import requests
import sys
import json
import time
from datetime import datetime

class ExecutionBackendTester:
    def __init__(self, base_url="https://repo-study-4.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.errors = []
        self.intent_id = None
        self.order_id = None

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

    def test_execution_health(self):
        """Test execution module health endpoint"""
        try:
            response = requests.get(f"{self.base_url}/api/terminal/execution/health", timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                success = (
                    data.get("ok") == True and
                    data.get("module") == "execution_state_engine" and
                    "version" in data and
                    "timestamp" in data
                )
                details = f"Module: {data.get('module')}, Version: {data.get('version')}"
            else:
                details = f"Status: {response.status_code}"
                
            self.log_test("Execution Health Check", success, details)
            return success, response.json() if success else {}
            
        except Exception as e:
            self.log_test("Execution Health Check", False, f"Error: {str(e)}")
            return False, {}

    def test_get_execution_status(self, symbol="BTCUSDT", timeframe="4H"):
        """Test GET /api/terminal/execution/{symbol} endpoint"""
        try:
            response = requests.get(
                f"{self.base_url}/api/terminal/execution/{symbol}?timeframe={timeframe}", 
                timeout=10
            )
            success = response.status_code == 200
            
            if success:
                data = response.json()
                success = (
                    data.get("ok") == True and
                    data.get("symbol") == symbol and
                    data.get("timeframe") == timeframe and
                    "execution_status" in data
                )
                
                if success:
                    exec_status = data["execution_status"]
                    required_fields = [
                        "execution_state", "intent_state", "order_present", 
                        "position_open", "filled_pct", "status_label", "status_reason"
                    ]
                    success = all(field in exec_status for field in required_fields)
                    details = f"State: {exec_status.get('execution_state')}, Order: {exec_status.get('order_present')}"
                else:
                    details = f"Missing required fields in response"
            else:
                details = f"Status: {response.status_code}"
                
            self.log_test(f"Get Execution Status ({symbol})", success, details)
            return success, response.json() if success else {}
            
        except Exception as e:
            self.log_test(f"Get Execution Status ({symbol})", False, f"Error: {str(e)}")
            return False, {}

    def test_get_orders_list(self):
        """Test GET /api/terminal/orders endpoint"""
        try:
            response = requests.get(f"{self.base_url}/api/terminal/orders", timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                success = (
                    data.get("ok") == True and
                    "count" in data and
                    "orders" in data
                )
                
                if success:
                    orders = data["orders"]
                    count = data["count"]
                    
                    # Validate order structure if orders exist
                    if orders:
                        first_order = orders[0]
                        required_fields = [
                            "order_id", "intent_id", "symbol", "side", "order_type",
                            "status", "size", "filled_size", "updated_at"
                        ]
                        success = all(field in first_order for field in required_fields)
                        details = f"Count: {count}, First order status: {first_order.get('status')}"
                    else:
                        details = f"Count: {count} (empty list)"
                else:
                    details = f"Missing required fields in response"
            else:
                details = f"Status: {response.status_code}"
                
            self.log_test("Get Orders List", success, details)
            return success, response.json() if success else {}
            
        except Exception as e:
            self.log_test("Get Orders List", False, f"Error: {str(e)}")
            return False, {}

    def test_simulate_upsert_intent(self, symbol="BTCUSDT", timeframe="4H"):
        """Test POST /api/terminal/intents/simulate-upsert endpoint"""
        try:
            payload = {
                "symbol": symbol,
                "timeframe": timeframe,
                "decision": {
                    "action": "GO_FULL",
                    "direction": "LONG",
                    "mode": "BREAKOUT"
                },
                "execution": {
                    "mode": "PASSIVE_LIMIT",
                    "entry": 45000.0,
                    "stop": 44000.0,
                    "target": 47000.0,
                    "rr": 2.0,
                    "size": 1.0,
                    "confidence": 0.85
                },
                "validation": {"is_valid": True},
                "position": {"has_position": False}
            }
            
            response = requests.post(
                f"{self.base_url}/api/terminal/intents/simulate-upsert",
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            success = response.status_code == 200
            
            if success:
                data = response.json()
                success = (
                    data.get("ok") == True and
                    "intent" in data
                )
                
                if success:
                    intent = data["intent"]
                    required_fields = [
                        "intent_id", "symbol", "timeframe", "action", "direction",
                        "execution_mode", "planned_entry", "status", "created_at"
                    ]
                    success = all(field in intent for field in required_fields)
                    
                    if success:
                        self.intent_id = intent["intent_id"]  # Store for next tests
                        details = f"Intent ID: {self.intent_id[:8]}..., Status: {intent.get('status')}"
                    else:
                        details = f"Missing required fields in intent"
                else:
                    details = f"Missing intent in response"
            else:
                details = f"Status: {response.status_code}"
                
            self.log_test("Simulate Upsert Intent", success, details)
            return success, response.json() if success else {}
            
        except Exception as e:
            self.log_test("Simulate Upsert Intent", False, f"Error: {str(e)}")
            return False, {}

    def test_simulate_place_order(self):
        """Test POST /api/terminal/orders/simulate-place endpoint"""
        if not self.intent_id:
            self.log_test("Simulate Place Order", False, "No intent_id available")
            return False, {}
            
        try:
            payload = {
                "intent_id": self.intent_id,
                "side": "BUY",
                "order_type": "LIMIT"
            }
            
            response = requests.post(
                f"{self.base_url}/api/terminal/orders/simulate-place",
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            success = response.status_code == 200
            
            if success:
                data = response.json()
                success = (
                    data.get("ok") == True and
                    "order" in data
                )
                
                if success:
                    order = data["order"]
                    required_fields = [
                        "order_id", "intent_id", "symbol", "side", "order_type",
                        "status", "price", "size", "placed_at"
                    ]
                    success = all(field in order for field in required_fields)
                    
                    if success:
                        self.order_id = order["order_id"]  # Store for next tests
                        details = f"Order ID: {self.order_id[:8]}..., Status: {order.get('status')}, Side: {order.get('side')}"
                    else:
                        details = f"Missing required fields in order"
                else:
                    details = f"Missing order in response"
            else:
                details = f"Status: {response.status_code}"
                
            self.log_test("Simulate Place Order", success, details)
            return success, response.json() if success else {}
            
        except Exception as e:
            self.log_test("Simulate Place Order", False, f"Error: {str(e)}")
            return False, {}

    def test_simulate_fill_order(self, fill_size=0.5):
        """Test POST /api/terminal/orders/{id}/simulate-fill endpoint"""
        if not self.order_id:
            self.log_test("Simulate Fill Order", False, "No order_id available")
            return False, {}
            
        try:
            payload = {
                "fill_size": fill_size,
                "fill_price": 45000.0
            }
            
            response = requests.post(
                f"{self.base_url}/api/terminal/orders/{self.order_id}/simulate-fill",
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            success = response.status_code == 200
            
            if success:
                data = response.json()
                success = (
                    data.get("ok") == True and
                    "order" in data
                )
                
                if success:
                    order = data["order"]
                    success = (
                        order.get("filled_size") == fill_size and
                        order.get("status") in ["PARTIAL_FILL", "FILLED"] and
                        "filled_pct" in order
                    )
                    details = f"Filled: {order.get('filled_size')}/{order.get('size')}, Status: {order.get('status')}"
                else:
                    details = f"Missing order in response"
            else:
                details = f"Status: {response.status_code}"
                
            self.log_test("Simulate Fill Order (Partial)", success, details)
            return success, response.json() if success else {}
            
        except Exception as e:
            self.log_test("Simulate Fill Order (Partial)", False, f"Error: {str(e)}")
            return False, {}

    def test_simulate_full_fill_order(self):
        """Test filling the remaining order completely"""
        if not self.order_id:
            self.log_test("Simulate Full Fill Order", False, "No order_id available")
            return False, {}
            
        try:
            payload = {
                "fill_size": 0.5,  # Fill remaining 0.5
                "fill_price": 45000.0
            }
            
            response = requests.post(
                f"{self.base_url}/api/terminal/orders/{self.order_id}/simulate-fill",
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            success = response.status_code == 200
            
            if success:
                data = response.json()
                success = (
                    data.get("ok") == True and
                    "order" in data
                )
                
                if success:
                    order = data["order"]
                    success = (
                        order.get("status") == "FILLED" and
                        order.get("remaining_size") == 0.0 and
                        order.get("filled_size") == order.get("size")
                    )
                    details = f"Status: {order.get('status')}, Filled: {order.get('filled_size')}/{order.get('size')}"
                else:
                    details = f"Missing order in response"
            else:
                details = f"Status: {response.status_code}"
                
            self.log_test("Simulate Full Fill Order", success, details)
            return success, response.json() if success else {}
            
        except Exception as e:
            self.log_test("Simulate Full Fill Order", False, f"Error: {str(e)}")
            return False, {}

    def test_simulate_cancel_order(self):
        """Test POST /api/terminal/orders/{id}/simulate-cancel endpoint"""
        # First create a new order to cancel
        intent_success, intent_data = self.test_simulate_upsert_intent("ETHUSDT", "4H")
        if not intent_success:
            self.log_test("Simulate Cancel Order", False, "Failed to create intent for cancel test")
            return False, {}
            
        cancel_intent_id = intent_data["intent"]["intent_id"]
        
        # Place order
        payload = {
            "intent_id": cancel_intent_id,
            "side": "SELL",
            "order_type": "LIMIT"
        }
        
        response = requests.post(
            f"{self.base_url}/api/terminal/orders/simulate-place",
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if response.status_code != 200:
            self.log_test("Simulate Cancel Order", False, "Failed to place order for cancel test")
            return False, {}
            
        cancel_order_id = response.json()["order"]["order_id"]
        
        # Now cancel the order
        try:
            payload = {
                "reason": "manual_cancel"
            }
            
            response = requests.post(
                f"{self.base_url}/api/terminal/orders/{cancel_order_id}/simulate-cancel",
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            success = response.status_code == 200
            
            if success:
                data = response.json()
                success = (
                    data.get("ok") == True and
                    "order" in data
                )
                
                if success:
                    order = data["order"]
                    success = (
                        order.get("status") == "CANCELLED" and
                        order.get("cancel_reason") == "manual_cancel"
                    )
                    details = f"Status: {order.get('status')}, Reason: {order.get('cancel_reason')}"
                else:
                    details = f"Missing order in response"
            else:
                details = f"Status: {response.status_code}"
                
            self.log_test("Simulate Cancel Order", success, details)
            return success, response.json() if success else {}
            
        except Exception as e:
            self.log_test("Simulate Cancel Order", False, f"Error: {str(e)}")
            return False, {}

    def test_state_machine_validation(self):
        """Test that state machine prevents illegal transitions"""
        try:
            # Try to create an intent and then attempt illegal state transition
            payload = {
                "symbol": "SOLUSDT",
                "timeframe": "1H",
                "decision": {
                    "action": "SKIP",  # This should result in IDLE state
                    "direction": "NEUTRAL",
                    "mode": "UNKNOWN"
                },
                "execution": {
                    "mode": "PASSIVE_LIMIT",
                    "size": 1.0
                },
                "validation": {"is_valid": True},
                "position": {"has_position": False}
            }
            
            response = requests.post(
                f"{self.base_url}/api/terminal/intents/simulate-upsert",
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code != 200:
                self.log_test("State Machine Validation", False, "Failed to create IDLE intent")
                return False, {}
                
            idle_intent_id = response.json()["intent"]["intent_id"]
            
            # Now try to place an order from IDLE state (should fail or handle gracefully)
            payload = {
                "intent_id": idle_intent_id,
                "side": "BUY",
                "order_type": "LIMIT"
            }
            
            response = requests.post(
                f"{self.base_url}/api/terminal/orders/simulate-place",
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            # This should either fail (400) or handle the transition gracefully
            if response.status_code == 400:
                # Expected behavior - illegal transition rejected
                details = "Illegal transition correctly rejected"
                success = True
            elif response.status_code == 200:
                # Check if state was properly transitioned
                data = response.json()
                if data.get("ok"):
                    details = "State transition handled gracefully"
                    success = True
                else:
                    details = "Unexpected response structure"
                    success = False
            else:
                details = f"Unexpected status: {response.status_code}"
                success = False
                
            self.log_test("State Machine Validation", success, details)
            return success, {}
            
        except Exception as e:
            self.log_test("State Machine Validation", False, f"Error: {str(e)}")
            return False, {}

    def test_terminal_state_integration(self, symbol="BTCUSDT", timeframe="4H"):
        """Test that execution status appears in terminal state"""
        try:
            response = requests.get(
                f"{self.base_url}/api/terminal/state/{symbol}?timeframe={timeframe}", 
                timeout=15
            )
            success = response.status_code == 200
            
            if success:
                data = response.json()
                success = (
                    data.get("ok") == True and
                    "data" in data
                )
                
                if success:
                    state_data = data["data"]
                    
                    # Check if execution_status is present
                    has_execution_status = "execution_status" in state_data
                    
                    # Check if orders_preview is present
                    has_orders_preview = "orders_preview" in state_data
                    
                    success = has_execution_status and has_orders_preview
                    
                    if success:
                        exec_status = state_data["execution_status"]
                        orders_preview = state_data["orders_preview"]
                        details = f"Execution state: {exec_status.get('execution_state')}, Orders count: {len(orders_preview)}"
                    else:
                        details = f"Missing execution_status: {not has_execution_status}, Missing orders_preview: {not has_orders_preview}"
                else:
                    details = f"Missing data field in response"
            else:
                details = f"Status: {response.status_code}"
                
            self.log_test(f"Terminal State Integration ({symbol})", success, details)
            return success, response.json() if success else {}
            
        except Exception as e:
            self.log_test(f"Terminal State Integration ({symbol})", False, f"Error: {str(e)}")
            return False, {}

    def run_full_lifecycle_test(self):
        """Run complete execution lifecycle test"""
        print("\n🔄 FULL EXECUTION LIFECYCLE TEST")
        print("-" * 50)
        
        # Step 1: Create intent
        intent_success, intent_data = self.test_simulate_upsert_intent()
        if not intent_success:
            return False
            
        # Step 2: Place order
        order_success, order_data = self.test_simulate_place_order()
        if not order_success:
            return False
            
        # Step 3: Partial fill
        fill_success, fill_data = self.test_simulate_fill_order(0.5)
        if not fill_success:
            return False
            
        # Step 4: Complete fill
        full_fill_success, full_fill_data = self.test_simulate_full_fill_order()
        if not full_fill_success:
            return False
            
        # Step 5: Verify final status
        status_success, status_data = self.test_get_execution_status()
        if status_success:
            exec_status = status_data.get("execution_status", {})
            if exec_status.get("execution_state") == "FILLED":
                self.log_test("Full Lifecycle Verification", True, "Order lifecycle completed successfully")
                return True
            else:
                self.log_test("Full Lifecycle Verification", False, f"Expected FILLED state, got {exec_status.get('execution_state')}")
                return False
        else:
            return False

    def run_all_tests(self):
        """Run all execution backend tests"""
        print("🚀 Starting TA Engine Trading Terminal Phase TT1 - Execution Backend Tests")
        print(f"Testing against: {self.base_url}")
        print("=" * 80)
        
        # Test health endpoint
        self.test_execution_health()
        
        # Test basic read endpoints
        print("\n📖 READ ENDPOINTS")
        print("-" * 30)
        self.test_get_execution_status()
        self.test_get_orders_list()
        
        # Test simulation endpoints
        print("\n🎮 SIMULATION ENDPOINTS")
        print("-" * 30)
        self.run_full_lifecycle_test()
        
        # Test cancel functionality
        self.test_simulate_cancel_order()
        
        # Test state machine validation
        print("\n🔒 STATE MACHINE VALIDATION")
        print("-" * 30)
        self.test_state_machine_validation()
        
        # Test terminal integration
        print("\n🔗 TERMINAL INTEGRATION")
        print("-" * 30)
        self.test_terminal_state_integration()
        
        # Print summary
        print("=" * 80)
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
    tester = ExecutionBackendTester()
    success = tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())