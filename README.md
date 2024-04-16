# q3ctf bot
## Run
```bash
python3 qutpy.py
```
or with docker
```bash
docker build -t qutpy .
docker run -it --rm --name qutpyd qutpy
```

Make sure you've installed the required pip packages

## Available App Commands
Submit a flag to a challenge
```
/submit <chal_id> <flag> 
```
View details of a challenge
```
/chal <chal_id>
```
