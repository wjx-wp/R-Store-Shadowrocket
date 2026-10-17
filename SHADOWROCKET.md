# R-Store → Shadowrocket：安装与自动更新

这是 [zirawell/R-Store](https://github.com/zirawell/R-Store) 的**非官方 Shadowrocket 适配版本**。保留原许可证与来源。主仓库里的 Rule 和 Res 目录仍是最初 Fork 的上游快照；**真正自动更新的是新生成的 Shadowrocket 目录**，它每次从官方上游重新获取最新源码。

本项目采用保守转换：**不执行、不引用任何上游 JavaScript**。因此大部分纯域名广告拦截可以迁移，但依赖响应脚本的深度去广告不保证有效。不能保证微博的摇一摇跳转完全被禁止，也没有逐个 iPhone 实测全部模块。

## 两种生成版本

| 模块路径 | 作用 | 推荐方式 |
| --- | --- | --- |
| Shadowrocket/Lite/App/... | 仅拦截广告域名/IP，不运行脚本，不解密 HTTPS | **首选，隐私风险较低** |
| Shadowrocket/App/... | 域名/IP + 允许的 URL Rewrite 和 Map Local 映射 | 需谨慎选择；映射和改写可能需要 HTTPS 解密 |
| Shadowrocket/Lite/Applet/... 和 Shadowrocket/Applet/... | 微信、支付宝小程序广告规则 | 先试 Lite；不要随便解密支付相关接口 |
| Shadowrocket/Lite/Web/... 和 Shadowrocket/Web/... | 网站去广告 | 同上 |
| Shadowrocket/All/... | 广告规则聚合包 | 体积大，可能重复，**不建议和单 App 模块同时启用** |
| Shadowrocket/manifest.json | 记录原版上游 SHA、每个模块内容 SHA-256、剔除规则以及跳过的脚本 | 查看构建结果与差异 |

Lite 只为确实包含域名/IP 拦截规则的模块生成，不能靠伪造空规则覆盖所有 App。因此 Lite 的文件数会比完整网络版少。

## 常用下载链接

- [微博 Lite（建议先用）](https://raw.githubusercontent.com/wjx-wp/R-Store-Shadowrocket/main/Shadowrocket/Lite/App/W/%E5%BE%AE%E5%8D%9A/weibo.module)
- [微博网络规则完整版](https://raw.githubusercontent.com/wjx-wp/R-Store-Shadowrocket/main/Shadowrocket/App/W/%E5%BE%AE%E5%8D%9A/weibo.module)
- [哔哩哔哩网络规则完整版](https://raw.githubusercontent.com/wjx-wp/R-Store-Shadowrocket/main/Shadowrocket/App/B/%E5%93%94%E5%93%A9%E5%93%94%E5%93%A9/bilibili.module)

注：如果某个 Lite 链接不存在，意味着该上游模块**没有符合安全白名单的域名/IP 拦截规则**，请不要把完整版误认为无须 HTTPS 解密的完全去广告方案。

### 在 Shadowrocket 中安装

1. 保留现有的 VMess 节点、订阅和代理配置，无需购买 QuanX，也无需替换主配置。
2. 复制你需要的模块的 **Raw URL**。
3. 打开 Shadowrocket → 配置 → 模块 → 右上角添加；粘贴 URL 导入并启用。
4. 建议全局路由使用“配置”，观察广告拦截与 App 功能有没有异常。
5. 先用 Lite。若 Lite 不够，再考虑完整网络版；若需 HTTPS 解密，只信任你自己在 Shadowrocket 中生成并安装的 CA 证书。HTTPS 解密可以涉及微博 Cookie、响应数据等，敏感支付 App 不建议这样操作。
6. GitHub 上更新不会立即推送到手机；在 Shadowrocket 中定期刷新远程模块或使用它的自动更新功能。

## 全自动同步和验证

- 工作流：[同步并转换 Shadowrocket](.github/workflows/shadowrocket-sync.yml)。
- GitHub Actions 每天 **UTC 02:17、14:17** 尝试同步，或者在 [Actions 页面](https://github.com/wjx-wp/R-Store-Shadowrocket/actions) 手动执行 Sync R-Store to Shadowrocket → Run workflow。
- 自动从官方 zirawell/R-Store 最新主分支克隆源码，记录实际提交 SHA，不在 CI 执行上游任何脚本。
- 经过 Python 语法检查、单元测试、规则白名单、危险 URL 重定向排除、敏感 MITM 域名排除、Map Local 静态替换限制、输出路径去重、完整性 SHA-256 校验、模块数量阈值检查。
- 只有通过检查的低风险静态规则变化才能自动提交到 main。
- **如发现上游 JavaScript 内容变化、新 HTTPS 解密域名、新 Map Local 映射或已发布模块删除**，构建产生审核分支并尝试开启 PR，人工审核前不更新主分支。
- 如果 Fork 的 Actions 被 GitHub 暂停，需要仓库所有者手动重新启用。自动开 PR 可能需要 Settings → Actions → General → Workflow permissions 中允许 GitHub Actions 创建 Pull Request。权限不足时，审核分支仍会保留。
- 不需要提供任何 GitHub PAT、Apple 账号密码或代理节点订阅。

### 安全边界与当前未完成部分

这里是有意限制能力的 Shadowrocket 转换器，而不是全部 Surge/QuanX 功能的无条件兼容层：

- **上游 JavaScript/ProtoBuf 二进制操作不转换**，脚本数量及来源指纹保存在 manifest 中。因此部分广告拦截效果会低于原仓库。
- **不自动搬运上游的 Rule/Res 源文件到本 Fork**；只同步并发布其生成结果。
- 可以静态验证生成结构，但**不代表已经在真机上逐个验证 App、HTTPS 解密或者实际去广告效果**。
- 拦截网络请求无法阻止 App 本身读取加速度计，所以不保证解决所有摇一摇广告。
- 没有魔法绕过防证书固定（certificate pinning）的能力。遇到有证书绑定的 App，完整网络规则可能完全不生效。
- 尽量只订阅自己要用的单 App 模块，减少误伤和 HTTPS 解密范围。

## 本地复核

需 Python 3.11+。先在此项目同级克隆官方 R-Store。接着执行：

~~~bash
python3 -m unittest discover -s tests -v
python3 scripts/shadowrocket_build.py build \
  --source ../R-Store/Rule/Surge/Adblock \
  --scripts ../R-Store/Res/Scripts/AntiAd \
  --out /tmp/rstore-shadowrocket \
  --sha "$(git -C ../R-Store rev-parse HEAD)"
python3 scripts/shadowrocket_build.py check --out /tmp/rstore-shadowrocket
python3 scripts/shadowrocket_build.py gate \
  --old Shadowrocket --new /tmp/rstore-shadowrocket
~~~

## 来源与许可证

原仓库：https://github.com/zirawell/R-Store 。保留原仓库 LICENSE（GPL-3.0）及作者署名。使用或进一步分发时仍须遵守上游与第三方素材各自的授权条款。
