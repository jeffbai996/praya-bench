"""Shared voxel builder helpers and architectural primitives for reference examples."""
from __future__ import annotations

import random
import re
from typing import Any, Sequence

from .voxel_tasks import FACINGS, rotate_xz

PROVENANCE = 'Deterministic reference example; not a model run.'
_FACING_RE = re.compile(r'facing=(north|east|south|west)')
_HEAD_ROT = {'south': 0, 'sw': 2, 'west': 4, 'nw': 6, 'north': 8, 'ne': 10, 'east': 12, 'se': 14}
_OPP = {'north': 'south', 'south': 'north', 'east': 'west', 'west': 'east'}
_VEC2 = {'north': (0, -1), 'south': (0, 1), 'east': (1, 0), 'west': (-1, 0)}


class VoxelBuilder:
    """Coordinate helper with CAD, facade-relief, retail, washroom and PNW tree primitives."""

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
        frame: dict[str, Any] | None = None,
    ) -> None:
        comp = self.default_component if component is None else component
        row: list[Any] = [x, y, z, state, lines, comp, asset]
        if frame is not None:
            row.append(frame)
        self.cells[x, y, z] = row

    def get_state(self, x: int, y: int, z: int) -> str:
        c = self.cells.get((x, y, z))
        return c[3] if c is not None else 'air'

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
        wood: str = 'dark_oak',
        hinge: str = 'left',
    ) -> None:
        base_d = wood if wood.endswith('_door') else f'{wood}_door'
        self.put(x, y, z, f'{base_d}[facing={facing},half=lower,hinge={hinge}]', component='door')
        self.put(x, y + 1, z, f'{base_d}[facing={facing},half=upper,hinge={hinge}]', component='door')

    def bed(
        self,
        x: int,
        y: int,
        z: int,
        facing: str = 'south',
        color: str = 'red',
    ) -> None:
        dx, dz = _VEC2[facing]
        self.put(x, y, z, f'{color}_bed[facing={facing},part=foot]', component='furniture')
        self.put(x + dx, y, z + dz, f'{color}_bed[facing={facing},part=head]', component='furniture')

    def sign(
        self,
        x: int,
        y: int,
        z: int,
        facing: str,
        lines: list[str],
        wood: str = 'oak',
        component: str = 'sign',
    ) -> None:
        padded = [str(s) for s in lines[:4]]
        while len(padded) < 4:
            padded.append('')
        self.put(x, y, z, f'{wood}_wall_sign[facing={facing}]', lines=padded, component=component)

    def blade_sign(
        self,
        x: int,
        y: int,
        z: int,
        facing: str,
        lines: list[str],
        wood: str = 'spruce',
        component: str = 'sign',
    ) -> None:
        padded = [str(s) for s in lines[:4]]
        while len(padded) < 4:
            padded.append('')
        self.put(x, y, z, f'{wood}_wall_hanging_sign[facing={facing}]', lines=padded, component=component)

    def address_plaque(
        self,
        x: int,
        y: int,
        z: int,
        facing: str,
        number: int | str,
        street_en: str,
        street_zh: str = '',
        wood: str = 'oak',
    ) -> None:
        num_s = f'| {number} |'
        rule = '-' * max(3, min(10, len(num_s) - 1))
        self.sign(x, y, z, facing, [num_s, rule, street_en, street_zh], wood=wood, component='facade')

    def framed_sign(
        self,
        x: int,
        y: int,
        z: int,
        facing: str,
        line1: str,
        line2: str,
        wood: str = 'oak',
        component: str = 'sign',
    ) -> None:
        w = max(4, min(14, max(len(line1), len(line2))))
        rule = '-' * w
        self.sign(x, y, z, facing, [rule, line1, line2, rule], wood=wood, component=component)

    def dedication_placard(
        self,
        x: int,
        y: int,
        z: int,
        facing: str,
        mon_day: str = 'Nov. 14,',
        year: str = '2026',
        label: str = 'Built',
        tool: str = 'stone_axe',
        wood: str = 'oak',
    ) -> None:
        rule = '-' * max(5, min(12, len(label)))
        self.sign(x, y, z, facing, [label, rule, mon_day, year], wood=wood, component='placard')
        cur_up = self.get_state(x, y + 1, z)
        self.put(x, y + 1, z, cur_up, component='placard', frame={'facing': facing, 'item': tool})

    def occupancy_plaque(self, x: int, y: int, z: int, facing: str, persons: int = 36) -> None:
        self.sign(
            x, y, z, facing,
            ['Max Occupancy', f'{persons} Persons', 'By Order of', 'Fire Marshal'],
            wood='birch', component='interior',
        )

    def head(
        self,
        x: int,
        y: int,
        z: int,
        asset: str,
        facing: str | int = 'north',
        wall: bool = False,
        component: str = 'prop',
    ) -> None:
        if wall:
            f_str = facing if isinstance(facing, str) else 'north'
            self.put(x, y, z, f'player_wall_head[facing={f_str}]', component=component, asset=asset)
        else:
            rot = facing if isinstance(facing, int) else _HEAD_ROT.get(facing, 8)
            self.put(x, y, z, f'player_head[rotation={rot}]', component=component, asset=asset)

    def recessed_north_portal(
        self,
        x0: int,
        x1: int,
        y: int,
        z_outer: int,
        door_xs: int | Sequence[int] | None = None,
        door_wood: str = 'dark_oak',
        pier_mat: str = 'smooth_quartz',
        jamb_mat: str = 'stripped_spruce_wood[axis=y]',
        glass_mat: str = 'gray_stained_glass',
        threshold_mat: str = 'polished_andesite',
        height: int = 3,
        uplight: bool = False,
    ) -> None:
        """1-block recessed north-facing entrance portal (outer frame at z_outer, door at z_outer + 1)."""
        xa, xb = min(x0, x1), max(x0, x1)
        if door_xs is None:
            dcols = [(xa + xb) // 2]
        elif isinstance(door_xs, int):
            dcols = [door_xs]
        else:
            dcols = sorted(int(v) for v in door_xs)
        portal_h = 2 if height <= 3 else 3
        for dy in range(height):
            self.put(xa, y + dy, z_outer, pier_mat, component='facade')
            self.put(xb, y + dy, z_outer, pier_mat, component='facade')
            self.put(xa, y + dy, z_outer + 1, pier_mat, component='facade')
            self.put(xb, y + dy, z_outer + 1, pier_mat, component='facade')
        for x in range(xa + 1, xb):
            self.put(x, y - 1, z_outer, 'sea_lantern' if (uplight and x in dcols) else threshold_mat, component='floor')
            self.put(x, y - 1, z_outer + 1, threshold_mat, component='floor')
            for dy in range(portal_h):
                self.put(x, y + dy, z_outer, 'air', component='porch')
            for dy in range(portal_h, height):
                is_light = (x in dcols) and (dy == portal_h)
                self.put(x, y + dy, z_outer, 'sea_lantern' if is_light else pier_mat, component='lights' if is_light else 'facade')
        inner = list(range(xa + 1, xb))
        flank = jamb_mat if len(inner) >= 3 else glass_mat
        for x in inner:
            if x in dcols:
                hinge = 'right' if (len(dcols) == 2 and x == dcols[1]) else 'left'
                self.door(x, y, z_outer + 1, 'north', door_wood, hinge=hinge)
                for dy in range(2, height):
                    self.put(x, y + dy, z_outer + 1, glass_mat, component='facade')
            elif any(abs(x - dc) == 1 for dc in dcols):
                for dy in range(height):
                    self.put(x, y + dy, z_outer + 1, flank, component='facade')
            else:
                for dy in range(height):
                    self.put(x, y + dy, z_outer + 1, 'gray_stained_glass_pane', component='facade')

    def recessed_west_portal(
        self,
        z0: int,
        z1: int,
        y: int,
        x_outer: int,
        door_z: int | None = None,
        door_wood: str = 'spruce',
        pier_mat: str = 'smooth_quartz',
        jamb_mat: str = 'stripped_spruce_wood[axis=y]',
        glass_mat: str = 'gray_stained_glass',
        threshold_mat: str = 'polished_andesite',
        height: int = 3,
    ) -> None:
        """1-block recessed west-facing entrance portal (outer frame at x_outer, door at x_outer + 1)."""
        za, zb = min(z0, z1), max(z0, z1)
        dz_col = (za + zb) // 2 if door_z is None else door_z
        for dy in range(height):
            self.put(x_outer, y + dy, za, pier_mat, component='facade')
            self.put(x_outer, y + dy, zb, pier_mat, component='facade')
            self.put(x_outer + 1, y + dy, za, pier_mat, component='facade')
            self.put(x_outer + 1, y + dy, zb, pier_mat, component='facade')
        for z in range(za + 1, zb):
            self.put(x_outer, y - 1, z, threshold_mat, component='floor')
            self.put(x_outer + 1, y - 1, z, threshold_mat, component='floor')
            self.put(x_outer, y, z, 'air', component='porch')
            self.put(x_outer, y + 1, z, 'air', component='porch')
            for dy in range(2, height):
                self.put(x_outer, y + dy, z, 'sea_lantern' if (z == dz_col and dy == 2) else pier_mat,
                         component='lights' if (z == dz_col and dy == 2) else 'facade')
            if z == dz_col:
                self.door(x_outer + 1, y, z, 'west', door_wood)
                for dy in range(2, height):
                    self.put(x_outer + 1, y + dy, z, glass_mat, component='facade')
            elif abs(z - dz_col) == 1:
                for dy in range(height):
                    self.put(x_outer + 1, y + dy, z, jamb_mat if (zb - za >= 4) else glass_mat, component='facade')
            else:
                for dy in range(height):
                    self.put(x_outer + 1, y + dy, z, 'gray_stained_glass_pane', component='facade')

    def dressed_window(
        self,
        side: str,
        wall_coord: int,
        t0: int,
        t1: int,
        y0: int,
        y1: int,
        glass: str = 'gray_stained_glass',
        sill_stair: str = 'smooth_quartz_stairs',
        shutter_wood: str | None = 'spruce',
    ) -> None:
        """Place window glazing in ``side`` wall with exterior bracketed sill and optional open shutters."""
        ta, tb = min(t0, t1), max(t0, t1)
        dx_out, dz_out = _VEC2[side]
        inward = _OPP[side]
        for t in range(ta, tb + 1):
            wx, wz = (t, wall_coord) if side in ('north', 'south') else (wall_coord, t)
            for y in range(y0, y1 + 1):
                self.put(wx, y, wz, glass, component='window')
            sx, sz = wx + dx_out, wz + dz_out
            if self.get_state(sx, y0 - 1, sz) == 'air':
                self.put(sx, y0 - 1, sz, f'{sill_stair}[facing={inward},half=top]', component='relief')
        if shutter_wood:
            for t in (ta - 1, tb + 1):
                wx, wz = (t, wall_coord) if side in ('north', 'south') else (wall_coord, t)
                sx, sz = wx + dx_out, wz + dz_out
                for y in range(y0, y1 + 1):
                    if self.get_state(sx, y, sz) == 'air' and 'glass' not in self.get_state(wx, y, wz) and not self.get_state(wx, y, wz).endswith('_door'):
                        self.put(sx, y, sz, f'{shutter_wood}_trapdoor[facing={side},half=bottom,open=true]', component='relief')

    def fan_unit_2x2(self, x: int, y: int, z: int, casing: str = 'smooth_quartz') -> None:
        """2x2 white/quartz rooftop condenser topped with 4 circular fan rails."""
        for dx in (0, 1):
            for dz in (0, 1):
                self.put(x + dx, y, z + dz, casing, component='roof')
                self.put(x + dx, y + 1, z + dz, 'rail[shape=north_south]', component='roof')

    def slatted_ceiling(
        self,
        x0: int,
        z0: int,
        x1: int,
        z1: int,
        y: int,
        wood: str = 'oak',
        light_every: int = 3,
    ) -> None:
        """Commercial slatted trapdoor ceiling with integrated end_rod tube runs."""
        xa, xb = min(x0, x1), max(x0, x1)
        za, zb = min(z0, z1), max(z0, z1)
        for z in range(za, zb + 1):
            light_row = light_every > 0 and ((z - za) % light_every == 1)
            for x in range(xa, xb + 1):
                if light_row and xa < x < xb:
                    self.put(x, y, z, 'end_rod[facing=east]', component='lights')
                else:
                    self.put(x, y, z, f'{wood}_trapdoor[facing=north,half=top,open=false]', component='ceiling')

    def bench(self, x0: int, z0: int, x1: int, z1: int, y: int, facing: str, wood: str = 'spruce') -> None:
        """Street or park bench with end trapdoor armrests."""
        if z0 == z1:
            xa, xb = min(x0, x1), max(x0, x1)
            for x in range(xa, xb + 1):
                self.put(x, y, z0, f'{wood}_stairs[facing={facing},half=bottom]', component='bench')
        else:
            za, zb = min(z0, z1), max(z0, z1)
            for z in range(za, zb + 1):
                self.put(x0, y, z, f'{wood}_stairs[facing={facing},half=bottom]', component='bench')

    def bcparks_post_sign(self, x: int, base_y: int, z: int, facing: str, park_name: str) -> None:
        """Grounded BCParks stone-brick-wall + double-quartz-slab + deepslate-cap monument sign."""
        dx, dz = _VEC2[facing]
        self.put(x, base_y, z, 'stone_brick_wall', component='park-sign')
        self.put(x, base_y + 1, z, 'smooth_quartz_slab[type=double]', component='park-sign')
        self.put(x, base_y + 2, z, 'deepslate_tile_slab[type=bottom]', component='park-sign')
        rule = '-' * max(8, min(14, len(park_name) + 2))
        self.sign(x + dx, base_y + 1, z + dz, facing, [park_name, 'Park', rule, 'BCParks'], wood='oak', component='park-sign')

    def conifer(self, cx: int, base_y: int, cz: int, height: int = 10, seed: int = 7) -> None:
        """PNW layered conical spruce/Douglas-fir."""
        rng = random.Random(f'conifer:{cx}:{base_y}:{cz}:{seed}')
        h = max(7, int(height))
        clear = max(2, h // 4)
        widest = 3 if h >= 10 else 2
        slope = 2.2
        tree: dict[tuple[int, int, int], str] = {}
        for i in range(h - 2):
            tree[cx, base_y + i, cz] = 'spruce_log[axis=y]'
        top = base_y + h - 1
        count = h - clear + 1
        for j in range(count):
            yy = top - j
            r = min(widest, int((j + 1) / slope))
            if r >= 2 and j % 3 == 2 and j < count - 1:
                r -= 1
            limit = r * r + r * 0.65
            for dx in range(-r, r + 1):
                for dz in range(-r, r + 1):
                    d2 = dx * dx + dz * dz
                    if d2 > limit:
                        continue
                    rim = r >= 2 and d2 > (r - 1) * (r - 1) + (r - 1) * 0.65
                    if rim and rng.random() < 0.2:
                        continue
                    if dx == 0 and dz == 0 and yy < base_y + h - 2:
                        continue
                    tree[cx + dx, yy, cz + dz] = 'spruce_leaves[persistent=true]'

        self._write_pruned_tree(tree)

    def _prune_disconnected_leaves(self, seed: tuple[int, int, int], max_dist: int = 6) -> int:
        """Drop leaves that do not reach a log through at most ``max_dist`` leaf steps.

        Starts from the log at ``seed`` and walks the connected logs, then spreads
        through leaves the way Minecraft measures leaf distance. Anything left over
        is a floating clump. Returns how many leaves were removed.
        """
        def base(p: tuple[int, int, int]) -> str:
            return self.get_state(*p).split('[', 1)[0]

        steps = ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1))
        if not base(seed).endswith('_log'):
            raise ValueError(f'prune seed {seed} is not a log')
        logs = {seed}
        stack = [seed]
        while stack:
            x, y, z = stack.pop()
            for dx, dy, dz in steps:
                nb = (x + dx, y + dy, z + dz)
                if nb not in logs and base(nb).endswith('_log'):
                    logs.add(nb)
                    stack.append(nb)
        dist = {p: 0 for p in logs}
        queue = list(logs)
        i = 0
        while i < len(queue):
            x, y, z = queue[i]
            i += 1
            if dist[x, y, z] >= max_dist:
                continue
            for dx, dy, dz in steps:
                nb = (x + dx, y + dy, z + dz)
                if nb not in dist and base(nb).endswith('_leaves'):
                    dist[nb] = dist[x, y, z] + 1
                    queue.append(nb)
        doomed = [p for p in self.cells if base(p).endswith('_leaves') and p not in dist]
        for p in doomed:
            del self.cells[p]
        return len(doomed)

    def _write_pruned_tree(self, tree: dict[tuple[int, int, int], str]) -> None:
        logs = [p for p, st in tree.items() if st.split('[', 1)[0].endswith('_log')]
        if not logs:
            return
        dist: dict[tuple[int, int, int], int] = {p: 0 for p in logs}
        queue = list(logs)
        head = 0
        while head < len(queue):
            px, py, pz = queue[head]
            head += 1
            d = dist[px, py, pz]
            if d >= 5:
                continue
            for dx, dy, dz in ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)):
                nb = (px + dx, py + dy, pz + dz)
                if nb in tree and nb not in dist:
                    dist[nb] = d + 1
                    queue.append(nb)
        for (tx, ty, tz), st in tree.items():
            if (tx, ty, tz) in dist:
                self.put(tx, ty, tz, st, component='tree')

    def broadleaf(self, cx: int, base_y: int, cz: int, height: int = 8, seed: int = 11, oak_only: bool = False) -> None:
        """Organic forked PNW bigleaf maple / oak with multi-dome asymmetric crown."""
        rng = random.Random(f'broadleaf:{cx}:{base_y}:{cz}:{seed}')
        h = max(6, int(height))
        fork_y = base_y + max(3, h // 2 - 1)
        tree: dict[tuple[int, int, int], str] = {}
        for y in range(base_y, fork_y + 2):
            tree[cx, y, cz] = 'oak_log[axis=y]'
        boughs = [
            ((1, 0, 'x'), (2, 0, 'x'), fork_y + 2, 2),
            ((-1, 0, 'x'), (-2, 0, 'x'), fork_y + 2, 2),
            ((0, 1, 'z'), (0, 2, 'z'), fork_y + 1, 2),
            ((0, -1, 'z'), (0, -2, 'z'), fork_y + 3, 2),
        ]
        domes = [(cx, fork_y + 3, cz, 2)]
        for (dx1, dz1, ax1), (dx2, dz2, ax2), top_y, rad in boughs:
            tree[cx + dx1, fork_y + 1, cz + dz1] = f'oak_log[axis={ax1}]'
            tree[cx + dx2, fork_y + 2, cz + dz2] = f'oak_log[axis={ax2}]'
            domes.append((cx + dx2, top_y, cz + dz2, rad))
        for px, py, pz, r in domes:
            for ly, lr in ((-1, max(1, r - 1)), (0, r), (1, max(1, r - 1))):
                lim = lr * lr + lr * 0.65
                for dx in range(-lr, lr + 1):
                    for dz in range(-lr, lr + 1):
                        d2 = dx * dx + dz * dz
                        if d2 > lim:
                            continue
                        if lr >= 2 and d2 > (lr - 1) ** 2 + 0.5 and rng.random() < 0.2:
                            continue
                        tx, ty, tz = px + dx, py + ly, pz + dz
                        if tree.get((tx, ty, tz), '').endswith('_log') or self.get_state(tx, ty, tz).endswith('_log'):
                            continue
                        leaf = 'oak_leaves[persistent=true]' if (oak_only or rng.random() >= 0.2) else 'azalea_leaves[persistent=true]'
                        tree[tx, ty, tz] = leaf
        self._write_pruned_tree(tree)

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
