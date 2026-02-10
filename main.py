import discord
from discord import app_commands
import tempfile
import os
import imageio
from PIL import Image

intents = discord.Intents.default()
intents.guilds = True
intents.dm_messages = True

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

@tree.command(name="gif", description="Convert a video or image into a GIF")
@app_commands.describe(file="Upload an mp4 or image file")

# Enables the command in:
# - servers (guilds=True)
# - DMs (dms=True)
# - group DMs (private_channels=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def gif(interaction: discord.Interaction, file: discord.Attachment):
    await interaction.response.defer(thinking=True)

    filename = (file.filename or "").lower()

    with tempfile.TemporaryDirectory() as tmp:
        input_path = os.path.join(tmp, "input")
        gif_path = os.path.join(tmp, "output.gif")

        try:
            await file.save(input_path)
        except Exception as e:
            await interaction.followup.send(f"Failed to download attachment: {e}")
            return

        try:
            if filename.endswith(".mp4"):
                reader = imageio.get_reader(input_path)
                frames = []

                for i, frame in enumerate(reader):
                    if i % 2 == 0:
                        img = Image.fromarray(frame)
                        new_w = 480
                        new_h = int(img.height * new_w / img.width)
                        img = img.resize((new_w, new_h))
                        frames.append(img)

                reader.close()

                if not frames:
                    await interaction.followup.send("Video had no readable frames.")
                    return

                frames[0].save(
                    gif_path,
                    save_all=True,
                    append_images=frames[1:],
                    duration=50,
                    loop=0
                )

            elif filename.endswith((".png", ".jpg", ".jpeg", ".webp")):
                img = Image.open(input_path).convert("RGBA")
                img.save(gif_path, format="GIF")

            else:
                await interaction.followup.send("Unsupported file type. Use .mp4, .png, .jpg, .jpeg, or .webp")
                return

        except Exception as e:
            await interaction.followup.send(f"Conversion failed: {e}")
            return

        new_name = "Gif Made By @kevin_is_cool.gif"
        await interaction.followup.send(file=discord.File(gif_path, filename=new_name))

@client.event
async def on_ready():
    try:
        await tree.sync()
        print("Commands synced globally (servers + DMs).")
    except Exception as e:
        print("Sync failed:", e)

    print(f"Logged in as {client.user}")

client.run("MTQ3MDM1MjE4MDc4NjQ5NTU4MQ.GiD6ed.cUynsXf7M6L6NYn6L2W7Qp0EWm-gv3ynmejUH0")
