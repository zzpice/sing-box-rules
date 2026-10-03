# sing-box-rules

[![Build SRS](https://github.com/zzpice/sing-box-rules/actions/workflows/build-srs.yml/badge.svg)](https://github.com/zzpice/sing-box-rules/actions/workflows/build-srs.yml)

个人维护的 sing-box / SMbox **例外分流规则**。

这个仓库只保存个人覆盖规则，不重复维护完整的中国 / 非中国规则库。主规则仍可继续使用 MetaCubeX 等现有规则集。

## 文件

- `proxy.json`：强制走代理的域名，手动维护。
- `direct.json`：强制直连的域名，手动维护。
- `proxy.srs`：由 GitHub Actions 自动编译。
- `direct.srs`：由 GitHub Actions 自动编译。

> `.srs` 是生成文件，不建议手动修改。

## Raw 地址

强制代理：

```text
https://raw.githubusercontent.com/zzpice/sing-box-rules/main/proxy.srs
```

强制直连：

```text
https://raw.githubusercontent.com/zzpice/sing-box-rules/main/direct.srs
```

## 如何添加域名

例如希望 `example.cn` 及其所有子域名都强制走代理，在 `proxy.json` 中加入：

```json
{
  "version": 5,
  "rules": [
    {
      "domain_suffix": [
        "example.cn"
      ]
    }
  ]
}
```

如果只想匹配一个完整域名，例如 `www.example.cn`：

```json
{
  "version": 5,
  "rules": [
    {
      "domain": [
        "www.example.cn"
      ]
    }
  ]
}
```

通常优先使用 `domain_suffix`，这样主域名及其子域名可以一起覆盖。

## SMbox 中的顺序

规则按从上到下匹配，先命中者优先。建议把个人例外规则放在通用规则之前：

```text
自定义直连
自定义代理
↓
Bing / CN-CDN / Finance / YouTube / Telegram / ...
↓
CN
↓
!CN
↓
漏网规则
```

这样即使某个域名属于中国规则，只要先命中个人规则，仍然会按照个人覆盖规则处理。

## 自动编译

平时只修改 `proxy.json` 或 `direct.json`。

提交到 `main` 后，GitHub Actions 会：

1. 校验两个 JSON 的基本结构；
2. 下载固定版本的 sing-box；
3. 编译生成 `proxy.srs` 和 `direct.srs`；
4. 只有生成结果发生变化时才提交回仓库。

当前编译版本：**sing-box 1.14.2**。

## 安全边界

本仓库只保存域名规则，不保存：

- 节点配置；
- 订阅链接；
- UUID；
- Reality 私钥；
- API Secret；
- SSH 凭据。

服务端与客户端完整配置应保存在私有仓库中。

## License

本仓库自有规则与自动化配置使用 [MIT License](./LICENSE)。
