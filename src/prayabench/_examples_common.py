"""Shared voxel builder helpers for deterministic reference examples."""
from __future__ import annotations

import re
from typing import Any

from .voxel_tasks import FACINGS, rotate_xz

PROVENANCE = 'Deterministic reference example; not a model run.'
_FACING_RE = re.compile(r'facing=(north|east|south|west)')


class VoxelBuilder:
    """Thin coordinate helper emitting validated prayabench cell dicts."""

    def __init__(self, component: str = 'reference') -> None:
        self.cells: dict[tuple[int, int, int], list[Any]] = {}
        self.default_component = component

    def put(
        self,
        x: int,
        y: int,
        z: int,
        state: str,
        lines: list[str] | None = None,
        component: str | None = None,
        asset: str | None = None,
    ) -> None:
        comp = self.default_component if component is None else component
        self.cells[x, y, z] = [x, y, z, state, lines, comp, asset]

    def box(
        self,
        x0: int,
        y0: int,
        z0: int,
        x1: int,
        y1: int,
        z1: int,
        state: str,
        component: str | None = None,
    ) -> None:
        for x in range(min(x0, x1), max(x0, x1) + 1):
            for y in range(min(y0, y1), max(y0, y1) + 1):
                for z in range(min(z0, z1), max(z0, z1) + 1):
                    self.put(x, y, z, state, component=component)

    def door(
        self,
        x: int,
        y: int,
        z: int,
        facing: str = 'north',
        wood: str = 'oak',
        hinge: str = 'left',
    ) -> None:
        self.put(x, y, z, f'{wood}_door[facing={facing},half=lower,hinge={hinge}]')
        self.put(x, y + 1, z, f'{wood}_door[facing={facing},half=upper,hinge={hinge}]')

    def bed(
        self,
        x: int,
        y: int,
        z: int,
        facing: str = 'south',
        color: str = 'red',
    ) -> None:
        dx, dz = {'north': (0, -1), 'south': (0, 1), 'east': (1, 0), 'west': (-1, 0)}[facing]
        self.put(x, y, z, f'{color}_bed[facing={facing},part=foot]')
        self.put(x + dx, y, z + dz, f'{color}_bed[facing={facing},part=head]')

    def sign(
        self,
        x: int,
        y: int,
        z: int,
        facing: str,
        lines: list[str],
        wood: str = 'oak',
        component: str | None = None,
    ) -> None:
        self.put(x, y, z, f'{wood}_wall_sign[facing={facing}]', lines=lines, component=component)

    def head(
        self,
        x: int,
        y: int,
        z: int,
        asset: str,
        rotation: int = 0,
    ) -> None:
        self.put(x, y, z, f'player_head[rotation={rotation}]', asset=asset)

    def conifer(self, cx: int, base_y: int, cz: int, height: int = 8) -> None:
        """Tiered spruce tree rooted at base_y."""
        top_trunk = base_y + height - 2
        for y in range(base_y, top_trunk + 1):
            self.put(cx, y, cz, 'spruce_log[axis=y]')
        tiers = [
            (base_y + 2, 2, True),
            (base_y + 3, 2, False),
            (base_y + 4, 1, True),
            (base_y + 5, 1, False),
            (base_y + 6, 1, False),
        ]
        for y, r, corners in tiers:
            if y > top_trunk + 1:
                continue
            for dx in range(-r, r + 1):
                for dz in range(-r, r + 1):
                    if dx == 0 and dz == 0 and y <= top_trunk:
                        continue
                    if not corners and abs(dx) == r and abs(dz) == r and r >= 2:
                        continue
                    if abs(dx) + abs(dz) <= (2 * r if corners else r + 1):
                        self.put(cx + dx, y, cz + dz, 'spruce_leaves[persistent=true]')
        self.put(cx, top_trunk + 1, cz, 'spruce_leaves[persistent=true]')
        self.put(cx, top_trunk + 2, cz, 'spruce_leaves[persistent=true]')

    def broadleaf(self, cx: int, base_y: int, cz: int, height: int = 7) -> None:
        """Rounded oak canopy with clear trunk rooted at base_y."""
        trunk_top = base_y + height - 3
        for y in range(base_y, trunk_top + 1):
            self.put(cx, y, cz, 'oak_log[axis=y]')
        for dy, r in ((0, 2), (1, 2), (2, 1)):
            y = trunk_top + dy
            for dx in range(-r, r + 1):
                for dz in range(-r, r + 1):
                    if dx == 0 and dz == 0 and y <= trunk_top:
                        continue
                    if dy in (0, 1) and abs(dx) == 2 and abs(dz) == 2:
                        continue
                    self.put(cx + dx, y, cz + dz, 'oak_leaves[persistent=true]')

    def result(self) -> dict[str, Any]:
        return {'cells': list(self.cells.values()), 'provenance': PROVENANCE}


def rotate_facing(local_facing: str, vehicle_facing: str) -> str:
    turn = FACINGS.index(vehicle_facing)
    return FACINGS[(FACINGS.index(local_facing) + turn) % 4]


def rotate_state(state: str, vehicle_facing: str) -> str:
    if vehicle_facing == 'north' or 'facing=' not in state:
        return state
    return _FACING_RE.sub(lambda m: 'facing=' + rotate_facing(m.group(1), vehicle_facing), state)


class VehicleBuilder:
    """Builds a north-facing vehicle in local coordinates and rotates to any compass facing."""

    def __init__(self, x0: int, z0: int, min_y: int, facing: str) -> None:
        self.x0 = x0
        self.z0 = z0
        self.min_y = min_y
        self.facing = facing
        self.cells: dict[tuple[int, int, int], list[Any]] = {}

    def put(
        self,
        lx: int,
        ly: int,
        lz: int,
        state: str,
        lines: list[str] | None = None,
        component: str = 'vehicle',
    ) -> None:
        wx, wz = rotate_xz(self.x0 + lx, self.z0 + lz, self.facing)
        wy = self.min_y + ly
        self.cells[wx, wy, wz] = [wx, wy, wz, rotate_state(state, self.facing), lines, component, None]

    def box(self, x0: int, y0: int, z0: int, x1: int, y1: int, z1: int, state: str) -> None:
        for x in range(min(x0, x1), max(x0, x1) + 1):
            for y in range(min(y0, y1), max(y0, y1) + 1):
                for z in range(min(z0, z1), max(z0, z1) + 1):
                    self.put(x, y, z, state)

    def door(self, lx: int, ly: int, lz: int, local_facing: str, wood: str = 'oak') -> None:
        self.put(lx, ly, lz, f'{wood}_door[facing={local_facing},half=lower]')
        self.put(lx, ly + 1, lz, f'{wood}_door[facing={local_facing},half=upper]')

    def result(self) -> dict[str, Any]:
        return {'cells': list(self.cells.values()), 'provenance': PROVENANCE}
