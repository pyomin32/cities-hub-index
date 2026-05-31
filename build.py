#!/usr/bin/env python3
"""웹사이트용 데이터 빌드.

results/*.csv 와 viz/*.png 를 읽어 web/ 안에서 바로 쓸 수 있는
data.js (전역 window.DATA) 와 web/viz/ 사본을 만든다. 외부 서버 없이
index.html 을 그대로 열어도 동작하도록 모든 데이터를 JS 에 임베드한다.
"""
import csv
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WEB = ROOT / "web"
RESULTS = ROOT / "results"
VIZ = ROOT / "viz"


def read_csv(path: Path):
    with path.open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    # 숫자로 보이는 값은 float 로 변환 (정렬·포맷용)
    for row in rows:
        for k, v in row.items():
            if v in ("", None):
                row[k] = None
                continue
            try:
                row[k] = float(v) if ("." in v or "e" in v.lower()) else int(v)
            except (ValueError, TypeError):
                pass  # 문자열 유지 (city, country, True/False 등)
    return rows


# 시각화 그림 메타데이터 (파일명 → 제목·설명)
FIGURES = [
    ("fig1_ranking.png", "허브 지수 랭킹", "67개 도시의 종합 허브 지수 순위 막대그래프."),
    ("fig10_innovation_heatmap.png", "혁신중시 히트맵", "혁신 가중 시나리오 지표 히트맵."),
    ("fig3_corr.png", "지표 상관관계", "6개 지표 간 상관계수 행렬."),
    ("fig4_pca_clusters.png", "PCA 군집", "주성분 분석으로 본 도시 군집 분포."),
    ("fig5_weight_sensitivity.png", "가중치 민감도", "가중치 변화에 따른 순위 안정성."),
    ("fig6_method_comparison.png", "합성 방법 비교", "동일가중·5팩터 등 합성 방법별 순위 비교."),
    ("fig7_5factor.png", "5팩터 랭킹", "5팩터 합성 기준 도시 순위."),
    ("fig8_scenarios_bump.png", "시나리오별 순위 변화", "균형·혁신중시·소득중시 시나리오 범프 차트."),
    ("fig9_rank_acceptability.png", "순위 수용도 (SMAA)", "가중치 불가지론 하 순위별 수용 확률."),
]

# 6개 지표 메타데이터 (열 이름 → 한글 라벨)
INDICATORS = {
    "bachelors_pct_25_64": "고등교육 이수율(%)",
    "pct_patents_per_100k": "10만명당 PCT 특허",
    "gdp_per_capita_ppp": "1인당 GDP(PPP)",
    "labour_productivity": "노동생산성",
    "pop_growth_rate": "인구증가율(%)",
    "startup_ecosystem_score": "스타트업 생태계 점수",
}


def main():
    WEB.mkdir(exist_ok=True)

    data = {
        "ranking": read_csv(RESULTS / "hub_ranking.csv"),
        "innovation": read_csv(RESULTS / "hub_ranking_innovation.csv"),
        "robust": read_csv(RESULTS / "hub_ranking_robust.csv"),
        "alt": read_csv(RESULTS / "hub_ranking_alt.csv"),
        "indicators": INDICATORS,
        "figures": [
            {"file": f, "title": t, "desc": d}
            for f, t, d in FIGURES
            if (VIZ / f).exists()
        ],
    }

    # viz 그림을 web/viz 로 복사 (정적 서빙·file:// 모두 대응)
    out_viz = WEB / "viz"
    out_viz.mkdir(exist_ok=True)
    for fig in data["figures"]:
        shutil.copy2(VIZ / fig["file"], out_viz / fig["file"])

    (WEB / "data.js").write_text(
        "window.DATA = " + json.dumps(data, ensure_ascii=False) + ";\n",
        encoding="utf-8",
    )
    print(f"data.js 생성 완료 — 도시 {len(data['ranking'])}개, 그림 {len(data['figures'])}장")


if __name__ == "__main__":
    main()
