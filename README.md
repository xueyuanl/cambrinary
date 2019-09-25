### NOTE: After a quite hard and dull work to rematch the html tags and refactor,the cambrinary comes back. Thanks for your waiting. By now, no support for russian and italian, cause the cambridge server issue.
# Usage
In python3 and the version must be 3.5.3 or later. to install package from a local checkout, run:
```
pip3 install .
```

or from PyPI:
```
pip3 install cambrinary
```
Look up 'world' for example:
```
cambrinary -w world
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
- russian (temporarily no)
- italian (temporarily no)

### multi-words support
powered by coroutine, support as many as words you like,
```
cambrinary -w hello word
```
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
logs is written into `$XDG_DATA_HOME/cambrinary/dict.log` (or `~/.local/share/cambrinary/dict.log`) in append way.
# Help
```
cambrinary --help
```
