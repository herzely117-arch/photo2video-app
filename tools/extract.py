"""Extract English UI strings from index.html: L('he','en') calls + EN?x:y literals. ${..} -> {0},{1}."""
import json, re, sys
src = open(sys.argv[1] if len(sys.argv) > 1 else "index.html").read()

def read_str(s, i):
    q = s[i]; j = i + 1; out = ""; depth = 0
    while j < len(s):
        c = s[j]
        if c == "\\": out += s[j:j+2]; j += 2; continue
        if q == "`" and s.startswith("${", j):
            k = j + 2; d = 1
            while d:
                if s[k] == "{": d += 1
                elif s[k] == "}": d -= 1
                elif s[k] in "'\"`":
                    _, k = read_str(s, k); continue
                k += 1
            out += "\x00"; j = k; continue
        if c == q: return out, j + 1
        out += c; j += 1
    raise ValueError

keys = []
for m in re.finditer(r"(?<![\w$.])L\(", src):
    i = m.end()
    try:
        if src[i] not in "'\"`": continue
        h, i = read_str(src, i)
        while src[i] in " ,\n": i += 1
        if src[i] not in "'\"`": continue
        e, i = read_str(src, i)
    except Exception:
        continue
    n = [0]
    def ph(_):
        n[0] += 1; return "{%d}" % (n[0] - 1)
    k = re.sub("\x00", ph, e).replace("\\n", "\n").replace("\\'", "'")
    if re.search("[A-Za-z]", k) and k not in keys: keys.append(k)
print(json.dumps(keys, ensure_ascii=False, indent=0))
