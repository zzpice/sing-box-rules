# 仓库协作约定

- 默认直接在 `main` 修改、提交并推送；只有用户明确要求时才使用其他分支或 Pull Request。
- 这里只维护个人“强制代理 / 强制直连”例外覆盖，不扩展成完整规则库。
- `proxy.json` 与 `direct.json` 是规则源；`proxy.srs` 与 `direct.srs` 是生成文件，不手动编辑。
- 修改规则或工作流后必须通过 JSON、冲突检查和 sing-box 编译验证。
- 不加入节点、订阅、UUID、Secret、私钥或其他连接凭据。
