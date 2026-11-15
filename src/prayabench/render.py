"""Original flat-colour SVG renderer. No Minecraft artwork or texture downloads."""
import html
from .scene import state_parts,full_block

def colour(b):
    colors={'white':(225,225,218),'light_gray':(169,174,171),'gray':(66,72,76),'black':(33,37,41),
        'red':(166,64,53),'orange':(206,125,53),'yellow':(222,188,66),'green':(74,120,68),
        'lime':(128,165,72),'blue':(58,91,145),'light_blue':(129,172,192),'cyan':(70,139,142),
        'purple':(130,93,150),'magenta':(172,105,150),'pink':(208,153,167),'brown':(112,81,59)}
    if b in ('air','water'):return (140,181,195)
    if 'leaves' in b or b in ('grass_block','moss_block','azalea','fern','bush','sweet_berry_bush'):return (72,116,62)
    if any(t in b for t in ('poppy','dandelion','flower','cornflower','bluet','peony')):return (192,148,115)
    if 'glass' in b:return (125,159,169)
    if 'spruce' in b or 'dark_oak' in b:return (109,80,50)
    if any(t in b for t in ('oak','birch','barrel','bookshelf','chest')):return (159,123,77)
    if 'deepslate' in b or 'blackstone' in b:return (57,63,67)
    if 'quartz' in b or b=='calcite':return (226,223,209)
    if b in ('bricks','brick_wall') or b.startswith('brick_'):return (158,102,84)
    if any(t in b for t in ('lantern','torch','end_rod','glowstone')):return (238,209,130)
    if b in ('dirt','podzol','coarse_dirt'):return (120,89,61)
    for color in sorted(colors,key=len,reverse=True):
        if b.startswith(color+'_'):return colors[color]
    if b=='terracotta':return (155,103,79)
    if 'head' in b:return (145,135,112)
    return (143,147,145)

def shape(b,p):
    if b.endswith('_slab'):
        t=p.get('type','bottom');return [(0,.5 if t=='top' else 0,0,1,1 if t!='bottom' else .5,1)]
    if b.endswith('_stairs'):
        up=p.get('half')=='top';parts=[(0,.5 if up else 0,0,1,1 if up else .5,1)]
        f=p.get('facing','north');x0,x1=(.5,1) if f=='east' else (0,.5) if f=='west' else (0,1)
        z0,z1=(0,.5) if f=='north' else (.5,1) if f=='south' else (0,1)
        return parts+[(x0,0 if up else .5,z0,x1,.5 if up else 1,z1)]
    if 'wall_sign' in b or b=='player_wall_head':
        t=.12 if 'sign' in b else .5;f=p.get('facing','north')
        x0,x1=(0,t) if f=='east' else (1-t,1) if f=='west' else (.15,.85)
        z0,z1=(1-t,1) if f=='north' else (0,t) if f=='south' else (.15,.85)
        return [(x0,.3,z0,x1,.8,z1)]
    if b=='player_head':return [(.25,0,.25,.75,.5,.75)]
    if b.endswith('_door') or b.endswith('_trapdoor'):
        f=p.get('facing','north')
        if b.endswith('_trapdoor') and p.get('open')!='true':return [(0,.85 if p.get('half')=='top' else 0,0,1,1 if p.get('half')=='top' else .15,1)]
        return [(0,0,0,1,1,.15)] if f in ('north','south') else [(0,0,0,.15,1,1)]
    if b.endswith(('_pane','_bars','_fence','_wall')):
        pieces=[(.43,0,.43,.57,1,.57)]
        for f,ext in [('north',(.43,0,0,.57,1,.5)),('south',(.43,0,.5,.57,1,1)),('east',(.5,0,.43,1,1,.57)),('west',(0,0,.43,.5,1,.57))]:
            if p.get(f) in ('true','low','tall'):pieces.append(ext)
        return pieces
    if b in ('iron_chain','chain','end_rod','torch','redstone_torch'):return [(.45,0,.45,.55,1,.55)]
    if b.endswith('_carpet'):return [(0,0,0,1,.07,1)]
    if b.startswith('potted_') or b in ('fern','poppy','dandelion','cornflower','azure_bluet','azalea','sweet_berry_bush','candle','cake'):return [(.2,0,.2,.8,.6,.8)]
    return [(0,0,0,1,1,1)]

def svg(grid,view=0,cut=18):
    scale=19; width,height=940,790
    def rotate(x,z):
        return ((x,z),(z,24-x),(24-x,22-z),(22-z,x))[view%4]
    def point(x,y,z):
        a,b=rotate(x,z);return (width/2+(a-b)*scale,330+(a+b)*scale/2-y*scale)
    faces=[]
    for (x,y,z),cell in grid.items():
        if not(0<=x<24 and 0<=y<cut and 0<=z<22):continue
        b,p=state_parts(cell[3])
        if b=='air':continue
        if b.endswith(('_pane','_bars','_fence','_wall')):
            p=dict(p)
            for f,(dx,dz) in {'north':(0,-1),'south':(0,1),'east':(1,0),'west':(-1,0)}.items():
                adjacent=grid.get((x+dx,y,z+dz),[0,0,0,'air'])[3]
                if f not in p and (full_block(adjacent) or state_parts(adjacent)[0]==b):p[f]='true'
        rgb=colour(b)
        for a0,h0,c0,a1,h1,c1 in shape(b,p):
            vertices=[(x+a0,y+h0,z+c0),(x+a1,y+h0,z+c0),(x+a1,y+h0,z+c1),(x+a0,y+h0,z+c1),
                      (x+a0,y+h1,z+c0),(x+a1,y+h1,z+c0),(x+a1,y+h1,z+c1),(x+a0,y+h1,z+c1)]
            # Keep all four sides; painter ordering hides back faces.
            for inds,factor,offset in [((0,1,5,4),.72,(0,0,-1)),((1,2,6,5),.84,(1,0,0)),((2,3,7,6),.72,(0,0,1)),((3,0,4,7),.84,(-1,0,0)),((4,5,6,7),1.0,(0,1,0))]:
                nx,ny,nz=x+offset[0],y+offset[1],z+offset[2]
                neighbor=grid.get((nx,ny,nz),[0,0,0,'air'])[3]
                if full_block(cell[3]) and ny<cut and full_block(neighbor):continue
                pts=[vertices[i] for i in inds];depth=sum(sum(rotate(v[0],v[2]))+v[1]*.08 for v in pts)/4
                fill='#'+''.join(f'{int(c*factor):02x}' for c in rgb)
                coords=' '.join(f'{px:.1f},{py:.1f}' for px,py in (point(*v) for v in pts))
                faces.append((depth,f'<polygon points="{coords}" fill="{fill}" stroke="{fill}" stroke-width="0.4"/>'))
    title=html.escape('Isometric voxel scene; approximate geometry and placeholder props')
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" aria-label="{title}"><rect width="100%" height="100%" fill="#eef2ef"/>'+''.join(s for _,s in sorted(faces,key=lambda q:q[0]))+'</svg>'
