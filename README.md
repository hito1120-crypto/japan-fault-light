# 日本の断層の光

日本列島と近海の地震を起こす断層を、30年発生確率で明るさと脈動が変わる光として描く。3D点群風の操作ページ(`index.html`)と32秒の横動画(`fault_light.mp4`)。

- 操作ページ: 断層の選択パネル、種類別ON/OFF、深さ倍率、震源の重ね表示、3D/真上の切替
- データの出典と加工: `data/SOURCES.md`
- 統合データ: `data/faults.geojson` (name, type, length_km, dip, top_km, bottom_km, M, p30, last_event, interpolated)
- 再生成: `scripts/` (harvest → fetch_faults → build_faults → build_html → render_video)

形状は公表モデルの簡略表現で、位置・深さは目安。傾斜や深さが不明な断層は上端2km・下端15km・傾斜60度で補った推定(暗い点線)。
