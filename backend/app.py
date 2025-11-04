"""
電信門市銷售助理系統 - 應用程式入口點
"""
if __name__ == "__main__":
    import hypercorn.asyncio
    import hypercorn.config
    import asyncio
    from app import create_app
    
    # 建立應用程式實例
    app = create_app()
    
    # 開發環境配置
    config = hypercorn.config.Config()
    config.bind = ["localhost:8000"]
    config.debug = True
    config.reload = True
    
    print("🚀 啟動電信門市銷售助理系統...")
    print("📍 API 端點: http://localhost:8000")
    print("🔍 健康檢查: http://localhost:8000/health")
    print("📖 API 文件: http://localhost:8000/docs")
    
    # 啟動伺服器
    asyncio.run(hypercorn.asyncio.serve(app, config))