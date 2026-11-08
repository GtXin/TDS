# MACD teaching figures
Two self-drawn examples from deterministic synthetic closing prices, not market data.
- [Components](macd-components.png): close, EMA12/EMA26, DIF, DEA, and histogram.
- [Indicator divergence](macd-divergence.png): price peaks rise from 119.99 to 124.98 while each upward leg’s DIF peak falls from 4.39 to 2.23; their peak times may differ.
- [Source data](synthetic_macd.csv) includes 160 warm-up bars plus 141 displayed bars; [renderer](render_macd.py) reproduces the figures with NumPy and Matplotlib. Chinese text uses Arial Unicode MS when installed.
Calculation: EMA uses alpha=2/(period+1), seeded with the first close. DIF=EMA12(close)−EMA26(close); DEA=EMA9(DIF); histogram=DIF−DEA (1× scale).
The second figure illustrates indicator divergence; formal Chan 背驰 still requires level and structural conditions.
Sources: [StockCharts MACD histogram documentation](https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/macd-histogram), [Chan lesson 24](../../references/chan_theory/024.md).
