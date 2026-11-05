# P1 · 客户台账

## 运行

```powershell
cd 'D:\My_documents\3.计算机专业学习笔记\创业助手\项目\P1'
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

浏览器打开 `http://127.0.0.1:8000/customers`，接口文档在 `http://127.0.0.1:8000/docs`。

## 测试

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

## 目录

- `app/main.py`：FastAPI 入口与路由
- `app/db.py`：SQLite 数据访问
- `app/templates/`：页面模板
- `app/static/`：样式
- `tests/`：验收测试
