"""
Redis 管理器 - Redis 連線與快取管理
"""
import json
from typing import Optional, Any, Dict, List, Union
import redis.asyncio as redis
import structlog
from datetime import timedelta

logger = structlog.get_logger()

class RedisManager:
    """Redis 管理器"""
    
    def __init__(self):
        self.redis: Optional[redis.Redis] = None
        self.url: Optional[str] = None
    
    async def initialize(self, url: str = "redis://localhost:6379"):
        """初始化 Redis 連線"""
        self.url = url
        
        try:
            # 建立 Redis 連線
            self.redis = redis.from_url(
                url,
                encoding="utf-8",
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True
            )
            
            # 測試連線
            await self.redis.ping()
            
            logger.info("✅ Redis 連線初始化成功", url=url)
            
        except Exception as e:
            logger.warning(f"⚠️ Redis 連線失敗，使用模擬快取: {e}")
            self.redis = MockRedis()
    
    async def get(self, key: str) -> Optional[str]:
        """取得值"""
        try:
            return await self.redis.get(key)
        except Exception as e:
            logger.error("Redis GET 錯誤", key=key, error=str(e))
            return None
    
    async def set(self, key: str, value: Union[str, Dict, List], 
                  ex: Optional[int] = None) -> bool:
        """設定值"""
        try:
            if isinstance(value, (dict, list)):
                value = json.dumps(value, ensure_ascii=False)
            
            return await self.redis.set(key, value, ex=ex)
        except Exception as e:
            logger.error("Redis SET 錯誤", key=key, error=str(e))
            return False
    
    async def get_json(self, key: str) -> Optional[Dict]:
        """取得 JSON 值"""
        try:
            value = await self.get(key)
            if value:
                return json.loads(value)
            return None
        except (json.JSONDecodeError, Exception) as e:
            logger.error("Redis GET JSON 錯誤", key=key, error=str(e))
            return None
    
    async def set_json(self, key: str, value: Dict, ex: Optional[int] = None) -> bool:
        """設定 JSON 值"""
        return await self.set(key, value, ex=ex)
    
    async def delete(self, key: str) -> bool:
        """刪除鍵"""
        try:
            result = await self.redis.delete(key)
            return result > 0
        except Exception as e:
            logger.error("Redis DELETE 錯誤", key=key, error=str(e))
            return False
    
    async def exists(self, key: str) -> bool:
        """檢查鍵是否存在"""
        try:
            return await self.redis.exists(key)
        except Exception as e:
            logger.error("Redis EXISTS 錯誤", key=key, error=str(e))
            return False
    
    async def expire(self, key: str, seconds: int) -> bool:
        """設定過期時間"""
        try:
            return await self.redis.expire(key, seconds)
        except Exception as e:
            logger.error("Redis EXPIRE 錯誤", key=key, error=str(e))
            return False
    
    async def sadd(self, key: str, *values) -> int:
        """集合新增元素"""
        try:
            return await self.redis.sadd(key, *values)
        except Exception as e:
            logger.error("Redis SADD 錯誤", key=key, error=str(e))
            return 0
    
    async def srem(self, key: str, *values) -> int:
        """集合移除元素"""
        try:
            return await self.redis.srem(key, *values)
        except Exception as e:
            logger.error("Redis SREM 錯誤", key=key, error=str(e))
            return 0
    
    async def smembers(self, key: str) -> set:
        """取得集合所有成員"""
        try:
            return await self.redis.smembers(key)
        except Exception as e:
            logger.error("Redis SMEMBERS 錯誤", key=key, error=str(e))
            return set()
    
    async def close(self):
        """關閉 Redis 連線"""
        if self.redis and hasattr(self.redis, 'close'):
            await self.redis.close()
            logger.info("✅ Redis 連線已關閉")

class MockRedis:
    """模擬 Redis（開發用）"""
    
    def __init__(self):
        self.data = {}
        self.sets = {}
    
    async def ping(self):
        """模擬 ping"""
        return True
    
    async def get(self, key: str) -> Optional[str]:
        """模擬 GET"""
        logger.debug("🔧 模擬 Redis GET", key=key)
        return self.data.get(key)
    
    async def set(self, key: str, value: str, ex: Optional[int] = None) -> bool:
        """模擬 SET"""
        logger.debug("🔧 模擬 Redis SET", key=key, ex=ex)
        self.data[key] = value
        return True
    
    async def delete(self, key: str) -> int:
        """模擬 DELETE"""
        logger.debug("🔧 模擬 Redis DELETE", key=key)
        if key in self.data:
            del self.data[key]
            return 1
        return 0
    
    async def exists(self, key: str) -> bool:
        """模擬 EXISTS"""
        return key in self.data
    
    async def expire(self, key: str, seconds: int) -> bool:
        """模擬 EXPIRE"""
        logger.debug("🔧 模擬 Redis EXPIRE", key=key, seconds=seconds)
        return True
    
    async def sadd(self, key: str, *values) -> int:
        """模擬 SADD"""
        if key not in self.sets:
            self.sets[key] = set()
        count = 0
        for value in values:
            if value not in self.sets[key]:
                self.sets[key].add(value)
                count += 1
        return count
    
    async def srem(self, key: str, *values) -> int:
        """模擬 SREM"""
        if key not in self.sets:
            return 0
        count = 0
        for value in values:
            if value in self.sets[key]:
                self.sets[key].remove(value)
                count += 1
        return count
    
    async def smembers(self, key: str) -> set:
        """模擬 SMEMBERS"""
        return self.sets.get(key, set())