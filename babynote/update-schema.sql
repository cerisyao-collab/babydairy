-- 数据库更新脚本 - 添加 detail 字段
-- 如果表已存在，运行此脚本添加 detail 字段

-- 1. 添加 detail 字段（如果不存在）
ALTER TABLE records 
ADD COLUMN IF NOT EXISTS detail TEXT;

-- 2. 更新记录类型（可选，用于兼容旧数据）
-- 如果你有旧的 feeding 或 diaper 类型数据，可以保持不变
-- 新数据将使用更详细的类型：
-- - feeding_breast: 母乳
-- - feeding_formula: 奶粉
-- - diaper_urine: 小便
-- - diaper_stool: 大便
-- - diaper_both: 大小便

-- 3. 确认字段已添加
\d records

-- 示例数据
INSERT INTO records (type, user_name, detail) VALUES
  ('feeding_breast', '妈妈', '母乳'),
  ('feeding_formula', '爸爸', '150ml'),
  ('diaper_urine', '妈妈', 'urine'),
  ('diaper_stool', '爸爸', 'stool'),
  ('diaper_both', '妈妈', 'both');
