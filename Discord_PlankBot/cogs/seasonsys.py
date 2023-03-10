import discord
from discord.ext import commands, tasks
from datetime import datetime, timedelta
from random import randint
import json
from termcolor import colored


class SeasonSystem(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.check_db.start()
        print('Season System Cog Online')

    @tasks.loop(hours=24)
    async def check_db(self):
        seasons = dbload('seasons')

        print(colored('\nUpdate time:{}'.format(datetime.now()), 'green'))

        try:
            for server in seasons.copy():
                if seasons[server]["isOn"]:
                    endDate = datetime.strptime(seasons[server]["date"], '%Y-%m-%d %H:%M:%S')
                    if endDate < datetime.now():
                        pusers = dbload('premiumusers')
                        users = dbload('users')

                        for user in pusers[str(server)].copy():
                            del pusers[str(server)][user]

                        for user in users[str(server)]:
                            users[str(server)][user]['plankpass'] = False

                        dbsave(pusers, 'premiumusers')
                        dbsave(users, 'users')
                        del pusers
                        del users

                        del seasons[str(server)]['rewards']
                        seasons[str(server)]['rewards'] = {}
                        for i in range(1, 41):
                            seasons[str(server)]['rewards'][str(i)] = {}

                        seasons[str(server)]["isOn"] = False
                        seasons[str(server)]["name"] = ""
                        seasons[str(server)]["date"] = ""
                        seasons[str(server)]["role"] = ""
                        seasons[id]['siderole'] = None
                        seasons[str(server)]["price"] = -1
            print(colored("Season Database Updated", 'green'))

        except Exception as e:
            print(colored("Season Database couldn\'t be updated:\n\t{}".format(e), 'yellow'))

        dbsave(seasons, 'seasons')

    @commands.Cog.listener()
    async def on_member_join(self, member):

        seasons = dbload('seasons')

        if seasons[str(member.guild.id)]['isOn']:
            del seasons
            if not member.bot:
                pusers = dbload('premiumusers')

                await update_db(self, pusers, member, member.guild.id)

                dbsave(pusers, 'premiumusers')

    @commands.Cog.listener()
    async def on_message(self, message):

        try:
            if str(message.channel.type) != 'private':

                seasons = dbload('seasons')
                if seasons[str(message.guild.id)]['isOn']:
                    del seasons
                    if not message.author.bot:
                        pusers = dbload('premiumusers')
                        await update_db(self, pusers, message.author, message.guild.id)
                        await addExp(self, pusers, message.author, message.guild)

                        dbsave(pusers, 'premiumusers')

        except KeyError:
            print('Season Key Error\nMessage: {}\nAuthor: {}\nServer: {}'.format(message.content, message.author.name, message.guild.name))

    @commands.group(invoke_without_command=True)
    @commands.guild_only()
    async def ppreward(self, ctx):
        rewards = dbload('seasons')[str(ctx.guild.id)]['rewards']

        embed = discord.Embed(title='PlankPass Nyerem??nyei', description='A season nyerem??nyei',
                              color=0x8a7c74)

        embed.set_author(name=ctx.author, url=f'https://discord.com/users/{ctx.author.id}',
                         icon_url=ctx.author.avatar_url)

        embed.set_footer(
            text='Tov??bbi inform??ci??k??rt !pb help <parancs>'
        )

        for i in rewards:
            if not len(rewards[i]) == 0:
                if rewards[i]['type'] == "role":
                    role = ctx.guild.get_role(rewards[i]['id'])
                    embed.add_field(name='{}. tier'.format(i), value=role.mention, inline=False)
                elif rewards[i]['type'] == "bal":
                    embed.add_field(name='{}. tier'.format(i),
                                    value='{} <:plancoin:799180662166781992>'.format(rewards[i]['amount']),
                                    inline=False)
                else:
                    embed.add_field(name='{}. tier'.format(i),
                                    value='{} k??rtya\n{}'.format(rewards[i]['name'], rewards[i]['desc']), inline=False)

        await ctx.send(ctx.author.mention, embed=embed)

    @ppreward.command()
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def remove(self, ctx, tier: int):
        isOn = dbload('seasons')[str(ctx.guild.id)]['isOn']
        if not isOn:
            seasons = dbload('seasons')

            del seasons[str(ctx.guild.id)]['rewards'][str(tier)]

            embed = discord.Embed(
                title='Tier t??r??lve',
                description=None,
                color=0x8a7c74
            )

            embed.set_author(name=ctx.author, url=f'https://discord.com/users/{ctx.author.id}',
                             icon_url=ctx.author.avatar_url)

            embed.add_field(
                name='T??r??lted a k??vetkez?? tier rewardot',
                value=tier
            )

            seasons[str(ctx.guild.id)]['rewards'][str(tier)] = {}

            dbsave(seasons, 'seasons')

        else:
            embed = newErr('Akt??v Season-t nem tudsz szerkeszteni.')

        await ctx.send(ctx.author.mention, embed=embed)

    @remove.error
    async def remove_error(self, ctx, error):
        if isinstance(error, commands.errors.MissingRequiredArgument):
            embed = newErr('Nem adt??l meg Tier-t.')

            embed.add_field(
                name='Helyes parancs',
                value='`!pb ppreward remove <tier>`'
            )

            await ctx.send(embed=embed)

    @ppreward.group(invoke_without_command=True)
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def add(self, ctx):
        embed = discord.Embed(title='Aj??nd??k hozz??ad??sa',
                              description='PlankPass Tier Aj??nd??k hozz??ad??sa',
                              color=0x8a7c74)

        embed.set_author(name=ctx.author, url=f'https://discord.com/users/{ctx.author.id}',
                         icon_url=ctx.author.avatar_url)

        embed.set_author(name=ctx.guild.name,
                         url=f'https://discord.com/user/{ctx.guild.owner.id}',
                         icon_url=ctx.guild.icon_url)
        embed.add_field(name='K??rtya hozz??ad??sa',
                        value='ppreward add kartya <tier> \"<n??v>\" \"<le??r??s>\"',
                        inline=False)
        embed.add_field(name='Rang hozz??ad??sa',
                        value='ppreward add rang <tier> <rang>',
                        inline=False)
        embed.add_field(name='PlanCoin hozz??ad??sa',
                        value='ppreward add penz <tier> <??sszeg>',
                        inline=False)
        embed.set_footer(
            text='Tov??bbi inform??ci??k??rt !pb help <parancs>'
        )

        await ctx.send(ctx.author.mention, embed=embed)

    @add.command()
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def penz(self, ctx, tier: int, amount: int):
        isOn = dbload('seasons')[str(ctx.guild.id)]['isOn']
        if not isOn:
            rewards = dbload('seasons')

            if len(rewards[str(ctx.guild.id)]['rewards'][str(tier)]) == 0:
                rewards[str(ctx.guild.id)]['rewards'][str(tier)]['type'] = 'bal'
                rewards[str(ctx.guild.id)]['rewards'][str(tier)]['amount'] = amount

                embed = discord.Embed(title='Tier {}'.format(tier),
                                      description='Aj??nd??ka be??ll??tva.',
                                      color=0x8a7c74)

                embed.set_author(name=ctx.author, url=f'https://discord.com/users/{ctx.author.id}',
                                 icon_url=ctx.author.avatar_url)

            else:
                embed = newErr('Ezen a tieren m??r van aj??nd??k.')

            dbsave(rewards, 'seasons')
        else:
            embed = newErr('Akt??v Season-t nem tudsz szerkeszteni.')

        await ctx.send(ctx.author.mention, embed=embed)

    @penz.error
    async def penz_error(self, ctx, error):
        if isinstance(error, commands.errors.MissingRequiredArgument):
            embed = newErr('Nem adt??l meg Tier-t vagy ??sszeget.')

            embed.add_field(
                name='Helyes parancs',
                value='`!pb ppreward add penz <tier> <??sszeg>`'
            )

            await ctx.send(embed=embed)

    @add.command()
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def rang(ctx, tier: int, role: discord.Role):
        isOn = dbload('seasons')[str(ctx.guild.id)]['isOn']
        if not isOn:
            if not role.is_bot_managed():
                rewards = dbload('seasons')

                if len(rewards[str(ctx.guild.id)]['rewards'][str(tier)]) == 0:
                    rewards[str(ctx.guild.id)]['rewards'][str(tier)]['type'] = 'role'
                    rewards[str(ctx.guild.id)]['rewards'][str(tier)]['id'] = role.id

                    embed = discord.Embed(title='Tier {}'.format(tier),
                                          description='Aj??nd??ka be??ll??tva.',
                                          color=0x8a7c74)

                    embed.set_author(name=ctx.author, url=f'https://discord.com/users/{ctx.author.id}',
                                     icon_url=ctx.author.avatar_url)

                else:
                    embed = newErr('Ezen a tieren m??r van aj??nd??k.')

                dbsave(rewards, 'seasons')

            else:
                embed = newErr('Ez a rang Bot exkluz??v.')
                embed.add_field(
                    name='Adj meg m??sik rangot',
                    value='** **'
                )

        else:
            embed = newErr('Akt??v Season-t nem tudsz szerkeszteni.')

        await ctx.send(ctx.author.mention, embed=embed)

    @rang.error
    async def rang_error(self, ctx, error):
        if isinstance(error, commands.errors.MissingRequiredArgument):
            embed = newErr('Nem adt??l meg Tier-t vagy rangot.')

            embed.add_field(
                name='Helyes parancs',
                value='`!pb ppreward add rang <tier> <@rang>`'
            )

            await ctx.send(embed=embed)

            if isinstance(error, commands.errors.RoleNotFound):
                embed = newErr('Nem l??tezik ilyen rang.')

                embed.add_field(
                    name='Megadott rang',
                    value=error.argument,
                    inline=False
                )

                embed.add_field(
                    name='Helyes parancs',
                    value='`!pb ppreward add rang <tier> <@rang>`',
                    inline=False
                )
                await ctx.send(embed=embed)

    @add.command(aliases=['k??rtya', 'card'])
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def kartya(self, ctx, tier: int, name: str, desc: str):
        isOn = dbload('seasons')[str(ctx.guild.id)]['isOn']
        if not isOn:
            rewards = dbload('seasons')
            name = name.replace('_', ' ')
            desc = desc.replace('_', ' ')

            if len(rewards[str(ctx.guild.id)]['rewards'][str(tier)]) == 0:
                rewards[str(ctx.guild.id)]['rewards'][str(tier)]['type'] = "card"
                id = 0
                while id in rewards[str(ctx.guild.id)]['rewards']:
                    id = randint(6000, 10000)

                rewards[str(ctx.guild.id)]['rewards'][str(tier)]['id'] = id
                rewards[str(ctx.guild.id)]['rewards'][str(tier)]['name'] = name
                rewards[str(ctx.guild.id)]['rewards'][str(tier)]['desc'] = desc

                embed = discord.Embed(title='Tier {}'.format(tier),
                                      description='Aj??nd??ka be??ll??tva.',
                                      color=0x8a7c74)

                embed.set_author(name=ctx.author, url=f'https://discord.com/users/{ctx.author.id}',
                                 icon_url=ctx.author.avatar_url)

            else:
                embed = newErr('Ezen a tieren m??r van aj??nd??k.')

            dbsave(rewards, 'seasons')
        else:
            embed = newErr('Akt??v Season-t nem tudsz szerkeszteni.')

        await ctx.send(ctx.author.mention, embed=embed)

    @kartya.error
    async def kartya_error(self, ctx, error):
        if isinstance(error, commands.errors.MissingRequiredArgument):
            embed = newErr('Nem adt??l meg Tier-t, nevet vagy le??r??st.')

            embed.add_field(
                name='Helyes parancs',
                value='`!pb ppreward add kartya <tier> "n??v" "le??r??s"`'
            )

            await ctx.send(embed=embed)

    @commands.group(invoke_without_command=True)
    @commands.guild_only()
    async def season(self, ctx):

        season = dbload('seasons')[str(ctx.guild.id)]

        if season['isOn']:
            embed = discord.Embed(title=season['name'],
                                  description='A Season r??szletei',
                                  color=0x8a7c74)

            embed.set_author(name=ctx.author, url=f'https://discord.com/users/{ctx.author.id}',
                             icon_url=ctx.author.avatar_url)

            embed.add_field(name='Id??tartam',
                            value=season['date'],
                            inline=False)
            role = ctx.guild.get_role(season['role'])
            embed.add_field(name='Rang',
                            value=role.mention,
                            inline=False)
            embed.add_field(name='??r',
                            value='{} <:plancoin:799180662166781992>'.format(season['price']),
                            inline=False)

        else:
            embed = newErr('Nincs akt??v season')

        await ctx.send(ctx.author.mention, embed=embed)

    @season.command(aliases=['date', 'd??tum'])
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def datum(self, ctx, date: str):
        isOn = dbload('seasons')[str(ctx.guild.id)]['isOn']

        if not isOn:
            try:
                seasons = dbload('seasons')

                time = datetime.strptime(str(date), '%Y-%m-%d')

                if time < datetime.now() + timedelta(weeks=3):
                    embed = newErr('Helytelen id??t adt??l meg.')
                    embed.add_field(name='Inform??ci??:',
                                    value="A Season-nek legal??bb 1 h??nap hossz??nak kell lennie.")
                    await ctx.send(embed=embed)

                else:
                    seasons[str(ctx.guild.id)]['date'] = str(time)
                    embed = discord.Embed(title='Season hossza be??ll??tva',
                                          description='A k??vetkez?? season v??ge: {}'.format(str(time)),
                                          color=0x8a7c74)

                    embed.set_author(name=ctx.author, url=f'https://discord.com/users/{ctx.author.id}',
                                     icon_url=ctx.author.avatar_url)

                dbsave(seasons, 'seasons')

            except:
                embed = newErr('Helytelen id??t adt??l meg.')
                embed.add_field(
                    name='Helyes form??tum:',
                    value='??v-h??nap-nap\n*2021-09-29*'
                )

        else:
            embed = newErr('Akt??v Season-t nem tudsz szerkeszteni.')

        await ctx.send(ctx.author.mention, embed=embed)

    @datum.error
    async def datum_error(self, ctx, error):
        if isinstance(error, commands.errors.MissingRequiredArgument):
            embed = newErr('Nem adt??l meg d??tumot.')

            embed.add_field(
                name='Helyes parancs',
                value='`!pb season datum "??v-h??nap-nap"`'
            )

            await ctx.send(embed=embed)

    @season.command(aliases=['n??v', 'name'])
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def nev(self, ctx, name: str):
        isOn = dbload('seasons')[str(ctx.guild.id)]['isOn']
        if not isOn:
            seasons = dbload('seasons')

            name = name.replace('_', ' ')
            seasons[str(ctx.guild.id)]['name'] = name

            embed = discord.Embed(title='Season neve be??ll??tva',
                                  description='A k??vetkez?? season neve: {}'.format(name),
                                  color=0x8a7c74)

            embed.set_author(name=ctx.author, url=f'https://discord.com/users/{ctx.author.id}',
                             icon_url=ctx.author.avatar_url)

            await ctx.send(embed=embed)

            dbsave(seasons, 'seasons')
        else:
            embed = newErr('Akt??v Season-t nem tudsz szerkeszteni.')

        await ctx.send(ctx.author.mention, embed=embed)

    @nev.error
    async def nev_error(self, ctx, error):
        if isinstance(error, commands.errors.MissingRequiredArgument):
            embed = newErr('Nem adt??l meg nevet.')

            embed.add_field(
                name='Helyes parancs',
                value='`!pb season nev "n??v"`'
            )

            await ctx.send(embed=embed)

    @season.command(aliases=['role'])
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def rang(self, ctx, role: discord.Role):
        isOn = dbload('seasons')[str(ctx.guild.id)]['isOn']
        if not isOn:
            if not role.is_bot_managed():
                seasons = dbload('seasons')

                seasons[str(ctx.guild.id)]['role'] = role.id

                embed = discord.Embed(title='Season rang be??ll??tva',
                                      description='A k??vetkez?? season rangja: {}'.format(role.name),
                                      color=0x8a7c74)

                embed.set_author(name=ctx.author, url=f'https://discord.com/users/{ctx.author.id}',
                                 icon_url=ctx.author.avatar_url)

                dbsave(seasons, 'seasons')

            else:
                embed = newErr('Ez a rang Bot exkluz??v.')
                embed.add_field(
                    name='Adj meg m??sik rangot',
                    value='** **'
                )
        else:
            embed = newErr('Akt??v Season-t nem tudsz szerkeszteni.')

        await ctx.send(ctx.author.mention, embed=embed)

    @rang.error
    async def rang_error(self, ctx, error):
        if isinstance(error, commands.errors.MissingRequiredArgument):
            embed = newErr('Nem adt??l meg rangot.')

            embed.add_field(
                name='Helyes parancs',
                value='`!pb season rang <@rang>`'
            )

            await ctx.send(embed=embed)

        elif isinstance(error, commands.errors.RoleNotFound):
            embed = newErr('Nem l??tezik ilyen rang.')

            embed.add_field(
                name='Megadott rang',
                value=error.argument,
                inline=False
            )

            embed.add_field(
                name='Helyes parancs',
                value='`!pb season rang <@rang>`',
                inline=False
            )
            await ctx.send(embed=embed)

    @season.command(aliases=['siderole'])
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def mellekrang(self, ctx, role: discord.Role):
        isOn = dbload('seasons')[str(ctx.guild.id)]['isOn']
        if not isOn:
            if not role.is_bot_managed():
                seasons = dbload('seasons')

                seasons[str(ctx.guild.id)]['siderole'] = role.id

                embed = discord.Embed(title='Season rang be??ll??tva',
                                      description='A k??vetkez?? season mell??k rangja: {}'.format(role.name),
                                      color=0x8a7c74)

                embed.set_author(name=ctx.author, url=f'https://discord.com/users/{ctx.author.id}',
                                 icon_url=ctx.author.avatar_url)

                dbsave(seasons, 'seasons')

            else:
                embed = newErr('Ez a rang Bot exkluz??v.')
                embed.add_field(
                    name='Adj meg m??sik rangot',
                    value='** **'
                )
        else:
            embed = newErr('Akt??v Season-t nem tudsz szerkeszteni.')

        await ctx.send(ctx.author.mention, embed=embed)

    @mellekrang.error
    async def rang_error(self, ctx, error):
        if isinstance(error, commands.errors.MissingRequiredArgument):
            embed = newErr('Nem adt??l meg rangot.')

            embed.add_field(
                name='Helyes parancs',
                value='`!pb season mellekrang <@rang>`'
            )

            await ctx.send(embed=embed)

        elif isinstance(error, commands.errors.RoleNotFound):
            embed = newErr('Nem l??tezik ilyen rang.')

            embed.add_field(
                name='Megadott rang',
                value=error.argument,
                inline=False
            )

            embed.add_field(
                name='Helyes parancs',
                value='`!pb season mellekrang <@rang>`',
                inline=False
            )
            await ctx.send(embed=embed)

    @season.command(aliases=['price', '??r'])
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def ar(self, ctx, price: int):
        isOn = dbload('seasons')[str(ctx.guild.id)]['isOn']
        if not isOn:
            seasons = dbload('seasons')

            seasons[str(ctx.guild.id)]['price'] = price

            embed = discord.Embed(title='PlankPass ??ra be??ll??tva',
                                  description='A k??vetkez?? PlankPass ??ra: {}'.format(price),
                                  color=0x8a7c74)

            embed.set_author(name=ctx.author, url=f'https://discord.com/users/{ctx.author.id}',
                             icon_url=ctx.author.avatar_url)

            dbsave(seasons, 'seasons')
        else:
            embed = newErr('Akt??v Season-t nem tudsz szerkeszteni.')

        await ctx.send(ctx.author.mention, embed=embed)

    @ar.error
    async def ar_error(self, ctx, error):
        if isinstance(error, commands.errors.MissingRequiredArgument):
            embed = newErr('Nem adt??l meg ??rat.')

            embed.add_field(
                name='Helyes parancs',
                value='`!pb season ar <??r>`'
            )

            await ctx.send(embed=embed)

    @season.command(aliases=['start'])
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def kezd(self, ctx):
        isOn = dbload('seasons')[str(ctx.guild.id)]['isOn']

        if not isOn:
            seasons = dbload('seasons')

            if seasons[str(ctx.guild.id)]['date'] == "":
                embed = newErr('Nincs be??ll??tva a season hossza.')
                await ctx.send(embed=embed)

            elif seasons[str(ctx.guild.id)]['name'] == "":
                embed = newErr('Nincs be??ll??tva a season neve.')
                await ctx.send(embed=embed)

            elif seasons[str(ctx.guild.id)]['role'] == "":
                embed = newErr('Nincs be??ll??tva a season rangja.')
                await ctx.send(embed=embed)

            elif seasons[str(ctx.guild.id)]['price'] == -1:
                embed = newErr('Nincs megadva a PlankPass ??ra.')
                await ctx.send(embed=embed)

            else:

                embed = discord.Embed(
                    title='Biztosan elkezded a Seasont?',
                    description='Kezd??s el??tt aj??nlatos megn??zni a Tier aj??nd??kokat, mivel kezd??s ut??n nem tudod m??dos??tani.',
                    color=0x8a7c74
                )

                embed.set_author(name=ctx.author, url=f'https://discord.com/users/{ctx.author.id}',
                                 icon_url=ctx.author.avatar_url)

                embed.add_field(
                    name='Ha k??szen ??llsz ??rd be',
                    value='Igen'
                )

                embed.set_footer(
                    text='V??laszodra 5 m??sodperc ??ll rendelkez??sre'
                )

                msg = await ctx.send(ctx.author.mention, embed=embed)

                def check(m):
                    return m.channel == ctx.channel and m.content.lower() == 'igen' and m.author == ctx.author

                try:
                    ready = await self.bot.wait_for('message', timeout=5, check=check)

                    if ready:
                        embed = discord.Embed(title='Season elkezdve',
                                              description='Elind??tottad a {} Season-t'.format(
                                                  seasons[str(ctx.guild.id)]['name']),
                                              color=0x00b000)

                        embed.set_author(name=ctx.guild.owner,
                                         url=f'https://discord.com/users/{ctx.guild.owner.id}',
                                         icon_url=ctx.guild.owner.avatar_url)

                        seasons[str(ctx.guild.id)]['isOn'] = True

                        dbsave(seasons, 'seasons')

                        await msg.edit(embed=embed)

                except:
                    embed = newErr('Letelt a d??nt??s id??.')
                    embed.add_field(
                        name='A season nem lett elind??tva',
                        value='** **'
                    )
                    await ctx.send(ctx.author.mention, embed=embed)
        else:
            embed = newErr('Akt??v Season-t nem tudsz ??jra elkezdeni.')
            await ctx.send(ctx.author.mention, embed=embed)

    @season.command(aliases=['stop', 'le??ll??t'])
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def leallit(self, ctx):
        isOn = dbload('seasons')[str(ctx.guild.id)]['isOn']

        if isOn:
            seasons = dbload('seasons')

            seasons[str(ctx.guild.id)]['isOn'] = False

            embed = discord.Embed(
                title='Season meg??ll??tva',
                description='A Season-t b??rmikor ??jra ind??thatod',
                colour=0xb80000
            )

            embed.set_author(name=ctx.guild.owner,
                             url=f'https://discord.com/users/{ctx.guild.owner.id}',
                             icon_url=ctx.guild.owner.avatar_url)

            embed.add_field(
                name='Le??ll??tottad a Season-t',
                value='** **',
                inline=False
            )

            embed.add_field(
                name='??jra ind??t??shoz ??rd',
                value='`!pb season kezd`',
                inline=False
            )

            dbsave(seasons, 'seasons')

        else:
            embed = newErr('Nincs akt??v season.')

        await ctx.send(embed=embed)

    @season.command()
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def kikapcsol(self, ctx):
        isOn = dbload('seasons')[str(ctx.guild.id)]['isOn']

        if isOn:
            try:
                seasons = dbload('seasons')

                embed = discord.Embed(
                    title='Season kikapcsol??sa',
                    description='Biztosan kikapcsolod a Season-t?\n'
                                'Ezzel elveszed mindenki PlankPass-??t ??s mindenki Tiere 0 lesz.\n'
                                'Ezt nem vonhatod vissza.',
                    colour=0x8a7c74
                )

                embed.add_field(
                    name='Ha k??szen ??llsz ??rd',
                    value='Igen'
                )

                embed.set_footer(
                    text='V??laszodra 5 m??sodperc van'
                )

                msg = await ctx.send(embed=embed)

                def check(m):
                    return m.content.lower() == 'igen' and m.author == ctx.author

                choice = await self.bot.wait_for('message', check=check, timeout=5)

                if choice:
                    embed = discord.Embed(
                        title='Season le??ll??tva',
                        description='Le??ll??tottad a Season-t.',
                        colour=0xff0000
                    )

                    server = ctx.guild.id

                    pusers = dbload('premiumusers')
                    users = dbload('users')

                    for user in pusers[str(server)].copy():
                        del pusers[str(server)][user]

                    for user in users[str(server)]:
                        users[str(server)][user]['plankpass'] = False

                    dbsave(pusers, 'premiumusers')
                    dbsave(users, 'users')
                    del pusers
                    del users

                    del seasons[str(server)]['rewards']
                    seasons[str(server)]['rewards'] = {}
                    for i in range(1, 41):
                        seasons[str(server)]['rewards'][str(i)] = {}

                    seasons[str(server)]["isOn"] = False
                    seasons[str(server)]["name"] = ""
                    seasons[str(server)]["date"] = ""
                    seasons[str(server)]["role"] = ""
                    seasons[str(server)]["price"] = -1

                    dbsave(seasons, 'seasons')

                    await msg.edit(embed=embed)

            except:
                embed = newErr('Letelt a v??laszt??si id??')
                embed.add_field(
                    name='A Season nem lett kikapcsolva',
                    value='** **'
                )

                await ctx.send(embed=embed)

        else:
            embed = newErr('Nincs akt??v season.')
            await ctx.send(embed=embed)


def dbload(name: str):
    with open('db/{}.json'.format(name), 'r') as f:
        return json.load(f)


def dbsave(db, name: str):
    with open('db/{}.json'.format(name), 'w') as f:
        json.dump(db, f)


async def update_db(self, db, user, serverId):
    if f'{serverId}' not in db:
        db[f'{serverId}'] = {}
    if f'{user.id}' not in db[f'{serverId}']:
        db[f'{serverId}'][f'{user.id}'] = {}
        db[f'{serverId}'][f'{user.id}']['exp'] = 0
        db[f'{serverId}'][f'{user.id}']['lvl'] = 0


async def addExp(self, db, user, server):
    serverId = server.id
    lvlCurrent = db[f'{serverId}'][f'{user.id}']['lvl']

    if str(user.id) in db[str(serverId)]:
        users = dbload('users')
        users[str(server.id)][str(user.id)]['plankpass'] = True
        dbsave(users, 'users')

    if lvlCurrent < 40:
        db[f'{serverId}'][f'{user.id}']['exp'] += randint(5, 10)
        lvlUpXp = 40 * lvlCurrent * lvlCurrent - 30 * lvlCurrent

        if db[f'{serverId}'][f'{user.id}']['exp'] >= lvlUpXp:
            pfx = dbload('prefixes')
            reward = dbload('seasons')[str(serverId)]['rewards'][str(lvlCurrent + 1)]

            db[str(serverId)][str(user.id)]['lvl'] += 1

            embed = discord.Embed(title='Tier l??p??s', description="", color=0x8a7c74)
            embed.set_author(name=user, url="https://discord.com/users/{}".format(user.id))
            embed.set_thumbnail(url=user.avatar_url)
            embed.add_field(name='??j tier: ', value=lvlCurrent + 1, inline=False)

            if hasPP(user, server):
                if not len(reward) == 0:
                    if reward['type'] == 'role':
                        role = server.get_role(reward["id"])
                        if role is not None:
                            embed.add_field(name='Megkaptad a k??vetkez?? rangot', value=role.mention, inline=False)
                            await user.add_roles(role)
                        else:
                            print('Season rang hiba... {}'.format(reward["id"]))
                            embed.add_field(name='Hiba t??rt??nt.',
                                            value="Nem kaptad meg a rangot. K??rlek ezt jelezd egy szerver admin fel??.")
                        embed.add_field(name='Megkaptad a k??vetkez?? rangot', value=role.mention, inline=False)
                    elif reward['type'] == 'bal':
                        users = dbload('users')
                        users[str(serverId)][str(user.id)]['bal'] += reward['amount']
                        dbsave(users, 'users')
                        embed.add_field(name='Kapt??l',
                                        value='{}<:plancoin:799180662166781992>'.format(reward['amount']), inline=False)
                    elif reward['type'] == "card":
                        users = dbload('users')
                        id = reward['id']
                        name = reward['name']
                        desc = reward['desc']
                        users[str(serverId)][str(user.id)]['cards'][id] = {}
                        users[str(serverId)][str(user.id)]['cards'][id]['name'] = name
                        users[str(serverId)][str(user.id)]['cards'][id]['desc'] = desc
                        users[str(serverId)][str(user.id)]['cards'][id]['id'] = id
                        dbsave(users, 'users')
                        embed.add_field(name='Speci??lis k??rtya el??rve', value='{}\n{}'.format(name, desc), inline=False)

                channel = None
                isChnl = False

                if 'lvlChnl' in pfx[f'{serverId}']:
                    channel = self.bot.get_channel(pfx[f'{serverId}']['lvlChnl'])
                    isChnl = True

                del pfx

                if isChnl == True:
                    await channel.send(user.mention, embed=embed)


def hasPP(user: discord.Member, server: discord.Guild):
    users = dbload('users')

    if users[str(server.id)][str(user.id)]['plankpass']:
        return True
    else:
        return False


def newErr(reason: str):
    embed = discord.Embed(title='Hiba', description=reason, color=0xff0000)
    embed.set_thumbnail(url='https://imgur.com/CAc2Sar.png')
    return embed


def setup(bot):
    bot.add_cog(SeasonSystem(bot))
