"""
資料庫管理器 - Oracle 連線管理
"""
import asyncio
from typing import Optional, Dict, Any, List
import structlog
from contextlib import asynccontextmanager

try:
    import oracledb
    ORACLE_AVAILABLE = True
except ImportError:
    ORACLE_AVAILABLE = False
    oracledb = None

logger = structlog.get_logger()

class DatabaseManager:    
    """Oracle 資料庫管理器"""
    
    def __init__(self):
        self.pool = None  # Connection pool
        self.dsn = None   # DSN for direct connections
        self.host: Optional[str] = None
        self.port: Optional[int] = None
        self.service_name: Optional[str] = None
        self.user: Optional[str] = None
        self.password: Optional[str] = None
    
    async def initialize(self):
        import os
        from dotenv import load_dotenv
        
        load_dotenv()

        """初始化資料庫連線池"""
        self.host = os.getenv('ORACLE_HOST', 'localhost')
        self.port = int(os.getenv('ORACLE_PORT', '1521'))
        self.service_name = os.getenv('ORACLE_SERVICE', 'XEPDB1')
        self.user = os.getenv('ORACLE_USER', 'system')
        self.password = os.getenv('ORACLE_PASSWORD', 'password')
        
        logger.info("🔧 資料庫設定", 
                host=self.host, 
                port=self.port, 
                service=self.service_name, 
                user=self.user)
        
        if not ORACLE_AVAILABLE:
            logger.warning("⚠️ Oracle 模組不可用，使用模擬資料庫")
            self.pool = None
            return
        
        try:
            # 在開發環境中，我們強制使用模擬模式
            # 除非明確設置了環境變數要使用真實資料庫
            import os
            use_real_db = os.getenv('USE_REAL_ORACLE_DB', 'false').lower() == 'true'
            
            if not use_real_db:
                logger.info("🔧 開發模式：強制使用模擬資料庫")
                self.pool = None
                return
            
            # 使用 makedsn 建立 DSN
            dsn = oracledb.makedsn(self.host, self.port, service_name=self.service_name)
            
            # 測試連線
            test_conn = oracledb.connect(user=self.user, password=self.password, dsn=dsn)
            test_conn.close()
            
            logger.info("✅ Oracle 資料庫連線測試成功", 
                       host=self.host, port=self.port, service=self.service_name)

            # 儲存連線參數供後續使用
            self.dsn = dsn
            
        except Exception as e:
            logger.error("❌ Oracle 資料庫連線失敗，切換到模擬模式", error=str(e))
            # 連線失敗時，設置為 None 以使用模擬資料庫
            self.pool = None
            self.dsn = None
    
    @asynccontextmanager
    async def get_connection(self):
        """取得資料庫連線的上下文管理器"""
        if not self.dsn:
            logger.warning("⚠️ 資料庫 DSN 未初始化，使用模擬連線")
            yield MockConnection()
            return
        
        connection = None
        try:
            # 使用 oracledb.connect 建立直接連線
            connection = oracledb.connect(
                user=self.user, 
                password=self.password, 
                dsn=self.dsn
            )
            yield connection
        except Exception as e:
            logger.error("資料庫連線錯誤", error=str(e))
            # 如果連線失敗，退回到模擬模式
            logger.warning("⚠️ 連線失敗，使用模擬連線")
            # 確保我們沒有持有無效的連線
            connection = None
            yield MockConnection()
            return
        finally:
            if connection:
                try:
                    connection.close()
                except Exception as e:
                    logger.warning("關閉連線時發生錯誤", error=str(e))
    
    async def execute_query(self, sql: str, params: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """執行查詢並返回結果"""
        async with self.get_connection() as conn:
            if isinstance(conn, MockConnection):
                return conn.execute_query(sql, params)
            
            with conn.cursor() as cursor:
                if params:
                    cursor.execute(sql, params)
                else:
                    cursor.execute(sql)
                
                # 取得欄位名稱
                columns = [desc[0] for desc in cursor.description] if cursor.description else []
                
                # 取得所有結果
                rows = cursor.fetchall()
                
                # 轉換為字典列表
                result = []
                for row in rows:
                    result.append(dict(zip(columns, row)))
                
                return result
    
    async def execute_non_query(self, sql: str, params: Optional[Dict] = None) -> int:
        """執行非查詢 SQL（INSERT, UPDATE, DELETE）並返回影響的行數"""
        async with self.get_connection() as conn:
            if isinstance(conn, MockConnection):
                return conn.execute_non_query(sql, params)
            
            with conn.cursor() as cursor:
                if params:
                    cursor.execute(sql, params)
                else:
                    cursor.execute(sql)
                
                rowcount = cursor.rowcount
                conn.commit()
                return rowcount
    
    async def close(self):
        """關閉資料庫連線"""
        if self.dsn:
            logger.info("✅ Oracle 資料庫連線管理器已關閉")
        # 由於使用直接連線而非連線池，無需特別清理

class MockConnection:
    """模擬資料庫連線（開發用）"""
    
    def execute_query(self, sql: str, params: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """模擬查詢執行"""
        logger.info("🔧 模擬查詢執行", sql=sql[:100], params=params)
        
        # 根據 SQL 返回模擬資料
        if "staff" in sql.lower() and "staff_code" in sql.lower():
            # 模擬員工登入查詢（Oracle 返回大寫欄位名稱）
            logger.info("🔧 檢測到員工查詢", staff_code=params.get('staff_code') if params else None)
            if params and params.get('staff_code') == 'S001':
                result = [{
                    "STAFF_ID": "STAFF001",
                    "STAFF_CODE": "S001",
                    "NAME": "王小明",
                    "ROLE": "Sales",
                    "STORE_ID": "STORE_A",
                    "PASSWORD_HASH": "$2b$12$r593FHMKa38SIZuyT/Fty.3Qau1bvmcqAU4.GNCoK/dm876G7qDZu",  # password
                    "IS_ACTIVE": 1
                }]
                logger.info("🔧 返回員工資料", result=result)
                return result
            else:
                logger.info("🔧 員工不存在或非活躍")
                return []  # 員工不存在或非活躍
        elif "staff" in sql.lower():
            return [{
                "staff_id": "STAFF001",
                "staff_code": "S001",
                "email": "staff@example.com",
                "name": "測試人員",
                "role": "Sales",
                "store_id": "STORE_A"
            }]
        elif "customer" in sql.lower():
            return [{
                "customer_id": "C123456",
                "id_number": "A123456789",
                "name": "張三",
                "phone": "0912345678"
            }]
        
        logger.info("🔧 無匹配的查詢，返回空結果")
        return []
    
    def execute_non_query(self, sql: str, params: Optional[Dict] = None) -> int:
        """模擬非查詢執行"""
        logger.info("🔧 模擬非查詢執行", sql=sql[:100], params=params)
        return 1