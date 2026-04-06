-- BabyNote 数据库架构
-- 在 Supabase SQL Editor 中运行此脚本

-- 创建记录表
CREATE TABLE IF NOT EXISTS records (
  id BIGSERIAL PRIMARY KEY,
  type TEXT NOT NULL,          -- 'feeding', 'diaper', 'bathing', 'changing', 'nail_cutting' 等
  user_id TEXT,                -- 用户标识
  user_name TEXT,              -- 用户昵称
  detail TEXT,                 -- 额外信息（如奶量、尿布类型等）
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 启用 Row Level Security (可选)
ALTER TABLE records ENABLE ROW LEVEL SECURITY;

-- 创建策略：允许所有人读取和插入
DROP POLICY IF EXISTS "允许所有人读取" ON records;
CREATE POLICY "允许所有人读取" ON records
  FOR SELECT USING (true);

DROP POLICY IF EXISTS "允许所有人插入" ON records;
CREATE POLICY "允许所有人插入" ON records
  FOR INSERT WITH CHECK (true);

-- 创建索引加速查询
CREATE INDEX IF NOT EXISTS idx_records_created_at ON records(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_records_type ON records(type);

-- 插入测试数据（可选）
-- INSERT INTO records (type, user_name) VALUES 
--   ('feeding', '妈妈'),
--   ('diaper', '爸爸'),
--   ('feeding', '妈妈');
