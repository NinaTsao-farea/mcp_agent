"""
續約工作流程 Session 管理器
管理 Redis 中的續約流程狀態
"""
from typing import Dict, List, Optional, Any
from datetime import datetime
import secrets
import structlog
from enum import Enum

from .redis_manager import RedisManager

logger = structlog.get_logger()


class WorkflowStep(str, Enum):
    """工作流程步驟"""
    INIT = "init"
    QUERY_CUSTOMER = "query_customer"
    LIST_PHONES = "list_phones"
    SELECT_PHONE = "select_phone"
    CHECK_ELIGIBILITY = "check_eligibility"
    SELECT_DEVICE_TYPE = "select_device_type"
    SELECT_DEVICE_OS = "select_device_os"
    SELECT_DEVICE = "select_device"
    LIST_PLANS = "list_plans"
    COMPARE_PLANS = "compare_plans"
    CONFIRM = "confirm"
    COMPLETED = "completed"


class WorkflowSessionManager:
    """續約工作流程 Session 管理器"""
    
    # 狀態轉換規則
    TRANSITIONS = {
        WorkflowStep.INIT: [WorkflowStep.QUERY_CUSTOMER],
        WorkflowStep.QUERY_CUSTOMER: [WorkflowStep.LIST_PHONES],
        WorkflowStep.LIST_PHONES: [WorkflowStep.SELECT_PHONE],
        WorkflowStep.SELECT_PHONE: [WorkflowStep.CHECK_ELIGIBILITY],
        WorkflowStep.CHECK_ELIGIBILITY: [WorkflowStep.SELECT_DEVICE_TYPE],
        WorkflowStep.SELECT_DEVICE_TYPE: [WorkflowStep.SELECT_DEVICE_OS, WorkflowStep.LIST_PLANS],
        WorkflowStep.SELECT_DEVICE_OS: [WorkflowStep.SELECT_DEVICE],
        WorkflowStep.SELECT_DEVICE: [WorkflowStep.LIST_PLANS],
        WorkflowStep.LIST_PLANS: [WorkflowStep.COMPARE_PLANS, WorkflowStep.CONFIRM],
        WorkflowStep.COMPARE_PLANS: [WorkflowStep.LIST_PLANS, WorkflowStep.CONFIRM],
        WorkflowStep.CONFIRM: [WorkflowStep.COMPLETED]
    }
    
    def __init__(self, redis_manager: RedisManager):
        """初始化"""
        self.redis = redis_manager
        
    async def create_session(self, staff_id: str, clear_existing: bool = True) -> Dict[str, Any]:
        """
        建立新的續約工作流程 Session
        
        Args:
            staff_id: 員工 ID
            clear_existing: 是否清除該員工現有的續約 Session（預設：True）
            
        Returns:
            Session 資料
        """
        # 清除該員工現有的續約 Session
        if clear_existing:
            await self.clear_staff_sessions(staff_id)
        
        session_id = f"renewal_{staff_id}_{secrets.token_hex(16)}"
        
        session_data = {
            "session_id": session_id,
            "staff_id": staff_id,
            "current_step": WorkflowStep.INIT,
            "customer_selection": {},
            "chat_history": [],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        # 儲存到 Redis (TTL: 1 小時)
        await self.redis.set_json(
            f"renewal_session:{session_id}",
            session_data,
            ex=3600
        )
        
        # 將 session_id 加入員工的 session 集合
        await self.redis.redis.sadd(
            f"staff_renewal_sessions:{staff_id}",
            session_id
        )
        
        logger.info(
            "建立續約流程 Session",
            session_id=session_id,
            staff_id=staff_id,
            cleared_existing=clear_existing
        )
        
        return session_data
    
    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        取得 Session 資料
        
        Args:
            session_id: Session ID
            
        Returns:
            Session 資料，若不存在則返回 None
        """
        session_data = await self.redis.get_json(f"renewal_session:{session_id}")
        
        if not session_data:
            logger.warning("Session 不存在", session_id=session_id)
            
        return session_data
    
    async def update_session(
        self,
        session_id: str,
        updates: Dict[str, Any]
    ) -> bool:
        """
        更新 Session 資料
        
        Args:
            session_id: Session ID
            updates: 要更新的資料
            
        Returns:
            是否更新成功
        """
        session_data = await self.get_session(session_id)
        
        if not session_data:
            return False
        
        # 更新資料
        session_data.update(updates)
        session_data["updated_at"] = datetime.now().isoformat()
        
        # 儲存回 Redis
        await self.redis.set_json(
            f"renewal_session:{session_id}",
            session_data,
            ex=3600  # 重置 TTL
        )
        
        logger.info(
            "更新續約流程 Session",
            session_id=session_id,
            updates=list(updates.keys())
        )
        
        return True
    
    async def update_customer_selection(
        self,
        session_id: str,
        selection_data: Dict[str, Any]
    ) -> bool:
        """
        更新客戶選擇資料
        
        Args:
            session_id: Session ID
            selection_data: 客戶選擇資料
            
        Returns:
            是否更新成功
        """
        session_data = await self.get_session(session_id)
        
        if not session_data:
            return False
        
        # 更新 customer_selection
        session_data["customer_selection"].update(selection_data)
        session_data["updated_at"] = datetime.now().isoformat()
        
        # 儲存回 Redis
        await self.redis.set_json(
            f"renewal_session:{session_id}",
            session_data,
            ex=3600
        )
        
        logger.info(
            "更新客戶選擇資料",
            session_id=session_id,
            selection_keys=list(selection_data.keys())
        )
        
        return True
    
    async def transition_to_step(
        self,
        session_id: str,
        next_step: WorkflowStep
    ) -> bool:
        """
        轉換到下一個步驟
        
        Args:
            session_id: Session ID
            next_step: 下一個步驟
            
        Returns:
            是否轉換成功
            
        Raises:
            ValueError: 如果狀態轉換不合法
        """
        session_data = await self.get_session(session_id)
        
        if not session_data:
            error_msg = f"Session 不存在: {session_id}"
            logger.error("Session 不存在", session_id=session_id)
            raise ValueError(error_msg)
        
        current_step = WorkflowStep(session_data["current_step"])
        
        # 檢查狀態轉換是否合法
        if next_step not in self.TRANSITIONS.get(current_step, []):
            error_msg = f"非法的狀態轉換: {current_step} -> {next_step}"
            logger.error(
                "非法的狀態轉換",
                session_id=session_id,
                current_step=current_step,
                next_step=next_step
            )
            raise ValueError(error_msg)
        
        # 更新步驟（確保保存的是字串值）
        session_data["current_step"] = next_step.value
        session_data["updated_at"] = datetime.now().isoformat()
        
        logger.info(
            "準備儲存狀態轉換",
            session_id=session_id,
            from_step=current_step,
            to_step=next_step,
            to_step_value=next_step.value,
            current_step_in_data=session_data["current_step"]
        )
        
        # 儲存回 Redis
        await self.redis.set_json(
            f"renewal_session:{session_id}",
            session_data,
            ex=3600
        )
        
        # 驗證儲存結果
        saved_data = await self.get_session(session_id)
        logger.info(
            "狀態轉換完成",
            session_id=session_id,
            from_step=current_step,
            to_step=next_step,
            saved_current_step=saved_data.get("current_step") if saved_data else None
        )
        
        return True
    
    async def add_chat_message(
        self,
        session_id: str,
        role: str,
        content: str
    ) -> bool:
        """
        新增對話訊息
        
        Args:
            session_id: Session ID
            role: 角色 (user/assistant)
            content: 訊息內容
            
        Returns:
            是否新增成功
        """
        session_data = await self.get_session(session_id)
        
        if not session_data:
            return False
        
        # 新增訊息
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        
        session_data["chat_history"].append(message)
        session_data["updated_at"] = datetime.now().isoformat()
        
        # 儲存回 Redis
        await self.redis.set_json(
            f"renewal_session:{session_id}",
            session_data,
            ex=3600
        )
        
        logger.debug(
            "新增對話訊息",
            session_id=session_id,
            role=role,
            content_length=len(content)
        )
        
        return True
    
    async def delete_session(self, session_id: str) -> bool:
        """
        刪除 Session
        
        Args:
            session_id: Session ID
            
        Returns:
            是否刪除成功
        """
        session_data = await self.get_session(session_id)
        
        if not session_data:
            return False
        
        staff_id = session_data["staff_id"]
        
        # 從 Redis 刪除
        await self.redis.redis.delete(f"renewal_session:{session_id}")
        
        # 從員工 session 集合中移除
        await self.redis.redis.srem(
            f"staff_renewal_sessions:{staff_id}",
            session_id
        )
        
        logger.info(
            "刪除續約流程 Session",
            session_id=session_id,
            staff_id=staff_id
        )
        
        return True
    
    async def clear_staff_sessions(self, staff_id: str) -> int:
        """
        清除員工的所有續約 Session
        
        Args:
            staff_id: 員工 ID
            
        Returns:
            清除的 Session 數量
        """
        session_ids = await self.get_staff_sessions(staff_id)
        
        if not session_ids:
            return 0
        
        count = 0
        for session_id in session_ids:
            # 刪除 session 資料
            await self.redis.redis.delete(f"renewal_session:{session_id}")
            count += 1
        
        # 清空員工 session 集合
        await self.redis.redis.delete(f"staff_renewal_sessions:{staff_id}")
        
        logger.info(
            "清除員工所有續約 Session",
            staff_id=staff_id,
            count=count
        )
        
        return count
    
    async def get_staff_sessions(self, staff_id: str) -> List[str]:
        """
        取得員工的所有 Session ID
        
        Args:
            staff_id: 員工 ID
            
        Returns:
            Session ID 列表
        """
        session_ids = await self.redis.redis.smembers(
            f"staff_renewal_sessions:{staff_id}"
        )
        
        # Redis 返回的是 set 或空 set
        if not session_ids:
            return []
        
        # Redis 返回的是 bytes，需要解碼
        return [sid.decode('utf-8') if isinstance(sid, bytes) else sid for sid in session_ids]
    
    async def can_transition_to(
        self,
        session_id: str,
        next_step: WorkflowStep
    ) -> bool:
        """
        檢查是否可以轉換到指定步驟
        
        Args:
            session_id: Session ID
            next_step: 目標步驟
            
        Returns:
            是否可以轉換
        """
        session_data = await self.get_session(session_id)
        
        if not session_data:
            return False
        
        current_step = WorkflowStep(session_data["current_step"])
        
        return next_step in self.TRANSITIONS.get(current_step, [])
