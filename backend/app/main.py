"""
電信門市銷售助理系統 - 主應用程式
"""
import os
import logging
import logging.handlers
from pathlib import Path
from quart import Quart, jsonify
from quart_cors import cors
import structlog
from dotenv import load_dotenv

from .routes import auth, renewal_workflow, statistics
from .utils.exceptions import APIException
from .services.database import DatabaseManager
from .services.redis_manager import RedisManager
from .middleware.auth import authenticate_session

# 載入環境變數
load_dotenv()


def setup_logging():
    """
    設定結構化日誌
    
    日誌輸出：
    1. 控制台（Console）- 開發模式使用彩色輸出
    2. 檔案（File）- logs/app.log，每日輪替，保留 30 天
    """
    # 創建 logs 目錄
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # 取得環境設定
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    log_to_file = os.getenv("LOG_TO_FILE", "true").lower() == "true"
    
    # 設定標準 logging
    logging.basicConfig(
        format="%(message)s",
        level=getattr(logging, log_level),
    )
    
    # 設定檔案處理器（如果啟用）
    if log_to_file:
        # 使用 TimedRotatingFileHandler 每日輪替
        file_handler = logging.handlers.TimedRotatingFileHandler(
            filename=log_dir / "app.log",
            when="midnight",  # 每天午夜輪替
            interval=1,
            backupCount=30,  # 保留 30 天
            encoding="utf-8"
        )
        file_handler.setLevel(getattr(logging, log_level))
        
        # 添加到 root logger
        logging.root.addHandler(file_handler)
    
    # 設定 structlog 處理器
    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
    ]
    
    # 根據是否輸出到檔案選擇不同的渲染器
    if log_to_file:
        # 檔案輸出：使用 JSON 格式（便於解析），ensure_ascii=False 讓中文可讀
        processors.append(structlog.processors.JSONRenderer(ensure_ascii=False))
    else:
        # 控制台輸出：使用彩色格式（開發友好）
        processors.append(structlog.dev.ConsoleRenderer())
    
    # 配置 structlog
    structlog.configure(
        processors=processors,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


# 初始化日誌
setup_logging()
logger = structlog.get_logger()

def create_app() -> Quart:
    """建立 Quart 應用程式"""
    app = Quart(__name__)
    
    # 基本配置
    app.config.update({
        "SECRET_KEY": os.getenv("SECRET_KEY", "dev-secret-key"),
        "DEBUG": os.getenv("DEBUG", "False").lower() == "true",
        
        # 資料庫配置
        "ORACLE_HOST": os.getenv("ORACLE_HOST", "localhost"),
        "ORACLE_PORT": int(os.getenv("ORACLE_PORT", "1521")),
        "ORACLE_SERVICE": os.getenv("ORACLE_SERVICE", "XEPDB1"),
        "ORACLE_USER": os.getenv("ORACLE_USER"),
        "ORACLE_PASSWORD": os.getenv("ORACLE_PASSWORD"),
        
        # Redis 配置
        "REDIS_URL": os.getenv("REDIS_URL", "redis://localhost:6379"),
        
        # Session 配置
        "SESSION_SECRET_KEY": os.getenv("SESSION_SECRET_KEY", "session-secret-key"),
        "SESSION_EXPIRE_HOURS": int(os.getenv("SESSION_EXPIRE_HOURS", "8")),
        
        # Azure OpenAI 配置
        "AZURE_OPENAI_ENDPOINT": os.getenv("AZURE_OPENAI_ENDPOINT"),
        "AZURE_OPENAI_API_KEY": os.getenv("AZURE_OPENAI_API_KEY"),
        "AZURE_OPENAI_API_VERSION": os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01"),
        
        # Azure AI Search 配置
        "AZURE_SEARCH_ENDPOINT": os.getenv("AZURE_SEARCH_ENDPOINT"),
        "AZURE_SEARCH_API_KEY": os.getenv("AZURE_SEARCH_API_KEY"),
        "AZURE_SEARCH_INDEX_NAME": os.getenv("AZURE_SEARCH_INDEX_NAME", "promotions-index"),
        
        # CRM 整合配置
        #"CRM_API_BASE_URL": os.getenv("CRM_API_BASE_URL"),
        #"CRM_API_KEY": os.getenv("CRM_API_KEY"),
    })
    
    # CORS 設定
    app = cors(app, allow_origin="*", allow_methods=["GET", "POST", "PUT", "DELETE"])
    
    # 註冊中介軟體
    @app.before_request
    async def before_request():
        """每個請求前執行認證檢查"""
        await authenticate_session()
    
    # 註冊路由
    app.register_blueprint(auth.bp, url_prefix="/api/auth")
    app.register_blueprint(renewal_workflow.bp, url_prefix="/api/renewal-workflow")
    app.register_blueprint(statistics.bp, url_prefix="/api/statistics")
    
    # 健康檢查端點
    @app.route("/health")
    async def health_check():
        """健康檢查端點"""
        return jsonify({
            "status": "healthy",
            "service": "電信門市銷售助理系統",
            "version": "1.0.0"
        })
    
    # 根路徑
    @app.route("/")
    async def root():
        """根路徑"""
        return jsonify({
            "message": "電信門市銷售助理系統 API",
            "version": "1.0.0",
            "docs": "/docs",
            "health": "/health"
        })
    
    # 全域異常處理
    @app.errorhandler(APIException)
    async def handle_api_exception(error: APIException):
        """處理自定義 API 異常"""
        logger.error("API 異常", error=str(error), status_code=error.status_code)
        return jsonify({
            "error": error.message,
            "status_code": error.status_code
        }), error.status_code
    
    @app.errorhandler(Exception)
    async def handle_unexpected_exception(error: Exception):
        """處理未預期的異常"""
        logger.error("未預期的異常", error=str(error), type=type(error).__name__)
        return jsonify({
            "error": "Internal server error",
            "status_code": 500
        }), 500
    
    # 應用程式啟動/關閉事件
    @app.before_serving
    async def startup():
        """應用程式啟動時初始化"""
        logger.info("🚀 應用程式啟動中...")
        
        # 初始化資料庫連線
        db_manager = DatabaseManager()
        await db_manager.initialize()
        app.db_manager = db_manager
        
        # 初始化 Redis 連線
        redis_manager = RedisManager()
        await redis_manager.initialize()
        app.redis_manager = redis_manager
        
        logger.info("✅ 應用程式啟動完成")
    
    @app.after_serving
    async def shutdown():
        """應用程式關閉時清理"""
        logger.info("🛑 應用程式關閉中...")
        
        # 關閉資料庫連線
        if hasattr(app, 'db_manager'):
            await app.db_manager.close()
        
        # 關閉 Redis 連線
        if hasattr(app, 'redis_manager'):
            await app.redis_manager.close()
        
        logger.info("✅ 應用程式關閉完成")
    
    # 立即初始化（開發模式）
    async def init_services():
        """立即初始化服務"""
        logger.info("🚀 立即初始化服務...")
        
        # 初始化資料庫連線
        db_manager = DatabaseManager()
        await db_manager.initialize()
        app.db_manager = db_manager
        
        # 初始化 Redis 連線
        redis_manager = RedisManager()
        await redis_manager.initialize()
        app.redis_manager = redis_manager
        
        logger.info("✅ 服務初始化完成")
    
    # 在開發模式下立即初始化
    import asyncio
    try:
        asyncio.run(init_services())
    except Exception as e:
        logger.error("服務初始化失敗", error=str(e))
    
    return app