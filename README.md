# dinagon

deno <https://deno.land/>
velociraptor <https://velociraptor.run/>

## セットアップ

``` bash
# denoのインストール(Mac, Linux)
curl -fsSL https://deno.land/x/install/install.sh | sh
# denoのタスクランナー"velociraptor"をインストール
deno install --no-check -qAn vr https://deno.land/x/velociraptor@1.0.0/cli.ts
```

次のvscode拡張機能をインストール

| 名前         | URL                                                                            |
| ------------ | ------------------------------------------------------------------------------ |
| deno         | <https://marketplace.visualstudio.com/items?itemName=denoland.vscode-deno>     |
| velociraptor | <https://marketplace.visualstudio.com/items?itemName=umbo.vscode-velociraptor> |

## 起動

```bash
vr start
```
