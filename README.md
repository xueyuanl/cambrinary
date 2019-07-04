# Usage
use python 3 env, to install package dependencies using pip3, run:
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

in german
```
python3 cambrinary.py -w world -t german
```
### Supported language list
- english
- french
- german
- chinese
- japanese
- russian
- italian
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
