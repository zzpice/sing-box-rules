# sing-box-rules

个人维护的 sing-box / SMbox 例外分流规则。

这个仓库只保存**个人覆盖规则**，不重复维护完整的中国 / 非中国规则库。主规则仍可继续使用 MetaCubeX 等现有规则集。

## 文件

- `proxy.json`：强制走代理的域名。
- `direct.json`：强制直连的域名。
- `proxy.srs`：由 GitHub Actions 自动编译，供 SMbox / sing-box 使用。
- `direct.srs`：由 GitHub Actions 自动编译，供 SMbox / sing-box 使用。

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

规则按从上到下匹配，先命中者优先。

建议把个人例外规则放在通用规则之前：

```text
自定义直连（如需要）
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

这样即使某个域名属于中国规则，只要先命中 `proxy.srs`，仍然会按照“自定义代理”处理。

## 维护方式

平时只需要修改 `proxy.json` 或 `direct.json`。提交后 GitHub Actions 会自动使用 sing-box 1.14.2 编译对应的 `.srs` 文件并提交回仓库。

## 说明

- 源规则格式使用 sing-box 1.14 的 `version: 5`。
- 本仓库不保存节点、订阅、UUID、Reality 私钥、API Secret 等敏感信息。
