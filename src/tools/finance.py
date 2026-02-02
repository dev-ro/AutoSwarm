
import json
import os
from agno.tools import Toolkit

WALLET_FILE = "wallet_balance.json"

class FinanceTools(Toolkit):
    def __init__(self):
        super().__init__(name="finance_tools")
        self.register(self.read_balance)
        self.register(self.evaluate_opportunity)
        self.register(self.send_transaction)

    def read_balance(self) -> str:
        """
        Reads the local wallet balance from a JSON file.
        """
        print("  [FinanceTool] Reading wallet balance...")
        if not os.path.exists(WALLET_FILE):
             return "Error: Wallet file not found."
        
        try:
            with open(WALLET_FILE, 'r') as f:
                data = json.load(f)
            return f"Wallet Address: {data.get('address')}\nETH: {data.get('balance_eth')}\nUSDC: {data.get('balance_usdc')}"
        except Exception as e:
            return f"Error reading wallet: {e}"

    def evaluate_opportunity(self, risk: int, reward: int) -> str:
        """
        Evaluates a financial opportunity based on risk (1-10) and reward potential (1-10).
        Risk: 1 (Safe) to 10 (Extremely Risky)
        Reward: 1 (Low) to 10 (High)
        """
        print(f"  [FinanceTool] Evaluating opportunity: Risk={risk}, Reward={reward}")
        
        score = reward - risk
        
        if risk > 8:
            return "Recommendation: REJECT. Risk is too high."
        
        if score > 2:
            return "Recommendation: APPROVE. Reward outweighs risk."
        elif score >= 0:
            return "Recommendation: CONSIDER. Balanced risk/reward."
        else:
            return "Recommendation: REJECT. Risk outweighs reward."

    def send_transaction(self, recipient: str, amount: float, token: str = "USDC") -> str:
        """
        MOCK function to send instructions.
        Does not actually sign or broadcast transactions on chain.
        """
        print(f"  [FinanceTool] **MOCK** Sending {amount} {token} to {recipient}")
        return f"Transaction Sent (Mock): {amount} {token} -> {recipient}. Status: Pending Confirmation."
