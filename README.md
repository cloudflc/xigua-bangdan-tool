# 榜单制作工具 - Web版本

## 本地运行

```bash
pip install -r requirements.txt
python app.py
```

然后访问 http://localhost:5000

## 部署到 Cloudflare Pages

### 方法一：使用 Cloudflare Workers + Pages（推荐）

1. **安装 Wrangler CLI**
```bash
npm install -g wrangler
```

2. **登录 Cloudflare**
```bash
wrangler login
```

3. **创建 Worker 项目**
```bash
wrangler init榜单制作工具
```

4. **配置 wrangler.toml**
```toml
name = "榜单制作工具"
main = "app.py"
compatibility_date = "2024-01-01"

[build]
command = "pip install -r requirements.txt -t ."
```

5. **部署**
```bash
wrangler deploy
```

### 方法二：使用 Docker 部署

1. **构建 Docker 镜像**
```bash
docker build -t 榜单制作工具 .
```

2. **运行容器**
```bash
docker run -p 5000:5000 榜单制作工具
```

### 方法三：上传到 GitHub 部署到 Vercel（更简单）

1. 将代码推送到 GitHub
2. 访问 https://vercel.com
3. 导入项目
4. Vercel 会自动识别为 Flask 项目并部署
