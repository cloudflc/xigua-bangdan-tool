# 榜单制作工具 - 部署指南

## 方式一：部署到 Vercel（最简单，推荐）

### 步骤：

1. **注册 Vercel 账号**
   - 访问 https://vercel.com
   - 使用 GitHub 账号登录

2. **上传代码到 GitHub**
   - 创建新仓库
   - 将 `榜单制作` 文件夹中的以下文件上传：
     ```
     app.py
     requirements.txt
     vercel.json
     README.md
     templates/
     ```

3. **在 Vercel 导入项目**
   - 访问 https://vercel.com/new
   - 点击 "Import Project"
   - 选择刚才创建的 GitHub 仓库
   - Vercel 会自动识别为 Python/Flask 项目
   - 点击 "Deploy"

4. **完成！**
   - 部署完成后会得到一个 URL，例如：`https://xxx.vercel.app`

---

## 方式二：部署到 Cloudflare Workers

### 步骤：

1. **安装 Wrangler CLI**
```bash
npm install -g wrangler
```

2. **登录 Cloudflare**
```bash
wrangler login
```

3. **创建项目**
```bash
wrangler init 榜单制作工具
```

4. **配置 wrangler.toml**
```toml
name = "榜单制作工具"
main = "app.py"
compatibility_date = "2024-01-01"

[build]
command = "pip install flask pandas openpyxl -t ."
```

5. **部署**
```bash
wrangler deploy
```

---

## 方式三：本地运行（开发用）

```bash
pip install -r requirements.txt
python app.py
```

然后访问 http://localhost:5000
