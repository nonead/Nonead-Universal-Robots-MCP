# 无需Git到仓库的文件清单

## 1. IDE相关文件
```
# IntelliJ IDEA
.idea/
*.iml
*.ipr
*.iws

# VSCode
.vscode/
!.vscode/settings.json
!.vscode/tasks.json
!.vscode/launch.json
!.vscode/extensions.json

# Eclipse
.project
.classpath
.settings/

# NetBeans
nbproject/

# PyCharm
.idea/
*.iml
```

## 2. Python项目文件
```
# 编译生成的文件
__pycache__/
*.py[cod]
*$py.class
*.so

# 虚拟环境
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# 包管理和构建文件
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# PyInstaller
*.manifest
*.spec

# 测试和覆盖率
htmlcov/
.tox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
.hypothesis/
.pytest_cache/

# 类型检查
.mypy_cache/

# Jupyter Notebook
.ipynb_checkpoints

# 其他Python工具
.pyenv/
.python-version
.ropeproject/
.spyderproject
.spyproject
```

## 3. 日志和临时文件
```
# 日志文件
*.log
logs/

# 临时文件
*.tmp
*.temp
.tmp/
.temp/
*.swp
*.swo
*~

# 操作系统文件
.DS_Store
Thumbs.db

# Windows文件
$RECYCLE.BIN/
```

## 4. 配置和敏感信息
```
# 环境变量文件
.env
.env.local
.env.development.local
.env.test.local
.env.production.local

# 敏感配置文件
*.pem
*.key
*.cert
*.p12
*.pfx
*.jks

# 数据库文件
*.sqlite3
*.db
*.db-journal
```

## 5. 文档和构建输出
```
# Sphinx文档构建
docs/_build/

# mkdocs文档构建
/site

# 其他文档构建输出
build/
target/
```

## 6. 项目特定文件
```
# 项目日志和数据
*.log
operation_history/

# 临时测试文件
register_reset_test.py

# RTDE配置文件（如果有本地修改）
rtdeConfiguration.xml

# 图片处理临时文件
*.tmp.gif
*.tmp.svg
```

## 7. 版本控制相关
```
# Git相关
.git/
.gitattributes
.gitmodules

# Mercurial
.hg/
.hgignore
.hgsigs
.hgtags

# SVN
.svn/
```

## 8. 其他工具
```
# Docker
.dockerignore
Dockerfile.local

# Kubernetes
*.kubeconfig

# Terraform
.terraform/
*.tfstate
*.tfstate.backup

# Ansible
*.retry
```

## 使用说明
1. 将上述内容复制到项目根目录的 `.gitignore` 文件中
2. 根据项目实际情况调整忽略项
3. 确保敏感信息和本地配置文件不被提交到Git仓库
4. 定期更新 `.gitignore` 文件，添加新的忽略项

## 注意事项
- 不要将包含敏感信息的文件提交到Git仓库
- 不要将本地配置文件提交到Git仓库
- 不要将构建输出和临时文件提交到Git仓库
- 不要将IDE特定文件提交到Git仓库，除非团队统一使用相同IDE
- 确保 `.gitignore` 文件本身被提交到Git仓库