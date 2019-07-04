
## 模拟交易系统


### 安装依赖
```python
pip install -r requirements.txt
```

### 数据库配置
```sql
-- 设置postgres用户密码
ALTER USER {USER} PASSWORD '{PASSWORD}';

```

### 运行项目
`python application.py`


## 代码检查
```python
pip install tox

# 在项目目录下，即在tox.ini目录下运行tox

~/workSpace/mock_trading $ tox

```