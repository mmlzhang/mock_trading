
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

### 项目配置
- 在settions.py中修改_token为自己的dingding webhook token
- 在constant中修改salt加密口令,确保安全

### 运行项目
`python application.py`


## 代码检查
```python
pip install tox

# 在项目目录下，即在tox.ini目录下运行tox

~/workSpace/mock_trading $ tox

```