# mcwiki

> A scraping library for the Minecraft wiki.

```python
import mcwiki

page = mcwiki.load("Advancement/JSON format")
section = page["File Format"]
print(section.extract(mcwiki.TREE))
```

---

License - [MIT](https://github.com/vberlier/mcwiki/blob/master/LICENSE)
