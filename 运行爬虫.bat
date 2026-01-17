@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

:: 设置标题
title 湖南省律师协会知识库爬虫

:: 设置颜色
color 0A

:: 清屏
cls

echo ============================================================
echo           湖南省律师协会行业规范知识库爬虫
echo ============================================================
echo.
echo [功能说明]
echo   - 自动爬取行业规范、法律法规、业务指引等内容
echo   - 支持增量更新：自动检测新内容并征求确认
echo   - 首次运行会下载所有文章（约130篇，需5-15分钟）
echo.
echo [操作选项]
echo   1. 运行爬虫（检测并下载新内容）
echo   2. 查看知识库状态
echo   3. 查看使用说明
echo   4. 退出
echo.
echo ============================================================

:menu
set /p choice="请选择操作 (1-4): "

if "%choice%"=="1" goto run_crawler
if "%choice%"=="2" goto check_status
if "%choice%"=="3" goto show_help
if "%choice%"=="4" goto end
echo [错误] 无效选择，请输入 1-4
goto menu

:run_crawler
cls
echo ============================================================
echo [启动] 正在启动爬虫...
echo ============================================================
echo.

:: 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到Python，请先安装Python 3.10或更高版本
    echo.
    echo [下载地址] https://www.python.org/downloads/
    echo.
    pause
    goto menu
)

:: 检查依赖是否安装
echo [检查] 正在检查依赖库...
pip show requests >nul 2>&1
if errorlevel 1 (
    echo.
    echo [提示] 缺少必要的依赖库，正在自动安装...
    echo.
    pip install requests beautifulsoup4 lxml -q
    if errorlevel 1 (
        echo [错误] 依赖安装失败
        pause
        goto menu
    )
    echo [完成] 依赖安装成功
    echo.
)

:: 运行爬虫
echo [运行] 正在运行爬虫...
echo.
python "%~dp0hunan_lawyer_crawler.py"

echo.
echo ============================================================
echo [完成] 爬虫运行结束
echo ============================================================
echo.
pause
goto menu

:check_status
cls
echo ============================================================
echo           知识库状态检查
echo ============================================================
echo.

set "data_dir=%~dp0hunan_lawyer_data"

:: 检查数据目录是否存在
if not exist "%data_dir%" (
    echo [状态] 知识库尚未创建
    echo [提示] 请选择选项1运行爬虫下载知识库
    echo.
    pause
    goto menu
)

:: 统计各分类文件数量
set total=0
set categories=法律法规 行政文件 行业文件 业务指引 办事指南

echo [知识库目录] %data_dir%
echo.
echo [文件统计]
echo ------------------------------------------------------------

for %%c in (%categories%) do (
    set "folder=%data_dir%\%%c"
    set count=0
    if exist "!folder!" (
        for /f %%a in ('dir /b "!folder!\*.md" 2^>nul ^| find /c /v ""') do set count=%%a
    )
    echo   %%c: !count! 篇
    set /a total+=count
)

echo ------------------------------------------------------------
echo   [总计]: %total% 篇
echo.

:: 检查progress.json
if exist "%data_dir%\progress.json" (
    echo [进度] 已下载进度已保存
    echo [提示] 再次运行将只下载新增内容
) else (
    echo [警告] 未找到进度文件
)

echo.
echo [索引文件]
if exist "%data_dir%\索引.md" (
    echo   [存在] 索引.md
) else (
    echo   [缺失] 索引.md
)

echo.
echo ============================================================
pause
goto menu

:show_help
cls
echo ============================================================
echo           使用说明
echo ============================================================
echo.
echo [首次使用]
echo   1. 确保已安装Python 3.10或更高版本
echo   2. 选择选项1运行爬虫
echo   3. 等待下载完成（首次约需5-15分钟）
echo   4. 所有内容保存在 hunan_lawyer_data 文件夹
echo.
echo [日常更新]
echo   1. 定期运行此工具
echo   2. 如有新内容，会显示列表并征求确认
echo   3. 选择 y 下载新内容，n 取消，a 重新下载全部
echo.
echo [文件位置]
echo   - 知识库: %~dp0hunan_lawyer_data\
echo   - 爬虫脚本: %~dp0hunan_lawyer_crawler.py
echo   - 本启动器: %~dp0运行爬虫.bat
echo.
echo [常见问题]
echo   Q: 提示未安装Python？
echo   A: 访问 https://www.python.org/downloads/ 下载安装
echo.
echo   Q: 爬虫运行很慢？
echo   A: 正常现象，避免对服务器造成压力
echo.
echo   Q: 想要重新下载所有文件？
echo   A: 运行时选择 a (全部)
echo.
echo   Q: 可以只下载某个分类吗？
echo   A: 可以编辑 hunan_lawyer_crawler.py 中的 CATEGORIES 配置
echo.
echo ============================================================
pause
goto menu

:end
cls
echo [退出] 感谢使用！
timeout /t 2 >nul
exit /b 0
