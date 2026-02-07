import os
pkg_size = 0
for f in os.listdir('.'):
    if f.endswith('.tar.gz'): pkg_size += os.path.getsize(f)
pkg_mb = pkg_size / (1024*1024)
md = f"# 🌌 Omni-Intelligence Hub (1 Million)\n\n![Status](https://img.shields.io/badge/Status-Stable-green) ![Data](https://img.shields.io/badge/Records-1,000,000+-blue)\n"
md += f"## 🎛️ Mission Control\n- **Payload:** {pkg_mb:.2f} MB\n- **Security:** 500k\n- **Jobs:** 300k\n"
with open("README.md", "w") as f: f.write(md)
