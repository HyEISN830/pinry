# ![Pinry](https://raw.github.com/pinry/pinry/master/docs/src/imgs/logo-dark.png)

![NodeJS Build](https://github.com/pinry/pinry/actions/workflows/node.js.yml/badge.svg)
![Python Build](https://github.com/pinry/pinry/actions/workflows/pythonpackage.yml/badge.svg)
![Docker Image Version](https://img.shields.io/docker/v/getpinry/pinry?arch=amd64&style=flat&label=docker-amd64)
![Docker Pulls](https://img.shields.io/docker/pulls/getpinry/pinry)

The open-source core of Pinry, a tiling image board system for people
who want to save, tag, and share images, videos and webpages in an easy
to skim through format.

For more information ( screenshots and document ) visit [https://pinry.github.io/pinry/](https://pinry.github.io/pinry/).

## How to use
下面是一份可以直接放到 `README.md` 或 `DEPLOY.md` 里的部署说明模板。  
它覆盖了从 clone 源码、自定义配置、构建 Docker 镜像、Dockge 托管、Caddy 反代、创建管理员账号的完整流程。

你可以按自己的仓库名和域名稍微改一下。

---

# Pinry Custom Deployment Guide

本项目是基于 Pinry 的自定义版本，用于部署个人图片灵感墙 / 艺术画廊。

当前部署方式：

```text
Caddy 负责 HTTPS 和反向代理
Dockge 负责 Docker Compose 托管
Pinry 使用自定义 Docker 镜像
SQLite 数据库和媒体文件持久化到 /data
```

---

## 1. Clone 源码

建议将源码放在：

```bash
/opt/src/pinry
```

执行：

```bash
sudo mkdir -p /opt/src
sudo chown -R $USER:$USER /opt/src

cd /opt/src
git clone <你的仓库地址> pinry
cd /opt/src/pinry
```

例如：

```bash
git clone https://github.com/yourname/pinry-custom.git pinry
cd pinry
```

---

## 2. 准备本地配置文件

项目使用：

```text
pinry/settings/local_settings.py
```

作为本地运行配置。

如果文件不存在，从示例文件复制：

```bash
cd /opt/src/pinry
cp pinry/settings/local_settings.example.py pinry/settings/local_settings.py
```

编辑配置：

```bash
nano pinry/settings/local_settings.py
```

推荐配置示例：

```python
import os


STATIC_ROOT = '/data/static'
MEDIA_ROOT = os.path.join(STATIC_ROOT, 'media')

SECRET_KEY = "change-this-secret-key"

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ALLOWED_HOSTS = ['*']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': '/data/production.db',
    }
}

ALLOW_NEW_REGISTRATIONS = False

IMAGE_AUTO_DELETE = True

IMAGE_SIZES = {
    'thumbnail': {'size': [240, 0]},
    'medium': {'size': [480, 0]},
    'standard': {'size': [600, 0]},
    'square': {'crop': True, 'size': [125, 125]},
}

PUBLIC = True

ENABLED_PLUGINS = [
    'pinry_plugins.batteries.plugin_example.Plugin',
]
```

说明：

- `ALLOW_NEW_REGISTRATIONS = False`：关闭公开注册；
- 用户只能通过 `/admin/` 后台添加；
- 数据库保存到 `/data/production.db`；
- 上传图片保存到 `/data/static/media`；
- `/data` 会通过 Docker Compose 挂载到宿主机。

---

## 3. 确认 `development.py` 加载本地配置

当前容器默认使用：

```text
pinry.settings.development
```

需要确认 `pinry/settings/development.py` 最后包含：

```python
try:
    from .local_settings import *
except ImportError:
    pass
```

可以执行：

```bash
grep -n "local_settings" pinry/settings/development.py
```

如果没有，追加：

```bash
cat >> pinry/settings/development.py <<'EOF'

try:
    from .local_settings import *
except ImportError:
    pass
EOF
```

---

## 4. 构建自定义 Docker 镜像

在源码目录执行：

```bash
cd /opt/src/pinry
sudo docker build -t local/pinry-custom:latest .
```

构建成功后查看镜像：

```bash
sudo docker images | grep pinry
```

应该能看到：

```text
local/pinry-custom   latest
```

---

## 5. 创建 Dockge Stack

在 Dockge 中新建 Stack，例如：

```text
pinry
```

推荐 stack 路径：

```text
/opt/stacks/pinry
```

创建 `compose.yaml`：

```yaml
services:
  pinry:
    image: local/pinry-custom:latest
    container_name: pinry
    restart: unless-stopped
    environment:
      - SQLITE_DATABASE=/data/production.db
      - MEDIA_ROOT=/data/static/media
    volumes:
      - ./data:/data
    networks:
      - caddy

networks:
  caddy:
    external: true
```

说明：

- 不暴露 `ports`；
- 只通过 Caddy 反向代理访问；
- 数据库和上传文件持久化到：

```text
/opt/stacks/pinry/data
```

---

## 6. 启动 Pinry

在 Dockge 中点击部署。

或者命令行：

```bash
cd /opt/stacks/pinry
sudo docker compose up -d
```

查看日志：

```bash
sudo docker logs -f pinry
```

首次启动时会执行数据库迁移：

```text
Applying migrations...
```

---

## 7. 验证持久化配置

执行：

```bash
sudo docker exec -it pinry sh -lc 'cd /app && python manage.py shell -c "from django.conf import settings; print(settings.DATABASES); print(settings.MEDIA_ROOT); print(settings.ALLOW_NEW_REGISTRATIONS); print(settings.DEBUG)"'
```

期望看到：

```text
/data/production.db
/data/static/media
False
```

查看宿主机数据目录：

```bash
ls -lh /opt/stacks/pinry/data
```

应该能看到：

```text
production.db
static/
```

---

## 8. 创建超级管理员账号

执行：

```bash
sudo docker exec -it pinry sh -lc 'cd /app && python manage.py createsuperuser'
```

按提示输入：

```text
Username
Email
Password
```

后台地址：

```text
https://art.example.com/admin/
```

---

## 9. 配置 Caddy 反向代理

编辑 Caddyfile：

```bash
cd /opt/stacks/caddy
nano Caddyfile
```

增加站点配置：

```caddy
art.example.com {
    @admin path /admin /admin/*

    handle @admin {
        basic_auth "Pinry Admin" {
            username password_hash
        }

        reverse_proxy pinry:80
    }

    handle {
        reverse_proxy pinry:80
    }
}
```

其中 `password_hash` 需要生成。

生成 Basic Auth 密码 hash：

```bash
sudo docker exec -it caddy caddy hash-password
```

输入密码后会得到类似：

```text
$2a$14$xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

把它填入 Caddyfile：

```caddy
basic_auth "Pinry Admin" {
    hyeisn $2a$14$xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
}
```

完整示例：

```caddy
art.example.com {
    @admin path /admin /admin/*

    handle @admin {
        basic_auth "Pinry Admin" {
            hyeisn $2a$14$xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
        }

        reverse_proxy pinry:80
    }

    handle {
        reverse_proxy pinry:80
    }
}
```

验证 Caddy 配置：

```bash
sudo docker exec caddy caddy validate --config /etc/caddy/Caddyfile --adapter caddyfile
```

重载 Caddy：

```bash
sudo docker exec caddy caddy reload --config /etc/caddy/Caddyfile
```

---

## 10. DNS 配置

添加 A 记录：

```text
art.example.com -> 服务器公网 IP
```

Caddy 会自动申请 HTTPS 证书。

访问：

```text
https://art.example.com/
```

后台：

```text
https://art.example.com/admin/
```

---

## 11. 测试 Basic Auth

不带账号密码访问后台：

```bash
curl -I https://art.example.com/admin/
```

期望返回：

```text
HTTP/2 401
```

带账号密码：

```bash
curl -I -u username:your_password https://art.example.com/admin/
```

期望返回：

```text
HTTP/2 200
```

或：

```text
HTTP/2 302
```

注意：浏览器会缓存 Basic Auth 凭据。  
如果测试时不弹窗，可以使用无痕窗口。

---

## 12. 更新源码后的重新构建流程

当修改源码后，例如：

```text
pinry-spa/src/components/...
pinry/settings/...
pinry/urls.py
```

执行：

```bash
cd /opt/src/pinry
sudo docker build -t local/pinry-custom:latest .
```

然后重建容器：

```bash
cd /opt/stacks/pinry
sudo docker compose up -d --force-recreate
```

查看日志：

```bash
sudo docker logs -f pinry
```

如果修改了前端 UI，建议清理浏览器缓存：

```text
F12 -> Application -> Storage -> Clear site data
```

如果之前启用了 Service Worker，还需要：

```text
F12 -> Application -> Service Workers -> Unregister
```

---

## 13. 备份数据

运行数据位于：

```text
/opt/stacks/pinry/data
```

备份：

```bash
cd /opt/stacks
sudo tar czf pinry-data-backup-$(date +%F-%H%M%S).tar.gz pinry/data
```

恢复时解压回：

```text
/opt/stacks/pinry/data
```

---

## 14. 备份源码

源码建议通过 Git 管理：

```bash
cd /opt/src/pinry
git status
git add .
git commit -m "update pinry custom version"
git push
```

注意不要提交运行数据和敏感配置。

推荐 `.gitignore`：

```gitignore
# Runtime settings
pinry/settings/local_settings.py

# Runtime data
data/
static/
media/
*.sqlite3
*.db

# Python
__pycache__/
*.pyc
*.pyo
*.pyd
.venv/
venv/

# Node
node_modules/
pinry-spa/node_modules/
pinry-spa/dist/

# Logs
*.log

# Editors
.DS_Store
.idea/
.vscode/
*.swp
```

---

## 15. 常用维护命令

查看容器状态：

```bash
sudo docker ps | grep pinry
```

查看日志：

```bash
sudo docker logs -f pinry
```

进入容器：

```bash
sudo docker exec -it pinry sh
```

执行 Django shell：

```bash
sudo docker exec -it pinry sh -lc 'cd /app && python manage.py shell'
```

创建超级管理员：

```bash
sudo docker exec -it pinry sh -lc 'cd /app && python manage.py createsuperuser'
```

修改用户密码：

```bash
sudo docker exec -it pinry sh -lc 'cd /app && python manage.py changepassword 用户名'
```

重新执行迁移：

```bash
sudo docker exec -it pinry sh -lc 'cd /app && python manage.py migrate'
```

收集静态文件：

```bash
sudo docker exec -it pinry sh -lc 'cd /app && python manage.py collectstatic --noinput'
```

---

## 16. 清理 Docker 构建缓存

查看 Docker 占用：

```bash
sudo docker system df
```

清理 build cache：

```bash
sudo docker builder prune -f
```

清理悬空镜像：

```bash
sudo docker image prune -f
```

不要随便执行：

```bash
sudo docker system prune -a --volumes
```

因为可能误删 volume 数据。

---

# Quick Start

```bash
# 1. Clone
sudo mkdir -p /opt/src
sudo chown -R $USER:$USER /opt/src
cd /opt/src
git clone <your-repo-url> pinry
cd pinry

# 2. Configure
cp pinry/settings/local_settings.example.py pinry/settings/local_settings.py
nano pinry/settings/local_settings.py

# 3. Build image
sudo docker build -t local/pinry-custom:latest .

# 4. Create Dockge stack with compose.yaml
mkdir -p /opt/stacks/pinry
cd /opt/stacks/pinry
nano compose.yaml

# 5. Start
sudo docker compose up -d

# 6. Create admin
sudo docker exec -it pinry sh -lc 'cd /app && python manage.py createsuperuser'
```

`compose.yaml`:

```yaml
services:
  pinry:
    image: local/pinry-custom:latest
    container_name: pinry
    restart: unless-stopped
    environment:
      - SQLITE_DATABASE=/data/production.db
      - MEDIA_ROOT=/data/static/media
    volumes:
      - ./data:/data
    networks:
      - caddy

networks:
  caddy:
    external: true
```

Caddy:

```caddy
art.example.com {
    @admin path /admin /admin/*

    handle @admin {
        basic_auth "Pinry Admin" {
            username password_hash
        }

        reverse_proxy pinry:80
    }

    handle {
        reverse_proxy pinry:80
    }
}
```

## Features
- Image fetch and online preview
- Tagging system for Pins
- Browser Extensions
- Multi-user support
- Works well with docker
- Both public and private boards (add @2020.02.11)
- Search by tags / Search boards with name (add @2020.02.14)
- Full API support via DRF (add @2022.02.19)
- CLI support (Add image or url to Pinry via [command-line tool](https://github.com/pinry/pinry-cli-py)) (add @2022.02.20)
- i18n support (if you want to help to translate, please contact us in issues) (add @2020.04.23)
  - [x] English
  - [x] 简体中文
  - [x] French Support by [Lilian](https://github.com/LilianBoulard)
  
## Preview
![image](https://user-images.githubusercontent.com/4109722/166976413-38b575f2-a246-4852-ba05-11bca5f9b052.png)


## Install with Docker
Now we have pre-built docker image on multiple architectures like **ARMv7/ARMv8/AMD64**.

See our full documentation at [https://pinry.github.io/pinry/install-with-docker/](https://pinry.github.io/pinry/install-with-docker/)

## Requirements

See our full documentation at [https://pinry.github.io/pinry/development/](https://pinry.github.io/pinry/development/)


## Development

See our full documentation at [https://pinry.github.io/pinry/development/](https://pinry.github.io/pinry/development/)

## Contributors

The core contributors for Pinry have been/currently are:

* Isaac Bythewood <http://isaacbythewood.com/>
* Krzysztof Klimonda <https://github.com/kklimonda>
* Lapo Luchini <https://github.com/lapo-luchini>
* Ji Qu <https://winkidney.com/>

For a full list of contributors check out the [GitHub Contributors Graph](https://github.com/pinry/pinry/graphs/contributors)
