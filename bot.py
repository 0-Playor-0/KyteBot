import os
import discord
import json
import requests
from discord.ext import commands
import aiofiles

# Load token from environment variables for security
OurToken = os.getenv('DISCORD_BOT_TOKEN')

emotirl = "https://d3f8-35-201-212-43.ngrok-free.app/feeling_pred"
disorderl = ""
positivityl = ""
toxicityrl = "https://d79c-35-245-112-115.ngrok-free.app/toxicity_pred"

bot = commands.Bot(command_prefix='-', intents=discord.Intents.all())

@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))

@bot.command(name='reports')
async def reports(ctx):
    async with aiofiles.open('database.txt', 'r') as db_file:
        Data = eval(await db_file.read())
    Client = ctx.author.id
    DataParse = Data[0][Client]
    print(DataParse)
    DataParse['moodRating'] = 100 - (DataParse['anxiety'] + DataParse['sadness'] + DataParse['anger']) / 3
    DataParse = Data[0]
    
    embed = discord.Embed(
        title="Your Comprehensive Report",
        description="",
        color=discord.Colour.blue()
    )
    embed.set_thumbnail(url="https://w7.pngwing.com/pngs/291/499/png-transparent-robot-cartoon-robot-s-cartoon-fictional-character-material-thumbnail.png")
    embed.add_field(
        name="Mood Rating",
        value=f"Your mood rating is {DataParse[ctx.author.id]['moodRating']}",
        inline=True
    )
    embed.add_field(
        name="Positivity",
        value=f"Your positivity rating is {DataParse[ctx.author.id]['positivity']}",
        inline=True
    )
    embed.add_field(
        name="Personality",
        value=f"Your personality rating is {DataParse[ctx.author.id]['personality']}",
        inline=True
    )
    
    await ctx.reply(embed=embed)

@bot.event
async def on_message(message):
    if message.author.id == bot.user.id:
        return
    
    input_data_for_model = {'StringInput': message.content}
    async with aiofiles.open('database.txt', 'r') as db_file:
        Data = eval(await db_file.read())
    
    DataParse = Data[0]
    Client = message.author.id
    
    if Client not in DataParse:
        DataParse[Client] = {
            "moodRating": 0, "positivity": 100, "personality": 100, "anger": 0,
            "anxiety": 0, "sadness": 0, "BPD": 0, "bipolar": 0, "depression": 0,
            "schizofrenia": 0, "mentalillness": 0
        }
        await message.channel.send(f'Hey @{message.author}! You have been added to my database')
        async with aiofiles.open('database.txt', 'w') as db_file:
            Data[0] = DataParse
            await db_file.write(str(Data))
    else:
        if len(message.content) > 15:
            input_json = json.dumps(input_data_for_model)
            try:
                emotion_json = requests.post(emotirl, data=input_json)
                toxic_json = requests.post(toxicityrl, data=input_json)

                if toxic_json.status_code == 200:
                    response_text = str(toxic_json.text.strip().strip('"'))
                    print(response_text)
                else:
                    print(f"Error: {toxic_json.status_code} {toxic_json.text}")    
                    return

                response_lines = response_text.strip().split('\\n')
                print(response_lines)

                flag = None
                for line in response_lines:
                    print(line)
                    if ':' in line:
                        key, value = line.split(':', 1)
                        if value.strip() == 'True':
                            flag = key.strip()
                            break

                if emotion_json.status_code == 200:
                    response_texte = str(emotion_json.text.strip().strip('"'))
                    print(response_texte)
                else:
                    print(f"Error: {emotion_json.status_code} {emotion_json.text}")    
                    return

                response_linese = response_texte.strip().split('\\n')
                print(response_linese)

                flage = None
                for line in response_linese:
                    print(line)
                    if ':' in line:
                        key, value = line.split(':', 1)
                        if value.strip() == 'True':
                            flage = key.strip()
                            break

                if flag =='toxic'or flag =='severe_toxicity' or flag == 'threat' or flag == 'identity_hate' and DataParse[Client]['personality'] > 0:
                    DataParse[Client]['personality'] -= 1
                
                if flage == 'sadness' or flage == 'liwc_negative_emotion':
                    DataParse[Client]['sadness'] += 1
                
                if flage == 'liwc_anger':
                    DataParse[Client]['anger'] += 1
                
                if flage == 'liwc_anxiety':
                    DataParse[Client]['anxiety'] += 1

                async with aiofiles.open('database.txt', 'w') as db_file:
                    Data[0] = DataParse
                    await db_file.write(str(Data))

                async with aiofiles.open('database.txt', 'w') as db_file:
                    Data[0] = DataParse
                    await db_file.write(str(Data))
            
            except requests.RequestException as e:
                print(f"Error with the request: {e}")
    
    await bot.process_commands(message)

bot.run(OurToken)