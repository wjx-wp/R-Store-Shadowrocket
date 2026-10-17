# R-Store for Shadowrocket（小火箭自动适配）

本 Fork 已增加 **Shadowrocket 去广告模块自动转换与定期同步**。原项目 [zirawell/R-Store](https://github.com/zirawell/R-Store) 的规则、版权及许可证均予保留。**不会改变你的小火箭 VMess 节点和订阅**。

- **[Shadowrocket 安装教程与安全说明](SHADOWROCKET.md)**（推荐先看）
- **[Lite 规则目录](Shadowrocket/Lite/App)**：只拦截域名/IP，不使用 HTTPS 解密、不执行 JavaScript（推荐）
- **[完整网络规则目录](Shadowrocket/App)**：含可静态适配的 URL Rewrite / Map Local，不含上游 JS
- **[转换清单与审核报告](Shadowrocket/manifest.json)**：每个模块 SHA-256、上游版本和遗漏说明
- **[自动同步运行记录](https://github.com/wjx-wp/R-Store-Shadowrocket/actions)**：每日两次同步，敏感变化人工审核

**注意：** 这不是 100% 功能移植。上游 JS、二进制响应处理等不会自动转换；生成模块通过 CI 静态检查，但没有逐个 App 的真机验证。以下保留原版 R-Store 说明，其 QuanX / Surge 链接仍指向原仓库；自动生成的 Shadowrocket 结果位于本 Fork 的 Shadowrocket 文件夹。

---

![](https://raw.githubusercontent.com/zirawell/R-Store/main/Res/Images/R-Store_Header.png)
# R-Store

本项目旨在建立一个没有广告环境的清爽环境，同时增加功能化插件进行一些定制;

本项目主要以神机Lite规则为基础，整合并完善了一些其他仓库的规则;

同时也通过自行抓包加入了一些个人常用App/小程序的规则

## 项目结构

| 序号        | 项目                                                 | 说明		   |
| :--------- | :---------------------------------------------------| :------------ |
| 1 | [`Res`](https://github.com/zirawell/R-Store/tree/main/Res)   | 收录各类静态资源 |
| 2 | [`Rule`](https://github.com/zirawell/R-Store/tree/main/Rule) | 收录各类规则资源 |

## 项目指南

| 序号        | 配置主页                                                    | 目前进度|
| :--------- | :----------------------------------------------------------| :-- |
| 1 | [`QuanX`](https://github.com/zirawell/R-Store/tree/main/Rule/QuanX) | 完善中 |
| 2 | [`Surge`](https://github.com/zirawell/R-Store/tree/main/Rule/Surge) | 完善中 |

### `QuanX`规则

此项目中，[App](https://github.com/zirawell/R-Store/tree/main/Rule/QuanX/Adblock/App)目录下;

以每个App为独立目录收录各App的相应规则，

高阶用户可以自行寻找所需的具体某个App的规则进行引用；

如果不想根据单个App引用规则，本仓库也提供了一键导入:

- [全部规则](https://quantumult.app/x/open-app/add-resource?remote-resource=%7B%22rewrite_remote%22%3A%20%5B%22https%3A%2F%2Fraw.githubusercontent.com%2Fzirawell%2FR-Store%2Fmain%2FRule%2FQuanX%2FAdblock%2FAll%2Fsnippet%2FallAdBlock.snippet%2C%20tag%3DAdblock%22%5D%7D)

- [app规则](https://quantumult.app/x/open-app/add-resource?remote-resource=%7B%22rewrite_remote%22%3A%20%5B%22https%3A%2F%2Fraw.githubusercontent.com%2Fzirawell%2FR-Store%2Fmain%2FRule%2FQuanX%2FAdblock%2FAll%2Fsnippet%2FappAdBlock.snippet%2C%20tag%3DApp%22%5D%7D)

- [微信小程序](https://quantumult.app/x/open-app/add-resource?remote-resource=%7B%22rewrite_remote%22%3A%20%5B%22https%3A%2F%2Fraw.githubusercontent.com%2Fzirawell%2FR-Store%2Fmain%2FRule%2FQuanX%2FAdblock%2FAll%2Fsnippet%2FwechatAdBlock.snippet%2C%20tag%3DWechat%22%5D%7D)

- [支付宝小程序](https://quantumult.app/x/open-app/add-resource?remote-resource=%7B%22rewrite_remote%22%3A%20%5B%22https%3A%2F%2Fraw.githubusercontent.com%2Fzirawell%2FR-Store%2Fmain%2FRule%2FQuanX%2FAdblock%2FAll%2Fsnippet%2FalipayAdBlock.snippet%2C%20tag%3DAlipay%22%5D%7D)


>旧版本写法目前已归档，供 Quantumult X 1.5.2(844) 版本以下使用

<details>
<summary>
Quantumult X 1.5.2(844) 版本以下导入由此进入
</summary>

- [全部规则](https://quantumult.app/x/open-app/add-resource?remote-resource=%7B%22filter_remote%22%3A%20%5B%22https%3A%2F%2Fraw.githubusercontent.com%2Fzirawell%2FR-Store%2Fmain%2FRule%2FQuanX%2FAdblock%2FAll%2Ffilter%2FallAdBlock.list%2C%20tag%3DAdblock%22%5D%2C%22rewrite_remote%22%3A%20%5B%22https%3A%2F%2Fraw.githubusercontent.com%2Fzirawell%2FR-Store%2Fmain%2FRule%2FQuanX%2FAdblock%2FAll%2Frewrite%2FallAdRewrite.conf%2C%20tag%3DAdblock%22%5D%7D)

- [app规则](https://quantumult.app/x/open-app/add-resource?remote-resource=%7B%22filter_remote%22%3A%20%5B%22https%3A%2F%2Fraw.githubusercontent.com%2Fzirawell%2FR-Store%2Fmain%2FRule%2FQuanX%2FAdblock%2FAll%2Ffilter%2FappAdBlock.list%2C%20tag%3DApp%22%5D%2C%22rewrite_remote%22%3A%20%5B%22https%3A%2F%2Fraw.githubusercontent.com%2Fzirawell%2FR-Store%2Fmain%2FRule%2FQuanX%2FAdblock%2FAll%2Frewrite%2FappAdRewrite.conf%2C%20tag%3DApp%22%5D%7D)

- [微信小程序](https://quantumult.app/x/open-app/add-resource?remote-resource=%7B%22filter_remote%22%3A%20%5B%22https%3A%2F%2Fraw.githubusercontent.com%2Fzirawell%2FR-Store%2Fmain%2FRule%2FQuanX%2FAdblock%2FAll%2Ffilter%2FwechatAdBlock.list%2C%20tag%3DWechat%22%5D%2C%22rewrite_remote%22%3A%20%5B%22https%3A%2F%2Fraw.githubusercontent.com%2Fzirawell%2FR-Store%2Fmain%2FRule%2FQuanX%2FAdblock%2FAll%2Frewrite%2FwechatAdRewrite.conf%2C%20tag%3DWechat%22%5D%7D)

- [支付宝小程序](https://quantumult.app/x/open-app/add-resource?remote-resource=%7B%22filter_remote%22%3A%20%5B%22https%3A%2F%2Fraw.githubusercontent.com%2Fzirawell%2FR-Store%2Fmain%2FRule%2FQuanX%2FAdblock%2FAll%2Ffilter%2FalipayAdBlock.list%2C%20tag%3DAlipay%22%5D%2C%22rewrite_remote%22%3A%20%5B%22https%3A%2F%2Fraw.githubusercontent.com%2Fzirawell%2FR-Store%2Fmain%2FRule%2FQuanX%2FAdblock%2FAll%2Frewrite%2FalipayAdRewrite.conf%2C%20tag%3DAlipay%22%5D%7D)

</details>



### `Surge`规则

此项目中，[App](https://github.com/zirawell/R-Store/tree/main/Rule/Surge/Adblock/App)目录下;

以每个App为独立目录收录各App的相应规则，

高阶用户可以自行寻找所需的具体某个App的规则进行引用；

如果不想根据单个App引用规则，本仓库也提供了一键导入：

（⚠️注意：由于Surge不支持http导入方式，需要先添加[【神机模块】](https://raw.githubusercontent.com/zirawell/R-Store/main/Rule/Surge/Redirect/DivineEngine.sgmodule)）

- [全部规则](https://surge.app/install-module?url=https%3A%2F%2Fraw.githubusercontent.com%2Fzirawell%2FR-Store%2Fmain%2FRule%2FSurge%2FAdblock%2FAll%2FallAdBlock.sgmodule)

- [app规则](https://surge.app/install-module?url=https%3A%2F%2Fraw.githubusercontent.com%2Fzirawell%2FR-Store%2Fmain%2FRule%2FSurge%2FAdblock%2FAll%2FappAdBlock.sgmodule)

- [微信小程序](https://surge.app/install-module?url=https%3A%2F%2Fraw.githubusercontent.com%2Fzirawell%2FR-Store%2Fmain%2FRule%2FSurge%2FAdblock%2FAll%2FwechatAdBlock.sgmodule)

- [支付宝小程序](https://surge.app/install-module?url=https%3A%2F%2Fraw.githubusercontent.com%2Fzirawell%2FR-Store%2Fmain%2FRule%2FSurge%2FAdblock%2FAll%2FalipayAdBlock.sgmodule)

## 收录统计

| Type | Count |
|----------|----------|
| 全部    | 673 |
| App    | 530 |
| 微信小程序| 133 |
| 支付宝小程序| 7 |
| 网站    | 3 |

## 特别鸣谢
[![](https://raw.githubusercontent.com/zirawell/R-Store/main/Res/Icon/Author/app2smile.png)](https://github.com/app2smile)
[![](https://raw.githubusercontent.com/zirawell/R-Store/main/Res/Icon/Author/blackmatrix7.png)](https://github.com/blackmatrix7)
[![](https://raw.githubusercontent.com/zirawell/R-Store/main/Res/Icon/Author/DivineEngine.png)](https://github.com/DivineEngine)
[![](https://raw.githubusercontent.com/zirawell/R-Store/main/Res/Icon/Author/KOP-XIAO.png)](https://github.com/KOP-XIAO)
[![](https://raw.githubusercontent.com/zirawell/R-Store/main/Res/Icon/Author/NobyDa.png)](https://github.com/NobyDa)
[![](https://raw.githubusercontent.com/zirawell/R-Store/main/Res/Icon/Author/Orz-3.png)](https://github.com/Orz-3)
[![](https://raw.githubusercontent.com/zirawell/R-Store/main/Res/Icon/Author/fmz200.png)](https://github.com/fmz200)
[![](https://raw.githubusercontent.com/zirawell/R-Store/main/Res/Icon/Author/RuCu6.png)](https://github.com/RuCu6)
[![](https://raw.githubusercontent.com/zirawell/R-Store/main/Res/Icon/Author/Sliverkiss.png)](https://github.com/Sliverkiss)
[![](https://raw.githubusercontent.com/zirawell/R-Store/main/Res/Icon/Author/luestr.png)](https://github.com/luestr)
[![](https://raw.githubusercontent.com/zirawell/R-Store/main/Res/Icon/Author/wf021325.png)](https://github.com/wf021325)
[![](https://raw.githubusercontent.com/zirawell/R-Store/main/Res/Icon/Author/Maasea.png)](https://github.com/Maasea)
[![](https://raw.githubusercontent.com/zirawell/R-Store/main/Res/Icon/Author/ClydeTime.png)](https://github.com/ClydeTime)
[![](https://raw.githubusercontent.com/zirawell/R-Store/main/Res/Icon/Author/FoKit.png)](https://github.com/FoKit)
[![](https://raw.githubusercontent.com/zirawell/R-Store/main/Res/Icon/Author/Yuheng0101.png)](https://github.com/Yuheng0101)
[![](https://raw.githubusercontent.com/zirawell/R-Store/main/Res/Icon/Author/XiangwanGuan.png)](https://github.com/XiangwanGuan)
