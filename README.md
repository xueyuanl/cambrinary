# Usage
In python3 and the version must be 3.5.3 or later. to install package from a local checkout, run:
```
pip3 install .
```

or from PyPI:
```
pip3 install cambrinary
```
Look up 'hello' for example:
```
cambrinary -w hello
```
![word hello](./images/hello)

### multi-languages support
in chinese(traditional)
```
cambrinary -w world -t chinese
```
![word world](./images/world)
#### Supported language list
- english
- french
- german
- chinese
- japanese
- italian 
- russian (temporarily no, cause cambrige web issue)

### multi-words support
powered by coroutine, support as many as words you like,
```
cambrinary -w hello word
```
![word hello-world](./images/hello-world)

or
```
cambrinary -w hello word -t chinese
```
even or more
```
cambrinary -w one two three four five -t french
```

### Support phrase
```
cambrinary -w kick-off
```
or
```
cambrinary -w kick-off -t japanese
```
### Customize your color scheme
Your cambrinary, you design.

Use [conf.json](./cambrinary/conf.json) to customize the color scheme, for instance,
setting `pronunciation`, `definition` or `example_sentence` as you like. They could be in `bold` format, `blue` foreground  and `black` background, or any supported format and colors.
All supported color please refer to [color_const.py](./cambrinary/color_const.py).

### Log
logs is written into `~/.local/share/cambrinary/dict.log` in the append way.

### Road map
more development plan, please refer to [Wiki](https://github.com/xueyuanl/cambrinary/wiki/Road-Map)
# Help
```
cambrinary --help
```
