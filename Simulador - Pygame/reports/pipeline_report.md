# Relatório do Pipeline

- Python: `C:\Users\artur\AppData\Local\Programs\Python\Python313\python.exe`
- CWD: `C:\Users\artur\Desktop\ECA\IC - LCA Redes Neurais\Simulador_Labirinto_LCA\Simulador - Pygame`
- Data/Hora: `2025-08-13 18:50:08`

## Resultados

| Modo | Gerador | Slip | TurnErr | Episodes | Success | PathCostRatio | Turns | Collisions/ep | Lat p50 (ms) | Lat p95 (ms) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| professor | prim | 0.000 | 0.000 | 200 | 0.005 | 994.010 | 742.500 | 376.075 | 0.010 | 0.036 |
| professor | prim | 0.100 | 0.050 | 200 | 0.050 | 954.405 | 676.955 | 357.500 | 0.018 | 0.079 |
| residual | prim | 0.000 | 0.000 | 200 | 0.025 | 974.053 | 804.305 | 16.750 | 0.024 | 0.077 |
| residual | prim | 0.100 | 0.050 | 200 | 0.080 | 923.350 | 773.570 | 14.915 | 0.026 | 0.074 |
| professor | kruskal | 0.000 | 0.000 | 200 | 0.005 | 994.010 | 860.625 | 258.160 | 0.017 | 0.037 |
| residual | kruskal | 0.000 | 0.000 | 200 | 0.005 | 994.011 | 934.935 | 16.755 | 0.022 | 0.084 |
| professor | growingtree | 0.000 | 0.000 | 200 | 0.015 | 984.030 | 804.375 | 302.870 | 0.017 | 0.045 |
| residual | growingtree | 0.000 | 0.000 | 200 | 0.035 | 964.108 | 962.345 | 5.590 | 0.023 | 0.087 |