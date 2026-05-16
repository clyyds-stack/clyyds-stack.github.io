"""
Rebuild index.html with safe optimizations only:
- Image resize (safe, huge win)
- CSS minification (safe)
- Inline assets with base64
- Correct JS execution order
- NO JS minification (avoids regex corruption)
"""
import base64, json, os, re

BASE = r'c:\Users\CHENLEI\Desktop\ndMWsJ'

def b64(path):
    with open(path, 'rb') as f:
        return base64.b64encode(f.read()).decode()

def read_txt(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

# ================================================================
# 1. Optimize images
# ================================================================
print("1/5 Optimizing hello kitty.png...")
from PIL import Image
img = Image.open(os.path.join(BASE, 'img', 'hello kitty.png'))
img = img.resize((270, 220), Image.LANCZOS)
opt_path = os.path.join(BASE, 'img', '_opt_kitty.png')
img.save(opt_path, 'PNG', optimize=True)
orig_sz = os.path.getsize(os.path.join(BASE, 'img', 'hello kitty.png'))
new_sz = os.path.getsize(opt_path)
print(f"  {orig_sz:,} -> {new_sz:,} bytes ({new_sz/orig_sz*100:.0f}%)")

# ================================================================
# 2. Base64 encode all assets
# ================================================================
print("2/5 Encoding assets...")
img_files = {
    'favicon.ico': 'image/x-icon',
    'hello kitty.png': 'image/png',
    'stamp.png': 'image/png',
    'stamp-base.png': 'image/png',
    'wax.png': 'image/png',
    'texture.png': 'image/png',
    'bgm.png': 'image/png',
}
imgs = {}
for name, mime in img_files.items():
    if name == 'hello kitty.png':
        path = opt_path
    else:
        path = os.path.join(BASE, 'img', name)
    imgs[name] = f'data:{mime};base64,{b64(path)}'

font_b64 = b64(os.path.join(BASE, 'font', 'op.woff2'))

# ================================================================
# 3. Process CSS (minify safely)
# ================================================================
print("3/5 Processing CSS...")
css_files = ['main.css', 'letter.css', 'sakura.css', 'typed.css', 'bgm.css']
css_all = ''
for f in css_files:
    css_all += read_txt(os.path.join(BASE, 'css', f)) + '\n'

# Replace font URL
css_all = css_all.replace(
    "url('./../font/op.woff2') format('woff2')",
    f"url('data:font/woff2;base64,{font_b64}') format('woff2')"
)
# Replace image URLs
for name, uri in imgs.items():
    css_all = re.sub(
        r'url\(["\x27](?:\.\./)+img/' + re.escape(name) + r'["\x27]\)',
        f'url("{uri}")', css_all
    )
    css_all = re.sub(
        r'url\((?:\.\./)+img/' + re.escape(name) + r'\)',
        f'url({uri})', css_all
    )

# Safe CSS minification: just remove comments and collapse whitespace
css_min = re.sub(r'/\*.*?\*/', '', css_all, flags=re.DOTALL)
css_min = re.sub(r'\s+', ' ', css_min)
css_min = re.sub(r'\s*([{};:,>+~])\s*', r'\1', css_min)
css_min = css_min.replace(';}', '}')
css_min = css_min.strip()
print(f"  CSS: {len(css_all):,} -> {len(css_min):,} bytes")

# ================================================================
# 4. Read JS (RAW, NO MINIFICATION)
# ================================================================
print("4/5 Reading JavaScript (raw, no minification)...")
typed_js = read_txt(os.path.join(BASE, 'js', 'typed.js'))
sakura_js = read_txt(os.path.join(BASE, 'js', 'sakura.js'))
letter_js = read_txt(os.path.join(BASE, 'js', 'letter.js'))

# Defer WebGL sakura init by 50ms for better perceived performance
sakura_js = sakura_js.replace(
    "window.addEventListener('load', function (e) {",
    "window.addEventListener('load', function (e) { setTimeout(function() {"
)
sakura_js = sakura_js.replace(
    "    animate();\n});",
    "    animate();\n    }, 50);\n});"
)

# Fix: sakura.js uses 'experimental-webgl' -> add 'webgl' fallback
sakura_js = sakura_js.replace(
    "canvas.getContext('experimental-webgl')",
    "canvas.getContext('webgl') || canvas.getContext('experimental-webgl')"
)

# Fix: global variables
sakura_js = sakura_js.replace(
    "    fullw = Math.max",
    "    var fullw = Math.max"
)
sakura_js = sakura_js.replace(
    "    fullh = Math.max",
    "    var fullh = Math.max"
)

# ================================================================
# 5. Build main.js with inline content data
# ================================================================
print("5/5 Building main.js...")

with open(os.path.join(BASE, 'font', 'content.json'), 'r', encoding='utf-8') as f:
    cdata = json.load(f)

cdata_json = json.dumps(cdata, ensure_ascii=False)

# Build main script with CORRECT execution order
main_script = f'''var _d = {cdata_json};

var envelope_opened = false;
var content = {{
    salutation: _d.salutation,
    signature: _d.signature,
    body: _d.body,
    sign: 0
}};

function playPause() {{
    var player = document.getElementById('music');
    var play_btn = $('#music_btn');
    if (player.paused) {{
        player.play();
        play_btn.attr('class', 'play');
    }} else {{
        player.pause();
        play_btn.attr('class', 'mute');
    }}
}}

window.onload = function () {{
    content.sign = getPureStr(content.signature).pxWidth('18px Satisfy, serif');
    document.title = _d.title;
    $('#recipient').append(_d.recipient);
    $('#flipback').text(_d.sender);
    $('#music').attr('src', _d.bgm);
    $('#envelope').fadeIn('slow');

    var currentUrl = window.location.href;
    var firstIndex = currentUrl.indexOf("#");
    if (firstIndex <= 0) window.location.href = currentUrl + "#contact";

    var contact = $('#contact');
    var mtop = (window.innerHeight - contact.height()) * 0.5;
    contact.css('margin-top', mtop + 'px');
    $('body').css('opacity', '1');
    $('#jsi-cherry-container').css('z-index', '-99');
}};

window.onresize = function () {{
    var cherry_container = $('#jsi-cherry-container');
    var canvas = cherry_container.find('canvas').eq(0);
    canvas.height(cherry_container.height());
    canvas.width(cherry_container.width());
}};'''

# ================================================================
# Assemble HTML
# ================================================================
print("Assembling HTML...")

# Shaders inlined directly (raw, readable)
shaders_vsh = '''uniform mat4 uProjection;
uniform mat4 uModelview;
uniform vec3 uResolution;
uniform vec3 uOffset;
uniform vec3 uDOF;
uniform vec3 uFade;
attribute vec3 aPosition;
attribute vec3 aEuler;
attribute vec2 aMisc;
varying vec3 pposition;
varying float psize;
varying float palpha;
varying float pdist;
varying vec3 normX;
varying vec3 normY;
varying vec3 normZ;
varying vec3 normal;
varying float diffuse;
varying float specular;
varying float rstop;
varying float distancefade;
void main(void) {
    vec4 pos = uModelview * vec4(aPosition + uOffset, 1.0);
    gl_Position = uProjection * pos;
    gl_PointSize = aMisc.x * uProjection[1][1] / -pos.z * uResolution.y * 0.5;
    pposition = pos.xyz;
    psize = aMisc.x;
    pdist = length(pos.xyz);
    palpha = smoothstep(0.0, 1.0, (pdist - 0.1) / uFade.z);
    vec3 elrsn = sin(aEuler);
    vec3 elrcs = cos(aEuler);
    mat3 rotx = mat3(1.0, 0.0, 0.0, 0.0, elrcs.x, elrsn.x, 0.0, -elrsn.x, elrcs.x);
    mat3 roty = mat3(elrcs.y, 0.0, -elrsn.y, 0.0, 1.0, 0.0, elrsn.y, 0.0, elrcs.y);
    mat3 rotz = mat3(elrcs.z, elrsn.z, 0.0, -elrsn.z, elrcs.z, 0.0, 0.0, 0.0, 1.0);
    mat3 rotmat = rotx * roty * rotz;
    normal = rotmat[2];
    mat3 trrotm = mat3(rotmat[0][0], rotmat[1][0], rotmat[2][0], rotmat[0][1], rotmat[1][1], rotmat[2][1], rotmat[0][2], rotmat[1][2], rotmat[2][2]);
    normX = trrotm[0];
    normY = trrotm[1];
    normZ = trrotm[2];
    const vec3 lit = vec3(0.6917144638660746, 0.6917144638660746, -0.20751433915982237);
    float tmpdfs = dot(lit, normal);
    if(tmpdfs < 0.0) {
        normal = -normal;
        tmpdfs = dot(lit, normal);
    }
    diffuse = 0.4 + tmpdfs;
    vec3 eyev = normalize(-pos.xyz);
    if(dot(eyev, normal) > 0.0) {
        vec3 hv = normalize(eyev + lit);
        specular = pow(max(dot(hv, normal), 0.0), 20.0);
    } else {
        specular = 0.0;
    }
    rstop = clamp((abs(pdist - uDOF.x) - uDOF.y) / uDOF.z, 0.0, 1.0);
    rstop = pow(rstop, 0.5);
    distancefade = min(1.0, exp((uFade.x - pdist) * 0.69315 / uFade.y));
}'''

shaders_fsh = '''#ifdef GL_ES
precision highp float;
#endif
uniform vec3 uDOF;
uniform vec3 uFade;
const vec3 fadeCol = vec3(0.08, 0.03, 0.06);
varying vec3 pposition;
varying float psize;
varying float palpha;
varying float pdist;
varying vec3 normX;
varying vec3 normY;
varying vec3 normZ;
varying vec3 normal;
varying float diffuse;
varying float specular;
varying float rstop;
varying float distancefade;
float ellipse(vec2 p, vec2 o, vec2 r) {
    vec2 lp = (p - o) / r;
    return length(lp) - 1.0;
}
void main(void) {
    vec3 p = vec3(gl_PointCoord - vec2(0.5, 0.5), 0.0) * 2.0;
    vec3 d = vec3(0.0, 0.0, -1.0);
    float nd = normZ.z;
    if(abs(nd) < 0.0001) discard;
    float np = dot(normZ, p);
    vec3 tp = p + d * np / nd;
    vec2 coord = vec2(dot(normX, tp), dot(normY, tp));
    const float flwrsn = 0.258819045102521;
    const float flwrcs = 0.965925826289068;
    mat2 flwrm = mat2(flwrcs, -flwrsn, flwrsn, flwrcs);
    vec2 flwrp = vec2(abs(coord.x), coord.y) * flwrm;
    float r;
    if(flwrp.x < 0.0) {
        r = ellipse(flwrp, vec2(0.065, 0.024) * 0.5, vec2(0.36, 0.96) * 0.5);
    } else {
        r = ellipse(flwrp, vec2(0.065, 0.024) * 0.5, vec2(0.58, 0.96) * 0.5);
    }
    if(r > rstop) discard;
    vec3 col = mix(vec3(1.0, 0.8, 0.75), vec3(1.0, 0.9, 0.87), r);
    float grady = mix(0.0, 1.0, pow(coord.y * 0.5 + 0.5, 0.35));
    col *= vec3(1.0, grady, grady);
    col *= mix(0.8, 1.0, pow(abs(coord.x), 0.3));
    col = col * diffuse + specular;
    col = mix(fadeCol, col, distancefade);
    float alpha = (rstop > 0.001)? (0.5 - r / (rstop * 2.0)) : 1.0;
    alpha = smoothstep(0.0, 1.0, alpha) * palpha;
    gl_FragColor = vec4(col * 0.5, alpha);
}'''

html = f'''<!DOCTYPE html>
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
<meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<meta name="description" content="Put on headphones" />
<title>eLuvLetter</title>
<link rel="shortcut icon" type="image/x-icon" href="{imgs['favicon.ico']}" />
<link href="https://fonts.googleapis.com/css2?family=Dancing+Script:wght@400;500;600;700&family=Ma+Shan+Zheng&family=ZCOOL+KuaiLe&family=ZCOOL+QingKe+HuangYou&display=swap" rel="stylesheet">
<style>
{css_min}
</style>
<script src="https://cdn.bootcdn.net/ajax/libs/jquery/3.7.1/jquery.min.js"></script>
</head>
<body class="unselect">
<div id="jsi-cherry-container"><canvas id="sakura"></canvas></div>
<div id="envelope">
<section class="container" id="contact">
<form class="flip">
<div class="front">
<a id="stamp" href="#"><img src="{imgs['hello kitty.png']}" alt="stamp"></a>
<span id="recipient"></span>
</div>
<div id="content" class="back">
<div id="letter">
<div class="container">
<div class="flip">
<div class="front"></div>
<div class="back">
<div id="data"><p class="letter"></p></div>
<a id="close" href="#"></a>
</div>
</div>
</div>
</div>
<div id="top">
<a id="wax-half" href="#"></a>
<a id="flipback" href="#contact">&hearts;</a>
</div>
<div id="lid" class="container">
<div class="flip">
<div class="front">
<a id="open" href="#content"><span id="wax"></span></a>
</div>
<div class="back"></div>
</div>
</div>
</div>
</form>
</section>
<div id="footer">
<audio id="music" preload="none" loop></audio>
<a id="music_btn" class="play" href="javascript:playPause();"></a>
</div>
</div>

<!-- sakura vertex shader -->
<script id="sakura_point_vsh" type="x-shader/x_vertex">
{shaders_vsh}
</script>
<!-- sakura fragment shader -->
<script id="sakura_point_fsh" type="x-shader/x_fragment">
{shaders_fsh}
</script>
<!-- effects common vertex shader -->
<script id="fx_common_vsh" type="x-shader/x_vertex">
uniform vec3 uResolution;
attribute vec2 aPosition;
varying vec2 texCoord;
varying vec2 screenCoord;
void main(void) {
    gl_Position = vec4(aPosition, 0.0, 1.0);
    texCoord = aPosition.xy * 0.5 + vec2(0.5, 0.5);
    screenCoord = aPosition.xy * vec2(uResolution.z, 1.0);
}
</script>
<!-- background fragment shader -->
<script id="bg_fsh" type="x-shader/x_fragment">
#ifdef GL_ES
precision highp float;
#endif
uniform vec2 uTimes;
varying vec2 texCoord;
varying vec2 screenCoord;
void main(void) {
    vec3 col;
    float c;
    vec2 tmpv = texCoord * vec2(0.8, 1.0) - vec2(0.95, 1.0);
    c = exp(-pow(length(tmpv) * 1.8, 2.0));
    col = mix(vec3(0.02, 0.0, 0.03), vec3(0.96, 0.98, 1.0) * 1.5, c);
    gl_FragColor = vec4(col * 0.5, 1.0);
}
</script>
<!-- bright buffer fragment shader -->
<script id="fx_brightbuf_fsh" type="x-shader/x_fragment">
#ifdef GL_ES
precision highp float;
#endif
uniform sampler2D uSrc;
uniform vec2 uDelta;
varying vec2 texCoord;
varying vec2 screenCoord;
void main(void) {
    vec4 col = texture2D(uSrc, texCoord);
    gl_FragColor = vec4(col.rgb * 2.0 - vec3(0.5), 1.0);
}
</script>
<!-- directional blur fragment shader -->
<script id="fx_dirblur_r4_fsh" type="x-shader/x_fragment">
#ifdef GL_ES
precision highp float;
#endif
uniform sampler2D uSrc;
uniform vec2 uDelta;
uniform vec4 uBlurDir;
varying vec2 texCoord;
varying vec2 screenCoord;
void main(void) {
    vec4 col = texture2D(uSrc, texCoord);
    col = col + texture2D(uSrc, texCoord + uBlurDir.xy * uDelta);
    col = col + texture2D(uSrc, texCoord - uBlurDir.xy * uDelta);
    col = col + texture2D(uSrc, texCoord + (uBlurDir.xy + uBlurDir.zw) * uDelta);
    col = col + texture2D(uSrc, texCoord - (uBlurDir.xy + uBlurDir.zw) * uDelta);
    gl_FragColor = col / 5.0;
}
</script>
<!-- common fragment shader template -->
<script id="fx_common_fsh" type="x-shader/x_fragment">
#ifdef GL_ES
precision highp float;
#endif
uniform sampler2D uSrc;
uniform vec2 uDelta;
varying vec2 texCoord;
varying vec2 screenCoord;
void main(void) {
    gl_FragColor = texture2D(uSrc, texCoord);
}
</script>
<!-- post process vertex shader -->
<script id="pp_final_vsh" type="x-shader/x_vertex">
uniform vec3 uResolution;
attribute vec2 aPosition;
varying vec2 texCoord;
varying vec2 screenCoord;
void main(void) {
    gl_Position = vec4(aPosition, 0.0, 1.0);
    texCoord = aPosition.xy * 0.5 + vec2(0.5, 0.5);
    screenCoord = aPosition.xy * vec2(uResolution.z, 1.0);
}
</script>
<!-- post process fragment shader -->
<script id="pp_final_fsh" type="x-shader/x_fragment">
#ifdef GL_ES
precision highp float;
#endif
uniform sampler2D uSrc;
uniform sampler2D uBloom;
uniform vec2 uDelta;
varying vec2 texCoord;
varying vec2 screenCoord;
void main(void) {
    vec4 srccol = texture2D(uSrc, texCoord) * 2.0;
    vec4 bloomcol = texture2D(uBloom, texCoord);
    vec4 col;
    col = srccol + bloomcol * (vec4(1.0) + srccol);
    col *= smoothstep(1.0, 0.0, pow(length((texCoord - vec2(0.5)) * 2.0), 1.2) * 0.5);
    col = pow(col, vec4(0.45454545454545));
    gl_FragColor = vec4(col.rgb, 1.0);
    gl_FragColor.a = 1.0;
}
</script>

<script>
{typed_js}
</script>
<script>
{sakura_js}
</script>
<script>
{letter_js}
</script>
<script>
{main_script}
</script>
</body>
</html>'''

output = os.path.join(BASE, 'index.html')
with open(output, 'w', encoding='utf-8') as f:
    f.write(html)

size = os.path.getsize(output)
print(f'\nDone! index.html: {size:,} bytes ({size/1024/1024:.2f} MB)')

# Cleanup
os.remove(opt_path)
os.remove(os.path.join(BASE, 'build.py'))

print('\nVerification:')
checks = [
    ('var _d = {', 'content data declared'),
    ('var envelope_opened', 'state declared'),
    ('var content = {', 'content object declared'),
    ('function playPause', 'playPause defined'),
    ('window.onload = function', 'window.onload defined'),
]
for pattern, desc in checks:
    print(f"  {'OK' if pattern in html else 'MISSING'}: {desc}")
