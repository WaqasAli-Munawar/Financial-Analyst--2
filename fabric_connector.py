"""
Microsoft Fabric SQL Connector
Executes queries against the Fabric Data Warehouse using Service Principal
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Try to import pyodbc
try:
    import pyodbc
    PYODBC_AVAILABLE = True
except ImportError:
    PYODBC_AVAILABLE = False
    print("WARNING: pyodbc not installed. Install with: pip install pyodbc")

# Configuration from environment
FABRIC_SQL_ENDPOINT = os.getenv("FABRIC_SQL_ENDPOINT", "")
FABRIC_DATABASE = os.getenv("FABRIC_DATABASE", "salic_finance_warehouse")
AZURE_TENANT_ID = os.getenv("AZURE_TENANT_ID", "")
AZURE_CLIENT_ID = os.getenv("AZURE_CLIENT_ID", "")
AZURE_CLIENT_SECRET = os.getenv("AZURE_CLIENT_SECRET", "")
USE_MOCK_DATA = os.getenv("USE_MOCK_DATA", "true").lower() == "true"


class FabricConnector:
    """
    Connector for Microsoft Fabric SQL Endpoint using Service Principal.
    """
    
    def __init__(self):
        self.connection = None
        
    def _get_connection_string(self) -> str:
        """Get connection string for Service Principal authentication."""
        return (
            f"Driver={{ODBC Driver 18 for SQL Server}};"
            f"Server={FABRIC_SQL_ENDPOINT};"
            f"Database={FABRIC_DATABASE};"
            f"Encrypt=Yes;"
            f"TrustServerCertificate=No;"
            f"Authentication=ActiveDirectoryServicePrincipal;"
            f"UID={AZURE_CLIENT_ID}@{AZURE_TENANT_ID};"
            f"PWD={AZURE_CLIENT_SECRET};"
        )
    
    def connect(self):
        """Connect to Microsoft Fabric using Service Principal."""
        if not PYODBC_AVAILABLE:
            raise ImportError("pyodbc is required. Install with: pip install pyodbc")
        
        if not all([FABRIC_SQL_ENDPOINT, AZURE_TENANT_ID, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET]):
            raise ValueError("Missing required environment variables for Fabric connection")
        
        conn_str = self._get_connection_string()
        self.connection = pyodbc.connect(conn_str)
        print("✓ Connected to Microsoft Fabric")
        return self.connection
    
    def connect_interactive(self):
        """Alias for connect() - maintains compatibility."""
        return self.connect()
    
    def execute_query(self, sql: str) -> dict:
        """
        Execute a SQL query and return results.
        
        Args:
            sql: The SQL query to execute
            
        Returns:
            dict with 'columns' (list of column names) and 'rows' (list of row dicts)
        """
        if not self.connection:
            self.connect()
        
        try:
            cursor = self.connection.cursor()
            cursor.execute(sql)
            
            # Get column names
            columns = [column[0] for column in cursor.description]
            
            # Fetch all rows
            rows = []
            for row in cursor.fetchall():
                row_dict = {}
                for i, value in enumerate(row):
                    # Convert Decimal to float for JSON serialization
                    if hasattr(value, 'is_integer'):
                        value = float(value)
                    # Convert string numbers to float where applicable
                    if isinstance(value, str):
                        try:
                            value = float(value)
                        except ValueError:
                            pass
                    row_dict[columns[i]] = value
                rows.append(row_dict)
            
            cursor.close()
            
            return {
                "columns": columns,
                "rows": rows,
                "row_count": len(rows)
            }
            
        except Exception as e:
            raise Exception(f"Query execution failed: {str(e)}")
    
    def close(self):
        """Close the database connection."""
        if self.connection:
            self.connection.close()
            self.connection = None
            print("✓ Fabric connection closed")


class MockFabricConnector:
    """
    Mock connector for testing without actual Fabric connection.
    """
    
    def __init__(self):
        self.connected = False
        
    def connect(self):
        self.connected = True
        print("Mock: Connected")
        return self
    
    def connect_interactive(self):
        return self.connect()
    
    def execute_query(self, sql: str) -> dict:
        """Return mock data based on query content."""
        
        # Sample G&A expenses data
        if "General and administrative" in sql:
            return {
                "columns": ["CalendarYear", "PeriodName", "FiscalQuarter", "PeriodNumber", 
                           "FinalParentAccountCode", "Amount"],
                "rows": [
                    {"CalendarYear": 2024, "PeriodName": "Sep", "FiscalQuarter": "Q3", 
                     "PeriodNumber": 9, "FinalParentAccountCode": "General and administrative expenses",
                     "Amount": 218927.84},
                    {"CalendarYear": 2024, "PeriodName": "Oct", "FiscalQuarter": "Q4",
                     "PeriodNumber": 10, "FinalParentAccountCode": "General and administrative expenses",
                     "Amount": 9322.16},
                    {"CalendarYear": 2024, "PeriodName": "Nov", "FiscalQuarter": "Q4",
                     "PeriodNumber": 11, "FinalParentAccountCode": "General and administrative expenses",
                     "Amount": 9154.40},
                    {"CalendarYear": 2024, "PeriodName": "Dec", "FiscalQuarter": "Q4",
                     "PeriodNumber": 12, "FinalParentAccountCode": "General and administrative expenses",
                     "Amount": -891.92}
                ],
                "row_count": 4
            }
        
        # Default response
        return {
            "columns": ["FinalParentAccountCode", "TotalAmount"],
            "rows": [
                {"FinalParentAccountCode": "General and administrative expenses", "TotalAmount": 236512.48},
            ],
            "row_count": 1
        }
    
    def close(self):
        self.connected = False
        print("Mock: Connection closed")


def get_connector(use_mock: bool = None):
    """
    Get a Fabric connector instance.
    
    Args:
        use_mock: If True, return mock connector. If None, use USE_MOCK_DATA env var.
        
    Returns:
        FabricConnector or MockFabricConnector instance
    """
    if use_mock is None:
        use_mock = USE_MOCK_DATA
    
    if use_mock or not PYODBC_AVAILABLE:
        return MockFabricConnector()
    return FabricConnector()


# Test the connector
if __name__ == "__main__":
    print("Testing Fabric Connector...")
    print(f"USE_MOCK_DATA: {USE_MOCK_DATA}")
    print("-" * 50)
    
    connector = get_connector()
    connector.connect()
    
    # Test with a real query
    sql = """
    SELECT TOP 5
        y.CalendarYear,
        p.PeriodName,
        a.FinalParentAccountCode,
        SUM(CAST(f.Amount AS DECIMAL(18,2))) AS Amount
    FROM vw_Fact_Actuals_SALIC_Ukraine f
    JOIN Dim_Account a ON f.AccountKey = a.AccountKey
    JOIN Dim_Period p ON f.PeriodKey = p.PeriodKey
    JOIN Dim_Year y ON f.YearKey = y.YearKey
    GROUP BY y.CalendarYear, p.PeriodName, a.FinalParentAccountCode
    """
    
    result = connector.execute_query(sql)
    
    print(f"Columns: {result['columns']}")
    print(f"Row count: {result['row_count']}")
    print("\nData:")
    for row in result['rows']:
        print(row)
    
    connector.close()
