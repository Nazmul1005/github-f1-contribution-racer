#!/usr/bin/env python3
"""Generate an animated F1 car that races across a GitHub contribution grid."""
import json, math, os, urllib.request
from datetime import date, timedelta
from pathlib import Path
from PIL import Image, ImageDraw

USERNAME = os.environ["GH_USERNAME"]
TOKEN = os.environ["GH_TOKEN"]
OUT = Path("dist")
OUT.mkdir(exist_ok=True)

QUERY = """
query($login: String!, $from: DateTime!, $to: DateTime!) {
  user(login: $login) {
    contributionsCollection(from: $from, to: $to) {
      contributionCalendar {
        weeks { contributionDays { contributionCount color date } }
      }
    }
  }
}
"""

def get_calendar():
    today = date.today()
    start = today - timedelta(days=364)
    payload = {"query": QUERY, "variables": {
        "login": USERNAME,
        "from": start.isoformat() + "T00:00:00Z",
        "to": today.isoformat() + "T23:59:59Z"}}
    req = urllib.request.Request("https://api.github.com/graphql",
        data=json.dumps(payload).encode(),
        headers={"Authorization": f"Bearer {TOKEN}",
                 "Content-Type": "application/json",
                 "User-Agent": "github-f1-contribution-racer"})
    with urllib.request.urlopen(req) as response:
        result = json.loads(response.read())
    if result.get("errors"):
        raise RuntimeError("GitHub GraphQL error: " + str(result["errors"]))
    weeks = result["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
    return [[day for day in week["contributionDays"]] for week in weeks]

def route_points(columns, cell, gap, left, top):
    points, cols = [], len(columns)
    for row in range(7):
        xs = range(cols) if row % 2 == 0 else range(cols - 1, -1, -1)
        for col in xs:
            points.append((left + col*(cell+gap) + cell/2,
                           top + row*(cell+gap) + cell/2))
    return points

def sample_route(points, count):
    lengths, total = [], 0.0
    for a, b in zip(points, points[1:]):
        d = math.hypot(b[0]-a[0], b[1]-a[1])
        lengths.append(d); total += d
    result = []
    for i in range(count):
        target, walked = (i/count)*total, 0.0
        for j, seg in enumerate(lengths):
            if walked + seg >= target:
                t = 0 if seg == 0 else (target-walked)/seg
                a, b = points[j], points[j+1]
                x, y = a[0]+(b[0]-a[0])*t, a[1]+(b[1]-a[1])*t
                angle = math.degrees(math.atan2(-(b[1]-a[1]), b[0]-a[0]))
                result.append((x, y, angle)); break
            walked += seg
    return result

def draw_car(size=(42, 24)):
    w, h = size
    car = Image.new("RGBA", size, (0,0,0,0))
    d = ImageDraw.Draw(car)
    d.rounded_rectangle((5,1,13,7), radius=2, fill="#171717")
    d.rounded_rectangle((5,h-7,13,h-1), radius=2, fill="#171717")
    d.rounded_rectangle((w-13,1,w-5,7), radius=2, fill="#171717")
    d.rounded_rectangle((w-13,h-7,w-5,h-1), radius=2, fill="#171717")
    d.rounded_rectangle((2,8,w-2,h-8), radius=6, fill="#d71920", outline="#ff7777")
    d.polygon([(w-2,9),(w-2,h-9),(w,h//2)], fill="#ef3038")
    d.rounded_rectangle((w//2-5,9,w//2+4,h-9), radius=4, fill="#20232a")
    d.line((4,h//2,w-4,h//2), fill="#ffffff", width=1)
    return car

def make_gif(columns, points, width, height, cell, gap, left, top):
    bg = Image.new("RGB", (width,height), "#0d1117")
    draw = ImageDraw.Draw(bg)
    for col, week in enumerate(columns):
        for row, day in enumerate(week):
            x, y = left+col*(cell+gap), top+row*(cell+gap)
            draw.rounded_rectangle((x,y,x+cell,y+cell), radius=2,
                                   fill=day["color"] or "#161b22")
    draw.line(points, fill="#25313c", width=2, joint="curve")
    frames, car = [], draw_car().resize((30, 17), Image.Resampling.LANCZOS)
    for x, y, angle in sample_route(points, 72):
        frame = bg.copy().convert("RGBA")
        rotated = car.rotate(angle, resample=Image.Resampling.BICUBIC, expand=True)
        frame.alpha_composite(rotated, (int(x-rotated.width/2), int(y-rotated.height/2)))
        frames.append(frame.convert("P", palette=Image.Palette.ADAPTIVE))
    frames[0].save(OUT/"f1-race.gif", save_all=True, append_images=frames[1:],
                   duration=270, loop=0, optimize=True, disposal=2)

def make_svg(columns, points, width, height, cell, gap, left, top):
    rects = []
    for col, week in enumerate(columns):
        for row, day in enumerate(week):
            x, y = left+col*(cell+gap), top+row*(cell+gap)
            rects.append(f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" '
                         f'rx="2" fill="{day["color"] or "#161b22"}"/>')
    path_d = "M " + " L ".join(f"{x:.1f},{y:.1f}" for x,y in points)
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg"
 xmlns:xlink="http://www.w3.org/1999/xlink" width="{width}" height="{height}"
 viewBox="0 0 {width} {height}">
 <rect width="100%" height="100%" rx="12" fill="#0d1117"/>
 <g>{''.join(rects)}</g>
 <path id="racePath" d="{path_d}" fill="none" stroke="#263746" stroke-width="2"/>
 <g>
  <g transform="translate(-14.7,-8.4) scale(0.7)">
   <rect x="2" y="8" width="38" height="8" rx="4" fill="#d71920" stroke="#ff7777"/>
   <rect x="16" y="8" width="9" height="8" rx="3" fill="#20232a"/>
   <rect x="5" y="5" width="8" height="4" rx="1" fill="#171717"/>
   <rect x="5" y="15" width="8" height="4" rx="1" fill="#171717"/>
   <rect x="31" y="5" width="8" height="4" rx="1" fill="#171717"/>
   <rect x="31" y="15" width="8" height="4" rx="1" fill="#171717"/>
   <path d="M2 12 H40" stroke="#fff" stroke-width="1"/>
  </g>
  <animateMotion dur="64s" repeatCount="indefinite" rotate="auto">
   <mpath xlink:href="#racePath"/>
  </animateMotion>
 </g>
</svg>"""
    (OUT/"f1-race.svg").write_text(svg, encoding="utf-8")

def main():
    columns = get_calendar()
    cell, gap, left, top = 10, 3, 18, 28
    width = left*2 + len(columns)*(cell+gap)-gap
    height = top + 7*(cell+gap) + 18
    points = route_points(columns, cell, gap, left, top)
    make_gif(columns, points, width, height, cell, gap, left, top)
    make_svg(columns, points, width, height, cell, gap, left, top)
    print(f"Created GIF and SVG for @{USERNAME}")

if __name__ == "__main__":
    main()
