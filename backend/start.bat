@echo off
echo ====================================
echo Fishpool 客户池管理系统 - 后端启动
echo ====================================
echo.

REM 检查虚拟环境
if not exist "venv\" (
    echo [1/5] 创建虚拟环境...
    python -m venv venv
    echo 虚拟环境创建完成！
    echo.
) else (
    echo [1/5] 虚拟环境已存在
    echo.
)

REM 激活虚拟环境
echo [2/5] 激活虚拟环境...
call venv\Scripts\activate.bat
echo.

REM 安装依赖
echo [3/5] 安装依赖包...
pip install -r requirements.txt
echo.

REM 执行迁移
echo [4/5] 执行数据库迁移...
python manage.py makemigrations
python manage.py migrate
echo.

REM 启动服务器
echo [5/5] 启动开发服务器...
echo.
echo 服务器将在 http://127.0.0.1:8000/ 启动
echo 管理后台: http://127.0.0.1:8000/admin/
echo API文档: http://127.0.0.1:8000/api/
echo.
echo 按 Ctrl+C 停止服务器
echo.
python manage.py runserver

pause
