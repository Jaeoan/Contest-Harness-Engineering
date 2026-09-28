"""격자 생성 + 시설/사건 기반 공간 특징 계산.

사용 예:
  python grid_features.py --boundary boundary.geojson --cell 250 \
      --points cctv=data/cctv.csv:lon:lat zone=data/zones.csv:lon:lat \
      --radii cctv=200,500 zone=300 --out data/processed/grid_features.parquet

- 거리 계산은 EPSG:5179(미터). 출력 geometry는 EPSG:4326.
- 경계 밖 점 개수를 로그로 남긴다 (리포트에 기록할 것).
"""
from __future__ import annotations

import argparse
import json
import sys

import geopandas as gpd
import numpy as np
import pandas as pd
from shapely.geometry import box

METRIC_CRS = "EPSG:5179"
OUT_CRS = "EPSG:4326"


def make_grid(boundary: gpd.GeoDataFrame, cell: float) -> gpd.GeoDataFrame:
    b = boundary.to_crs(METRIC_CRS)
    union = b.union_all() if hasattr(b, "union_all") else b.unary_union
    minx, miny, maxx, maxy = union.bounds
    xs = np.arange(minx, maxx, cell)
    ys = np.arange(miny, maxy, cell)
    cells = [box(x, y, x + cell, y + cell) for x in xs for y in ys]
    grid = gpd.GeoDataFrame(geometry=cells, crs=METRIC_CRS)
    grid = grid[grid.intersects(union)].copy()
    grid["geometry"] = grid.intersection(union)
    grid = grid[~grid.is_empty].reset_index(drop=True)
    grid.insert(0, "grid_id", [f"G{i:05d}" for i in range(len(grid))])
    return grid


def load_points(spec: str, boundary: gpd.GeoDataFrame) -> tuple[str, gpd.GeoDataFrame]:
    name, rest = spec.split("=", 1)
    path, lon_col, lat_col = rest.split(":")
    df = pd.read_csv(path)
    n_raw = len(df)
    df = df.dropna(subset=[lon_col, lat_col])
    gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df[lon_col], df[lat_col]), crs=OUT_CRS).to_crs(METRIC_CRS)
    union = boundary.to_crs(METRIC_CRS)
    union = union.union_all() if hasattr(union, "union_all") else union.unary_union
    inside = gdf[gdf.within(union)]
    print(json.dumps({"layer": name, "raw": n_raw, "with_coords": len(gdf), "inside_boundary": len(inside),
                      "dropped_outside": len(gdf) - len(inside)}, ensure_ascii=False), file=sys.stderr)
    return name, inside


def add_point_features(grid: gpd.GeoDataFrame, name: str, pts: gpd.GeoDataFrame, radii: list[float]) -> None:
    cent = grid.geometry.centroid
    if len(pts) == 0:
        grid[f"{name}_dist"] = np.nan
        for r in radii:
            grid[f"{name}_{int(r)}m"] = 0
        return
    cent_gdf = gpd.GeoDataFrame(geometry=cent, crs=METRIC_CRS)
    nearest = gpd.sjoin_nearest(cent_gdf, pts[["geometry"]], distance_col="d", how="left")
    grid[f"{name}_dist"] = nearest.groupby(level=0)["d"].min().round(1).values
    for r in radii:
        buf = gpd.GeoDataFrame(geometry=cent.buffer(r), crs=METRIC_CRS)
        j = gpd.sjoin(buf, pts[["geometry"]], predicate="contains", how="left")
        grid[f"{name}_{int(r)}m"] = j.groupby(level=0)["index_right"].count().values


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--boundary", required=True)
    ap.add_argument("--cell", type=float, default=250)
    ap.add_argument("--points", nargs="*", default=[], help="name=path.csv:lon_col:lat_col")
    ap.add_argument("--radii", nargs="*", default=[], help="name=200,500")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    boundary = gpd.read_file(a.boundary)
    grid = make_grid(boundary, a.cell)
    radii = {k: [float(x) for x in v.split(",")] for k, v in (s.split("=") for s in a.radii)}
    for spec in a.points:
        name, pts = load_points(spec, boundary)
        add_point_features(grid, name, pts, radii.get(name, []))

    out = grid.to_crs(OUT_CRS)
    print(json.dumps({"n_cells": len(out), "cell_m": a.cell}, ensure_ascii=False), file=sys.stderr)
    if a.out.endswith(".parquet"):
        out.to_parquet(a.out)
    else:
        out.to_file(a.out, driver="GeoJSON")


if __name__ == "__main__":
    main()
