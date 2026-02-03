@echo off
REM OAuth功能测试运行脚本 (Windows)

echo ================================
echo OAuth功能单元测试
echo ================================
echo.

REM 检查是否安装了测试依赖
echo 检查测试依赖...
pip show pytest >nul 2>&1
if errorlevel 1 (
    echo 未安装测试依赖，正在安装...
    pip install -r requirements-test.txt
)

echo.
echo 开始运行测试...
echo.

REM 运行测试
if "%1"=="coverage" (
    REM 运行测试并生成覆盖率报告
    echo 运行测试并生成覆盖率报告...
    pytest --cov=app --cov-report=html --cov-report=term-missing
    echo.
    echo 覆盖率报告已生成: htmlcov\index.html
) else if "%1"=="service" (
    REM 只运行服务测试
    echo 运行OAuth服务测试...
    pytest tests\test_oauth_service.py -v
) else if "%1"=="api" (
    REM 只运行API测试
    echo 运行OAuth API测试...
    pytest tests\test_oauth_api.py -v
) else if "%1"=="verbose" (
    REM 详细输出
    echo 运行测试（详细输出）...
    pytest -v -s
) else (
    REM 运行所有测试
    echo 运行所有测试...
    pytest -v
)

echo.
echo ================================
echo 测试完成
echo ================================
pause
