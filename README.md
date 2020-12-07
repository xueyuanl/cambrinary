# Usage
From PyPI:
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
- russian
- korean

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

## For develop mode
You can change and test locally by, git clone the repo, `cd` in the repo folder, run:
```
python3 -m venv venv
source venv/bin/activate
pip3 install .  (try `curl https://bootstrap.pypa.io/get-pip.py | python3` to update pip3 if any error)
# and then
cambrinary -w world
```
Once you change the code, re-run `pip3 install .`

### Log
logs is written into `~/.local/share/cambrinary/dict.log` in the append way.

### Road map
more development plan, please refer to [Wiki](https://github.com/xueyuanl/cambrinary/wiki/Road-Map)
# Help
```
cambrinary --help
```
