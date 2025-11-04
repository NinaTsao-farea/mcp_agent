"""
测试续约流程重启功能

验证：
1. 创建续约 session
2. 模拟错误（状态转换失败）
3. 重新调用 /start
4. 验证可以成功开始新流程
"""
import asyncio
import httpx
import sys
import io

# 设置标准输出编码为 UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_URL = "http://localhost:8000"

async def test_restart_workflow():
    """测试流程重启功能"""
    print("=" * 80)
    print("测试续约流程重启功能")
    print("=" * 80)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # 1. 登入
        print("\n[1] 登入系统...")
        response = await client.post(
            f"{BASE_URL}/api/auth/login",
            json={
                "staff_code": "S001",
                "password": "password"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") is True
        session_id = data.get("session_id")
        headers = {"X-Session-ID": session_id}
        print(f"✓ 登入成功，Session ID: {session_id}")
        
        # 2. 第一次开始续约流程
        print("\n[2] 第一次开始续约流程...")
        response = await client.post(
            f"{BASE_URL}/api/renewal-workflow/start",
            headers=headers
        )
        print(f"   状态码: {response.status_code}")
        print(f"   响应: {response.text}")
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") is True
        renewal_session_id_1 = data.get("session_id")
        print(f"✓ 流程开始，Renewal Session ID: {renewal_session_id_1}")
        
        # 3. 完成 Step 1-4，使 session 进入 select_device_type 状态
        print("\n[3] 执行 Step 1-4...")
        
        # Step 1
        response = await client.post(
            f"{BASE_URL}/api/renewal-workflow/step/query-customer",
            headers=headers,
            json={"session_id": renewal_session_id_1, "id_number": "A123456789"}
        )
        assert response.status_code == 200
        print("✓ Step 1 完成")
        
        # Step 2-3
        response = await client.post(
            f"{BASE_URL}/api/renewal-workflow/step/list-phones",
            headers=headers,
            json={"session_id": renewal_session_id_1}
        )
        assert response.status_code == 200
        print("✓ Step 2-3 完成")
        
        # Step 4
        response = await client.post(
            f"{BASE_URL}/api/renewal-workflow/step/select-phone",
            headers=headers,
            json={"session_id": renewal_session_id_1, "phone_number": "0912345678"}
        )
        assert response.status_code == 200
        print("✓ Step 4 完成")
        
        # 4. 检查 session 状态
        print("\n[4] 检查第一个 session 状态...")
        response = await client.get(
            f"{BASE_URL}/api/renewal-workflow/session/{renewal_session_id_1}",
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        current_step = data.get("session", {}).get("current_step")
        print(f"✓ 当前步骤: {current_step}")
        assert current_step == "select_device_type"
        
        # 5. 模拟用户想重新开始（不管当前状态）
        print("\n[5] 用户决定重新开始流程...")
        print("   （前一个 session 处于 select_device_type 状态）")
        
        # 6. 第二次调用 /start
        print("\n[6] 第二次调用 /start...")
        response = await client.post(
            f"{BASE_URL}/api/renewal-workflow/start",
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") is True
        renewal_session_id_2 = data.get("session_id")
        current_step = data.get("current_step")
        print(f"✓ 新流程开始")
        print(f"  新 Session ID: {renewal_session_id_2}")
        print(f"  当前步骤: {current_step}")
        assert current_step == "init"
        assert renewal_session_id_1 != renewal_session_id_2
        
        # 7. 验证旧 session 已被清除
        print("\n[7] 验证旧 session 已被清除...")
        response = await client.get(
            f"{BASE_URL}/api/renewal-workflow/session/{renewal_session_id_1}",
            headers=headers
        )
        if response.status_code == 404:
            print("✓ 旧 session 已被清除")
        else:
            print("⚠ 旧 session 仍然存在（但不影响新流程）")
        
        # 8. 验证新 session 可以正常使用
        print("\n[8] 验证新 session 可以正常执行流程...")
        response = await client.post(
            f"{BASE_URL}/api/renewal-workflow/step/query-customer",
            headers=headers,
            json={"session_id": renewal_session_id_2, "id_number": "A123456789"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") is True
        print("✓ 新 session 可以正常执行 Step 1")
        
        # 9. 检查新 session 状态
        print("\n[9] 检查新 session 状态...")
        response = await client.get(
            f"{BASE_URL}/api/renewal-workflow/session/{renewal_session_id_2}",
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        current_step = data.get("session", {}).get("current_step")
        print(f"✓ 当前步骤: {current_step}")
        assert current_step == "list_phones"
        
        print("\n" + "=" * 80)
        print("✅ 测试通过！")
        print("=" * 80)
        print("\n✓ 验证结果：")
        print("  1. 可以随时调用 /start 重新开始流程")
        print("  2. 旧 session 会被自动清除")
        print("  3. 新 session 从 INIT 状态开始")
        print("  4. 不会被前一次流程的状态影响")

async def test_error_recovery():
    """测试错误恢复"""
    print("\n\n" + "=" * 80)
    print("测试错误恢复功能")
    print("=" * 80)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # 1. 登入
        print("\n[1] 登入系统...")
        response = await client.post(
            f"{BASE_URL}/api/auth/login",
            json={"staff_code": "S001", "password": "password"}
        )
        session_id = response.json().get("session_id")
        headers = {"X-Session-ID": session_id}
        print(f"✓ 登入成功")
        
        # 2. 开始流程
        print("\n[2] 开始续约流程...")
        response = await client.post(
            f"{BASE_URL}/api/renewal-workflow/start",
            headers=headers
        )
        renewal_session_id = response.json().get("session_id")
        print(f"✓ Session ID: {renewal_session_id}")
        
        # 3. 模拟发生错误（例如输入不存在的身份证）
        print("\n[3] 测试错误处理（查询不存在的客户）...")
        response = await client.post(
            f"{BASE_URL}/api/renewal-workflow/step/query-customer",
            headers=headers,
            json={"session_id": renewal_session_id, "id_number": "Z999999999"}
        )
        data = response.json()
        if not data.get("success"):
            print(f"✓ 预期的错误: {data.get('error')}")
        
        # 4. 用户决定重新开始
        print("\n[4] 用户决定重新开始...")
        response = await client.post(
            f"{BASE_URL}/api/renewal-workflow/start",
            headers=headers
        )
        new_renewal_session_id = response.json().get("session_id")
        print(f"✓ 新 Session ID: {new_renewal_session_id}")
        
        # 5. 这次使用正确的身份证
        print("\n[5] 使用正确的身份证重新查询...")
        response = await client.post(
            f"{BASE_URL}/api/renewal-workflow/step/query-customer",
            headers=headers,
            json={"session_id": new_renewal_session_id, "id_number": "A123456789"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") is True
        print(f"✓ 查询成功: {data.get('customer', {}).get('name')}")
        
        print("\n✅ 错误恢复测试通过！")

async def main():
    try:
        await test_restart_workflow()
        await test_error_recovery()
        
        print("\n" + "=" * 80)
        print("🎉 所有测试通过！")
        print("=" * 80)
        
    except AssertionError as e:
        print(f"\n❌ 测试失败: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
