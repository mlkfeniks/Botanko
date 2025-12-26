import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
import json
import random

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='฿ ', intents=intents)

# Файлы для хранения данных
DATA_FILE = 'user_data.json'
CONFIG_FILE = 'config.json'
CASES_FILE = 'cases.json'
ITEMS_FILE = 'items.json'

def load_data():
    """Загрузка данных пользователей"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_data(data):
    """Сохранение данных пользователей"""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def load_config():
    """Загрузка конфигурации сервера"""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        'currency_symbol': '฿',
        'currency_name': 'батов'
    }

def save_config(config):
    """Сохранение конфигурации"""
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=4)

def load_cases():
    """Загрузка кейсов"""
    if os.path.exists(CASES_FILE):
        with open(CASES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_cases(cases):
    """Сохранение кейсов"""
    with open(CASES_FILE, 'w', encoding='utf-8') as f:
        json.dump(cases, f, ensure_ascii=False, indent=4)

def load_items():
    """Загрузка предметов"""
    if os.path.exists(ITEMS_FILE):
        with open(ITEMS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_items(items):
    """Сохранение предметов"""
    with open(ITEMS_FILE, 'w', encoding='utf-8') as f:
        json.dump(items, f, ensure_ascii=False, indent=4)

user_data = load_data()
config = load_config()
cases = load_cases()
items_db = load_items()

# Инициализация инвентаря пользователя
def init_user_inventory(user_id):
    """Инициализация инвентаря пользователя"""
    if 'inventory' not in user_data[user_id]:
        user_data[user_id]['inventory'] = []
    if 'luck_boost' not in user_data[user_id]:
        user_data[user_id]['luck_boost'] = 0

class RulesView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label='Я согласен с правилами', style=discord.ButtonStyle.green, custom_id='accept_rules')
    async def accept_rules(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_id = str(interaction.user.id)
        
        if user_id in user_data:
            await interaction.response.send_message('Вы уже авторизованы!', ephemeral=True)
            return
        
        money_ranges = [
            (500, 1000, 40),
            (1001, 5000, 30),
            (5001, 10000, 20),
            (10001, 15000, 7),
            (15001, 20000, 3)
        ]
        
        chosen_range = random.choices(
            money_ranges,
            weights=[r[2] for r in money_ranges]
        )[0]
        
        money = random.randint(chosen_range[0], chosen_range[1])
        
        user_data[user_id] = {
            'username': interaction.user.name,
            'money': money,
            'inventory': [],
            'luck_boost': 0
        }
        save_data(user_data)
        
        role_name = "Участник"
        role = discord.utils.get(interaction.guild.roles, name=role_name)
        
        if role:
            await interaction.user.add_roles(role)
            await interaction.response.send_message(
                f'🎉 **Поздравляем!**\n\n'
                f'Вы успешно авторизованы!\n'
                f'Вам выпало: **{money:,} {config["currency_symbol"]}**\n'
                f'Роль "{role_name}" была выдана!',
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                f'🎉 **Поздравляем!**\n\n'
                f'Вы успешно авторизованы!\n'
                f'Вам выпало: **{money:,} {config["currency_symbol"]}**\n\n'
                f'⚠️ Роль "{role_name}" не найдена на сервере.',
                ephemeral=True
            )

@bot.event
async def on_ready():
    print(f'Бот {bot.user} успешно запущен!')
    bot.add_view(RulesView())

@bot.command(name='Model')
async def Model(ctx):
    await ctx.send(f'Эта модель Botanko P.I.S.A Edition созданная @feniks3013 в 2025 году')

@bot.command(name='setup_rules')
@commands.has_permissions(administrator=True)
async def setup_rules(ctx):
    """Команда для отправки правил с кнопкой (только для администраторов)"""
    embed = discord.Embed(
        title="📜 Правила сервера",
        description=(
            "**1.** Будьте вежливы и уважайте других участников\n"
            "**2.** Запрещены оскорбления, спам и флуд\n"
            "**3.** Не распространяйте личную информацию\n"
            "**4.** Следуйте указаниям модераторов\n"
            "**5.** Запрещена реклама без разрешения\n"
            "**6.** Используйте каналы по назначению\n\n"
            "Нажмите кнопку ниже, чтобы согласиться с правилами и получить доступ к серверу!"
        ),
        color=discord.Color.blue()
    )
    embed.set_footer(text="Нажимая кнопку, вы соглашаетесь с правилами сервера")
    
    await ctx.send(embed=embed, view=RulesView())
    await ctx.message.delete()

@bot.command(name='balance')
async def balance(ctx, member: discord.Member = None):
    """Проверить баланс свой или другого участника"""
    target = member or ctx.author
    user_id = str(target.id)
    
    if user_id in user_data:
        money = user_data[user_id]['money']
        await ctx.send(f'💰 Баланс {target.mention}: **{money:,} {config["currency_symbol"]}**')
    else:
        await ctx.send(f'{target.mention} еще не авторизован на сервере!')

@bot.command(name='top')
async def top(ctx):
    """Топ 10 самых богатых участников"""
    if not user_data:
        await ctx.send('Пока нет авторизованных участников!')
        return
    
    sorted_users = sorted(user_data.items(), key=lambda x: x[1]['money'], reverse=True)[:10]
    
    embed = discord.Embed(
        title="💎 Топ 10 богатейших участников",
        color=discord.Color.gold()
    )
    
    medals = ['🥇', '🥈', '🥉']
    
    for idx, (user_id, data) in enumerate(sorted_users, 1):
        medal = medals[idx-1] if idx <= 3 else f'**{idx}.**'
        embed.add_field(
            name=f'{medal} {data["username"]}',
            value=f'💰 {data["money"]:,} {config["currency_symbol"]}',
            inline=False
        )
    
    await ctx.send(embed=embed)

@bot.command(name='reset_user')
@commands.has_permissions(administrator=True)
async def reset_user(ctx, member: discord.Member):
    """Сбросить авторизацию пользователя (только для администраторов)"""
    user_id = str(member.id)
    
    if user_id in user_data:
        del user_data[user_id]
        save_data(user_data)
        
        role_name = "Участник"
        role = discord.utils.get(ctx.guild.roles, name=role_name)
        if role in member.roles:
            await member.remove_roles(role)
        
        await ctx.send(f'✅ Авторизация {member.mention} была сброшена!')
    else:
        await ctx.send(f'{member.mention} не найден в базе данных!')

@bot.command(name='set_currency')
@commands.has_permissions(administrator=True)
async def set_currency(ctx, symbol: str, *, name: str = None):
    """Изменить символ и название валюты (только для администраторов)"""
    global config
    
    config['currency_symbol'] = symbol
    if name:
        config['currency_name'] = name
    
    save_config(config)
    
    if name:
        await ctx.send(f'✅ Валюта изменена!\n💰 Символ: **{symbol}**\n📝 Название: **{name}**')
    else:
        await ctx.send(f'✅ Символ валюты изменён на: **{symbol}**')

@bot.command(name='currency_info')
async def currency_info(ctx):
    """Показать текущую валюту сервера"""
    embed = discord.Embed(
        title="💰 Информация о валюте",
        color=discord.Color.green()
    )
    embed.add_field(name="Символ", value=config['currency_symbol'], inline=True)
    embed.add_field(name="Название", value=config['currency_name'], inline=True)
    await ctx.send(embed=embed)

# ============= СИСТЕМА КЕЙСОВ =============

@bot.command(name='create_case')
@commands.has_permissions(administrator=True)
async def create_case(ctx, name: str, price: int):
    """Создать новый кейс
    Использование: ฿ create_case "Деревянный_ящик" 1000"""
    if name in cases:
        await ctx.send(f'❌ Кейс с названием **{name}** уже существует!')
        return
    
    cases[name] = {
        'price': price,
        'rewards': []
    }
    save_cases(cases)
    
    await ctx.send(f'✅ Кейс **{name}** создан!\n💰 Цена: **{price} {config["currency_symbol"]}**\n\nТеперь добавьте награды командой `฿ add_reward`')

@bot.command(name='add_reward')
@commands.has_permissions(administrator=True)
async def add_reward(ctx, case_name: str, reward_type: str, reward_name: str, chance: int):
    """Добавить награду в кейс
    Типы: role (роль) или item (предмет)
    Использование: ฿ add_reward "Деревянный_ящик" role "VIP" 10
    Или: ฿ add_reward "Деревянный_ящик" item "Золотое_яблоко" 30"""
    
    if case_name not in cases:
        await ctx.send(f'❌ Кейс **{case_name}** не найден!')
        return
    
    if reward_type not in ['role', 'item']:
        await ctx.send('❌ Тип награды должен быть `role` или `item`!')
        return
    
    if chance < 1 or chance > 100:
        await ctx.send('❌ Шанс должен быть от 1 до 100!')
        return
    
    cases[case_name]['rewards'].append({
        'type': reward_type,
        'name': reward_name,
        'chance': chance
    })
    save_cases(cases)
    
    await ctx.send(f'✅ Награда добавлена в кейс **{case_name}**!\n🎁 Тип: **{reward_type}**\n📝 Название: **{reward_name}**\n🎲 Шанс: **{chance}%**')

@bot.command(name='cases')
async def show_cases(ctx):
    """Показать все доступные кейсы"""
    if not cases:
        await ctx.send('📦 Пока нет доступных кейсов!')
        return
    
    embed = discord.Embed(
        title="📦 Магазин кейсов",
        description="Доступные кейсы для покупки:",
        color=discord.Color.purple()
    )
    
    for case_name, case_data in cases.items():
        rewards_text = ""
        if case_data['rewards']:
            for reward in case_data['rewards']:
                emoji = "👑" if reward['type'] == 'role' else "🎁"
                rewards_text += f"{emoji} {reward['name']} - {reward['chance']}%\n"
        else:
            rewards_text = "Нет наград"
        
        embed.add_field(
            name=f"📦 {case_name}",
            value=f"💰 Цена: **{case_data['price']} {config['currency_symbol']}**\n{rewards_text}",
            inline=False
        )
    
    await ctx.send(embed=embed)

@bot.command(name='buy_case')
async def buy_case(ctx, *, case_name: str):
    """Купить и открыть кейс
    Использование: ฿ buy_case Деревянный_ящик"""
    user_id = str(ctx.author.id)
    
    if user_id not in user_data:
        await ctx.send('❌ Вы не авторизованы! Пройдите авторизацию сначала.')
        return
    
    if case_name not in cases:
        await ctx.send(f'❌ Кейс **{case_name}** не найден!')
        return
    
    case = cases[case_name]
    init_user_inventory(user_id)
    
    if user_data[user_id]['money'] < case['price']:
        await ctx.send(f'❌ Недостаточно средств! Нужно: **{case["price"]} {config["currency_symbol"]}**')
        return
    
    if not case['rewards']:
        await ctx.send(f'❌ В кейсе **{case_name}** нет наград!')
        return
    
    # Вычитаем деньги
    user_data[user_id]['money'] -= case['price']
    
    # Применяем буст удачи
    luck_boost = user_data[user_id]['luck_boost']
    
    # Открываем кейс с учетом удачи
    rewards_with_luck = []
    for reward in case['rewards']:
        boosted_chance = min(reward['chance'] + luck_boost, 100)
        rewards_with_luck.append((reward, boosted_chance))
    
    # Выбираем награду
    roll = random.randint(1, 100)
    cumulative = 0
    won_reward = None
    
    # Сортируем по шансу (от меньшего к большему)
    sorted_rewards = sorted(rewards_with_luck, key=lambda x: x[1])
    
    for reward, chance in sorted_rewards:
        cumulative += chance
        if roll <= cumulative:
            won_reward = reward
            break
    
    if not won_reward:
        won_reward = sorted_rewards[-1][0]  # Если ничего не выпало, даем самый частый предмет
    
    # Выдаем награду
    if won_reward['type'] == 'role':
        role = discord.utils.get(ctx.guild.roles, name=won_reward['name'])
        if role:
            await ctx.author.add_roles(role)
            result_text = f"👑 Роль: **{won_reward['name']}**"
        else:
            result_text = f"⚠️ Роль **{won_reward['name']}** не найдена на сервере"
    else:
        user_data[user_id]['inventory'].append({
            'name': won_reward['name'],
            'type': 'custom'
        })
        result_text = f"🎁 Предмет: **{won_reward['name']}**"
    
    save_data(user_data)
    
    embed = discord.Embed(
        title=f"📦 Открытие кейса: {case_name}",
        description=f"{ctx.author.mention} открыл кейс!",
        color=discord.Color.gold()
    )
    embed.add_field(name="🎉 Вы получили:", value=result_text, inline=False)
    embed.add_field(name="💰 Потрачено:", value=f"{case['price']} {config['currency_symbol']}", inline=True)
    embed.add_field(name="💰 Остаток:", value=f"{user_data[user_id]['money']} {config['currency_symbol']}", inline=True)
    if luck_boost > 0:
        embed.add_field(name="🍀 Буст удачи:", value=f"+{luck_boost}%", inline=True)
    
    await ctx.send(embed=embed)

# ============= СИСТЕМА ПРЕДМЕТОВ =============

@bot.command(name='create_item')
@commands.has_permissions(administrator=True)
async def create_item(ctx, name: str, item_type: str, luck_amount: int = 0):
    """Создать новый предмет
    Типы: normal (обычный, дает удачу) или custom (кастомный, сувенир)
    Использование: ฿ create_item "Золотое_яблоко" normal 5
    Или: ฿ create_item "Памятная_монета" custom"""
    
    if item_type not in ['normal', 'custom']:
        await ctx.send('❌ Тип должен быть `normal` или `custom`!')
        return
    
    items_db[name] = {
        'type': item_type,
        'luck_amount': luck_amount if item_type == 'normal' else 0
    }
    save_items(items_db)
    
    if item_type == 'normal':
        await ctx.send(f'✅ Обычный предмет **{name}** создан!\n🍀 Дает удачи: **+{luck_amount}%**')
    else:
        await ctx.send(f'✅ Кастомный предмет **{name}** создан!')

@bot.command(name='inventory')
async def inventory(ctx, member: discord.Member = None):
    """Показать инвентарь"""
    target = member or ctx.author
    user_id = str(target.id)
    
    if user_id not in user_data:
        await ctx.send(f'{target.mention} еще не авторизован на сервере!')
        return
    
    init_user_inventory(user_id)
    
    inv = user_data[user_id]['inventory']
    luck = user_data[user_id]['luck_boost']
    
    embed = discord.Embed(
        title=f"🎒 Инвентарь {target.display_name}",
        color=discord.Color.blue()
    )
    
    if luck > 0:
        embed.add_field(name="🍀 Активная удача", value=f"+{luck}%", inline=False)
    
    if not inv:
        embed.description = "Инвентарь пуст"
    else:
        normal_items = [item for item in inv if item.get('type') == 'normal']
        custom_items = [item for item in inv if item.get('type') == 'custom']
        
        if normal_items:
            normal_text = "\n".join([f"🍎 {item['name']}" for item in normal_items])
            embed.add_field(name="📦 Обычные предметы", value=normal_text, inline=False)
        
        if custom_items:
            custom_text = "\n".join([f"💎 {item['name']}" for item in custom_items])
            embed.add_field(name="🎁 Кастомные предметы", value=custom_text, inline=False)
    
    await ctx.send(embed=embed)

@bot.command(name='consume')
async def consume(ctx, *, item_name: str):
    """Использовать обычный предмет для увеличения удачи
    Использование: ฿ consume Золотое_яблоко"""
    user_id = str(ctx.author.id)
    
    if user_id not in user_data:
        await ctx.send('❌ Вы не авторизованы!')
        return
    
    init_user_inventory(user_id)
    
    # Ищем предмет в инвентаре
    item_found = None
    for i, item in enumerate(user_data[user_id]['inventory']):
        if item['name'].lower() == item_name.lower() and item.get('type') == 'normal':
            item_found = (i, item)
            break
    
    if not item_found:
        await ctx.send(f'❌ У вас нет обычного предмета **{item_name}** в инвентаре!')
        return
    
    idx, item = item_found
    
    # Получаем информацию о предмете
    if item_name in items_db:
        luck_gain = items_db[item_name]['luck_amount']
    else:
        luck_gain = 5  # По умолчанию
    
    # Удаляем предмет и даем удачу
    user_data[user_id]['inventory'].pop(idx)
    user_data[user_id]['luck_boost'] += luck_gain
    save_data(user_data)
    
    await ctx.send(f'✅ Вы использовали **{item_name}**!\n🍀 Ваша удача увеличена на **+{luck_gain}%**\n💫 Текущая удача: **+{user_data[user_id]["luck_boost"]}%**')

@bot.command(name='give_item')
@commands.has_permissions(administrator=True)
async def give_item(ctx, member: discord.Member, item_type: str, *, item_name: str):
    """Выдать предмет игроку
    Использование: ฿ give_item @user normal Золотое_яблоко
    Или: ฿ give_item @user custom Памятная_монета"""
    user_id = str(member.id)
    
    if user_id not in user_data:
        await ctx.send(f'❌ {member.mention} не авторизован!')
        return
    
    if item_type not in ['normal', 'custom']:
        await ctx.send('❌ Тип должен быть `normal` или `custom`!')
        return
    
    init_user_inventory(user_id)
    
    user_data[user_id]['inventory'].append({
        'name': item_name,
        'type': item_type
    })
    save_data(user_data)
    
    await ctx.send(f'✅ Предмет **{item_name}** ({item_type}) выдан {member.mention}!')

# Запуск бота
bot.run(token, log_handler=handler)
