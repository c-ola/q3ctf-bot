# q3ctf bot
## Run
First make sure you've installed the required pip packages
```bash
pip install -r requirements.txt
```
Make sure to have a `.env` file in the following format
```
DISCORD_TOKEN=<token_of_the_main_bot_you_want_to_run_on>
TESTBOT_TOKEN=<used_for_a_private_testbot>
OWNER_USER_ID=<your_user_id>
TEST_GUILD_ID=<guild_id_of_the_test_server>
```
Run normally
```bash
python3 ./src/qutpy.py
```
or with docker
```bash
docker build -t qutpy .
docker run -it --rm --name qutpyd qutpy
```

## Testing
This will use the test bot token
```bash
BOT_TEST_MODE=1 python3 ./src/qutpy.py
```

## Available App Commands
Submit a flag to a challenge
```
/submit <chal_id> <flag> 
```
```
/create 
```
```
/modify 
```
```
/sync & /synch 
```

