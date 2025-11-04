-- 電信門市銷售助理系統 - 測試資料
-- 建立日期: 2025-10-13
-- 說明: 建立開發和測試用的基礎資料

-- ========================================
-- 1. 門市資料
-- ========================================
INSERT INTO stores (store_id, store_name, store_address, store_phone, region) VALUES
('STORE_A', '台北信義門市', '台北市信義區信義路五段7號', '02-2345-6789', '台北區'),
('STORE_B', '新北板橋門市', '新北市板橋區文化路一段188號', '02-2987-6543', '新北區'),
('STORE_C', '桃園中壢門市', '桃園市中壢區中正路123號', '03-4567-890', '桃園區'),
('STORE_D', '台中西屯門市', '台中市西屯區台灣大道三段99號', '04-2234-5678', '台中區'),
('STORE_E', '高雄左營門市', '高雄市左營區博愛二路777號', '07-3456-789', '高雄區');

-- ========================================
-- 2. 員工資料 (密碼都是 "password")
-- ========================================
-- 密碼雜湊: $2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj6WUCU6VtHy (password)
INSERT INTO staff (staff_id, staff_code, name, role, store_id, password_hash, email, phone) VALUES
('STAFF001', 'S001', '王小明', 'Sales', 'STORE_A', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj6WUCU6VtHy', 'wang@example.com', '0912-345-678'),
('STAFF002', 'S002', '李美華', 'Sales', 'STORE_A', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj6WUCU6VtHy', 'li@example.com', '0923-456-789'),
('STAFF003', 'S003', '張志強', 'Manager', 'STORE_A', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj6WUCU6VtHy', 'zhang@example.com', '0934-567-890'),
('STAFF004', 'S004', '陳淑芬', 'Sales', 'STORE_B', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj6WUCU6VtHy', 'chen@example.com', '0945-678-901'),
('STAFF005', 'S005', '林建國', 'Manager', 'STORE_B', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj6WUCU6VtHy', 'lin@example.com', '0956-789-012'),
('ADMIN001', 'A001', '系統管理員', 'Admin', 'STORE_A', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj6WUCU6VtHy', 'admin@example.com', '0967-890-123');

-- ========================================
-- 3. 客戶資料
-- ========================================
INSERT INTO customers (customer_id, id_number, name, phone, email, is_company_customer, credit_rating) VALUES
('C123456', 'A123456789', '張三', '0912-111-111', 'zhang3@email.com', 1, 'GOOD'),
('C123457', 'B234567890', '李四', '0923-222-222', 'li4@email.com', 1, 'EXCELLENT'),
('C123458', 'C345678901', '王五', '0934-333-333', 'wang5@email.com', 1, 'GOOD'),
('C123459', 'D456789012', '趙六', '0945-444-444', 'zhao6@email.com', 0, 'POOR'),
('C123460', 'E567890123', '錢七', '0956-555-555', 'qian7@email.com', 1, 'GOOD');

-- ========================================
-- 4. 門號合約資料
-- ========================================
INSERT INTO phone_contracts (contract_id, customer_id, phone_number, current_plan, monthly_fee, contract_start_date, contract_end_date, status) VALUES
('CONTRACT001', 'C123456', '0912-111-111', '4G 688方案', 688, DATE '2023-01-15', DATE '2025-01-14', 'ACTIVE'),
('CONTRACT002', 'C123456', '0912-111-112', '5G 1399方案', 1399, DATE '2023-03-20', DATE '2025-03-19', 'ACTIVE'),
('CONTRACT003', 'C123457', '0923-222-222', '5G 999方案', 999, DATE '2023-06-10', DATE '2025-06-09', 'ACTIVE'),
('CONTRACT004', 'C123458', '0934-333-333', '4G 488方案', 488, DATE '2022-12-01', DATE '2024-11-30', 'ACTIVE'),
('CONTRACT005', 'C123460', '0956-555-555', '5G 1599方案', 1599, DATE '2023-08-15', DATE '2025-08-14', 'ACTIVE');

-- ========================================
-- 5. 促銷方案資料
-- ========================================
INSERT INTO promotions (promotion_id, promotion_name, description, plan_type, monthly_fee, data_allowance, voice_minutes, sms_count, contract_months, eligibility_rules, start_date, end_date) VALUES
('PROMO001', '5G 飆速999', '5G網路，30GB大流量，網內免費通話', '5G', 999, '30GB', '網內免費', '免費', 24, '{"min_months_on_network": 6, "min_monthly_spend": 500, "credit_rating": ["GOOD", "EXCELLENT"]}', DATE '2025-01-01', DATE '2025-12-31'),
('PROMO002', '學生專案588', '學生限定優惠方案，20GB流量', '4G', 588, '20GB', '500分鐘', '100則', 12, '{"student_discount": true, "age_max": 25}', DATE '2025-01-01', DATE '2025-06-30'),
('PROMO003', '5G 無限上網1299', '5G無限流量，適合重度使用者', '5G', 1299, 'Unlimited', '網內免費', '免費', 30, '{"min_months_on_network": 12, "min_monthly_spend": 800}', DATE '2025-01-01', DATE '2025-12-31'),
('PROMO004', '家庭共享1599', '家庭共享方案，最多4門號', '5G', 1599, '80GB共享', '網內免費', '免費', 24, '{"family_plan": true, "min_lines": 2}', DATE '2025-01-01', DATE '2025-12-31'),
('PROMO005', '長青專案399', '55歲以上長者專案', '4G', 399, '10GB', '300分鐘', '50則', 12, '{"age_min": 55, "senior_discount": true}', DATE '2025-01-01', DATE '2025-12-31');

-- ========================================
-- 6. 手機裝置資料
-- ========================================
INSERT INTO devices (device_id, device_name, brand, model, os_type, price, colors, specifications, is_recommended) VALUES
('DEVICE001', 'iPhone 15', 'Apple', 'iPhone 15', 'iOS', 28900, '["Pink", "Yellow", "Green", "Blue", "Black"]', '{"screen": "6.1吋", "storage": "128GB", "camera": "48MP", "battery": "3349mAh"}', 1),
('DEVICE002', 'iPhone 15 Pro', 'Apple', 'iPhone 15 Pro', 'iOS', 35900, '["Natural Titanium", "Blue Titanium", "White Titanium", "Black Titanium"]', '{"screen": "6.1吋", "storage": "128GB", "camera": "48MP Pro", "battery": "3274mAh"}', 1),
('DEVICE003', 'Samsung Galaxy S24', 'Samsung', 'Galaxy S24', 'Android', 25900, '["Onyx Black", "Marble Gray", "Cobalt Violet", "Amber Yellow"]', '{"screen": "6.2吋", "storage": "256GB", "camera": "50MP", "battery": "4000mAh"}', 1),
('DEVICE004', 'Samsung Galaxy S24 Ultra', 'Samsung', 'Galaxy S24 Ultra', 'Android', 42900, '["Titanium Black", "Titanium Gray", "Titanium Violet", "Titanium Yellow"]', '{"screen": "6.8吋", "storage": "256GB", "camera": "200MP", "battery": "5000mAh"}', 1),
('DEVICE005', 'Google Pixel 8', 'Google', 'Pixel 8', 'Android', 21900, '["Obsidian", "Snow", "Rose"]', '{"screen": "6.2吋", "storage": "128GB", "camera": "50MP", "battery": "4575mAh"}', 0);

-- ========================================
-- 7. 範例續約會話記錄
-- ========================================
INSERT INTO renewal_sessions (session_id, staff_id, customer_id, phone_number, current_step, status, is_sale_confirmed, session_data) VALUES
('renewal_S001_abc123', 'STAFF001', 'C123456', '0912-111-111', 'completed', 'COMPLETED', 1, '{"id_number": "A123456789", "selected_device": "DEVICE001", "selected_plan": "PROMO001", "total_amount": 28900}'),
('renewal_S001_def456', 'STAFF001', 'C123457', '0923-222-222', 'select_plan', 'IN_PROGRESS', 0, '{"id_number": "B234567890", "current_step": "select_plan"}'),
('renewal_S002_ghi789', 'STAFF002', 'C123458', '0934-333-333', 'completed', 'COMPLETED', 0, '{"id_number": "C345678901", "cancelled_reason": "客戶考慮中"}');

-- ========================================
-- 8. AI 使用記錄範例
-- ========================================
INSERT INTO ai_usage_logs (staff_id, session_id, usage_type, prompt_text, response_text, prompt_tokens, completion_tokens, total_tokens, cost_amount) VALUES
('STAFF001', 'renewal_S001_abc123', 'comparison', '比較 5G 飆速999 和 5G 無限上網1299 方案', '兩個方案的主要差異在於...', 50, 150, 200, 0.004),
('STAFF001', 'renewal_S001_def456', 'chat', '客戶詢問是否有學生優惠', '我們有學生專案588，適合25歲以下的學生...', 30, 80, 110, 0.0022),
('STAFF002', 'renewal_S002_ghi789', 'recommendation', '為55歲客戶推薦適合方案', '建議長青專案399，專為55歲以上客戶設計...', 40, 120, 160, 0.0032);

-- ========================================
-- 9. 客服記錄範例
-- ========================================
INSERT INTO customer_service_logs (staff_id, customer_id, service_type, service_result, notes, service_duration) VALUES
('STAFF001', 'C123456', 'renewal', 'completed', '客戶續約iPhone 15 + 5G飆速999方案，服務順利', 45),
('STAFF001', 'C123457', 'inquiry', 'pending', '客戶詢問方案詳情，尚在考慮中', 25),
('STAFF002', 'C123458', 'renewal', 'cancelled', '客戶暫時不續約，要回家討論', 30);

-- ========================================
-- 10. 每日統計範例 (近7天)
-- ========================================
INSERT INTO daily_staff_statistics (staff_id, stat_date, login_count, total_login_duration, customers_served, sessions_started, sessions_completed, sales_confirmed, ai_usage_count, total_ai_tokens, total_ai_cost) VALUES
('STAFF001', DATE '2025-10-13', 1, 480, 3, 3, 2, 1, 5, 500, 0.01),
('STAFF001', DATE '2025-10-12', 1, 450, 2, 2, 1, 1, 3, 300, 0.006),
('STAFF001', DATE '2025-10-11', 1, 420, 4, 4, 3, 2, 8, 800, 0.016),
('STAFF002', DATE '2025-10-13', 1, 460, 2, 2, 1, 0, 2, 200, 0.004),
('STAFF002', DATE '2025-10-12', 1, 440, 3, 3, 2, 1, 4, 400, 0.008),
('STAFF003', DATE '2025-10-13', 1, 300, 0, 0, 0, 0, 0, 0, 0); -- 主管通常不直接服務客戶

-- ========================================
-- 建立一些登入記錄
-- ========================================
INSERT INTO login_logs (staff_id, login_time, logout_time, ip_address, user_agent, session_duration) VALUES
('STAFF001', SYSDATE - 1, SYSDATE - 1 + (480/1440), '192.168.1.100', 'Mozilla/5.0 Chrome/119.0', 480),
('STAFF001', SYSDATE - 2, SYSDATE - 2 + (450/1440), '192.168.1.100', 'Mozilla/5.0 Chrome/119.0', 450),
('STAFF002', SYSDATE - 1, SYSDATE - 1 + (460/1440), '192.168.1.101', 'Mozilla/5.0 Chrome/119.0', 460),
('STAFF003', SYSDATE - 1, SYSDATE - 1 + (300/1440), '192.168.1.102', 'Mozilla/5.0 Chrome/119.0', 300);

COMMIT;

-- ========================================
-- 驗證資料
-- ========================================

-- 檢查資料筆數
SELECT 'stores' as table_name, COUNT(*) as count FROM stores
UNION ALL
SELECT 'staff', COUNT(*) FROM staff
UNION ALL
SELECT 'customers', COUNT(*) FROM customers
UNION ALL
SELECT 'phone_contracts', COUNT(*) FROM phone_contracts
UNION ALL
SELECT 'promotions', COUNT(*) FROM promotions
UNION ALL
SELECT 'devices', COUNT(*) FROM devices
UNION ALL
SELECT 'renewal_sessions', COUNT(*) FROM renewal_sessions
UNION ALL
SELECT 'ai_usage_logs', COUNT(*) FROM ai_usage_logs
UNION ALL
SELECT 'customer_service_logs', COUNT(*) FROM customer_service_logs
UNION ALL
SELECT 'daily_staff_statistics', COUNT(*) FROM daily_staff_statistics
UNION ALL
SELECT 'login_logs', COUNT(*) FROM login_logs;

-- 顯示員工登入資訊
SELECT 
    staff_code,
    name,
    role,
    store_id,
    '密碼: password' as login_info
FROM staff
ORDER BY staff_code;