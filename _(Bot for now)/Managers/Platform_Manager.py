import platform
import discord
import datetime
from pathlib import Path
import sys
import psutil
import datetime

def Get_Full_Path(path):
    return (Path(__file__).parent / path).resolve()

def Get_Platform():
    return platform.system()

def format_bytes(size):
    # Bytes in lesbare Größen umwandeln
    power = 1024
    n = 0
    units = ["B", "KB", "MB", "GB", "TB", "PB"]
    while size >= power and n < len(units) - 1:
        size /= power
        n += 1
    return f"{size:.2f} {units[n]}"

def get_stats():
    boot_time = datetime.datetime.fromtimestamp(psutil.boot_time())
    cpu_percent_per_core = psutil.cpu_percent(interval=1, percpu=True)
    cpu_percent_total = sum(cpu_percent_per_core) / len(cpu_percent_per_core)
    disk_io = psutil.disk_io_counters()
    swap = psutil.swap_memory()
    virtual_mem = psutil.virtual_memory()

    return {
        "🖥️ System": {
            "🧩 Platform": platform.system(),
            "📦 Release": platform.release(),
            "📜 Version": platform.version(),
            "🏗️ Architecture": platform.machine(),
            "⏰ Boot Time": boot_time.strftime("%Y-%m-%d %H:%M:%S"),
            "⏳ Uptime": str(datetime.datetime.now() - boot_time).split('.')[0],
            "💻 Hostname": platform.node(),
            "🐍 Python Version": sys.version.split()[0],
            "⚙️ Python Compiler": platform.python_compiler(),
        },
        "🧠 CPU": {
            "⚙️ Physical Cores": psutil.cpu_count(logical=False),
            "🔢 Logical Cores": psutil.cpu_count(logical=True),
            "📊 Usage (%)": cpu_percent_total,
            "🧮 Cores Usage (%)": {f"Core {i}": usage for i, usage in enumerate(cpu_percent_per_core)},
            "📈 Load Average": psutil.getloadavg(),
        },
        "🗄️ Memory": {
            "Total": virtual_mem.total,
            "Available": virtual_mem.available,
            "Used": virtual_mem.used,
            "Free": virtual_mem.free,
            "Percent Used": virtual_mem.percent,
            "Swap Total": swap.total,
            "Swap Used": swap.used,
            "Swap Free": swap.free,
            "Swap Percent": swap.percent
        },
        "💽 Disk": {
            "Total": psutil.disk_usage('/').total,
            "Used": psutil.disk_usage('/').used,
            "Free": psutil.disk_usage('/').free,
            "Percent": psutil.disk_usage('/').percent,
            "Reads": disk_io.read_count,
            "Writes": disk_io.write_count,
            "Read Bytes": disk_io.read_bytes,
            "Write Bytes": disk_io.write_bytes
        },
        "🌐 Network": {
            "Bytes Sent": psutil.net_io_counters().bytes_sent,
            "Bytes Received": psutil.net_io_counters().bytes_recv,
            "Packets Sent": psutil.net_io_counters().packets_sent,
            "Packets Received": psutil.net_io_counters().packets_recv,
        }
    }


def create_embed():
    stats = get_stats()
    embed = discord.Embed(title="📊 Live System Stats", color=discord.Color.blue())

    for section, values in stats.items():
        formatted = ""

        # Spezielle Formatierung für bestimmte Sektionen und Werte:
        if section == "🗄️ Memory":
            # Speicherwerte in lesbarer Einheit
            formatted += (
                f"**Total:** {format_bytes(values['Total'])}\n"
                f"**Available:** {format_bytes(values['Available'])}\n"
                f"**Used:** {format_bytes(values['Used'])}\n"
                f"**Free:** {format_bytes(values['Free'])}\n"
                f"**Percent Used:** {values['Percent Used']}%\n\n"
                f"**Swap Total:** {format_bytes(values['Swap Total'])}\n"
                f"**Swap Used:** {format_bytes(values['Swap Used'])}\n"
                f"**Swap Free:** {format_bytes(values['Swap Free'])}\n"
                f"**Swap Percent:** {values['Swap Percent']}%\n"
            )
        elif section == "💽 Disk":
            formatted += (
                f"**Total:** {format_bytes(values['Total'])}\n"
                f"**Used:** {format_bytes(values['Used'])}\n"
                f"**Free:** {format_bytes(values['Free'])}\n"
                f"**Percent:** {values['Percent']}%\n\n"
                f"**Reads:** {values['Reads']}\n"
                f"**Writes:** {values['Writes']}\n"
                f"**Read Bytes:** {format_bytes(values['Read Bytes'])}\n"
                f"**Write Bytes:** {format_bytes(values['Write Bytes'])}\n"
            )
        elif section == "🌐 Network":
            formatted += (
                f"**Bytes Sent:** {format_bytes(values['Bytes Sent'])}\n"
                f"**Bytes Received:** {format_bytes(values['Bytes Received'])}\n"
                f"**Packets Sent:** {values['Packets Sent']}\n"
                f"**Packets Received:** {values['Packets Received']}\n"
            )
        else:
            # Für alle anderen Sektionen allgemeine Ausgabe
            for key, value in values.items():
                if isinstance(value, dict):
                    formatted += f"**{key}**:\n"
                    for sub_key, sub_val in value.items():
                        formatted += f"- {sub_key}: {sub_val}\n"
                elif isinstance(value, list) or isinstance(value, set):
                    formatted += f"**{key}**:\n" + ", ".join(str(v) for v in value) + "\n"
                else:
                    # Prozentangaben schön formatieren
                    if isinstance(value, float):
                        formatted += f"**{key}**: {value:.2f}\n"
                    else:
                        formatted += f"**{key}**: {value}\n"

        # Discord-Embed-Feldgröße beachten (max 1024 Zeichen)
        for i in range(0, len(formatted), 1024):
            embed.add_field(
                name=section if i == 0 else f"{section} (cont.)",
                value=formatted[i:i+1024],
                inline=False,
            )

    embed.set_footer(text="Updated every 2 seconds")
    embed.timestamp = discord.utils.utcnow()
    return embed
