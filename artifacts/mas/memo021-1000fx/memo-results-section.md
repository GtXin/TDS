#### 真实数据：前1000个分型（XD-P1）

真实样本截到FX999完整分型窗口的右端，再重建得到3244根原始K线、2040根合并K线和恰好1000个分型，均与原快照前缀一致。两档笔由memo029算法生成；下面是本方案XD-P1试算，不是CC线段输出。

| 输入笔档位 | 笔数 | XD-P1段数 | 已完成路线FX边界 | 未决笔范围 | 中位秒 |
|---|---:|---:|---|---|---:|
| strong | 167 | 15 | FX0→FX917 | Bi[147,167) | 0.151 |
| weak | 239 | 26 | FX0→FX986 | Bi[234,239) | 0.412 |

耗时为三次暖进程的识别、建图及选路中位数，不含上游计算和绘图。独立实现重新核查21050个起终点假设、324份主证书、353个状态、327条边及41段选路，结果一致；20项合成测试通过。本口径每状态至多一条后继，DP在此退化为链式基线，尚不证明原文划分的完备性。

![前1000分型：strong输入的15段总览](memoWX_021_Chan_xianduan/xd-p1-1000fx-strong-overview.png)

![前1000分型：weak输入的26段总览](memoWX_021_Chan_xianduan/xd-p1-1000fx-weak-overview.png)

紫线为主证书段，橙线为父证书限定的派生段，灰线为输入笔；浅黄色为未输出为已完成段的尾部，其中的笔仍可参与确认。

![strong局部：MK1080–1279的线段与共享端点](memoWX_021_Chan_xianduan/xd-p1-1000fx-strong-detail.png)

![weak末尾局部：FX986之后保持开放](memoWX_021_Chan_xianduan/xd-p1-1000fx-weak-tail.png)

完整[26页交互／PNG图集](../../artifacts/mas/memo021-1000fx/charts/index.html)覆盖全部1000分型；已逐页目视检查。复现及边界见[试算说明](../../artifacts/mas/memo021-1000fx/README.md)，[独立核验](../../artifacts/mas/memo021-1000fx/independent-validation.json)保留实际检查结果。

