# Usage
In python3 and the version must be 3.5.3 or later. to install package dependencies using pip3, run:
```
pip3 install -r requirements.txt
```
Look up 'world' for example:
```
python3 cambrinary.py -w world
```
![word hello](./images/hello)

### multi-languages support
in chinese(traditional)
```
python3 cambrinary.py -w world -t chinese
```
![word world](./images/world)
#### Supported language list
- english
- french
- german
- chinese
- japanese
- russian
- italian

### multi-words support
powered by coroutine, support as many as words you like,
```
python3 cambrinary.py -w hello word
```
or
```
python3 cambrinary.py -w hello word -t chinese
```
even or more
```
python3 cambrinary.py -w one two three four five -t french
```

### Support phrase
```
python3 cambrinary.py -w kick-off
```
or
```
python3 cambrinary.py -w kick-off -t japanese
```
### Customize your color scheme
Your cambrinary, you design.

Use [conf.json](conf.json) to customize the color scheme, for instance,
setting `pronunciation`, `definition` or `example_sentence` as you like. They could be in `bold` format, `blue` foreground  and `black` blackground, or any supported format and colors.
All supported color please refer to [color_const.py](color_const.py).
# Help
```
python3 cambrinary.py --help
```
