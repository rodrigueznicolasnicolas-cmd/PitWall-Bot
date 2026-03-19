import discord
from discord.ext import commands
import requests
import config # 1. Importamos tu nueva caja fuerte
import os
from keep_alive import keep_alive # 1. Importamos el motor falso

# --- CONFIGURACIÓN DEL MONOPLAZA ---
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='/', intents=intents)

@bot.event
async def on_ready():
    print(f'🟢 ¡Semáforo en verde! {bot.user.name} está conectado y listo en el Pit Wall.')

# --- COMANDO 1: PRÓXIMA CARRERA ---
@bot.command(name='proxima-carrera')
async def proxima_carrera(ctx):
    url = "https://api.jolpi.ca/ergast/f1/current/next.json"
    
    try:
        respuesta = requests.get(url)
        datos = respuesta.json()
        
        carrera = datos['MRData']['RaceTable']['Races'][0]
        nombre_gp = carrera['raceName']
        circuito = carrera['Circuit']['circuitName']
        fecha = carrera['date']
        hora = carrera['time'].replace('Z', ' UTC')
        
        tarjeta = discord.Embed(
            title=f"🏎️ Próxima parada: {nombre_gp}",
            description="¡Preparen sus setups, ajusten la aerodinámica y que gane el mejor en la pista!",
            color=discord.Color.gold()
        )
        
        tarjeta.add_field(name="📍 Circuito", value=circuito, inline=False)
        tarjeta.add_field(name="📅 Fecha", value=fecha, inline=True)
        tarjeta.add_field(name="⏰ Hora", value=hora, inline=True)
        tarjeta.set_footer(text="Datos oficiales extraídos por PitWall Bot 🏁")
        
        await ctx.send(embed=tarjeta)
        
    except Exception as e:
        await ctx.send("🔧 ¡Bandera roja! Tuvimos un problema conectando con la telemetría.")

# --- COMANDO 2: TABLA DEL CAMPEONATO ---
@bot.command(name='campeonato')
async def campeonato(ctx):
    url = "https://api.jolpi.ca/ergast/f1/current/driverStandings.json"
    
    try:
        respuesta = requests.get(url)
        datos = respuesta.json()
        
        pilotos = datos['MRData']['StandingsTable']['StandingsLists'][0]['DriverStandings']
        
        tarjeta_campeonato = discord.Embed(
            title="🏆 Campeonato Mundial de Pilotos (Top 10)",
            description="Así va la batalla por el título mundial:",
            color=discord.Color.blue()
        )
        
        texto_tabla = ""
        
        for i in range(10): 
            piloto = pilotos[i]
            posicion = piloto['position']
            nombre = f"{piloto['Driver']['givenName']} {piloto['Driver']['familyName']}"
            equipo = piloto['Constructors'][0]['name']
            puntos = piloto['points']
            
            texto_tabla += f"**{posicion}.** {nombre} *({equipo})* - **{puntos} pts**\n"
            
        tarjeta_campeonato.add_field(name="Posiciones Actuales", value=texto_tabla, inline=False)
        tarjeta_campeonato.set_footer(text="Datos oficiales extraídos por PitWall Bot 🏁")
        
        await ctx.send(embed=tarjeta_campeonato)
        
    except Exception as e:
        await ctx.send("🔧 ¡Bandera roja! No pudimos cargar la tabla del campeonato.")

        # --- COMANDO 3: TABLA DE ESCUDERÍAS (CONSTRUCTORES) ---
@bot.command(name='escuderias')
async def escuderias(ctx):
    # La URL cambia para pedir los datos de los constructores
    url = "https://api.jolpi.ca/ergast/f1/current/constructorStandings.json"
    
    try:
        respuesta = requests.get(url)
        datos = respuesta.json()
        
        equipos = datos['MRData']['StandingsTable']['StandingsLists'][0]['ConstructorStandings']
        
        tarjeta_equipos = discord.Embed(
            title="🏭 Campeonato Mundial de Escuderías",
            description="La batalla de los ingenieros y el muro de pits:",
            color=discord.Color.red() # Color rojo/técnico para escuderías
        )
        
        texto_tabla = ""
        
        # Leemos el Top 10 de equipos
        for i in range(min(10, len(equipos))): 
            equipo = equipos[i]
            posicion = equipo['position']
            nombre = equipo['Constructor']['name']
            puntos = equipo['points']
            victorias = equipo['wins']
            
            texto_tabla += f"**{posicion}.** {nombre} - **{puntos} pts** *(Victorias: {victorias})*\n"
            
        tarjeta_equipos.add_field(name="Posiciones Actuales", value=texto_tabla, inline=False)
        tarjeta_equipos.set_footer(text="Datos oficiales extraídos por PitWall Bot 🏁")
        
        await ctx.send(embed=tarjeta_equipos)
        
    except Exception as e:
        await ctx.send("🔧 ¡Bandera roja! No pudimos cargar la tabla de escuderías.")
        keep_alive()

# --- 2. ENCENDIDO DEL MOTOR ---
# El bot lee el Token desde el archivo config.py
bot.run(config.TOKEN)