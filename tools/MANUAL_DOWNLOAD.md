# 湖南律师网内容下载指南

## 方法一：使用Claude MCP webReader工具（推荐）

在Claude Code中使用以下命令：

```
# 使用webReader工具
webReader https://www.hnlx.org.cn/show_n.php?t=2&id=11637
```

然后将输出内容保存为Markdown文件。

## 方法二：手动复制粘贴

1. 访问湖南律师网：https://www.hnlx.org.cn
2. 进入"行业规范"栏目
3. 打开需要的文章
4. 全选复制内容
5. 粘贴到Markdown文件中

## 已知重要文章URL

### 行业规范
- 湖南省律师协会章程: https://www.hnlx.org.cn/show_n.php?t=2&id=11637
- 申请律师执业人员实习管理规则: https://www.hnlx.org.cn/show_n.php?t=2&id=11528
- 中华全国律师协会章程: https://www.hnlx.org.cn/show_n.php?t=2&id=9384
- 关于进一步规范律师服务收费的意见: https://www.hnlx.org.cn/show_n.php?t=1&id=8986
- 加强和规范律师事务所内部管理的规定: https://www.hnlx.org.cn/show_n.php?t=2&id=8959

### 法律法规
- 律师执业管理办法: https://www.hnlx.org.cn/show_n.php?t=8&id=8956

## 文件命名规范

所有文档使用Markdown格式，放在对应目录下：
- 01-法律法规/
- 02-行业规范/
- 03-执业指引/
- 04-行政文件/
- 05-办事指南/
- 06-地方规范/

## 快速下载脚本

如果想批量下载，可以逐个运行以下命令（在Claude Code中）：

### 法律法规

```
webReader https://www.hnlx.org.cn/show_n.php?t=8&id=8956
```


### 行业规范

```
webReader https://www.hnlx.org.cn/show_n.php?t=2&id=11637
```

```
webReader https://www.hnlx.org.cn/show_n.php?t=2&id=11528
```

```
webReader https://www.hnlx.org.cn/show_n.php?t=2&id=9384
```

```
webReader https://www.hnlx.org.cn/show_n.php?t=1&id=8986
```

```
webReader https://www.hnlx.org.cn/show_n.php?t=2&id=8959
```

